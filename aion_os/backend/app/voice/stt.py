"""Speech-to-Text — Whisper-based voice recognition.

Supports:
- Local Whisper model for on-premise deployment
- OpenAI Whisper API fallback
- Streaming transcription (future)
- Multiple languages (auto-detected by Whisper)
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import AsyncGenerator

from app.config import settings


class STTService:
    """Speech-to-text service using Whisper.

    By default uses local Whisper model.
    Falls back to OpenAI/DeepSeek Whisper API if available.
    """

    def __init__(self) -> None:
        self._model = None
        self._use_local = bool(os.environ.get("USE_LOCAL_STT", "true").lower() == "true")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str | None = None,
        format: str = "ogg",
    ) -> str:
        """Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes.
            language: Expected language (auto-detect if None).
            format: Audio format (ogg, wav, mp3).

        Returns:
            Transcribed text.
        """
        if self._use_local:
            return await self._transcribe_local(audio_data, language)
        else:
            return await self._transcribe_api(audio_data, language)

    async def _transcribe_local(
        self,
        audio_data: bytes,
        language: str | None = None,
    ) -> str:
        """Transcribe using local Whisper model."""
        try:
            import whisper

            if self._model is None:
                model_name = settings.STT_MODEL
                self._model = whisper.load_model(model_name)

            # Save to temp file (Whisper reads from disk)
            temp_path = Path("/tmp/aion_voice_input.wav")
            temp_path.write_bytes(audio_data)

            result = self._model.transcribe(
                str(temp_path),
                language=language,
                task="transcribe",
                fp16=False,
            )

            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

            return result.get("text", "").strip()

        except Exception as e:
            raise RuntimeError(f"STT transcription failed: {e}") from e

    async def _transcribe_api(
        self,
        audio_data: bytes,
        language: str | None = None,
    ) -> str:
        """Transcribe via OpenAI-compatible API."""
        from openai import AsyncOpenAI

        api_key = settings.OPENAI_API_KEY or settings.DEEPSEEK_API_KEY
        if not api_key:
            raise RuntimeError("No API key for STT fallback")

        client = AsyncOpenAI(api_key=api_key)

        # Prepare audio file for upload
        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"voice.{'wav'}"

        try:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
            )
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"STT API failed: {e}") from e

    async def stream_transcribe(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming transcription (future feature)."""
        # Accumulate audio chunks
        audio_data = b""
        async for chunk in audio_stream:
            audio_data += chunk
            # Process in 5-second segments
            if len(audio_data) > 240000:  # ~30 seconds of audio
                text = await self.transcribe(audio_data, language)
                if text:
                    yield text
                audio_data = b""

        # Transcribe remaining
        if audio_data:
            text = await self.transcribe(audio_data, language)
            if text:
                yield text
