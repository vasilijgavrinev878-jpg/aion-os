"""WebSocket handler — real-time bidirectional communication.

Events:
- Client → Server: chat.message, chat.voice, ping
- Server → Client: chat.stream, chat.voice_stream, chat.done, chat.error, navigate, show_cards
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents.router import AgentContext, RouterAgent
from app.core.auth import decode_access_token, verify_telegram_init_data
from app.llm.adapter import LLMAdapter
from app.memory.manager import MemoryManager
from app.memory.store import ConversationStore
from app.voice.streaming import VoicePipeline

logger = logging.getLogger("aion.websocket")
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id] = [w for w in self._connections[user_id] if w != ws]
            if not self._connections[user_id]:
                del self._connections[user_id]

    async def send_json(self, user_id: int, data: dict[str, Any]) -> None:
        if user_id in self._connections:
            for ws in self._connections[user_id]:
                try:
                    await ws.send_json(data)
                except Exception:
                    pass


manager = ConnectionManager()
conversation_store = ConversationStore()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Main WebSocket endpoint for real-time chat."""
    user_id = 0
    try:
        # Accept the WebSocket connection first
        await ws.accept()

        # Wait for auth message
        data = await ws.receive_text()
        auth_data = json.loads(data)

        # Authenticate via token or initData
        if auth_data.get("type") == "auth":
            token = auth_data.get("token", "")
            payload = decode_access_token(token)
            if payload and "user_id" in payload:
                user_id = payload["user_id"]
                user_name = payload.get("first_name", "")
                user_lang = payload.get("lang", "ru")
            else:
                # Try initData
                init_data = auth_data.get("init_data", "")
                from app.core.auth import verify_telegram_init_data
                tg_user = verify_telegram_init_data(init_data)
                if tg_user:
                    user_id = tg_user.id
                    user_name = tg_user.first_name
                    user_lang = tg_user.language_code
                else:
                    await ws.send_json({"type": "error", "message": "Auth failed"})
                    await ws.close()
                    return

            # Track the connection
            if user_id not in manager._connections:
                manager._connections[user_id] = []
            manager._connections[user_id].append(ws)

            await ws.send_json({
                "type": "auth_ok",
                "user_id": user_id,
                "message": f"Connected as {user_name}",
            })
        else:
            await ws.send_json({"type": "error", "message": "Auth required"})
            await ws.close()
            return

        # Main message loop
        router_agent = RouterAgent()
        voice_pipeline = VoicePipeline()

        while True:
            try:
                data = await ws.receive_text()
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await ws.send_json({"type": "pong"})
                    continue

                if msg_type == "chat.message":
                    text = msg.get("text", "")
                    conv_id = msg.get("conversation_id", f"ws_{user_id}_{int(time.time())}")

                    # Store user message
                    await conversation_store.add_message(user_id, "user", text)

                    # Execute via Router agent (full pipeline: intent → agent → RAG → response)
                    ctx = AgentContext(
                        user_id=user_id,
                        message=text,
                        conversation_id=conv_id,
                        user_lang=msg.get("lang", "ru"),
                    )
                    result = await router_agent.execute(ctx)

                    # Stream response in chunks
                    for i in range(0, len(result.response), 30):
                        chunk = result.response[i:i+30]
                        await ws.send_json({
                            "type": "chat.stream",
                            "text": chunk,
                            "conversation_id": conv_id,
                        })

                    # Store AI response
                    await conversation_store.add_message(user_id, "assistant", result.response)

                    # Extract memories
                    memory_mgr = MemoryManager()
                    await memory_mgr.extract_and_store(user_id, text, result.response)

                    # Send completion with navigation and cards
                    await ws.send_json({
                        "type": "chat.done",
                        "text": result.response,
                        "conversation_id": conv_id,
                        "navigation": result.navigation,
                        "cards": result.cards,
                    })

                elif msg_type == "chat.voice":
                    audio_base64 = msg.get("audio", "")
                    text = await voice_pipeline.audio_to_text(audio_base64)

                    # Mirror the transcribed text back
                    await ws.send_json({
                        "type": "voice.transcribed",
                        "text": text,
                    })

                    # Process through agent router
                    ctx = AgentContext(
                        user_id=user_id,
                        message=text,
                        conversation_id=f"voice_{user_id}_{int(time.time())}",
                    )
                    result = await router_agent.execute(ctx)

                    # Stream response
                    for chunk in [result.response[i:i+20] for i in range(0, len(result.response), 20)]:
                        await ws.send_json({
                            "type": "chat.stream",
                            "text": chunk,
                        })

                    # If voice response requested, generate audio
                    if msg.get("voice_response", False):
                        audio = await voice_pipeline.text_to_audio(result.response)
                        await ws.send_json({
                            "type": "chat.voice_stream",
                            "audio": audio,
                            "format": "ogg",
                        })

                    await ws.send_json({
                        "type": "chat.done",
                        "text": result.response,
                        "navigation": result.navigation,
                        "cards": result.cards,
                    })

                else:
                    await ws.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                    })

            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if user_id:
            manager.disconnect(user_id, ws)
