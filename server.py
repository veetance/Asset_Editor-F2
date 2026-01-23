"""
ASSET EDITOR - FastAPI Server
"""

import os
import logging
import warnings

# === SOVEREIGN BOOT SEQUENCE ===
# 1. Resolve Namespace Friction: Statically select the high-performance distribution.
warnings.filterwarnings("ignore", message="Multiple distributions found for package modelopt")
try:
    from importlib.metadata import requires
    requires("nvidia-modelopt")
except Exception:
    pass

# 2. Silence Network Friction: Mute distributed heartbeats.
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
    print(f"[PRELOAD] Requested: {model}")
    try:
        # Clean string to avoid matching issues
        model_id = model.strip().lower()
        
        if "9b-gguf" in model_id:
            print("[PRELOAD] Target Identified: FLUX-9B (GGUF)")
            swapper.load_flux("flux-9b-gguf")
        elif "9b" in model_id:
            print("[PRELOAD] Target Identified: FLUX-9B (Safetensors)")
            swapper.load_flux("9b")
        elif "4b" in model_id:
            print("[PRELOAD] Target Identified: FLUX-4B")
            swapper.load_flux("4b")
        elif "qwen" in model_id:
            print("[PRELOAD] Target Identified: QWEN")
            swapper.load_qwen()
        else:
            return {"status": "error", "error": f"Unknown model: {model}"}
            
        return {
            "status": "loaded",
            "model": swapper.current,
            "vram": swapper.get_vram_usage()
        }
    except Exception as e:
        print(f"[PRELOAD] ERROR: {e}")
        return {"status": "error", "error": str(e)}


@app.post("/api/offload")
async def offload_models():
    """Offload all models from GPU to CPU and release memory."""
    from model_manager import swapper
    try:
        swapper.offload_current(hard_purge=True)
        return {
            "status": "offloaded",
            "vram": swapper.get_vram_usage()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/purge")
async def purge_cache():
    """
    PURGE PROTOCOL: Clear HuggingFace cache and system temp files.
    Reclaims storage consumed by diffusers downloads and pip residue.
    """
    import shutil
    import tempfile
    
    purged_paths = []
    errors = []
    
    # 1. HuggingFace Cache (~/.cache/huggingface)
    hf_cache = Path.home() / ".cache" / "huggingface"
    if hf_cache.exists():
        try:
            shutil.rmtree(hf_cache, ignore_errors=True)
            purged_paths.append(str(hf_cache))
        except Exception as e:
            errors.append(f"HF Cache: {e}")
    
    # 2. Torch Hub Cache (~/.cache/torch)
    torch_cache = Path.home() / ".cache" / "torch"
    if torch_cache.exists():
        try:
            shutil.rmtree(torch_cache, ignore_errors=True)
            purged_paths.append(str(torch_cache))
        except Exception as e:
            errors.append(f"Torch Cache: {e}")
    
    # 3. System Temp (Selective - only our pip/torch residue)
    temp_dir = Path(tempfile.gettempdir())
    for pattern in ["pip-*", "torch*", "tmp*"]:
        for item in temp_dir.glob(pattern):
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
                purged_paths.append(str(item))
            except Exception as e:
                errors.append(f"{item.name}: {e}")
    
    print(f"[PURGE] Cleared {len(purged_paths)} paths. Errors: {len(errors)}")
    
    return {
        "status": "purged",
        "cleared_count": len(purged_paths),
        "errors": errors if errors else None
    }


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
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"WS Exception: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass # Already closed or closing

# Routes
app.include_router(decompose_router, prefix="/api", tags=["decompose"])
app.include_router(generate_router, prefix="/api", tags=["generate"])

# Static files
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    # CRITICAL: reload=False to prevent WinError 1450 resource exhaustion during heavy model loads
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
