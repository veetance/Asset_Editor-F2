"""
ASSET EDITOR - VRAM Telemetry & Singleton
"""
import torch
import gc
from typing import Optional, Literal

ModelType = Literal["qwen", "flux", None]

class VRAMSwapper:
    """
    Singleton that manages GPU memory for large models.
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
    
    def offload_current(self, keep_state=False):
        """Move current model from GPU to CPU and clear cache."""
        if self.current == "qwen" and self._qwen_pipe is not None:
            print("[VRAM] Offloading Qwen to CPU...")
            self._qwen_pipe.to("cpu")
        elif self.current and self.current.startswith("flux-") and self._flux_pipe is not None:
            print(f"[VRAM] Offloading {self.current.upper()} to CPU...")
            self._flux_pipe.to("cpu")
        
        if not keep_state:
            self.current = None
        torch.cuda.empty_cache()
        gc.collect()
        print("[VRAM] GPU Repurposed.")

    def get_vram_usage(self) -> dict:
        """Return current memory stats (VRAM and System RAM)."""
        import psutil
        stats = {
            "status": "online" if torch.cuda.is_available() else "offline",
            "allocated_gb": 0.0,
            "reserved_gb": 0.0,
            "total_gb": 16.0,
            "ram_used_gb": round(psutil.Process().memory_info().rss / 1024**3, 2),
            "cpu_percent": psutil.cpu_percent(),
            "current_model": self.current
        }
        if torch.cuda.is_available():
            try:
                stats["allocated_gb"] = round(torch.cuda.memory_allocated() / 1024**3, 2)
                stats["reserved_gb"] = round(torch.cuda.memory_reserved() / 1024**3, 2)
                
                device = torch.cuda.current_device()
                props = torch.cuda.get_device_properties(device)
                stats["total_gb"] = round(props.total_memory / 1024**3, 2)
            except Exception as e:
                print(f"[VRAM] Telemetry Error: {e}")
        return stats


# Global singleton
swapper = VRAMSwapper()
