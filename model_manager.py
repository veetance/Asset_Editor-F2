"""
ASSET EDITOR - Model Manager
VRAM Swapper for hot-swapping Qwen and FLUX on 16GB GPU
"""

import gc
import torch
from typing import Optional, Literal

ModelType = Literal["qwen", "flux", None]


class VRAMSwapper:
    """
    Singleton that manages GPU memory for large models.
    Only one model in VRAM at a time. Others stay warm in System RAM.
    """
    
    _instance: Optional["VRAMSwapper"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.current: ModelType = None
        self._qwen_pipe = None
        self._flux_pipe = None
    
    @property
    def qwen_pipe(self):
        """Lazy load Qwen pipeline."""
        if self._qwen_pipe is None:
            from diffusers import QwenImageLayeredPipeline
            print("[VRAM] Loading Qwen-Image-Layered to CPU...")
            self._qwen_pipe = QwenImageLayeredPipeline.from_pretrained(
                "Qwen/Qwen-Image-Layered",
                torch_dtype=torch.bfloat16
            )
            self._qwen_pipe.to("cpu")
            print("[VRAM] Qwen loaded to CPU.")
        return self._qwen_pipe
    
    @property
    def flux_pipe(self):
        """Lazy load FLUX pipeline."""
        if self._flux_pipe is None:
            from diffusers import Flux2KleinPipeline
            print("[VRAM] Loading FLUX.2-klein-9b-fp8 to CPU...")
            self._flux_pipe = Flux2KleinPipeline.from_pretrained(
                "black-forest-labs/FLUX.2-klein-9b-fp8",
                torch_dtype=torch.bfloat16
            )
            self._flux_pipe.to("cpu")
            print("[VRAM] FLUX loaded to CPU.")
        return self._flux_pipe
    
    def _offload_current(self):
        """Move current model from GPU to CPU."""
        if self.current == "qwen" and self._qwen_pipe is not None:
            self._qwen_pipe.to("cpu")
            print("[VRAM] Qwen offloaded to CPU.")
        elif self.current == "flux" and self._flux_pipe is not None:
            self._flux_pipe.to("cpu")
            print("[VRAM] FLUX offloaded to CPU.")
        
        torch.cuda.empty_cache()
        gc.collect()
        self.current = None
    
    def load_qwen(self):
        """Swap Qwen into VRAM."""
        if self.current == "qwen":
            return self.qwen_pipe
        
        self._offload_current()
        self.qwen_pipe.to("cuda")
        self.current = "qwen"
        print("[VRAM] Qwen active on GPU.")
        return self.qwen_pipe
    
    def load_flux(self):
        """Swap FLUX into VRAM."""
        if self.current == "flux":
            return self.flux_pipe
        
        self._offload_current()
        self.flux_pipe.to("cuda")
        self.current = "flux"
        print("[VRAM] FLUX active on GPU.")
        return self.flux_pipe
    
    def get_vram_usage(self) -> dict:
        """Return current VRAM stats."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            return {
                "allocated_gb": round(allocated, 2),
                "reserved_gb": round(reserved, 2),
                "current_model": self.current
            }
        return {"error": "CUDA not available"}


# Global singleton
swapper = VRAMSwapper()
