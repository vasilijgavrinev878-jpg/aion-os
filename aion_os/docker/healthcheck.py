#!/usr/bin/env python3
"""Docker Integration Healthcheck — checks all AION OS services.

Usage:
    python healthcheck.py               # Quick check
    python healthcheck.py --verbose     # Detailed output
    python healthcheck.py --wait        # Wait until all services are up

This script checks:
├── 🐘 PostgreSQL (port 5432)
├── 🔴 Redis (port 6379)
├── 🚀 FastAPI (port 8000)
├── 🌐 nginx / Admin (port 8080)
├── 📄 Swagger docs (port 8000/docs)
├── 🔌 WebSocket (port 8000/ws)
└── 🤖 AI Agent Router (chat/text endpoint)
"""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

# ─── Configuration ─────────────────────────────────────────
API_HOST = os.environ.get("AION_API_HOST", "localhost")
API_PORT = int(os.environ.get("AION_API_PORT", "8000"))
ADMIN_PORT = int(os.environ.get("AION_ADMIN_PORT", "8080"))
PG_PORT = int(os.environ.get("AION_PG_PORT", "5432"))
REDIS_PORT = int(os.environ.get("AION_REDIS_PORT", "6379"))
TIMEOUT = int(os.environ.get("AION_CHECK_TIMEOUT", "5"))
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv
WAIT = "--wait" in sys.argv or "-w" in sys.argv

# ─── Colors ─────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ─── Helpers ────────────────────────────────────────────────


def ok(msg: str) -> str:
    return f"{GREEN}✓{RESET} {msg}"


def fail(msg: str) -> str:
    return f"{RED}✗{RESET} {msg}"


def warn(msg: str) -> str:
    return f"{YELLOW}⚠{RESET} {msg}"


def http_get(url: str, timeout: int = TIMEOUT) -> tuple[int, str]:
    """HTTP GET request — returns (status_code, body)."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")[:200]
    except (urllib.error.URLError, socket.timeout, ConnectionRefusedError) as e:
        return 0, str(e)


def tcp_check(host: str, port: int, timeout: int = TIMEOUT) -> bool:
    """Check if a TCP port is open."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


# ─── Checks ─────────────────────────────────────────────────


def check_postgres() -> str:
    """Check PostgreSQL connectivity."""
    if tcp_check(API_HOST, PG_PORT):
        # Try to get PostgreSQL version
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=API_HOST,
                port=PG_PORT,
                user="aion",
                password="changeme_in_production",
                dbname="aion",
                connect_timeout=TIMEOUT,
            )
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0][:40]
            cur.close()
            conn.close()
            return ok(f"PostgreSQL connected — {version}...")
        except ImportError:
            return ok("PostgreSQL port open (psycopg2 not installed for version check)")
        except Exception as e:
            return warn(f"PostgreSQL port open but query failed: {e}")
    else:
        return fail("PostgreSQL port 5432 — connection refused")


def check_redis() -> str:
    """Check Redis connectivity."""
    if tcp_check(API_HOST, REDIS_PORT):
        try:
            import redis
            r = redis.Redis(host=API_HOST, port=REDIS_PORT, socket_timeout=TIMEOUT)
            pong = r.ping()
            if pong:
                info = r.info("server")
                version = info.get("redis_version", "?")
                return ok(f"Redis connected — v{version}")
            else:
                return warn("Redis port open but ping failed")
        except ImportError:
            return ok("Redis port open (redis-py not installed for ping check)")
        except Exception as e:
            return warn(f"Redis port open but ping failed: {e}")
    else:
        return fail("Redis port 6379 — connection refused")


def check_api_health() -> str:
    """Check FastAPI health endpoint."""
    status, body = http_get(f"http://{API_HOST}:{API_PORT}/health")
    if status == 200:
        try:
            data = json.loads(body)
            return ok(f"API healthy — {data.get('status', 'ok')}")
        except json.JSONDecodeError:
            return ok(f"API responds — HTTP {status}")
    else:
        return fail(f"API health — HTTP {status}: {body[:80]}")


def check_api_root() -> str:
    """Check FastAPI root endpoint."""
    status, body = http_get(f"http://{API_HOST}:{API_PORT}/")
    if status == 200:
        try:
            data = json.loads(body)
            name = data.get("name", "AION OS")
            ver = data.get("version", "?")
            return ok(f"{name} v{ver} — API root OK")
        except json.JSONDecodeError:
            return ok(f"API root responds — HTTP {status}")
    else:
        return fail(f"API root — HTTP {status}")


def check_swagger() -> str:
    """Check Swagger docs."""
    status, body = http_get(f"http://{API_HOST}:{API_PORT}/docs")
    if status == 200 and "swagger" in body.lower():
        return ok("Swagger docs available at /docs")
    else:
        return warn(f"Swagger docs — HTTP {status}")


def check_admin_panel() -> str:
    """Check nginx / Admin panel."""
    status, body = http_get(f"http://{API_HOST}:{ADMIN_PORT}/")
    if status == 200:
        if "AION OS" in body or "Admin" in body:
            return ok("Admin panel serves correctly on :8080")
        else:
            return ok(f"Admin panel responds — HTTP {status}")
    else:
        return fail(f"Admin panel (nginx) — HTTP {status}")


def check_api_categories() -> str:
    """Check that the API returns categories."""
    status, body = http_get(f"http://{API_HOST}:{API_PORT}/api/v1/categories")
    if status == 200:
        try:
            data = json.loads(body)
            count = len(data.get("categories", []))
            return ok(f"Categories endpoint — {count} categories loaded")
        except json.JSONDecodeError:
            return ok(f"Categories endpoint responds — HTTP {status}")
    else:
        return fail(f"Categories — HTTP {status}")


def check_api_auth(verbose: bool = False) -> str:
    """Check auth endpoint returns 401 for bad data (security working)."""
    import urllib.request as req_lib
    data = json.dumps({"init_data": "bad_test_data"}).encode("utf-8")
    try:
        req = req_lib.Request(
            f"http://{API_HOST}:{API_PORT}/api/v1/auth/telegram",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with req_lib.urlopen(req, timeout=TIMEOUT) as resp:
            return fail(f"Auth accepted bad data — HTTP {resp.status} (security issue!)")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return ok(f"Auth rejects bad data — HTTP 401 (security OK)")
        return warn(f"Auth returned HTTP {e.code} (expected 401)")


def check_chat_endpoint() -> str:
    """Check chat/text endpoint exists (expect 401 without auth)."""
    import urllib.request as req_lib
    data = json.dumps({"message": "test", "lang": "ru"}).encode("utf-8")
    try:
        req = req_lib.Request(
            f"http://{API_HOST}:{API_PORT}/api/v1/chat/text",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with req_lib.urlopen(req, timeout=TIMEOUT) as resp:
            return fail(f"Chat accepted request without auth — HTTP {resp.status} (security issue!)")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return ok(f"Chat endpoint exists, auth required — HTTP 401")
        return warn(f"Chat endpoint returned HTTP {e.code} (expected 401)")


def check_api_admin_health() -> str:
    """Check admin/health endpoint."""
    status, body = http_get(f"http://{API_HOST}:{API_PORT}/api/v1/admin/health")
    if status == 200:
        try:
            data = json.loads(body)
            return ok(f"Admin health: {data.get('status', 'ok')}")
        except json.JSONDecodeError:
            return ok("Admin health endpoint OK")
    else:
        return fail(f"Admin health — HTTP {status}")


def check_websocket(verbose: bool = False) -> str:
    """Check WebSocket endpoint accepts connections."""
    try:
        import websockets.sync.client as ws_sync
        with ws_sync.connect(f"ws://{API_HOST}:{API_PORT}/ws", timeout=TIMEOUT) as ws:
            ws.send(json.dumps({"type": "ping"}))
            resp = json.loads(ws.recv())
            if resp.get("type") == "pong":
                return ok("WebSocket endpoint responds to ping")
            else:
                return warn(f"WebSocket unexpected response: {resp}")
    except ImportError:
        return warn("WebSocket check skipped (websockets library not installed)")
    except Exception as e:
        return warn(f"WebSocket check: {e}")


def check_nginx_proxy() -> str:
    """Check that nginx proxies /api to backend."""
    status, body = http_get(f"http://{API_HOST}:{ADMIN_PORT}/api/v1/admin/health")
    if status == 200:
        try:
            data = json.loads(body)
            return ok("nginx proxies /api/ to backend correctly")
        except json.JSONDecodeError:
            return ok(f"nginx proxy responds — HTTP {status}")
    else:
        return fail(f"nginx proxy — HTTP {status}")


def check_docker_containers() -> str:
    """Check Docker container status."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            containers = result.stdout.strip().split("\n") if result.stdout.strip() else []
            running = [c for c in containers if "Up" in c]
            if running:
                names = ", ".join(c.split("\t")[0] for c in running if "\t" in c)
                return ok(f"{len(running)} containers running: {names}")
            elif containers:
                return warn(f"{len(containers)} containers found, none running")
            else:
                return warn("No AION containers running. Run: docker compose up -d")
        else:
            return warn("Docker not available from this terminal")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return warn("Docker CLI not found in PATH")


# ─── Main ───────────────────────────────────────────────────


URL = f"{GREEN}{BOLD}http://{API_HOST}:{API_PORT}{RESET}"
ADMIN_URL = f"{GREEN}{BOLD}http://{API_HOST}:{ADMIN_PORT}{RESET}"


def run_checks() -> list[tuple[str, str, str]]:
    """Run all checks and return (name, result, status) tuples."""
    checks = [
        ("🐘 PostgreSQL", check_postgres()),
        ("🔴 Redis", check_redis()),
        ("🚀 API Health", check_api_health()),
        ("🏠 API Root", check_api_root()),
        ("📄 Swagger Docs", check_swagger()),
        ("📂 Categories", check_api_categories()),
        ("🔐 Auth Security", check_api_auth()),
        ("💬 Chat Endpoint", check_chat_endpoint()),
        ("🩺 Admin Health", check_api_admin_health()),
        ("🌐 nginx Proxy", check_nginx_proxy()),
        ("🖥️ Admin Panel", check_admin_panel()),
        ("🔌 WebSocket", check_websocket()),
        ("🐳 Docker Containers", check_docker_containers()),
    ]
    return [(name, result) for name, result in checks]


def print_header():
    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  AION OS — Docker Integration Healthcheck{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  API:  {URL}")
    print(f"  Admin:{ADMIN_URL}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print()


def print_results(results: list[tuple[str, str]]):
    print(f"{'─'*60}")
    print(f"  {BOLD}{'CHECK':40s} {'STATUS'}{RESET}")
    print(f"{'─'*60}")
    for name, result in results:
        result_str = result
        # Truncate for display
        if len(result_str) > 70:
            result_str = result_str[:67] + "..."
        print(f"  {name:40s} {result_str}")

    # Summary
    passed = sum(1 for _, r in results if r.startswith(GREEN))
    warnings = sum(1 for _, r in results if r.startswith(YELLOW))
    failed = sum(1 for _, r in results if r.startswith(RED))
    total = len(results)

    print()
    print(f"{'─'*60}")
    print(f"  {BOLD}Summary:{RESET}")
    print(f"  {GREEN}Passed:{RESET} {passed:2d}  {YELLOW}Warnings:{RESET} {warnings:2d}  {RED}Failed:{RESET} {failed:2d}  Total: {total}")
    print()

    if failed == 0 and warnings == 0:
        print(f"  {GREEN}{BOLD}✅ ALL SERVICES HEALTHY{RESET}")
    elif failed == 0:
        print(f"  {YELLOW}⚠️  All critical services up ({warnings} warnings){RESET}")
    else:
        print(f"  {RED}❌ {failed} service(s) need attention{RESET}")

    return passed, warnings, failed


def main():
    print_header()

    if WAIT:
        print("  Waiting for all services (timeout: 60s)...")

    for attempt in range(12 if WAIT else 1):
        if attempt > 0:
            print(f"  Retry {attempt}/12...")
            time.sleep(5)

        results = run_checks()
        passed, warnings, failed = print_results(results)

        if WAIT and failed > 0 and attempt < 11:
            # Only retry if waiting mode
            continue
        break

    if VERBOSE:
        print()
        print(f"{BOLD}Detailed Endpoints:{RESET}")
        print(f"  API Docs:     http://{API_HOST}:{API_PORT}/docs")
        print(f"  API Redoc:    http://{API_HOST}:{API_PORT}/redoc")
        print(f"  Admin Panel:  http://{API_HOST}:{ADMIN_PORT}/")
        print(f"  Health:       http://{API_HOST}:{API_PORT}/health")
        print(f"  Categories:   http://{API_HOST}:{API_PORT}/api/v1/categories")
        print(f"  WebSocket:    ws://{API_HOST}:{API_PORT}/ws")
        print()
        print(f"{BOLD}Quick tests:{RESET}")
        print(f"  # Check API")
        print(f"  curl http://{API_HOST}:{API_PORT}/health")
        print()
        print(f"  # Check categories")
        print(f"  curl http://{API_HOST}:{API_PORT}/api/v1/categories")
        print()
        print(f"  # Check admin panel")
        print(f"  curl http://{API_HOST}:{ADMIN_PORT}/")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
