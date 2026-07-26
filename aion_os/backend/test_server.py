"""Quick test script — tests the AION OS API without starting a server."""

import os
import sys

os.environ["AION_TEST_MODE"] = "1"

sys.stdout.reconfigure(encoding="utf-8")

from httpx import ASGITransport, AsyncClient
from app.db.session import init_db
from app.main import app


async def test_all():
    results = []
    transport = ASGITransport(app=app)

    print("\n" + "=" * 60)
    print("  AION OS — API Test Suite")
    print("=" * 60)

    # Initialize database first
    print("\n  [SETUP] Initializing database...")
    try:
        await init_db()
        print("  [SETUP] Database OK")
    except Exception as e:
        print(f"  [SETUP] DB init failed: {e}")

    async def test(name, method, path, json=None, expected=200):
        try:
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                if method == "GET":
                    r = await client.get(path)
                else:
                    r = await client.post(path, json=json or {})
                ok = "OK" if r.status_code == expected else f"FAIL (expected {expected}, got {r.status_code})"
                results.append((ok, f"  [{ok}] {method} {path} -> {r.status_code}"))
        except Exception as e:
            results.append(("ERROR", f"  [ERROR] {method} {path} -> {e}"))

    # Health
    await test("Health", "GET", "/")
    await test("Health", "GET", "/health")
    await test("Admin Health", "GET", "/api/v1/admin/health")
    await test("Admin Stats", "GET", "/api/v1/admin/stats")

    # Categories
    await test("Categories", "GET", "/api/v1/categories")

    # Auth required endpoints (401 expected — means auth is working)
    await test("Chat (no auth)", "POST", "/api/v1/chat/text",
               json={"message": "Hello"}, expected=401)
    # These endpoints don't require auth (public browsing)
    await test("Memory (public)", "GET", "/api/v1/memory/123", expected=200)
    await test("Partners search (public)", "POST", "/api/v1/partners/search",
               json={"category": "medical"}, expected=200)
    # Auth required endpoints
    await test("Bookings (no auth)", "GET", "/api/v1/bookings", expected=401)

    # Auth with bad data (401 expected)
    await test("Auth (bad)", "POST", "/api/v1/auth/telegram",
               json={"init_data": "bad_data"}, expected=401)

    # SSE streaming (no auth)
    await test("SSE (no auth)", "GET", "/api/v1/chat/stream?q=hello", expected=401)

    # Print results
    print("\n" + "-" * 60)
    for _, msg in results:
        print(msg)

    # Summary
    passed = sum(1 for ok, _ in results if ok == "OK")
    failed = sum(1 for ok, _ in results if ok.startswith("FAIL"))
    errors = sum(1 for ok, _ in results if ok == "ERROR")
    print()
    print(f"  Total: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Errors: {errors}")

    if errors == 0 and failed == 0:
        print("\n  ✅ ALL {len(results)} TESTS PASSED")
    else:
        print(f"\n  ⚠️  {failed + errors} tests need attention")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_all())
    finally:
        # Cleanup test database
        import os
        db_path = os.path.join(os.path.dirname(__file__), 'aion_test.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n  Cleaned up: {db_path}")
