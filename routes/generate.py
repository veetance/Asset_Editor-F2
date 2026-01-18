"""
ASSET EDITOR - Generate Routes
FLUX-KLEIN endpoints for txt2img, img2img, and inpaint
"""

import uuid
import torch
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageOps
import io

router = APIRouter()

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


@router.post("/txt2img")
async def text_to_image(
    prompt: str = Form(...),
    width: int = Form(default=1024),
    height: int = Form(default=1024),
    steps: int = Form(default=4),
    guidance: float = Form(default=0.0),  # FLUX.1-schnell uses 0.0 (distilled model)
    sampler: str = Form(default="euler"),
    seed: int = Form(default=-1)
):
    """Generate image from text prompt using FLUX.2-Klein."""
    from model_manager import swapper
    
    try:
        pipe = swapper.load_flux()
        if pipe is None:
            return JSONResponse({"error": "Failed to load FLUX model"}, status_code=500)
        
        # Set scheduler based on sampler choice (DISABLED for Manual Assembly)
        # pipe = set_scheduler(pipe, sampler)
        print("[VRAM] Using pre-configured FlowMatch scheduler (Manual Assembly)")
        
        # Seed
        if seed < 0:
            seed = torch.randint(0, 2**32, (1,)).item()
        generator = torch.Generator(device="cuda").manual_seed(seed)
        
        # Generate (Official FLUX.1-schnell pattern)
        with torch.inference_mode():
            result = pipe(
                prompt=prompt,
                height=height,
                width=width,
                guidance_scale=guidance,  # 0.0 for schnell/distilled models
                num_inference_steps=steps,
                max_sequence_length=512,  # Upgraded to 512 for max adherence
                generator=generator
            )
        
        # Save
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUTS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = session_dir / "generated.png"
        result.images[0].save(output_path)
        
        return JSONResponse({
            "session_id": session_id,
            "image": f"/outputs/{session_id}/generated.png",
            "seed": seed,
            "sampler": sampler
        })
    except Exception as e:
        print(f"[ERROR] txt2img failed: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


def set_scheduler(pipe, sampler_name: str):
    """Set the scheduler/sampler for the pipeline."""
    from diffusers import (
        EulerDiscreteScheduler,
        EulerAncestralDiscreteScheduler,
        DPMSolverMultistepScheduler,
        DDIMScheduler,
        LMSDiscreteScheduler
    )
    
    scheduler_map = {
        "euler": EulerDiscreteScheduler,
        "euler_a": EulerAncestralDiscreteScheduler,
        "dpm++_2m": lambda cfg: DPMSolverMultistepScheduler.from_config(cfg, algorithm_type="dpmsolver++"),
        "dpm++_2m_karras": lambda cfg: DPMSolverMultistepScheduler.from_config(cfg, algorithm_type="dpmsolver++", use_karras_sigmas=True),
        "ddim": DDIMScheduler,
        "lms": LMSDiscreteScheduler,
    }
    
    if sampler_name in scheduler_map:
        scheduler_class = scheduler_map[sampler_name]
        if callable(scheduler_class) and not isinstance(scheduler_class, type):
            # Lambda function for special configs
            pipe.scheduler = scheduler_class(pipe.scheduler.config)
        else:
            pipe.scheduler = scheduler_class.from_config(pipe.scheduler.config)
    
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
    
    pipe = swapper.load_flux()
    
    # Load image
    content = await image.read()
    pil_image = Image.open(io.BytesIO(content)).convert("RGB")
    
    # Seed
    if seed < 0:
        seed = torch.randint(0, 2**32, (1,)).item()
    generator = torch.Generator(device="cuda").manual_seed(seed)
    
    # Generate
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
    
    return JSONResponse({
        "session_id": session_id,
        "image": f"/outputs/{session_id}/edited.png",
        "seed": seed
    })


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
    
    pipe = swapper.load_flux()
    
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
    
    return JSONResponse({
        "session_id": session_id,
        "image": f"/outputs/{session_id}/inpainted.png",
        "seed": seed
    })
