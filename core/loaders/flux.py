"""
ASSET EDITOR - Flux Loader
Constructs FLUX.2-klein pipelines from LOCAL files.
"""
import os
import torch
from diffusers import (
    Flux2KleinPipeline,  # Klein-specific pipeline with Qwen3 support
    FlowMatchEulerDiscreteScheduler, 
    Flux2Transformer2DModel
)

try:
    import xformers
    HAS_XFORMERS = True
except ImportError:
    HAS_XFORMERS = False

def build_flux_pipeline(variant: str = "4b"):
    """
    Load FLUX.2-klein from complete local folder.
    
    Args:
        variant: "4b" for the 4B model, "9b" for the 9B FP8 model.
    """
    print(f"[LOADER] Initiating FLUX.2-Klein-{variant.upper()} pipeline...")
    
    # Base directory (shared components)
    flux_dir = r"e:\Data-D-2\FLUX-2-KLEIN\models\flux-klein"
    
    if not os.path.exists(flux_dir):
        print(f"[LOADER] ERROR: Model directory not found at {flux_dir}")
        return None
    
    # Use bfloat16 - works on both GPU and CPU (needed for offloading)
    dtype = torch.bfloat16
    
    # DISABLE Ampere-only flags for Turing stability
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    print(f"[LOADER] Loading Flux2KleinPipeline from {flux_dir}...")
    pipe = Flux2KleinPipeline.from_pretrained(
        flux_dir,
        torch_dtype=dtype,
        local_files_only=True,
        low_cpu_mem_usage=False
    )

    if variant == "9b":
        # 9B variant - load transformer from subfolder
        transformer_dir = os.path.join(flux_dir, "transformer", "klein-9b")
        if not os.path.exists(transformer_dir):
            print(f"[LOADER] ERROR: 9B transformer not found at {transformer_dir}")
            return None
        
        print("[LOADER] Loading 9B Transformer from subfolder...")
        transformer_9b = Flux2Transformer2DModel.from_pretrained(
            transformer_dir,
            torch_dtype=dtype,
            local_files_only=True
        )
        pipe.transformer = transformer_9b
        print("[LOADER] 9B Transformer Swapped.")
    
    print(f"[LOADER] Pipeline Assembled: {type(pipe).__name__}")
    
    # SIMPLIFIED DEVICE STRATEGY
    # Use diffusers native CPU offload - handles device transitions automatically
    print("[LOADER] Enabling Sequential CPU Offload (Turing Memory Safe)...")
    
    # First, move everything to CUDA with FP16 (Turing optimized)
    pipe = pipe.to("cuda", dtype=torch.float16)
    
    # Enable memory-efficient features
    pipe.enable_model_cpu_offload()  # Auto-offloads unused components to CPU during inference
    
    if HAS_XFORMERS:
        print("[LOADER] Enabling xformers Attention Manifold...")
        pipe.enable_xformers_memory_efficient_attention()

    # VAE Memory Management for 1024px
    print("[LOADER] Stabilizing VAE for 1024px Generation...")
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    
    # Scheduler
    pipe.scheduler = FlowMatchEulerDiscreteScheduler.from_config(pipe.scheduler.config)
    
    print(f"[LOADER] FLUX.2-klein-{variant.upper()} Pipeline Ready (Turing Optimized).")
    return pipe
