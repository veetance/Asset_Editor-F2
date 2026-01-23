"""
ASSET EDITOR - Model Manager (Entry Point)
Integrates VRAM Swapper with Loaders.
"""
import os
from core.vram import swapper
from core.loaders import build_flux_pipeline, build_qwen_pipeline

# Monkey patch loaders into the singleton to keep the API clean
def load_qwen_proxy():
    model_id = "qwen"
    
    # 1. Immediate GPU Shift if cached
    if swapper.shift_to_gpu(model_id):
        return swapper.pool[model_id]
    
    # 2. Cold Boot: Load from Disk
    swapper.current = "loading..."
    swapper.offload_current()
    
    # Paths (Official E: Drive Manifold)
    qwen_dir = r"e:\Data-D-2\FLUX-2-KLEIN\models\qwen-layered"
    qwen_gguf = os.path.join(qwen_dir, "Qwen_Image_Layered-Q5_0.gguf")
    qwen_vae = os.path.join(qwen_dir, "vae", "diffusion_pytorch_model.safetensors")
    
    pipe = build_qwen_pipeline(qwen_gguf, qwen_vae, qwen_dir)
    
    if pipe:
        swapper.register_manifold(model_id, pipe)
        swapper.shift_to_gpu(model_id)
        
    return pipe

def load_flux_proxy(variant: str = "4b"):
    """Load FLUX pipeline with specified variant (4b or 9b)."""
    clean_variant = variant.replace("flux-", "").strip()
    model_id = f"flux-{clean_variant}"
    
    # 1. Immediate GPU Shift if cached
    if swapper.shift_to_gpu(model_id):
        return swapper.pool[model_id]
    
    # 2. Cold Boot: Load from Disk
    swapper.current = "loading..."
    swapper.offload_current()
    
    print(f"[MANAGER] Cold Booting FLUX {clean_variant.upper()} (Disk -> RAM Pool)...")
    
    if clean_variant == "4b":
        from core.loaders.flux_4b import build_4b_pipeline
        pipe = build_4b_pipeline()
    elif clean_variant == "9b":
        from core.loaders.flux_9b import build_9b_pipeline
        pipe = build_9b_pipeline()
    else:
        # Generic fallback
        pipe = build_flux_pipeline(clean_variant)

    if pipe:
        swapper.register_manifold(model_id, pipe)
        swapper.shift_to_gpu(model_id)
        
    return pipe

# Attach methods
swapper.load_qwen = load_qwen_proxy
swapper.load_flux = load_flux_proxy
