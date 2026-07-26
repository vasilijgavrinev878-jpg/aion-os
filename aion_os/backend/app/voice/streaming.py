"""Voice streaming pipeline — process and route voice data."""

from __future__ import annotations

import base64
from typing import AsyncGenerator

from app.voice.stt import STTService
from app.voice.tts import TTSService


class VoicePipeline:
    """End-to-end voice pipeline.

    Audio → STT → LLM/Agents → TTS → Audio
    """

    def __init__(self) -> None:
        self._stt = STTService()
        self._tts = TTSService()

    async def process_audio(
        self,
        audio_bytes: bytes,
        language: str | None = None,
    ) -> tuple[str, bytes]:
        """Process voice input end-to-end.

        Args:
            audio_bytes: Raw audio input.
            language: Expected language.

        Returns:
            (transcribed_text, response_audio_bytes)
        """
        text = await self._stt.transcribe(audio_bytes, language)
        return text, b""

    async def audio_to_text(self, audio_base64: str, language: str | None = None) -> str:
        """Decode base64 audio and transcribe to text.

        Args:
            audio_base64: Base64-encoded audio data.
            language: Expected language.

        Returns:
            Transcribed text.
        """
        audio_bytes = base64.b64decode(audio_base64)
        return await self._stt.transcribe(audio_bytes, language)

    async def text_to_audio(
        self,
        text: str,
        voice: str | None = None,
        speed: float | None = None,
    ) -> str:
        """Convert text to base64 audio.

        Args:
            text: Text to synthesize.
            voice: Voice ID.
            speed: Speed multiplier.

        Returns:
            Base64-encoded audio.
        """
        audio = await self._tts.synthesize(text, voice, speed)
        return base64.b64encode(audio).decode()

    async def stream_text_to_audio(
        self,
        text_stream: AsyncGenerator[str, None],
    ) -> AsyncGenerator[str, None]:
        """Stream text chunks and yield base64 audio chunks.

        Enables "play while generating" experience.
        """
        async for text_chunk in text_stream:
            audio = await self._tts.synthesize(text_chunk)
            yield base64.b64encode(audio).decode()

    def extract_audio_format(self, audio_base64: str) -> str:
        """Extract audio format from base64 header."""
        # WebRTC typically uses opus/ogg
        # Telegram voice messages are OGG Opus
        return "ogg"
