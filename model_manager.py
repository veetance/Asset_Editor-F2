import gc
import torch
import os
from typing import Optional, Literal
from diffusers import FluxPipeline
from transformers import CLIPTextModel, T5EncoderModel

# Note: QwenImageLayeredPipeline requires diffusers from source
try:
    from diffusers import QwenImageLayeredPipeline
except ImportError:
    QwenImageLayeredPipeline = None

ModelType = Literal["qwen", "flux", None]

class VRAMSwapper:
    """
    Singleton that manages GPU memory for large models.
    Leverages external COMFY/FORGE assets to save space.
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
        
        # Paths for Local Downloads (The Core Weights)
        self.flux_ckpt = r"d:\FLUX-2-KLIEN\models\flux-schnell\flux-2-klein-9b-fp8.safetensors"
        self.flux_config = "black-forest-labs/FLUX.1-schnell"
        self.qwen_repo = r"d:\FLUX-2-KLIEN\models\qwen-layered"
        
        # External Linkage Paths (From your existing ComfyUI Manifold)
        self.ext_clip_path = r"C:\MAIN-COMFY\ComfyUI\models\clip\clip-vit-large-patch14"
        self.ext_t5_path = r"C:\MAIN-COMFY\ComfyUI\models\clip\t5-v1_1-xxl-encoder-Q3_K_S.gguf"
        self.ext_vae_path = r"C:\MAIN-COMFY\ComfyUI\models\vae\flux-vae-bf16.safetensors"
        self.qwen_vae_path = r"C:\MAIN-COMFY\ComfyUI\models\vae\qwen_image_vae.safetensors"
    
    @property
    def qwen_pipe(self):
        """Lazy load Qwen pipeline (Folder structure)."""
        if self._qwen_pipe is None:
            if QwenImageLayeredPipeline is None:
                print("[VRAM] Error: QwenImageLayeredPipeline not found. Ensure diffusers is installed from source.")
                return None
                
            print(f"[VRAM] Loading Qwen-Image-Layered from {self.qwen_repo}...")
            
            # Link external Qwen VAE
            print(f"[VRAM] Linking Qwen VAE from {self.qwen_vae_path}...")
            from diffusers import AutoencoderKL
            qwen_vae = AutoencoderKL.from_single_file(self.qwen_vae_path, torch_dtype=torch.bfloat16)

            self._qwen_pipe = QwenImageLayeredPipeline.from_pretrained(
                self.qwen_repo,
                vae=qwen_vae,
                torch_dtype=torch.bfloat16
            )
            self._qwen_pipe.to("cpu")
            print("[VRAM] Qwen loaded and linked to external VAE.")
        return self._qwen_pipe
    
    @property
    def flux_pipe(self):
        """Lazy load FLUX pipeline with External ComfyUI Linkage."""
        if self._flux_pipe is None:
            print(f"🦾 [VRAM] Initiating high-fidelity linkage to ComfyUI encoders...")
            
            # Load CLIP from C:
            print(f"[VRAM] Linking CLIP-L from {self.ext_clip_path}...")
            clip = CLIPTextModel.from_pretrained(self.ext_clip_path, torch_dtype=torch.bfloat16)
            
            # Load T5 GGUF from C:
            print(f"[VRAM] Linking T5-GGUF from {self.ext_t5_path}...")
            t5 = T5EncoderModel.from_single_file(self.ext_t5_path, torch_dtype=torch.bfloat16)

            # Load VAE from C:
            print(f"[VRAM] Linking FLUX VAE from {self.ext_vae_path}...")
            from diffusers import AutoencoderKL
            vae = AutoencoderKL.from_single_file(self.ext_vae_path, torch_dtype=torch.bfloat16)

            # Load the main Flux manifold from D:
            print(f"[VRAM] Loading FLUX-Klein from {self.flux_ckpt}...")
            self._flux_pipe = FluxPipeline.from_single_file(
                self.flux_ckpt,
                text_encoder=clip,
                text_encoder_2=t5,
                vae=vae,
                config=self.flux_config,
                torch_dtype=torch.bfloat16
            )
            
            self._flux_pipe.to("cpu")
            print("[VRAM] FLUX Manifold aligned and stabilized on CPU.")
        return self._flux_pipe
    
    def _offload_current(self):
        """Move current model from GPU to CPU and clear cache."""
        if self.current == "qwen" and self._qwen_pipe is not None:
            print("[VRAM] Offloading Qwen to CPU...")
            self._qwen_pipe.to("cpu")
        elif self.current == "flux" and self._flux_pipe is not None:
            print("[VRAM] Offloading FLUX to CPU...")
            self._flux_pipe.to("cpu")
        
        self.current = None
        torch.cuda.empty_cache()
        gc.collect()
        print("[VRAM] GPU Repurposed.")
    
    def load_qwen(self):
        """Swap Qwen into VRAM."""
        if self.current == "qwen":
            return self.qwen_pipe
        
        self._offload_current()
        pipe = self.qwen_pipe
        if pipe:
            print("[VRAM] Engaging Qwen GPU Manifold...")
            pipe.to("cuda")
            self.current = "qwen"
        return pipe
    
    def load_flux(self):
        """Swap FLUX into VRAM."""
        if self.current == "flux":
            return self.flux_pipe
        
        self._offload_current()
        pipe = self.flux_pipe
        if pipe:
            print("[VRAM] Engaging FLUX GPU Manifold...")
            pipe.to("cuda")
            self.current = "flux"
        return pipe
    
    def get_vram_usage(self) -> dict:
        """Return current VRAM stats."""
        stats = {"status": "offline"}
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            stats = {
                "status": "online",
                "allocated_gb": round(allocated, 2),
                "reserved_gb": round(reserved, 2),
                "max_reserved_gb": round(torch.cuda.max_memory_reserved() / 1024**3, 2),
                "current_model": self.current
            }
        return stats

# Global singleton
swapper = VRAMSwapper()
