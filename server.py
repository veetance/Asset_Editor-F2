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

# Routes
app.include_router(decompose_router, prefix="/api", tags=["decompose"])
app.include_router(generate_router, prefix="/api", tags=["generate"])

# Static files
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.get("/api/health")
async def health():
    """Health check."""
    from model_manager import swapper
    return {
        "status": "ok",
        "vram": swapper.get_vram_usage()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
