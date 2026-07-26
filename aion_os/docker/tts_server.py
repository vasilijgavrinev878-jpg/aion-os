"""TTS HTTP server — OpenAI-compatible audio/speech endpoint using Kokoro-82M.

Usage:
    python tts_server.py
    # or via docker: uvicorn tts_server:app --host 0.0.0.0 --port 5001

POST /v1/audio/speech
{
    "model": "kokoro-82m",
    "input": "Text to synthesize",
    "voice": "af_bella",
    "response_format": "wav",
    "speed": 1.0
}
"""

from __future__ import annotations

import io
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI(title="AION TTS", version="0.1.0")

_tts_model = None


class TTSRequest(BaseModel):
    model: str = "kokoro-82m"
    input: str = ""
    voice: str = "af_bella"
    response_format: str = "wav"
    speed: float = 1.0


def get_model():
    """Lazy-load Kokoro model."""
    global _tts_model
    if _tts_model is not None:
        return _tts_model
    try:
        from kokoro import KPipeline
        _tts_model = KPipeline(lang_code=os.environ.get("TTS_LANG", "a"))
        return _tts_model
    except ImportError:
        return None


@app.post("/v1/audio/speech")
async def synthesize_speech(request: TTSRequest):
    model = get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="TTS model not loaded")

    try:
        generator = model(
            request.input,
            voice=request.voice,
            speed=request.speed,
        )
        audio_chunks = []
        for _, _, audio in generator:
            if audio is not None:
                audio_chunks.append(audio.numpy().tobytes())

        if not audio_chunks:
            raise HTTPException(status_code=500, detail="No audio generated")

        audio_data = b"".join(audio_chunks)

        media_type = {
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "mp3": "audio/mpeg",
        }.get(request.response_format, "audio/wav")

        return Response(content=audio_data, media_type=media_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": _tts_model is not None}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "5001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
