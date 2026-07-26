"""
AION Engine v2 — Distributed Invite Machine
Core module: Telegram operations, account management, warm-up, scheduling.
Shared between central server and client nodes.
"""
import asyncio
import json
import sqlite3
import logging
import random
import re
from datetime import datetime, date, timedelta
from pathlib import Path
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.functions.messages import AddChatUserRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("aion-engine")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "invite.db"

# ─── Warm-up profiles ──────────────────────────────────────

WARMUP_PROFILES = {
    0: {"dm": 5,  "add": 3,   "label": "Day 1-2 — warm-up"},
    1: {"dm": 10, "add": 5,   "label": "Day 3-4 — start"},
    2: {"dm": 20, "add": 10,  "label": "Day 5-6 — growth"},
    3: {"dm": 30, "add": 20,  "label": "Day 7-8 — active"},
    4: {"dm": 50, "add": 30,  "label": "Day 9+ — full power"},
}
WARMUP_DAYS = [2, 2, 2, 2, 999]


# ─── Database ───────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS contacts (
            user_id INTEGER PRIMARY KEY,
            username TEXT, first_name TEXT, last_name TEXT, phone TEXT,
            source_chat TEXT, source_city TEXT,
            dm_sent INTEGER DEFAULT 0, dm_at TEXT, dm_account TEXT,
            added_chat_id TEXT, added_at TEXT,
            clicked_bot INTEGER DEFAULT 0, clicked_at TEXT,
            error TEXT,
            node_id TEXT
        );
        CREATE TABLE IF NOT EXISTS accounts (
            phone TEXT PRIMARY KEY,
            api_id INTEGER, api_hash TEXT,
            session_string TEXT,
            status TEXT DEFAULT 'active',
            real_name TEXT, created_at TEXT,
            warmup_level INTEGER DEFAULT 0,
            total_dm INTEGER DEFAULT 0,
            total_added INTEGER DEFAULT 0,
            last_error TEXT, last_error_at TEXT,
            banned_at TEXT, proxy TEXT, node_id TEXT
        );
        CREATE TABLE IF NOT EXISTS daily_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_phone TEXT, action TEXT, date TEXT,
            count INTEGER DEFAULT 0, node_id TEXT,
            UNIQUE(account_phone, action, date)
        );
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT, name TEXT, is_active INTEGER DEFAULT 1,
            source_chats TEXT, target_chats TEXT,
            dm_message TEXT, invite_link TEXT,
            created_at TEXT, created_by TEXT
        );
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER, hour INTEGER, minute INTEGER,
            days TEXT DEFAULT 'mon,tue,wed,thu,fri,sat,sun',
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            name TEXT, token TEXT,
            last_heartbeat TEXT, ip TEXT,
            status TEXT DEFAULT 'offline',
            total_accounts INTEGER DEFAULT 0,
            total_invites INTEGER DEFAULT 0,
            version TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS node_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT, campaign_ids TEXT,
            assigned_at TEXT, status TEXT DEFAULT 'pending'
        );
    """)
    # migrations
    try:
        c.execute("ALTER TABLE accounts ADD COLUMN session_string TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def dict_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = dict_factory
    return conn


# ─── Account helpers ────────────────────────────────────────

def get_warmup_level(account_age_days):
    days_left = account_age_days
    for level, d in enumerate(WARMUP_DAYS):
        if days_left <= d:
            return level
        days_left -= d
    return len(WARMUP_DAYS) - 1

def get_daily_limits(phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT warmup_level FROM accounts WHERE phone = ?", (phone,))
    row = c.fetchone()
    conn.close()
    level = row["warmup_level"] if row and row["warmup_level"] is not None else 4
    profile = WARMUP_PROFILES.get(level, WARMUP_PROFILES[4])
    return profile["dm"], profile["add"]

def get_daily_used(phone, action):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(count),0) as v FROM daily_usage WHERE account_phone=? AND action=? AND date=?",
              (phone, action, date.today().isoformat()))
    r = c.fetchone()["v"]
    conn.close()
    return r

def inc_daily(phone, action, node_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO daily_usage (account_phone, action, date, count, node_id)
        VALUES (?,?,?,1,?)
        ON CONFLICT(account_phone, action, date) DO UPDATE
        SET count = count + 1
    """, (phone, action, date.today().isoformat(), node_id or ""))
    conn.commit()
    conn.close()


# ─── Contact operations ─────────────────────────────────────

def save_contact(user, source_chat, source_city="", node_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO contacts
        (user_id, username, first_name, last_name, phone, source_chat, source_city, node_id)
        VALUES (?,?,?,?,?,?,?,?)
    """, (user.id, user.username or "", user.first_name or "", user.last_name or "",
          getattr(user, 'phone', "") or "", source_chat or "", source_city or "",
          node_id or ""))
    conn.commit()
    conn.close()

def mark_dm_sent(user_id, account_phone, source_chat, node_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE contacts SET dm_sent=1, dm_at=?, dm_account=?, node_id=COALESCE(node_id,?)
        WHERE user_id=?
    """, (datetime.now().isoformat(), account_phone, node_id or "", user_id))
    conn.commit()
    conn.close()

def mark_added(user_id, chat_id, node_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE contacts SET added_chat_id=?, added_at=?, node_id=COALESCE(node_id,?)
        WHERE user_id=?
    """, (chat_id, datetime.now().isoformat(), node_id or "", user_id))
    conn.commit()
    conn.close()

def mark_error(user_id, err):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE contacts SET error=? WHERE user_id=?", (str(err)[:200], user_id))
    conn.commit()
    conn.close()

def mark_clicked(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE contacts SET clicked_bot=1, clicked_at=? WHERE user_id=? AND clicked_bot=0",
              (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def is_contacted(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT dm_sent FROM contacts WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row["dm_sent"] == 1

def save_account(phone, api_id, api_hash, real_name="", node_id=None, session_string=None):
    conn = get_conn()
    c = conn.cursor()
    # bought accounts (with session_string) are already aged → full warmup
    warmup = 4 if session_string else 0
    c.execute("""
        INSERT OR REPLACE INTO accounts
        (phone, api_id, api_hash, session_string, real_name, status, created_at, warmup_level, node_id)
        VALUES (?,?,?,?,?, 'active', COALESCE((SELECT created_at FROM accounts WHERE phone=?), ?), ?, ?)
    """, (phone, api_id, api_hash, session_string or "", real_name, phone, datetime.now().isoformat(), warmup, node_id or ""))
    conn.commit()
    conn.close()

def get_accounts(node_id=None):
    conn = get_conn()
    c = conn.cursor()
    if node_id:
        c.execute("SELECT * FROM accounts WHERE node_id=? ORDER BY total_dm DESC", (node_id,))
    else:
        c.execute("SELECT * FROM accounts ORDER BY total_dm DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_healthy_accounts(node_id=None):
    conn = get_conn()
    c = conn.cursor()
    query = "SELECT * FROM accounts WHERE status='active'"
    params = []
    if node_id:
        query += " AND node_id=?"
        params.append(node_id)
    query += " ORDER BY total_dm DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def mark_account_banned(phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE accounts SET status='banned', banned_at=? WHERE phone=?",
              (datetime.now().isoformat(), phone))
    conn.commit()
    conn.close()

def update_account_warmup(phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT created_at, warmup_level FROM accounts WHERE phone=?", (phone,))
    row = c.fetchone()
    if row:
        created = datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now()
        age = (datetime.now() - created).days
        new_level = get_warmup_level(age)
        c.execute("UPDATE accounts SET warmup_level=? WHERE phone=?", (new_level, phone))
        conn.commit()
    conn.close()

def get_campaigns(city=None, only_active=False):
    conn = get_conn()
    c = conn.cursor()
    query = "SELECT * FROM campaigns"
    params = []
    wheres = []
    if city:
        wheres.append("city=?")
        params.append(city)
    if only_active:
        wheres.append("is_active=1")
    if wheres:
        query += " WHERE " + " AND ".join(wheres)
    query += " ORDER BY created_at DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats(city=None):
    conn = get_conn()
    c = conn.cursor()
    where = ""
    params = []
    if city:
        where = " WHERE source_city=?"
        params.append(city)
    c.execute(f"SELECT COUNT(*) as v FROM contacts{where}", params)
    total = c.fetchone()["v"]
    c.execute(f"SELECT COUNT(*) as v FROM contacts WHERE dm_sent=1{where.replace('source_city','source_city')}", params)
    dm = c.fetchone()["v"]
    c.execute("SELECT COUNT(*) as v FROM contacts WHERE added_chat_id IS NOT NULL")
    added = c.fetchone()["v"]
    c.execute("SELECT COUNT(*) as v FROM contacts WHERE clicked_bot=1")
    clicked = c.fetchone()["v"]
    c.execute("SELECT COUNT(*) as v FROM contacts WHERE error IS NOT NULL")
    errors = c.fetchone()["v"]
    c.execute("SELECT COUNT(DISTINCT source_chat) as v FROM contacts WHERE source_chat!=''")
    chats = c.fetchone()["v"]
    c.execute("SELECT COUNT(*) as v FROM accounts WHERE status='active'")
    healthy_accounts = c.fetchone()["v"]
    c.execute("SELECT COUNT(*) as v FROM nodes WHERE status='online'")
    online_nodes = c.fetchone()["v"]

    today = date.today().isoformat()
    c.execute("SELECT COALESCE(SUM(count),0) as v FROM daily_usage WHERE action='dm' AND date=?", (today,))
    today_dm = c.fetchone()["v"]
    c.execute("SELECT COALESCE(SUM(count),0) as v FROM daily_usage WHERE action='add' AND date=?", (today,))
    today_add = c.fetchone()["v"]

    c.execute("""
        SELECT date, SUM(CASE WHEN action='dm' THEN count ELSE 0 END) as dm_cnt,
               SUM(CASE WHEN action='add' THEN count ELSE 0 END) as add_cnt
        FROM daily_usage WHERE date >= ?
        GROUP BY date ORDER BY date
    """, ((date.today() - timedelta(days=7)).isoformat(),))
    history = c.fetchall()
    conn.close()
    return {
        "total": total, "dm_sent": dm, "added": added,
        "clicked": clicked, "errors": errors, "chats": chats,
        "healthy_accounts": healthy_accounts, "online_nodes": online_nodes,
        "today_dm": today_dm, "today_add": today_add, "history": history
    }


# ─── Account Manager ────────────────────────────────────────

class AccountManager:
    def __init__(self, node_id=None):
        self.node_id = node_id
        self.clients = {}

    async def create_client(self, acc):
        phone = acc["phone"]
        session_string = acc.get("session_string", "")
        proxy = acc.get("proxy", None)
        proxy_dict = None
        if proxy:
            parts = proxy.split(":")
            if len(parts) == 4:
                proxy_dict = {
                    "proxy_type": parts[0] if parts[0] in ("http", "socks5") else "http",
                    "addr": parts[1], "port": int(parts[2]),
                }
                if "/" in parts[3]:
                    proxy_dict["username"], proxy_dict["password"] = parts[3].split("/", 1)
        if session_string:
            client = TelegramClient(StringSession(session_string), acc["api_id"], acc["api_hash"], proxy=proxy_dict)
        else:
            session_path = f"sessions/{phone.replace('+', '')}"
            client = TelegramClient(session_path, acc["api_id"], acc["api_hash"], proxy=proxy_dict)
        return client

    async def auth_client(self, client, phone):
        try:
            me = await client.get_me()
            if me:
                save_account(phone, client.api_id, client.api_hash,
                             f"{me.first_name or ''} {me.last_name or ''}", self.node_id)
                update_account_warmup(phone)
                return me
        except Exception:
            pass
        await client.start(phone=phone)
        me = await client.get_me()
        save_account(phone, client.api_id, client.api_hash,
                     f"{me.first_name or ''} {me.last_name or ''}", self.node_id)
        update_account_warmup(phone)
        return me


# ─── Invite Engine ──────────────────────────────────────────

class InviteEngine:
    def __init__(self, am, node_id=None, callback=None):
        self.am = am
        self.node_id = node_id
        self.callback = callback or (lambda x: None)
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def can_invite(self, phone):
        used = get_daily_used(phone, "add")
        _, max_add = get_daily_limits(phone)
        return used < max_add, used, max_add

    async def scrape_chat(self, client, chat_entity):
        try:
            participants = await client.get_participants(chat_entity, limit=10000)
            return participants
        except Exception as e:
            self.callback(f"Scrape error {getattr(chat_entity, 'title', '?')}: {e}")
            return []

    async def invite_user(self, client, user_id, target_chat, phone):
        try:
            await client(AddChatUserRequest(target_chat.id, user_id, fwd_limit=0))
            mark_added(user_id, str(target_chat.id), self.node_id)
            inc_daily(phone, "add", self.node_id)
            return True
        except errors.FloodWaitError as e:
            self.callback(f"Flood {e.seconds}s on {phone}")
            await asyncio.sleep(min(e.seconds, 1800))
            return False
        except (errors.UserPrivacyRestrictedError, errors.UserNotMutualContactError):
            mark_added(user_id, str(target_chat.id), self.node_id)
            mark_error(user_id, "privacy")
            return False
        except errors.UserChannelsTooMuchError:
            mark_added(user_id, str(target_chat.id), self.node_id)
            return False
        except errors.UserKickedError:
            return False
        except Exception as e:
            mark_error(user_id, str(e)[:50])
            return False

    async def run_campaign(self, campaign, accounts):
        target_chats = json.loads(campaign["target_chats"]) if isinstance(campaign["target_chats"], str) else campaign["target_chats"]
        src_chats = json.loads(campaign["source_chats"]) if isinstance(campaign["source_chats"], str) else campaign["source_chats"]
        city = campaign.get("city", "global")
        name = campaign.get("name", city)

        if not accounts:
            self.callback("No healthy accounts on this node")
            return

        if not target_chats:
            self.callback("No target chats configured")
            return

        self.callback(f"Campaign '{name}' ({city}) — {len(accounts)} accounts, {len(src_chats)} sources, {len(target_chats)} targets")

        # Step 1: Scrape source chats
        all_new = []
        for chat_link in src_chats:
            if self._stop_flag:
                break
            acc = accounts[0]
            client = await self.am.create_client(acc)
            try:
                await self.am.auth_client(client, acc["phone"])
                entity = await client.get_entity(chat_link)
                title = getattr(entity, 'title', str(chat_link))
                self.callback(f"Scraping: {title}")
                participants = await self.scrape_chat(client, entity)
                for p in participants:
                    if p.bot or p.deleted:
                        continue
                    if is_contacted(p.id):
                        continue
                    save_contact(p, title, city, self.node_id)
                    all_new.append(p)
                self.callback(f"  → {len(participants)} total, {len([p for p in participants if not p.bot])} real, {len(all_new)} new so far")
            except Exception as e:
                self.callback(f"Error scraping {chat_link}: {e}")
            finally:
                await client.disconnect()
            await asyncio.sleep(3)

        if self._stop_flag or not all_new:
            self.callback("No new users found")
            return

        self.callback(f"Total candidates: {len(all_new)}")

        # Step 2: Invite to target chats
        for target_link in target_chats:
            if self._stop_flag:
                break
            client = await self.am.create_client(accounts[0])
            try:
                await self.am.auth_client(client, accounts[0]["phone"])
                target = await client.get_entity(target_link)
                t_title = getattr(target, 'title', str(target_link))
                self.callback(f"Inviting to: {t_title}")

                success = 0
                for i, user in enumerate(all_new):
                    if self._stop_flag:
                        break
                    acc = accounts[i % len(accounts)]
                    can, used, maks = self.can_invite(acc["phone"])
                    if not can:
                        # Try next account
                        for acc2 in accounts:
                            can2, used2, maks2 = self.can_invite(acc2["phone"])
                            if can2:
                                acc = acc2
                                can = True
                                break
                    if not can:
                        self.callback("All accounts reached daily limit")
                        break

                    # Auth with the current account
                    if i > 0:
                        await client.disconnect()
                        client = await self.am.create_client(acc)
                        await self.am.auth_client(client, acc["phone"])

                    self.callback(f"[{i+1}/{len(all_new)}] Inviting @{user.username or user.id} via {acc['phone']}")
                    ok = await self.invite_user(client, user.id, target, acc["phone"])
                    if ok:
                        success += 1

                    delay = random.randint(60, 180)  # 1-3 min between invites
                    await asyncio.sleep(delay)

                self.callback(f"Added {success}/{len(all_new)} to {t_title}")
            except Exception as e:
                self.callback(f"Error with target {target_link}: {e}")
            finally:
                await client.disconnect()


# ─── Campaign Scheduler ─────────────────────────────────────

class CampaignScheduler:
    def __init__(self, engine, accounts, node_id=None):
        self.engine = engine
        self.accounts = accounts
        self.node_id = node_id
        self._stop = False

    def stop(self):
        self._stop = True

    async def run_loop(self):
        while not self._stop:
            now = datetime.now()
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                SELECT s.*, c.* FROM schedule s
                JOIN campaigns c ON s.campaign_id = c.id
                WHERE s.is_active=1 AND c.is_active=1
            """)
            schedules = c.fetchall()
            conn.close()

            for s in schedules:
                if s["hour"] == now.hour and s["minute"] == now.minute:
                    days = s["days"].split(",")
                    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                    if day_names[now.weekday()] in days:
                        self.engine.callback(f"Scheduled run: {s.get('name', s.get('city', '?'))}")
                        # Only run if we have node-specific accounts or global accounts
                        accs = get_healthy_accounts(self.node_id)
                        if not accs:
                            accs = self.accounts
                        await self.engine.run_campaign(s, accs)
                        await asyncio.sleep(61)

            await asyncio.sleep(30)


# ─── Node operations ────────────────────────────────────────

def register_node(node_id, name, ip, version):
    conn = get_conn()
    c = conn.cursor()
    token = f"aion_{node_id}_{random.randint(10000,99999)}"
    c.execute("""
        INSERT OR REPLACE INTO nodes (id, name, token, last_heartbeat, ip, status, version, created_at)
        VALUES (?,?,?,?,?,?,?,?)
    """, (node_id, name, token, datetime.now().isoformat(), ip, "online", version, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return token

def node_heartbeat(node_id, accounts_count=0, invites_count=0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE nodes SET last_heartbeat=?, status='online', total_accounts=?, total_invites=?
        WHERE id=?
    """, (datetime.now().isoformat(), accounts_count, invites_count, node_id))
    conn.commit()
    conn.close()

def get_offline_nodes(minutes=5):
    conn = get_conn()
    c = conn.cursor()
    threshold = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    c.execute("UPDATE nodes SET status='offline' WHERE last_heartbeat < ?", (threshold,))
    conn.commit()
    conn.close()
