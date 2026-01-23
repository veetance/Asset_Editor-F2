"""
ASSET EDITOR - Decompose Route
Qwen-Image-Layered endpoint for RGBA layer extraction
"""

import uuid
import torch
import warnings
# Suppress Pydantic 'model_' protected namespace warnings
warnings.filterwarnings("ignore", message='.*protected namespace "model_".*')

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
import io

router = APIRouter()

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


@router.post("/decompose")
async def decompose_image(
    image: UploadFile = File(...),
    layers: int = Form(default=4),
    resolution: int = Form(default=640)
):
    """
    Decompose an image into RGBA layers using Qwen-Image-Layered.
    
    Args:
        image: Source image file
        layers: Number of layers to decompose (1-10)
        resolution: Processing resolution (640 or 1024, 640 recommended)
    
    Returns:
        JSON with session_id and layer URLs
    """
    from model_manager import swapper
    
    try:
        # Validate
        layers = max(1, min(10, layers))
        resolution = 640 if resolution < 800 else 1024
        
        # Create session
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUTS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Load image
        content = await image.read()
        pil_image = Image.open(io.BytesIO(content)).convert("RGBA")
        
        # Save original
        original_path = session_dir / "original.png"
        pil_image.save(original_path)
        
        # Load Qwen (swap FLUX out if needed)
        pipe = swapper.load_qwen()
        if pipe is None:
            return JSONResponse({"error": "Failed to load Qwen model. Ensure diffusers is installed from source."}, status_code=500)
        
        # Decompose (Official Qwen pattern from HuggingFace)
        inputs = {
            "image": pil_image,
            "generator": torch.Generator(device="cuda").manual_seed(42),
            "true_cfg_scale": 4.0,
            "negative_prompt": " ",
            "num_inference_steps": 50,
            "num_images_per_prompt": 1,
            "layers": layers,
            "resolution": resolution,  # 640 recommended per docs
            "cfg_normalize": True,
            "use_en_prompt": True,  # Auto-caption in English
        }
        
        with torch.inference_mode():
            output = pipe(**inputs)
        
        # Save layers
        layer_urls = []
        for i, layer_img in enumerate(output.images[0]):
            layer_path = session_dir / f"layer_{i}.png"
            layer_img.save(layer_path)
            layer_urls.append(f"/outputs/{session_id}/layer_{i}.png")
        
        return JSONResponse({
            "session_id": session_id,
            "layers": layer_urls,
            "count": len(layer_urls)
        })
    except Exception as e:
        print(f"[ERROR] decompose failed: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
