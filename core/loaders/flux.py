
"""
VEETANCE - Neural Pipeline Dispatcher
Phase 5.3 RE-ZERO Standard Implementation.
"""
from .flux_4b import build_4b_pipeline
from .flux_9b import build_9b_pipeline

def build_flux_pipeline(variant="4b", force_gguf=False):
    """
    Standard Safetensors Dispatcher.
    """
    if variant == "4b":
        return build_4b_pipeline()
    elif variant == "9b":
        return build_9b_pipeline()
    else:
        print(f"[DISPATCHER] Warning: Unknown variant {variant}. Defaulting to 4B.")
        return build_4b_pipeline()
