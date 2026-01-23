
"""
VEETANCE - High-Speed VRAM Swapper
Minimal logic for 16GB VRAM operation.
"""
import torch
import gc

class VRAMSwapper:
    def __init__(self):
        self.current = "idle"
        # The Sovereign Pool: Keyed by model_id
        self.pool = {}
        # Order of usage for LRU ejection
        self.usage_history = []
        # RAM Governor Limit (Updated to 50GB for 64GB Gear)
        self.ram_limit_gb = 50.0


    def register_manifold(self, model_id, pipeline):
        """Injects a pipeline into the Sovereign Pool with RAM guarding."""
        self.enforce_ram_limit()
        
        print(f"[VRAM] Registering layer: {model_id} to RAM Pool.")
        self.pool[model_id] = pipeline
        self._touch(model_id)

    def _touch(self, model_id):
        """Updates the usage history for the LRU governor."""
        if model_id in self.usage_history:
            self.usage_history.remove(model_id)
        self.usage_history.append(model_id)

    def enforce_ram_limit(self):
        """Ensures the pool doesn't exceed the defined RAM budget."""
        import psutil
        while len(self.pool) > 0:
            ram = psutil.virtual_memory()
            used_gb = ram.used / (1024**3)
            
            # If we are over the limit, eject the least recently used model (not current)
            if used_gb > self.ram_limit_gb:
                candidates = [m for m in self.usage_history if m != self.current and m in self.pool]
                if not candidates:
                    break # Nowhere to go
                
                eject_id = candidates[0]
                print(f"[VRAM] Governor: Ejecting {eject_id} to maintain RAM headroom.")
                del self.pool[eject_id]
                self.usage_history.remove(eject_id)
                
                # Force cleanup after ejection
                gc.collect()
                torch.cuda.empty_cache()
            else:
                break

    def offload_current(self, hard_purge=False):
        """Standard offload: Move weights to CPU RAM."""
        if self.current == "idle" or self.current == "loading...":
            return

        print(f"[VRAM] Offloading {self.current} to System Memory...")
        pipe = self.pool.get(self.current)
        
        if pipe:
            if hard_purge:
                print(f"[VRAM] HARD PURGE: Deleting {self.current}.")
                del self.pool[self.current]
                if self.current in self.usage_history:
                    self.usage_history.remove(self.current)
                self.current = "idle"
            else:
                # Move everything to CPU. Explicitly handle components
                # to avoid relying on patched .to()
                if hasattr(pipe, "transformer") and pipe.transformer:
                    pipe.transformer.to("cpu")
                if hasattr(pipe, "vae") and pipe.vae:
                    pipe.vae.to("cpu")
                if hasattr(pipe, "text_encoder") and pipe.text_encoder:
                    pipe.text_encoder.to("cpu")
        
        torch.cuda.empty_cache()
        gc.collect()

    def shift_to_gpu(self, model_id):
        """Registers the model as current. Carrier handles the actual silicon migration."""
        if model_id not in self.pool:
            return False
            
        print(f"[VRAM] Activating {model_id} via Sovereign Pool.")
        self.current = model_id
        self._touch(model_id) 
        return True

    def get_vram_usage(self):
        """Telemetry Feed: Returns GPU Stats for the Mission Control dashboard."""
        if not torch.cuda.is_available():
            return {"vram_used": 0, "vram_total": 0, "model": self.current}
            
        # Physical stats
        t = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        a = torch.cuda.memory_allocated(0) / (1024**3) # Actual tensors
        r = torch.cuda.memory_reserved(0) / (1024**3) # Cache/Reservoir
        
        import psutil
        ram = psutil.virtual_memory()
        
        return {
            "vram_allocated_gb": round(a, 2),
            "vram_reserved_gb": round(r, 2),
            "vram_used": round(a + r, 2), # Legacy compatible
            "vram_total": round(t, 2),
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "cpu_percent": psutil.cpu_percent(),
            "model": self.current,
            "pool": list(self.pool.keys())
        }

swapper = VRAMSwapper()
