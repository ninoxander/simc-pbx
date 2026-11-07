from fastapi import FastAPI
from app.routers import stt, pbx_control

app = FastAPI(
    title="SIMC-PBX Backend & STT",
    version="1.0.0",
    description="API modular para control de Asterisk y procesamiento Whisper"
)

app.include_router(stt.router)
app.include_router(pbx_control.router)

@app.get("/")
def root():
    return {"message": "SIMC-PBX Core API activa"}