"""
ASSET EDITOR - Qwen Loader
Constructs Qwen Image Layered pipelines.
"""
import os
import torch
from diffusers import AutoencoderKL

try:
    from diffusers import QwenImageLayeredPipeline
except ImportError:
    QwenImageLayeredPipeline = None

def build_qwen_pipeline(gguf_path: str, vae_path: str, repo_dir: str):
    """Construct Qwen Pipeline from GGUF + Local VAE."""
    if QwenImageLayeredPipeline is None:
        print("[LOADER] Error: QwenImageLayeredPipeline not found.")
        return None

    print(f"[LOADER] Loading Qwen from {gguf_path}...")
    
    qwen_vae = AutoencoderKL.from_single_file(vae_path, torch_dtype=torch.bfloat16)

    if os.path.exists(gguf_path):
        pipe = QwenImageLayeredPipeline.from_single_file(
            gguf_path,
            vae=qwen_vae,
            torch_dtype=torch.bfloat16
        )
    else:
        pipe = QwenImageLayeredPipeline.from_pretrained(
            repo_dir,
            vae=qwen_vae,
            torch_dtype=torch.bfloat16
        )
    
    pipe.to("cpu") # Initial state
    print("[LOADER] Qwen Assembled.")
    return pipe
