"""
ASSET EDITOR - Generate Routes
FLUX-KLEIN endpoints for txt2img, img2img, and inpaint
"""

import uuid
import torch
import warnings
# Suppress Pydantic 'model_' protected namespace warnings
warnings.filterwarnings("ignore", message='.*protected namespace "model_".*')

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageOps
import io
import inspect
import functools

router = APIRouter()

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

# VRAM Safety Constants
# base_model = Transformer (4.5) + VAE (1.0) + TE_Quant (2.6) = ~8.1GB
VRAM_4B_BASE_GB = 8.1

VRAM_9B_BASE_GB = 10.5
VRAM_PER_MEGAPIXEL_GB = 1.2

def estimate_vram_usage(width: int, height: int, is_9b: bool = False) -> float:
    """Estimate total VRAM usage for a generation at given resolution."""
    megapixels = (width * height) / 1_000_000
    base = VRAM_9B_BASE_GB if is_9b else VRAM_4B_BASE_GB
    
    # Base + Latent + Activation buffer (1.5x safety margin)
    estimated = base + (megapixels * VRAM_PER_MEGAPIXEL_GB * 1.5)
    return round(estimated, 2)


@router.post("/txt2img")
async def text_to_image(
    prompt: str = Form(...),
    width: int = Form(default=1024),
    height: int = Form(default=1024),
    steps: int = Form(default=4),
    guidance: float = Form(default=1.0),
    sampler: str = Form(default="euler"),
    scheduler: str = Form(default="standard"),
    seed: int = Form(default=-1),
    model_variant: str = Form(default="flux-4b"),
    vram_budget: float = Form(default=14.5)
):
    """Generate image from text prompt using FLUX.2-Klein Sovereign Dispatch."""
    from model_manager import model_manager
    
    # identify requested variant
    is_9b = "9b" in model_variant.lower()
    model_size = "9b" if is_9b else "4b"
    
    try:
        # 1. ENSURE LOADED
        if not model_manager.current or model_size not in model_manager.current:
            print(f"[VRAM] Auto-Negotiating {model_size} Manifold...")
            model_manager.load_flux_model(model_size=model_size)

        # 2. GENERATE
        # Seed logic
        if seed < 0:
            import random
            seed = random.randint(0, 2**32 - 1)

        print(f"[CARRIER] Dispatching Sovereign Request: {width}x{height} | {steps} steps")
        
        # Execute via Carrier
        image = model_manager.generate_image_with_flux(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=guidance,
            seed=seed
        )

        # 3. PERSISTENCE
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUTS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = session_dir / "generated.png"
        image.save(output_path)
        
        print(f"[VRAM] Generation Cycle Complete. Image persisted to {session_id}")

        return JSONResponse({
            "session_id": session_id,
            "image": f"/outputs/{session_id}/generated.png",
            "seed": seed,
            "model": model_manager.current,
            "status": "success"
        })

    except torch.cuda.OutOfMemoryError:
        print("[VRAM] CRITICAL: Silicon Exhaustion. Purging Manifold.")
        model_manager.clear_all_models()
        return JSONResponse({"error": "VRAM Exhaustion. Manifold Reset."}, status_code=507)
    except Exception as e:
        import traceback
        print(f"[ERROR] Sovereign Dispatch Failed: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


def set_scheduler(pipe, sampler_name: str, scheduler_mode: str = "standard", width: int = 1024, height: int = 1024, steps: int = 4):
    from diffusers import FlowMatchEulerDiscreteScheduler
    
    # ADAPTIVE SHIFT: 3.5 for 4-steps, 3.0 for 10+ steps
    shift_val = 3.5 if steps <= 4 else 3.0
    use_karras = (scheduler_mode == "karras")
    
    print(f"[LOADER] Applying Adaptive Shift: {shift_val} for {steps} steps.")
    
    # Re-initialize the scheduler with the optimal Flux configuration
    new_scheduler = FlowMatchEulerDiscreteScheduler.from_config(
        pipe.scheduler.config,
        shift=shift_val,
        use_karras_sigmas=use_karras
    )
    pipe.scheduler = new_scheduler
    return pipe
    
    
    if scheduler_mode == "beta":
        # Beta scheduling (if needed in future)
        pass

    # SHIM: Parameter Filtering for universal compatibility
    original_set_timesteps = new_scheduler.set_timesteps
    
    # Analyze the actual signature of the scheduler's set_timesteps
    sig = inspect.signature(original_set_timesteps)
    params = sig.parameters
    
    @functools.wraps(original_set_timesteps)
    def shimmed_set_timesteps(*args, **kwargs):
        # 1. Handle Flow-Match specific parameters (mu, shift)
        if "mu" not in kwargs and "mu" in params:
            kwargs["mu"] = 0.0 # Default mu for Flux
            
        if "shift" not in kwargs and "shift" in params:
            # Enforce Sovereign Shift (3.0)
            kwargs["shift"] = base_shift
        elif "shift" in kwargs and "shift" not in params:
            kwargs.pop("shift")
            
        return original_set_timesteps(*args, **kwargs)
    
    new_scheduler.set_timesteps = shimmed_set_timesteps
    pipe.scheduler = new_scheduler
    return pipe


@router.post("/img2img")
async def image_to_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    strength: float = Form(default=0.75),
    steps: int = Form(default=4),
    guidance: float = Form(default=4.0),
    seed: int = Form(default=-1)
):
    """Transform image based on prompt."""
    from model_manager import model_manager as swapper
    
    if swapper.current and swapper.current.startswith("flux-"):
        pipe = swapper._flux_pipe
    else:
        pipe = swapper.load_flux("4b")
    
    # Load image
    content = await image.read()
    pil_image = Image.open(io.BytesIO(content)).convert("RGB")
    
    # Seed
    if seed < 0:
        seed = torch.randint(0, 2**32, (1,)).item()
    generator = torch.Generator(device="cuda").manual_seed(seed)
    
    # Generate
    try:
        with torch.inference_mode():
            result = pipe(
                prompt=prompt,
                image=pil_image,
                strength=strength,
                guidance_scale=guidance,
                num_inference_steps=steps,
                generator=generator
            )
        
        # Save
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUTS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = session_dir / "edited.png"
        result.images[0].save(output_path)
        
        # Sanitization Protocol: Purge cache
        torch.cuda.empty_cache()
        import gc
        gc.collect()

        return JSONResponse({
            "session_id": session_id,
            "image": f"/outputs/{session_id}/edited.png",
            "seed": seed
        })
    except torch.cuda.OutOfMemoryError:
        print("[VRAM] CRITICAL: OutOfMemoryError in img2img. Purging Manifold.")
        swapper.offload_current(hard_purge=True)
        return JSONResponse({"error": "GPU Memory Exhaustion during Edit. Reservoir Purged."}, status_code=507)


@router.post("/inpaint")
async def inpaint_image(
    image: UploadFile = File(...),
    mask: UploadFile = File(None),
    prompt: str = Form(...),
    strength: float = Form(default=0.85),
    steps: int = Form(default=4),
    guidance: float = Form(default=4.0),
    seed: int = Form(default=-1),
    use_alpha_mask: bool = Form(default=True)
):
    """
    Inpaint masked region of image.
    
    If use_alpha_mask=True and no mask provided, extracts mask from alpha channel.
    """
    from model_manager import model_manager as swapper
    
    if swapper.current and swapper.current.startswith("flux-"):
        pipe = swapper._flux_pipe
    else:
        pipe = swapper.load_flux("4b")
    
    # Load source image
    content = await image.read()
    pil_image = Image.open(io.BytesIO(content))
    
    # Handle mask
    if mask:
        # Manual mask provided
        mask_content = await mask.read()
        mask_image = Image.open(io.BytesIO(mask_content)).convert("L")
    elif use_alpha_mask and pil_image.mode == "RGBA":
        # Auto mask from alpha channel
        mask_image = pil_image.split()[3]
        mask_image = ImageOps.invert(mask_image)
    else:
        return JSONResponse({"error": "No mask provided and image has no alpha"}, status_code=400)
    
    # Convert to RGB for pipeline
    rgb_image = pil_image.convert("RGB")
    
    # Seed
    if seed < 0:
        seed = torch.randint(0, 2**32, (1,)).item()
    generator = torch.Generator(device="cuda").manual_seed(seed)
    
    # Inpaint
    try:
        with torch.inference_mode():
            result = pipe(
                prompt=prompt,
                image=rgb_image,
                mask_image=mask_image,
                strength=strength,
                guidance_scale=guidance,
                num_inference_steps=steps,
                generator=generator
            )
        
        # Save
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUTS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = session_dir / "inpainted.png"
        result.images[0].save(output_path)
        
        # Sanitization Protocol: Purge cache
        torch.cuda.empty_cache()
        import gc
        gc.collect()

        return JSONResponse({
            "session_id": session_id,
            "image": f"/outputs/{session_id}/inpainted.png",
            "seed": seed
        })
    except torch.cuda.OutOfMemoryError:
        print("[VRAM] CRITICAL: OutOfMemoryError in inpaint. Purging Manifold.")
        swapper.offload_current(hard_purge=True)
        return JSONResponse({"error": "GPU Memory Exhaustion during Inpaint. Reservoir Purged."}, status_code=507)
