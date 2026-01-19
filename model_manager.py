"""
ASSET EDITOR - Model Manager (Entry Point)
Integrates VRAM Swapper with Loaders.
"""
import os
from core.vram import swapper
from core.loaders import build_flux_pipeline, build_qwen_pipeline

# Monkey patch loaders into the singleton to keep the API clean
def load_qwen_proxy():
    if swapper.current == "qwen":
        return swapper._qwen_pipe
    
    swapper.current = "loading..."
    swapper.offload_current(keep_state=True)
    
    if swapper._qwen_pipe is None:
        # Paths (CORRECTED to actual E: drive manifold)
        qwen_dir = r"e:\Data-D-2\FLUX-2-KLEIN\models\qwen-layered"
        qwen_gguf = os.path.join(qwen_dir, "Qwen_Image_Layered-Q5_0.gguf")
        qwen_vae = r"e:\Data-D-2\FLUX-2-KLEIN\models\vae\qwen-vae.safetensors"
        
        swapper._qwen_pipe = build_qwen_pipeline(qwen_gguf, qwen_vae, qwen_dir)
        
    if swapper._qwen_pipe:
        print("[MANAGER] Engaging Qwen GPU Manifold...")
        swapper._qwen_pipe.to("cuda")
        swapper.current = "qwen"
        
    return swapper._qwen_pipe

def load_flux_proxy(variant: str = "4b"):
    """Load FLUX pipeline with specified variant (4b or 9b)."""
    target_model = f"flux-{variant}"
    
    # Already loaded the correct variant
    if swapper.current == target_model:
        return swapper._flux_pipe
    
    swapper.current = "loading..."
    swapper.offload_current(keep_state=True)
    
    # Always rebuild if switching variants (different transformer)
    print(f"[MANAGER] Loading FLUX {variant.upper()}...")
    swapper._flux_pipe = build_flux_pipeline(variant)
        
    if swapper._flux_pipe:
        print(f"[MANAGER] FLUX {variant.upper()} Ready.")
        swapper.current = target_model
        
    return swapper._flux_pipe

# Attach methods
swapper.load_qwen = load_qwen_proxy
swapper.load_flux = load_flux_proxy
