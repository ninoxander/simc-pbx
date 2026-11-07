import time
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from faster_whisper import WhisperModel

app = FastAPI(title="PBX STT Service")

print("[STT-INIT]")
t0 = time.perf_counter()
model = WhisperModel("tiny", device="cpu", compute_type="int8")
print(f"[STT-INIT] Modelo listo en {(time.perf_counter() - t0):.2f}s")

class TranscribeRequest(BaseModel):
    filepath: str

@app.post("/transcribe")
def transcribe_audio(req: TranscribeRequest):
    t_start = time.perf_counter()

    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=404, detail=f"FIle not found: {req.filepath}")

    # Inferencia básica
    t_infer_start = time.perf_counter()
    segments, info = model.transcribe(
        req.filepath,
        language="es",
        beam_size=1,
        vad_filter=True
    )
    texto = " ".join([seg.text for seg in segments]).strip()
    t_end = time.perf_counter()

    infer_ms = (t_end - t_infer_start) * 1000
    total_ms = (t_end - t_start) * 1000

    # Log 
    print("\n" + "=" * 65, flush=True)
    print(f"[*] RECEIVED AUDIO   : {req.filepath}", flush=True)
    print(f"[*] STT INFERENCE   : {infer_ms:.2f} ms", flush=True)
    print(f"[✓] TET API : {total_ms:.2f} ms", flush=True)
    print(f">>> TRANSCRIPTION    : \"{texto}\"", flush=True)
    print("=" * 65 + "\n", flush=True)

    return {
        "status": "ok",
        "text": texto,
        "inference_ms": round(infer_ms, 2),
        "total_ms": round(total_ms, 2)
    }
