"""
AION Invite Machine v2 — Central Server
Cyberpunk admin panel · Node management · Campaign distribution · Analytics
"""
import json, os, uuid, hashlib, csv, io
from datetime import datetime, date, timedelta
from pathlib import Path
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, Response,
    session, redirect
)

os.environ["PYTHONIOENCODING"] = "utf-8"
from aion_engine import (
    init_db, get_conn, get_stats, get_accounts, get_healthy_accounts,
    get_campaigns, save_account, register_node, node_heartbeat,
    get_offline_nodes
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "aion-invite-machine-v2-2026")
app.config["DATA_DIR"] = Path("server_data")
app.config["DATA_DIR"].mkdir(exist_ok=True)

ADMIN_PASSWORD_HASH = hashlib.sha256(
    os.environ.get("ADMIN_PASSWORD", "admin123").encode()
).hexdigest()


# ─── Auth Middleware ──────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return (render_template("login.html"), 401)
        return f(*args, **kwargs)
    return decorated

def node_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "no token"}), 401
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id FROM nodes WHERE token=?", (token,))
        row = c.fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "invalid token"}), 401
        kwargs["node_id"] = row["id"]
        return f(*args, **kwargs)
    return decorated


# ─── Web Routes ──────────────────────────────────────────

@app.route("/")
def index():
    if session.get("admin"):
        return render_template("dashboard.html")
    return render_template("login.html")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_action():
    data = request.json
    pw_hash = hashlib.sha256(data.get("password", "").encode()).hexdigest()
    if pw_hash == ADMIN_PASSWORD_HASH:
        session["admin"] = True
        return jsonify({"ok": True})
    return jsonify({"error": "wrong password"}), 403

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


# ─── Admin API ───────────────────────────────────────────

@app.route("/api/admin/stats")
@login_required
def admin_stats():
    stats = get_stats()
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM nodes ORDER BY last_heartbeat DESC")
    nodes = c.fetchall()
    c.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
    campaigns = c.fetchall()
    c.execute("SELECT COUNT(*) as v FROM nodes WHERE status='online'")
    online = c.fetchone()["v"]

    start = (date.today() - timedelta(days=7)).isoformat()
    c.execute("""
        SELECT date, SUM(CASE WHEN action='dm' THEN count ELSE 0 END) as dm_cnt,
               SUM(CASE WHEN action='add' THEN count ELSE 0 END) as add_cnt
        FROM daily_usage WHERE date >= ? GROUP BY date ORDER BY date
    """, (start,))
    history = c.fetchall()
    conn.close()

    stats["online_nodes"] = online
    stats["nodes"] = nodes
    stats["campaigns"] = campaigns
    stats["history"] = history
    return jsonify(stats)


# ─── Campaigns ───────────────────────────────────────────

@app.route("/api/admin/campaigns", methods=["GET"])
@login_required
def admin_campaigns():
    city = request.args.get("city")
    return jsonify({"campaigns": get_campaigns(city)})

@app.route("/api/admin/campaigns", methods=["POST"])
@login_required
def admin_campaigns_create():
    data = request.json
    if not data.get("city") or not data.get("target_chats"):
        return jsonify({"error": "city and target_chats required"}), 400
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO campaigns (city, name, source_chats, target_chats, dm_message, invite_link, is_active, created_at)
        VALUES (?,?,?,?,?,?,1,?)
    """, (
        data["city"], data.get("name", data["city"]),
        json.dumps([x.strip() for x in data.get("source_chats", "").split("\n") if x.strip()]),
        json.dumps([x.strip() for x in data["target_chats"].split("\n") if x.strip()]),
        data.get("dm_message", ""), data.get("invite_link", ""),
        datetime.now().isoformat()
    ))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({"ok": True, "id": new_id})

@app.route("/api/admin/campaigns/<int:cid>", methods=["DELETE"])
@login_required
def admin_campaigns_delete(cid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM campaigns WHERE id=?", (cid,))
    c.execute("DELETE FROM schedule WHERE campaign_id=?", (cid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/admin/campaigns/<int:cid>/toggle", methods=["POST"])
@login_required
def admin_campaigns_toggle(cid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE campaigns SET is_active = 1 - is_active WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ─── Nodes ───────────────────────────────────────────────

@app.route("/api/admin/nodes")
@login_required
def admin_nodes():
    get_offline_nodes(minutes=3)
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM nodes ORDER BY last_heartbeat DESC")
    nodes = c.fetchall()
    conn.close()
    return jsonify({"nodes": nodes})

@app.route("/api/admin/nodes/<node_id>", methods=["DELETE"])
@login_required
def admin_nodes_delete(node_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM nodes WHERE id=?", (node_id,))
    c.execute("UPDATE accounts SET node_id=NULL WHERE node_id=?", (node_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/admin/node-accounts/<node_id>")
@login_required
def admin_node_accounts(node_id):
    return jsonify({"accounts": get_accounts(node_id)})


# ─── Schedule ────────────────────────────────────────────

@app.route("/api/admin/schedule", methods=["GET"])
@login_required
def admin_schedule():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT s.*, c.name as campaign_name, c.city
        FROM schedule s JOIN campaigns c ON s.campaign_id=c.id
        ORDER BY s.hour, s.minute
    """)
    schedules = c.fetchall()
    conn.close()
    return jsonify({"schedules": schedules})

@app.route("/api/admin/schedule", methods=["POST"])
@login_required
def admin_schedule_create():
    data = request.json
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO schedule (campaign_id, hour, minute, days, is_active) VALUES (?,?,?,?,1)
    """, (data["campaign_id"], data["hour"], data["minute"],
          ",".join(data.get("days", ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]))))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/admin/schedule/<int:sid>", methods=["DELETE"])
@login_required
def admin_schedule_delete(sid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM schedule WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/admin/schedule/<int:sid>/toggle", methods=["POST"])
@login_required
def admin_schedule_toggle(sid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE schedule SET is_active = 1 - is_active WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ─── Contacts ────────────────────────────────────────────

@app.route("/api/admin/contacts")
@login_required
def admin_contacts():
    limit = request.args.get("limit", 100, type=int)
    city = request.args.get("city", "")
    conn = get_conn()
    c = conn.cursor()
    query = """
        SELECT user_id, username, first_name, source_city, source_chat,
               dm_sent, added_chat_id, clicked_bot, dm_at, error, node_id
        FROM contacts
    """
    params = []
    if city:
        query += " WHERE source_city LIKE ?"
        params.append(f"%{city}%")
    query += " ORDER BY dm_at DESC, user_id DESC LIMIT ?"
    params.append(limit)
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return jsonify({"contacts": rows})

@app.route("/api/admin/export")
@login_required
def admin_export():
    city = request.args.get("city", "")
    conn = get_conn()
    c = conn.cursor()
    query = """
        SELECT user_id, username, first_name, last_name, phone, source_city,
               source_chat, dm_sent, dm_at, added_chat_id, clicked_bot, error, node_id
        FROM contacts
    """
    params = []
    if city:
        query += " WHERE source_city LIKE ?"
        params.append(f"%{city}%")
    query += " ORDER BY dm_at DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["ID", "Username", "Name", "City", "Source Chat", "DM Sent", "DM Date",
                 "Added", "Clicked Bot", "Error", "Node"])
    for r in rows:
        w.writerow([r["user_id"], r["username"], r["first_name"], r["source_city"],
                    r["source_chat"], "Yes" if r["dm_sent"] else "No", r["dm_at"],
                    "Yes" if r["added_chat_id"] else "No",
                    "Yes" if r["clicked_bot"] else "No", r.get("error", ""), r.get("node_id", "")])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=aion_contacts.csv"})


# ─── Node API ────────────────────────────────────────────

@app.route("/api/node/register", methods=["POST"])
def node_register():
    data = request.json
    node_id = data.get("node_id", uuid.uuid4().hex[:8])
    name = data.get("name", f"Node-{node_id}")
    ip = request.remote_addr or data.get("ip", "0.0.0.0")
    token = register_node(node_id, name, ip, data.get("version", "2.0"))
    return jsonify({"node_id": node_id, "token": token})

@app.route("/api/node/heartbeat", methods=["POST"])
@node_auth
def node_heartbeat_endpoint(node_id):
    data = request.json or {}
    node_heartbeat(node_id, data.get("accounts_count", 0), data.get("invites_count", 0))
    return jsonify({"ok": True})

@app.route("/api/node/tasks", methods=["GET"])
@node_auth
def node_tasks(node_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM campaigns WHERE is_active=1 ORDER BY created_at DESC")
    campaigns = c.fetchall()
    conn.close()
    return jsonify({"campaigns": campaigns})

@app.route("/api/node/stats/report", methods=["POST"])
@node_auth
def node_stats_report(node_id):
    data = request.json
    stats = data.get("stats", {})
    if stats:
        conn = get_conn()
        c = conn.cursor()
        for acct in stats.get("accounts", []):
            phone = acct.get("phone")
            if phone:
                c.execute("UPDATE accounts SET total_dm=?, total_added=?, status=? WHERE phone=?",
                          (acct.get("dm", 0), acct.get("added", 0), acct.get("status", "active"), phone))
        conn.commit()
        conn.close()
    return jsonify({"ok": True})


# ─── Static file serving ─────────────────────────────────

@app.route("/static/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)


# ─── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print("=" * 50)
    print("  AION INVITE MACHINE v2 — CENTRAL SERVER")
    print(f"  Admin panel : http://localhost:{port}")
    print(f"  Login       : http://localhost:{port}/login  (default: admin123)")
    print(f"  Node API    : http://localhost:{port}/api/node/register")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
