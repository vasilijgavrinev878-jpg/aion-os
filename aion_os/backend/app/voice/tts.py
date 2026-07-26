"""Text-to-Speech — Kokoro-82M and Piper.

Supports:
- Kokoro-82M: High quality, multilingual, Apache 2.0, 2-3GB VRAM
- Piper: Ultra-lightweight, CPU-friendly, MIT
- Streaming audio generation (play while generating)
"""

from __future__ import annotations

import io
import json
import os
from pathlib import Path
from typing import AsyncGenerator

from app.config import settings


class TTSService:
    """Text-to-speech service.

    Uses Kokoro-82M for quality. Falls back to Piper for CPU/edge.
    """

    def __init__(self) -> None:
        self._provider = os.environ.get("TTS_PROVIDER", "kokoro")  # kokoro or piper

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        speed: float | None = None,
        format: str = "ogg",
    ) -> bytes:
        """Convert text to speech audio.

        Args:
            text: Text to speak.
            voice: Voice ID (e.g., "af_bella", "am_adam").
            speed: Speech speed multiplier.
            format: Output audio format (ogg, wav, mp3).

        Returns:
            Audio bytes.
        """
        voice = voice or settings.TTS_VOICE
        speed = speed or settings.TTS_SPEED

        if self._provider == "kokoro":
            return await self._synthesize_kokoro(text, voice, speed, format)
        else:
            return await self._synthesize_piper(text, voice, speed, format)

    async def _synthesize_kokoro(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        format: str = "ogg",
    ) -> bytes:
        """Synthesize using Kokoro-82M via API."""
        import httpx

        # Kokoro API endpoint (runs in separate container)
        api_base = os.environ.get(
            "TTS_API_BASE",
            "http://tts:5001",
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{api_base}/v1/audio/speech",
                    json={
                        "model": "kokoro-82m",
                        "input": text,
                        "voice": voice,
                        "response_format": format,
                        "speed": speed,
                    },
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            # Fallback to piper if kokoro fails
            return await self._synthesize_piper(text, voice, speed, format)

    async def _synthesize_piper(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        format: str = "wav",
    ) -> bytes:
        """Synthesize using Piper TTS (lightweight, CPU-friendly)."""
        import subprocess

        voice_model = Path(f"/models/piper/{voice}.onnx")
        if not voice_model.exists():
            voice_model = Path("/models/piper/en_US-lessac-medium.onnx")

        if not voice_model.exists():
            raise RuntimeError("No TTS model available")

        try:
            result = subprocess.run(
                [
                    "piper",
                    "--model", str(voice_model),
                    "--output-raw",
                    "--length-scale", str(1.0 / speed),
                ],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )

            if format == "wav":
                return result.stdout

            # Convert to OGG if needed
            import subprocess as sp
            ogg_result = sp.run(
                ["ffmpeg", "-f", "s16le", "-ar", "22050", "-ac", "1",
                 "-i", "-", "-f", "ogg", "-"],
                input=result.stdout,
                capture_output=True,
                timeout=30,
            )
            return ogg_result.stdout

        except Exception as e:
            raise RuntimeError(f"Piper TTS failed: {e}") from e

    async def stream_synthesize(
        self,
        text_stream: AsyncGenerator[str, None],
        voice: str | None = None,
        speed: float | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio while text is being generated.

        This enables "play while generating" — audio starts before
        the full response is ready.
        """
        voice = voice or settings.TTS_VOICE
        speed = speed or settings.TTS_SPEED
        buffer = ""

        async for text_chunk in text_stream:
            buffer += text_chunk
            # Synthesize at sentence boundaries
            for sep in [". ", "! ", "? ", "\n"]:
                if sep in buffer:
                    sentence, buffer = buffer.split(sep, 1)
                    sentence += sep
                    if sentence.strip():
                        audio = await self.synthesize(sentence, voice, speed)
                        yield audio

        # Synthesize remaining buffer
        if buffer.strip():
            audio = await self.synthesize(buffer, voice, speed)
            yield audio
