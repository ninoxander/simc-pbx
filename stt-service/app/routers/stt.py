from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(
    prefix="/stt",
    tags=["Speech to Text"]
)

class TranscribeRequest(BaseModel):
    audio_path: str

@router.post("/transcribe")
def transcribe_audio(payload: TranscribeRequest):
    if not os.path.exists(payload.audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return {
        "status": "success",
        "audio_path": payload.audio_path,
        "text": "Texto transcrito de prueba"
    }

@router.get("/health")
def stt_status():
    return {"service": "stt", "ready": True}