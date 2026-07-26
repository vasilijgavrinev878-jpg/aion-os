"""
AION Invite Machine v2 — Node Client
Local web GUI for team laptops. Each node runs Telegram accounts on its own IP.
Pulls campaigns from central server, invites locally, reports back.
"""
import asyncio
import json
import os
import sys
import uuid
import threading
import argparse
import logging
import urllib.request
import urllib.error
from datetime import datetime, date, timedelta
from pathlib import Path

from flask import Flask, render_template, request, jsonify, Response

os.environ["PYTHONIOENCODING"] = "utf-8"
from aion_engine import (
    init_db, get_conn, get_stats, get_daily_limits, get_daily_used,
    save_account, get_healthy_accounts, get_campaigns, mark_account_banned,
    update_account_warmup, register_node, node_heartbeat,
    AccountManager, InviteEngine, CampaignScheduler, WARMUP_PROFILES
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

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = uuid.uuid4().hex

_node_engine = None
_engine_thread = None
_log_lines = []


# ─── Config ──────────────────────────────────────────────

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def get_server_url():
    return load_config().get("server_url", "http://localhost:5000")

def get_token():
    return load_config().get("token", "")


# ─── Node API calls ─────────────────────────────────────

def api(endpoint, method="GET", data=None):
    url = f"{get_server_url().rstrip('/')}{endpoint}"
    headers = {"Content-Type": "application/json"}
    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = json.dumps(data).encode() if data else None
    try:
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log.warning(f"API {method} {endpoint}: {e}")
        return None


# ─── Log capture ────────────────────────────────────────

def push_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    _log_lines.append(f"[{ts}] {msg}")
    if len(_log_lines) > 500:
        _log_lines[:100] = []


# ─── Engine runner (background thread) ──────────────────

class NodeEngineRunner:
    def __init__(self):
        self._stop = False

    def stop(self):
        self._stop = True

    async def run(self):
        push_log("Node engine starting...")
        node_id = load_config().get("node_id", "unknown")

        while not self._stop:
            campaigns = api("/api/node/tasks")
            if not campaigns or not campaigns.get("campaigns"):
                push_log("No active campaigns from server")
                await asyncio.sleep(60)
                continue

            accounts = get_healthy_accounts(node_id)
            if not accounts:
                push_log("No healthy accounts on this node. Add accounts via web UI.")
                await asyncio.sleep(120)
                continue

            for campaign in campaigns["campaigns"]:
                if self._stop:
                    break

                am = AccountManager(node_id)
                engine = InviteEngine(am, node_id, push_log)
                name = campaign.get("name", campaign.get("city", "?"))
                push_log(f"Running campaign: {name}")

                try:
                    await engine.run_campaign(campaign, accounts)
                except Exception as e:
                    push_log(f"Campaign error: {e}")

                # Report back
                dm_today = 0
                add_today = 0
                for a in accounts:
                    dm_today += get_daily_used(a["phone"], "dm")
                    add_today += get_daily_used(a["phone"], "add")
                api("/api/node/stats/report", "POST", {
                    "stats": {"accounts": [
                        {"phone": a["phone"], "dm": a.get("total_dm", 0),
                         "added": a.get("total_added", 0), "status": a["status"]}
                        for a in accounts
                    ]}
                })
                await asyncio.sleep(10)

            if not self._stop:
                push_log("Cycle complete. Next check in 5 min...")
                await asyncio.sleep(300)

        push_log("Node engine stopped")

    def start(self):
        global _engine_thread
        if _engine_thread and _engine_thread.is_alive():
            return

        async def _run():
            await self.run()

        def target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_run())

        _engine_thread = threading.Thread(target=target, daemon=True)
        _engine_thread.start()
        push_log("Engine started in background")


# ─── Web Routes ─────────────────────────────────────────

@app.route("/")
def index():
    cfg = load_config()
    node_id = cfg.get("node_id", "not registered")
    server_url = cfg.get("server_url", "not set")
    return render_template("node.html", node_id=node_id, server_url=server_url)


@app.route("/api/status")
def api_status():
    cfg = load_config()
    node_id = cfg.get("node_id", "")
    accounts = get_healthy_accounts(node_id)
    stats = get_stats()
    running = _engine_thread is not None and _engine_thread.is_alive()
    return jsonify({
        "node_id": node_id,
        "server_url": cfg.get("server_url", ""),
        "registered": bool(cfg.get("token")),
        "running": running,
        "accounts": len(accounts),
        "stats": {
            "total": stats.get("total", 0),
            "dm_sent": stats.get("dm_sent", 0),
            "added": stats.get("added", 0),
            "today_dm": stats.get("today_dm", 0),
            "today_add": stats.get("today_add", 0),
            "errors": stats.get("errors", 0),
        }
    })


@app.route("/api/accounts", methods=["GET"])
def api_accounts():
    cfg = load_config()
    node_id = cfg.get("node_id", "")
    conn = get_conn()
    c = conn.cursor()
    if node_id:
        c.execute("SELECT * FROM accounts WHERE node_id=? ORDER BY total_dm DESC", (node_id,))
    else:
        c.execute("SELECT * FROM accounts ORDER BY total_dm DESC")
    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        today_add = get_daily_used(r["phone"], "add")
        today_dm = get_daily_used(r["phone"], "dm")
        max_dm, max_add = get_daily_limits(r["phone"])
        result.append({
            "phone": r["phone"], "status": r["status"],
            "real_name": r.get("real_name", ""),
            "warmup_level": r.get("warmup_level", 4),
            "total_dm": r.get("total_dm", 0) + today_dm,
            "total_added": r.get("total_added", 0) + today_add,
            "today_dm": today_dm, "today_add": today_add,
            "daily_limit_dm": max_dm, "daily_limit_add": max_add,
            "last_error": r.get("last_error", ""),
        })
    return jsonify({"accounts": result})


@app.route("/api/accounts/add", methods=["POST"])
def api_accounts_add():
    data = request.json
    phone = data.get("phone", "").strip()
    api_id = data.get("api_id", "").strip()
    api_hash = data.get("api_hash", "").strip()
    session_string = data.get("session_string", "").strip()
    proxy = data.get("proxy", "").strip()

    if not phone or not api_id or not api_hash:
        return jsonify({"error": "phone, api_id, api_hash required"}), 400

    cfg = load_config()
    node_id = cfg.get("node_id", "")
    save_account(phone, int(api_id), api_hash, node_id=node_id, session_string=session_string or None)

    # Try auth in background
    def auth_bg():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        am = AccountManager(node_id)
        client = loop.run_until_complete(am.create_client({
            "phone": phone, "api_id": int(api_id),
            "api_hash": api_hash, "session_string": session_string, "proxy": proxy
        }))
        try:
            me = loop.run_until_complete(am.auth_client(client, phone))
            push_log(f"Account {phone} authorised as {me.first_name}")
        except Exception as e:
            push_log(f"Auth failed for {phone}: {e}")
        finally:
            loop.run_until_complete(client.disconnect())

    threading.Thread(target=auth_bg, daemon=True).start()

    return jsonify({"ok": True, "msg": f"Account {phone} added. Auth in background."})


@app.route("/api/accounts/<phone>/remove", methods=["POST"])
def api_accounts_remove(phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM accounts WHERE phone=?", (phone,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/server/connect", methods=["POST"])
def api_server_connect():
    data = request.json
    url = data.get("server_url", "").rstrip("/")
    if not url:
        return jsonify({"error": "server_url required"}), 400

    cfg = load_config()
    cfg["server_url"] = url

    # Try register
    node_id = cfg.get("node_id", f"node-{uuid.uuid4().hex[:6]}")
    try:
        req = urllib.request.Request(
            f"{url}/api/node/register", method="POST",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"node_id": node_id, "name": cfg.get("name", node_id), "version": "2.0"}).encode()
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("token"):
                cfg["node_id"] = node_id
                cfg["token"] = result["token"]
                save_config(cfg)
                push_log(f"Registered with server. Node ID: {node_id}")
                return jsonify({"ok": True, "node_id": node_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"error": "registration failed"}), 400


@app.route("/api/engine/start", methods=["POST"])
def api_engine_start():
    global _node_engine
    if _node_engine and _engine_thread and _engine_thread.is_alive():
        return jsonify({"error": "already running"}), 400
    _node_engine = NodeEngineRunner()
    _node_engine.start()
    return jsonify({"ok": True})


@app.route("/api/engine/stop", methods=["POST"])
def api_engine_stop():
    global _node_engine
    if _node_engine:
        _node_engine.stop()
        _node_engine = None
        push_log("Engine stopping...")
        return jsonify({"ok": True})
    return jsonify({"error": "not running"}), 400


@app.route("/api/log")
def api_log():
    return Response("\n".join(_log_lines[-200:]), mimetype="text/plain; charset=utf-8")


@app.route("/api/heartbeat", methods=["POST"])
def api_heartbeat():
    cfg = load_config()
    node_id = cfg.get("node_id", "")
    if node_id and cfg.get("token"):
        accounts = get_healthy_accounts(node_id)
        stats = get_stats()
        node_heartbeat(node_id, len(accounts), stats.get("today_add", 0))
    return jsonify({"ok": True})


@app.route("/api/clear-logs", methods=["POST"])
def api_clear_logs():
    _log_lines.clear()
    return jsonify({"ok": True})


# ─── Main ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AION Node Client")
    parser.add_argument("--server", help="Central server URL")
    parser.add_argument("--port", type=int, default=5100, help="Local web UI port")
    args = parser.parse_args()

    init_db()

    if args.server:
        cfg = load_config()
        cfg["server_url"] = args.server.rstrip("/")
        node_id = cfg.get("node_id", f"node-{uuid.uuid4().hex[:6]}")
        try:
            req = urllib.request.Request(
                f"{args.server}/api/node/register", method="POST",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"node_id": node_id, "version": "2.0"}).encode()
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                if result.get("token"):
                    cfg["node_id"] = node_id
                    cfg["token"] = result["token"]
                    save_config(cfg)
                    log.info(f"Registered with server. Node ID: {node_id}")
        except Exception as e:
            log.warning(f"Could not register with server: {e}")
            cfg["node_id"] = node_id
            save_config(cfg)

    push_log("AION Node Client started")
    print("=" * 50)
    print(f"  AION NODE CLIENT v2")
    print(f"  Web UI: http://localhost:{args.port}")
    print(f"  Server: {get_server_url()}")
    print("=" * 50)

    app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
