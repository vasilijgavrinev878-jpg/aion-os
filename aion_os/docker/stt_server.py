"""STT HTTP server — OpenAI-compatible audio/transcriptions endpoint using Whisper.

Usage:
    python stt_server.py
    # or via docker: uvicorn stt_server:app --host 0.0.0.0 --port 5002

POST /v1/audio/transcriptions (multipart form)
    file: audio file
    model: whisper-1
    language: optional language code
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI(title="AION STT", version="0.1.0")

_whisper_model = None


def get_model():
    """Lazy-load Whisper model."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        model_name = os.environ.get("STT_MODEL", "large-v3-turbo")
        _whisper_model = whisper.load_model(model_name)
        return _whisper_model
    except Exception as e:
        raise RuntimeError(f"Failed to load Whisper model: {e}")


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form("whisper-1"),
    language: str = Form(""),
):
    model_engine = get_model()

    # Save uploaded file to temp
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        options = {"task": "transcribe", "fp16": False}
        if language:
            options["language"] = language

        result = model_engine.transcribe(tmp_path, **options)

        return JSONResponse({
            "text": result.get("text", "").strip(),
            "language": result.get("language", ""),
            "segments": result.get("segments", []),
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": _whisper_model is not None}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "5002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
