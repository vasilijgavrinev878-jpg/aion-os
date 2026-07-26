"""
AION Invite Machine v2 — Node Client
Runs on team laptops. Each node has its own IP + Telegram accounts.
Pulls campaigns from central server, invites locally, reports back.
"""
import asyncio
import json
import os
import sys
import random
import time
import uuid
import argparse
import threading
import logging
from datetime import datetime, date, timedelta
from pathlib import Path

import urllib.request
import urllib.error

os.environ["PYTHONIOENCODING"] = "utf-8"
from aion_engine import (
    init_db, get_conn, get_daily_limits, get_daily_used, inc_daily,
    save_account, get_healthy_accounts, mark_account_banned,
    update_account_warmup, get_conn, get_stats, WARMUP_PROFILES,
    AccountManager, InviteEngine, CampaignScheduler
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("node.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("aion-node")

DATA_DIR = Path("node_data")
DATA_DIR.mkdir(exist_ok=True)
CONFIG_PATH = DATA_DIR / "config.json"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def api_call(server_url, endpoint, method="GET", data=None):
    url = f"{server_url.rstrip('/')}{endpoint}"
    headers = {"Content-Type": "application/json"}
    cfg = load_config()
    token = cfg.get("token", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else "{}"
        log.error(f"API {method} {endpoint}: {e.code} {body}")
        return None
    except Exception as e:
        log.error(f"API {method} {endpoint}: {e}")
        return None


class Node:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip("/")
        self.cfg = load_config()
        self.node_id = self.cfg.get("node_id", f"node-{uuid.uuid4().hex[:6]}")
        self.token = self.cfg.get("token", "")
        self.am = AccountManager(self.node_id)
        self._stop = False

    def register(self):
        """Register or authenticate with server."""
        if not self.token:
            log.info(f"Registering node {self.node_id} with server...")
            result = api_call(self.server_url, "/api/node/register", "POST", {
                "node_id": self.node_id,
                "name": self.cfg.get("name", self.node_id),
                "version": "2.0"
            })
            if result and result.get("token"):
                self.token = result["token"]
                self.cfg["node_id"] = self.node_id
                self.cfg["token"] = self.token
                save_config(self.cfg)
                log.info(f"Registered! Node ID: {self.node_id}")
                return True
            else:
                log.error("Failed to register with server")
                return False
        return True

    def heartbeat(self):
        """Send heartbeat to server."""
        accounts = get_healthy_accounts(self.node_id)
        stats = get_stats()
        result = api_call(self.server_url, "/api/node/heartbeat", "POST", {
            "accounts_count": len(accounts),
            "invites_count": stats.get("today_add", 0),
        })
        return result is not None

    def fetch_campaigns(self):
        """Get active campaigns from server."""
        result = api_call(self.server_url, "/api/node/tasks", "GET")
        if result and result.get("campaigns"):
            return result["campaigns"]
        return []

    def report_stats(self):
        """Send local stats back to server."""
        accounts = get_healthy_accounts(self.node_id)
        stats = get_stats()
        account_data = []
        for acc in accounts:
            dm_used = get_daily_used(acc["phone"], "dm")
            add_used = get_daily_used(acc["phone"], "add")
            account_data.append({
                "phone": acc["phone"],
                "dm": acc.get("total_dm", 0) + dm_used,
                "added": acc.get("total_added", 0) + add_used,
                "status": acc["status"]
            })
        api_call(self.server_url, "/api/node/stats/report", "POST", {
            "stats": {"accounts": account_data}
        })

    async def run_account_setup(self):
        """Interactive setup: add Telegram accounts on this node."""
        print("\n=== AION Node — Account Setup ===")
        print("Add Telegram accounts that will be used on THIS laptop.")
        print("Each account will register/authenticate via Telethon.\n")

        while True:
            phone = input("Phone (+84... or empty to finish): ").strip()
            if not phone:
                break
            api_id = input("API ID (my.telegram.org): ").strip()
            api_hash = input("API Hash: ").strip()
            proxy = input("Proxy (optional, format: type:ip:port or Enter to skip): ").strip()

            save_account(phone, int(api_id), api_hash, node_id=self.node_id)

            # Authenticate via Telethon
            try:
                client = await self.am.create_client({
                    "phone": phone, "api_id": int(api_id),
                    "api_hash": api_hash, "proxy": proxy
                })
                me = await self.am.auth_client(client, phone)
                log.info(f"Account {phone} authorised as {me.first_name}")
                await client.disconnect()
            except Exception as e:
                log.error(f"Auth failed for {phone}: {e}")
                print(f"  Error: {e}")

            print()

        print("Setup complete. Accounts saved locally.")

    async def run_campaign_loop(self):
        """Main loop: fetch campaigns and run them."""
        campaigns = self.fetch_campaigns()
        if not campaigns:
            log.info("No active campaigns from server")
            return

        for campaign in campaigns:
            if self._stop:
                break

            accounts = get_healthy_accounts(self.node_id)
            if not accounts:
                log.warning("No healthy accounts on this node. Add accounts via setup.")
                break

            engine = InviteEngine(self.am, self.node_id, callback=lambda m: log.info(m))
            log.info(f"Running campaign: {campaign.get('name', campaign.get('city', '?'))}")
            await engine.run_campaign(campaign, accounts)

            # Report stats after each campaign
            self.report_stats()

    async def run(self):
        """Node main entry point."""
        if not self.register():
            log.error("Cannot start without server registration")
            return

        log.info(f"Node {self.node_id} connected to {self.server_url}")

        # Check if we have accounts
        accounts = get_healthy_accounts(self.node_id)
        if not accounts:
            log.info("No accounts on this node. Run setup.")
            await self.run_account_setup()
            accounts = get_healthy_accounts(self.node_id)

        # Heartbeat loop in background
        async def heartbeat_loop():
            while not self._stop:
                self.heartbeat()
                await asyncio.sleep(60)

        hb_task = asyncio.create_task(heartbeat_loop())

        # Main campaign loop
        try:
            while not self._stop:
                await self.run_campaign_loop()
                if not self._stop:
                    log.info("Waiting 5 minutes before next check...")
                    await asyncio.sleep(300)
        finally:
            self._stop = True
            hb_task.cancel()


def main():
    parser = argparse.ArgumentParser(description="AION Invite Node Client")
    parser.add_argument("--server", default="http://localhost:5000",
                        help="Central server URL")
    parser.add_argument("--setup", action="store_true",
                        help="Run interactive account setup")
    args = parser.parse_args()

    init_db()
    node = Node(args.server)

    if args.setup:
        asyncio.run(node.run_account_setup())
        return

    # Normal mode: connect and run
    try:
        asyncio.run(node.run())
    except KeyboardInterrupt:
        log.info("Node stopped by user")


if __name__ == "__main__":
    main()
