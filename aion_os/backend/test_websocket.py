"""WebSocket test — validates full WS lifecycle: connect → auth → message → stream → done → pong.

Usage:
    AION_TEST_MODE=1 python test_websocket.py

Uses a mock RouterAgent to avoid requiring real LLM API keys.
"""

import asyncio
import json
import logging
import os
import sys
import time

logging.disable(logging.CRITICAL)

os.environ["AION_TEST_MODE"] = "1"
os.environ["OPENAI_API_KEY"] = "sk-test-dummy"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-dummy"
sys.stdout.reconfigure(encoding="utf-8")

from jose import jwt as jose_jwt

TEST_TOKEN = jose_jwt.encode(
    {
        "user_id": 123456789,
        "first_name": "Test",
        "username": "testuser",
        "lang": "ru",
        "exp": int(time.time()) + 3600,
    },
    "test_secret_key_not_for_production_use",
    algorithm="HS256",
)


async def test_websocket():
    """Full WebSocket lifecycle test."""
    results = []
    port = 9881
    server = None

    print("\n" + "=" * 60)
    print("  AION OS - WebSocket Test Suite")
    print("=" * 60)

    # 1. Mock the RouterAgent for deterministic response
    from app.agents.router import RouterAgent
    from app.agents.base import AgentResult

    _orig_execute = RouterAgent.execute

    async def _mock_execute(self, ctx):
        return AgentResult(
            response="Привет! AION — это AI-операционная система для жизни за границей. "
                     "Я помогу найти услуги, забронировать, ответить на вопросы.",
            navigation={"action": "show_cards", "params": {"category": "all"}},
            cards=[
                {"title": "Недвижимость", "desc": "Аренда и покупка"},
                {"title": "Медицина", "desc": "Врачи и клиники"},
            ],
        )

    RouterAgent.execute = _mock_execute

    try:
        # 2. Start server
        print("\n  [1/5] Starting ASGI server...")
        import uvicorn
        from app.main import app

        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", lifespan="on")
        server = uvicorn.Server(config)
        task = asyncio.create_task(server.serve())
        await asyncio.sleep(2)

        if not server.started:
            print("  [FAIL] Server failed to start")
            return

        print("  [OK] Server started on ws://127.0.0.1:" + str(port) + "/ws")
        results.append("[OK] Server started")

        # 3. Connect
        print("  [2/5] Connecting WebSocket...")
        import websockets

        async with websockets.connect("ws://127.0.0.1:" + str(port) + "/ws") as ws:
            print("  [OK] Connected")
            results.append("[OK] WebSocket connected")

            # 4. Auth
            print("  [3/5] Sending auth...")
            await ws.send(json.dumps({"type": "auth", "token": TEST_TOKEN}))
            resp = json.loads(await ws.recv())

            if resp.get("type") == "auth_ok":
                uid = resp.get("user_id", "?")
                print("  [OK] Auth: user_id=" + str(uid))
                results.append("[OK] Auth: user_id=" + str(uid))
            else:
                print("  [FAIL] Auth failed: " + json.dumps(resp, ensure_ascii=False))
                results.append("[FAIL] Auth")
                return

            # 5. Send chat message
            print("  [4/5] Sending chat.message...")
            await ws.send(json.dumps({
                "type": "chat.message",
                "text": "Что такое AION?",
                "conversation_id": "test_ws_" + str(int(time.time())),
                "lang": "ru",
            }))
            print("  [OK] Message sent")
            results.append("[OK] Message sent")

            # 6. Receive stream + done
            print("  [5/5] Receiving responses...")
            chunks = []
            done_data = None

            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=10)
                msg = json.loads(raw)
                t = msg.get("type")

                if t == "chat.stream":
                    chunks.append(msg.get("text", ""))
                    print("       Stream chunk (" + str(len(msg.get("text", ""))) + "c): "
                          + msg.get("text", "")[:50])

                elif t == "chat.done":
                    done_data = msg
                    total = len("".join(chunks))
                    print("       Done: " + str(len(chunks)) + " chunks, "
                          + str(len(msg.get("text", ""))) + " chars total")
                    break

                elif t == "error":
                    print("  [FAIL] Server error: " + msg.get("message", ""))
                    results.append("[FAIL] Server error: " + msg.get("message", ""))
                    break

            # Validate results
            if chunks:
                results.append("[OK] Stream: " + str(len(chunks)) + " chunks")
            if done_data:
                results.append("[OK] chat.done received")
                has_nav = done_data.get("navigation") is not None
                has_cards = done_data.get("cards") is not None
                results.append("[OK] Navigation: " + ("yes" if has_nav else "no"))
                results.append("[OK] Cards: " + ("yes" if has_cards else "no"))

            # 7. Ping
            print("\n  [PING] Sending ping...")
            await ws.send(json.dumps({"type": "ping"}))
            pong = json.loads(await ws.recv())
            if pong.get("type") == "pong":
                print("  [OK] Pong received")
                results.append("[OK] Pong received")
            else:
                print("  [FAIL] Ping response: " + str(pong))
                results.append("[FAIL] Pong")

    except Exception as e:
        print("  [ERROR] " + str(e))
        import traceback
        traceback.print_exc()
        results.append("[ERROR] " + str(e).split("\\n")[0])

    finally:
        # Restore original RouterAgent
        RouterAgent.execute = _orig_execute

        # Stop server
        if server:
            server.should_exit = True
            await asyncio.sleep(0.5)

    # Summary
    print("\n" + "-" * 60)
    for r in results:
        print("  " + r)

    passed = sum(1 for r in results if r.startswith("[OK]"))
    failed = sum(1 for r in results if r.startswith("[FAIL]"))
    errors = sum(1 for r in results if r.startswith("[ERROR]"))

    print("\n  Total: " + str(len(results)))
    print("  Passed: " + str(passed))
    print("  Failed: " + str(failed))
    print("  Errors: " + str(errors))

    if failed == 0 and errors == 0:
        print("\n  " + "=" * 60)
        print("    WEB SOCKET TEST PASSED - all " + str(len(results)) + " checks OK")
        print("  " + "=" * 60)

    # Cleanup test db
    db_path = os.path.join(os.path.dirname(__file__), "aion_test.db")
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    asyncio.run(test_websocket())
