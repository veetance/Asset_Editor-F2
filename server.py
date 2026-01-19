"""
ASSET EDITOR - FastAPI Server
"""

import os
import logging

# SILENCE HARMFUL WARNING: W0119 torch.distributed.elastic.multiprocessing.redirects
# This warning is aggressive and unfixable on Windows, so we mute the logger.
logging.getLogger("torch.distributed.elastic.multiprocessing.redirects").setLevel(logging.ERROR)

import uuid
from pathlib import Path
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routes.decompose import router as decompose_router
from routes.generate import router as generate_router

# Paths
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# App
app = FastAPI(title="ASSET EDITOR", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    """Health check."""
    from model_manager import swapper
    return {
        "status": "ok",
        "vram": swapper.get_vram_usage()
    }


@app.post("/api/preload")
async def preload_model(model: str = "flux-4b"):
    """Preload a model into GPU memory."""
    from model_manager import swapper
    try:
        if model == "flux-4b":
            swapper.load_flux("4b")
        elif model == "flux-9b":
            swapper.load_flux("9b")
        elif model == "qwen":
            swapper.load_qwen()
        else:
            return {"status": "error", "error": f"Unknown model: {model}"}
        return {
            "status": "loaded",
            "model": model,
            "vram": swapper.get_vram_usage()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/offload")
async def offload_models():
    """Offload all models from GPU to CPU."""
    from model_manager import swapper
    try:
        swapper.offload_current()
        return {
            "status": "offloaded",
            "vram": swapper.get_vram_usage()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()
    from model_manager import swapper
    try:
        while True:
            # 1. Receive Controls (Non-blocking check? No, we just push mostly)
            # For simplicity: Push stats every 100ms
            stats = swapper.get_vram_usage()
            await websocket.send_json(stats)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"WS Disconnect: {e}")
    finally:
        await websocket.close()

# Routes
app.include_router(decompose_router, prefix="/api", tags=["decompose"])
app.include_router(generate_router, prefix="/api", tags=["generate"])

# Static files
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
