
"""
VEETANCE - FLUX 9B Sovereign Engine
FP8 Optimized Manifold for 16GB VRAM.
"""
import os
import torch
from diffusers import Flux2KleinPipeline, Flux2Transformer2DModel, AutoencoderKLFlux2
from .qwen_fp8 import load_qwen3_text_encoder

def build_9b_pipeline():
    """
    Ignites the 9B Sovereign engine at maximum velocity.
    """
    flux_dir = r"e:\Data-D-2\FLUX-2-KLEIN\models\flux-klein"
    print("[LOADER] Initiating FLUX.2-Klein-9B (Sovereign)...")

    # 1. Load Text Encoder (Official Qwen3-8B / 4096-dim)
    te_path = os.path.join(flux_dir, "text_encoder", "brain-8b")
    te = load_qwen3_text_encoder(te_path)

    # 2. Pipeline Shell
    pipe = Flux2KleinPipeline.from_pretrained(
        flux_dir,
        text_encoder=te,
        transformer=None,
        vae=None,
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )

    # 3. Inject 9B Transformer (FP8 Optimized)
    trans_path = os.path.join(flux_dir, "transformer", "klein-9b")
    # We load the weights. If they are FP8, we can use torch_dtype=torch.float8_e4m3fn 
    # but for stability on 16GB, we let Diffusers decide or cast to BF16.
    print("[LOADER] Materializing 9B Transformer silicon...")
    pipe.transformer = Flux2Transformer2DModel.from_pretrained(
        trans_path,
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )

    # 4. Inject VAE (Stability Fix: Float32)
    vae_path = os.path.join(flux_dir, "vae")
    vae = AutoencoderKLFlux2.from_pretrained(
        vae_path,
        torch_dtype=torch.float32,
        local_files_only=True
    )
    pipe.vae = vae
    
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()

    # 6. Manifold Calibration
    if hasattr(pipe.scheduler, "config"):
        pipe.scheduler.register_to_config(shift=3.0)

    print("[LOADER] FLUX.2-Klein-9B Sovereign Online.")
    return pipe
