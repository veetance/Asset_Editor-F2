"""
ASSET EDITOR - FastAPI Server
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI
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
async def preload_model(model: str = "flux"):
    """Preload a model into GPU memory."""
    from model_manager import swapper
    try:
        if model == "flux":
            swapper.load_flux()
        elif model == "qwen":
            swapper.load_qwen()
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
        swapper._offload_current()
        return {
            "status": "offloaded",
            "vram": swapper.get_vram_usage()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Routes
app.include_router(decompose_router, prefix="/api", tags=["decompose"])
app.include_router(generate_router, prefix="/api", tags=["generate"])

# Static files
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
