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
    model_variant: str = Form(default="flux-4b"), # Explicit Steering
    vram_budget: float = Form(default=16.0)
):
    """Generate image from text prompt using FLUX.2-Klein."""
    from model_manager import swapper
    
    # Identify requested variant
    is_9b = "9b" in model_variant.lower()
    variant_id = "9b" if is_9b else "4b"
    
    # Audit Identity (Debug for singleton parity)
    print(f"[VRAM] Swapper Identity: {hex(id(swapper))} | Target: flux-{variant_id}")
    
    # ========== TELEMETRY VRAM CHECK (ADVISORY ONLY) ==========
    estimated_vram = estimate_vram_usage(width, height, is_9b)
    if estimated_vram > vram_budget:
        print(f"[VRAM] WARNING: Estimated {estimated_vram}GB exceeds Governor budget of {vram_budget}GB. PROCEEDING REGARDLESS.")
    else:
        print(f"[VRAM] Pre-Flight: Estimated {estimated_vram}GB (Budget: {vram_budget}GB) - SAFE")
    
    try:
        # FORCE REQUISITION of the correct variant
        pipe = swapper.load_flux(model_variant)
            
        if pipe is None:
            return JSONResponse({"error": "Failed to load FLUX model"}, status_code=500)
        
        # PROOF OF LIFE: Log Active Parameters
        transformer_params = sum(p.numel() for p in pipe.transformer.parameters())
        print(f"[VRAM] Using {swapper.current} for generation ({transformer_params/1e9:.2f}B Params Active)")
        
        # Apply Scheduler/Sampler Strategy
        pipe = set_scheduler(pipe, sampler, scheduler, width, height, steps)
        print(f"[LOADER] Manifold Strategy: {sampler} | {scheduler}")
        
        # Seed - Let pipeline determine device internally
        if seed < 0:
            seed = torch.randint(0, 2**32, (1,)).item()
        generator = torch.Generator().manual_seed(seed)
        
        # Flux2KleinPipeline handles Qwen3 prompt formatting internally
        print(f"[PROMPT] Raw: {prompt[:80]}...")
        
        # 6. ENFORCE SOVEREIGN EXECUTION (Carrier Layer)
        from core.carrier import carrier
        
        # Determine Execution Strategy
        try:
            # 6. UNIVERSAL DISPATCH: Delegate execution to the Sovereign Carrier
            # The Carrier automatically negotiates the optimal physics (SCM, Managed, or Qwen)
            result = carrier.dispatch(
                model_id=model_variant,
                pipe=pipe,
                prompt=prompt,
                height=height,
                width=width,
                guidance_scale=guidance,
                num_inference_steps=steps,
                generator=generator
            )
            
            # Save
            session_id = str(uuid.uuid4())[:8]
            session_dir = OUTPUTS_DIR / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = session_dir / "generated.png"
            result.images[0].save(output_path)
            
            # Sanitization Protocol: Purge silicon immediately
            del result
            torch.cuda.empty_cache()
            import gc
            gc.collect()

            return JSONResponse({
                "session_id": session_id,
                "image": f"/outputs/{session_id}/generated.png",
                "seed": seed,
                "sampler": sampler,
                "model": swapper.current,
                "vram_used": estimated_vram
            })
        except torch.cuda.OutOfMemoryError:
            print("[VRAM] CRITICAL: Silicon Exhaustion. Triggering Emergency Purge.")
            swapper.offload_current(hard_purge=True)
            return JSONResponse({"error": "VRAM Exhaustion. Manifold Reset."}, status_code=507)
    except Exception as e:
        import traceback
        print(f"[ERROR] txt2img failed: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


def set_scheduler(pipe, sampler_name: str, scheduler_mode: str = "standard", width: int = 1024, height: int = 1024, steps: int = 4):
    from diffusers import FlowMatchEulerDiscreteScheduler
    
    # ADAPTIVE SHIFT: 3.5 for 4-steps, 3.0 for 10+ steps
    shift_val = 3.5 if steps <= 4 else 3.0
    use_karras = (scheduler_mode == "karras")
    
    print(f"[LOADER] Applying Adaptive Shift: {shift_val} for {steps} steps.")
    
    # Re-initialize the scheduler with the optimal Flux configuration
    pipe.scheduler = FlowMatchEulerDiscreteScheduler.from_config(
        pipe.scheduler.config,
        shift=shift_val,
        use_karras_sigmas=use_karras
    )
    return pipe
    
    
    if scheduler_mode == "beta":
        if "use_beta_sigmas" in inspect.signature(new_scheduler.__class__.from_config).parameters:
            new_scheduler = new_scheduler.__class__.from_config(config, use_beta_sigmas=True)
        elif hasattr(new_scheduler, "config") and "beta" in new_scheduler.config:
            new_scheduler = new_scheduler.__class__.from_config(config, use_beta_sigmas=True)

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
    from model_manager import swapper
    
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
    from model_manager import swapper
    
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
