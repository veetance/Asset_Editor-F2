import os
import torch
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Core Imports
from core.logger_config import setup_asset_editor_logging
# Core Imports
from core.logger_config import setup_asset_editor_logging
from core.carrier import carrier
from core.vram import governor
from core.loaders.hybrid_loader import hybrid_loader


# Initialize Asset Editor Signal Manifold
setup_asset_editor_logging()
logger = logging.getLogger("ASSET_EDITOR")

app = FastAPI(title="Asset Editor | Zerodrag", description="Sovereign Image Editor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SOVEREIGN API ROUTER ---
api_router = APIRouter(prefix="/api")

@api_router.get("/health")
async def health():
    return {"status": "Asset Editor Online", "governor": governor.get_telemetry()}

@api_router.post("/preload")
async def preload(model: str = "flux-4b"):
    logger.info(f"[SYSTEM] Preload Sequence Initiated | Target: {model.upper()}")
    try:
        # Route to 4B Sovereign
        model_id = "4b"
        hybrid_loader.build_franklin_pipeline(model_id=model_id, precision="fp16")
        governor.active_model = "flux-4b"
        
        return {
            "status": "success", 
            "model": model,
            "loaded": True,
            "vram_governor": governor.get_telemetry()
        }
    except Exception as e:
        logger.error(f"Preload Fault: {e}")
        return {"status": "error", "message": str(e)}

@api_router.post("/offload")
async def offload():
    logger.info("[SYSTEM] Offload Sequence Initiated.")
    # Purge Both Manifolds
    carrier.clear_board()

    governor.active_model = "NONE"
    return {"status": "success", "message": "Silicon Purged (Global)"}

@api_router.post("/governor/limit")
async def set_vram_limit(limit_percent: float = Form(95.0)):
    governor.set_limit(limit_percent)
    return {"status": "success", "limit": float(limit_percent), "budget_gb": governor.get_budget_gb()}

@api_router.post("/txt2img")
async def txt2img(
    prompt: str = Form(...),
    width: int = Form(1024),
    height: int = Form(1024),
    steps: int = Form(4),
    guidance: float = Form(3.5),
    seed: int = Form(-1),
    target_model: str = Form("flux-4b", alias="model_variant"),
    sampler: str = Form("flow_euler"),
    scheduler: str = Form("linear")
):
    if isinstance(prompt, list): prompt = prompt[0]
    logger.info(f"[DATA] Inference Request Received | Target: {target_model} | {prompt[:40]}... | Sampler: {sampler} | Scheduler: {scheduler}")
    try:
        # ROUTING LOGIC
        m_id = "4b"
        result = carrier.dispatch(
            prompt=str(prompt),
            model_id=m_id,
            height=height,
            width=width,
            steps=steps,
            guidance=guidance,
            seed=seed,
            sampler=sampler,
            scheduler=scheduler
        )
        
        telemetry = governor.get_telemetry()
        return {
            "status": "success", 
            "image": result.get("path", "/outputs/latest.png"),
            "model": target_model.upper(),
            "vram_used": telemetry["gpu"]["used"],
            "telemetry": telemetry
        }
    except Exception as e:
        import traceback
        logger.error(f"Inference Fault: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}

app.include_router(api_router)

@app.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            status = governor.get_telemetry()
            await websocket.send_json(status)
            await asyncio.sleep(0.5)
    except (WebSocketDisconnect, Exception):
        pass

# --- STATIC ASSET SERVING ---
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    print("ASSET EDITOR INITIALIZED")
    print("PIPELINE: ZERODRAG")
    print("STATUS: IGNITION READY")
    print("ACCESS: http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")