import gc
import torch
import os
from typing import Optional, Literal
from diffusers import FluxPipeline, FlowMatchEulerDiscreteScheduler
from transformers import CLIPTextModel, CLIPTokenizer, T5EncoderModel, T5Tokenizer

# Note: QwenImageLayeredPipeline and GGUF support require diffusers from source
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
        # UPDATED: FLUX GGUF Q8_0
        self.flux_dir = r"d:\FLUX-2-KLIEN\models\flux-klein"
        self.flux_gguf = os.path.join(self.flux_dir, "flux-2-klein-9b-Q8_0.gguf")
        self.flux_config = "FLUX-KLEIN"
        
        # Qwen GGUF Path (UPDATED to Q5_0 for speed)
        self.qwen_dir = r"d:\FLUX-2-KLIEN\models\qwen-layered"
        self.qwen_gguf = os.path.join(self.qwen_dir, "Qwen_Image_Layered-Q5_0.gguf")
        
        # External Linkage Paths (From your existing ComfyUI Manifold)
        self.ext_clip_path = r"C:\MAIN-COMFY\ComfyUI\models\clip\clip-vit-large-patch14"
        self.ext_t5_path = r"C:\MAIN-COMFY\ComfyUI\models\clip\t5xxl_fp8_e4m3fn.safetensors"
        self.ext_t5_config = r"d:\FLUX-2-KLIEN\models\t5-xxl"  # Local T5 config
        self.ext_t5_tokenizer_path = r"C:\MAIN-COMFY\ComfyUI\custom_nodes\ComfyUI-WanVideoWrapper\configs\T5_tokenizer"
        self.ext_vae_path = r"C:\MAIN-COMFY\ComfyUI\models\vae\flux-vae-bf16.safetensors"
        
        # Local Qwen VAE path (consolidated in vae folder)
        self.qwen_vae_path = r"d:\FLUX-2-KLIEN\models\vae\qwen-vae.safetensors"
    
    @property
    def qwen_pipe(self):
        """Lazy load Qwen pipeline (Single-file GGUF preference)."""
        if self._qwen_pipe is None:
            if QwenImageLayeredPipeline is None:
                print("[VRAM] Error: QwenImageLayeredPipeline not found. Ensure diffusers is installed from source.")
                return None
                
            print(f"[VRAM] Loading Qwen-Image-Layered from {self.qwen_gguf}...")
            
            from diffusers import AutoencoderKL
            qwen_vae = AutoencoderKL.from_single_file(self.qwen_vae_path, torch_dtype=torch.bfloat16)

            if os.path.exists(self.qwen_gguf):
                self._qwen_pipe = QwenImageLayeredPipeline.from_single_file(
                    self.qwen_gguf,
                    vae=qwen_vae,
                    torch_dtype=torch.bfloat16
                )
            else:
                self._qwen_pipe = QwenImageLayeredPipeline.from_pretrained(
                    self.qwen_dir,
                    vae=qwen_vae,
                    torch_dtype=torch.bfloat16
                )
            
            self._qwen_pipe.to("cpu")
            print("[VRAM] Qwen loaded with local VAE.")
        return self._qwen_pipe
    
    @property
    def flux_pipe(self):
        """
        Lazy load FLUX pipeline from LOCAL files only.
        No internet required after initial setup.
        """
        if self._flux_pipe is None:
            print(f"🦾 [VRAM] Initiating LOCAL FLUX pipeline...")
            
            from diffusers import FluxTransformer2DModel, AutoencoderKL, GGUFQuantizationConfig
            
            # 1. Load FLUX Transformer from local GGUF
            print(f"[VRAM] Loading FLUX GGUF from {self.flux_gguf}...")
            quantization_config = GGUFQuantizationConfig(compute_dtype=torch.bfloat16)
            transformer = FluxTransformer2DModel.from_single_file(
                self.flux_gguf,
                quantization_config=quantization_config,
                torch_dtype=torch.bfloat16
            )
            
            # 2. Load CLIP from local ComfyUI folder (has config.json)
            print(f"[VRAM] Loading CLIP from {self.ext_clip_path}...")
            clip = CLIPTextModel.from_pretrained(
                self.ext_clip_path,
                torch_dtype=torch.bfloat16,
                local_files_only=True
            )
            
            # 3. Load T5 from local config + safetensors
            print(f"[VRAM] Loading T5 from {self.ext_t5_config}...")
            t5 = T5EncoderModel.from_pretrained(
                self.ext_t5_config,
                torch_dtype=torch.bfloat16,
                local_files_only=True
            )
            
            # 4. Load VAE from local safetensors
            print(f"[VRAM] Loading VAE from {self.ext_vae_path}...")
            vae = AutoencoderKL.from_single_file(
                self.ext_vae_path,
                torch_dtype=torch.bfloat16
            )
            
            # 5. Load Tokenizers and Scheduler
            print("[VRAM] Loading Tokenizers and Scheduler...")
            clip_tokenizer = CLIPTokenizer.from_pretrained(self.ext_clip_path, local_files_only=True)
            t5_tokenizer = T5Tokenizer.from_pretrained(self.ext_t5_tokenizer_path, local_files_only=True)
            
            scheduler_config_path = os.path.join(self.flux_dir, "scheduler_config.json")
            scheduler = FlowMatchEulerDiscreteScheduler.from_json_file(scheduler_config_path)
            
            # 6. Assemble pipeline manually (Bypass model_index.json/HF check)
            print("[VRAM] Assembling FLUX pipeline manually...")
            self._flux_pipe = FluxPipeline(
                scheduler=scheduler,
                vae=vae,
                text_encoder=clip,
                tokenizer=clip_tokenizer,
                transformer=transformer,
                text_encoder_2=t5,
                tokenizer_2=t5_tokenizer
            )
            self._flux_pipe.enable_model_cpu_offload()
            print("[VRAM] FLUX loaded 100% LOCAL (CPU Offload).")
                    
        return self._flux_pipe
    
    def _offload_current(self, keep_state=False):
        """Move current model from GPU to CPU and clear cache."""
        if self.current == "qwen" and self._qwen_pipe is not None:
            print("[VRAM] Offloading Qwen to CPU...")
            self._qwen_pipe.to("cpu")
        elif self.current == "flux" and self._flux_pipe is not None:
            print("[VRAM] Offloading FLUX to CPU...")
            self._flux_pipe.to("cpu")
        
        if not keep_state:
            self.current = None
        torch.cuda.empty_cache()
        gc.collect()
        print("[VRAM] GPU Repurposed.")
    
    def load_qwen(self):
        """Swap Qwen into VRAM."""
        if self.current == "qwen":
            return self.qwen_pipe
        
        self.current = "loading..."
        self._offload_current(keep_state=True)
        pipe = self.qwen_pipe
        if pipe:
            print("[VRAM] Engaging Qwen GPU Manifold...")
            pipe.to("cuda")
            self.current = "qwen"
        return pipe
    
    def load_flux(self):
        """Load FLUX pipeline (uses CPU offload for memory management)."""
        if self.current == "flux":
            return self.flux_pipe
        
        self.current = "loading..."
        self._offload_current(keep_state=True)
        pipe = self.flux_pipe
        if pipe:
            print("[VRAM] FLUX ready (CPU offload mode).")
            self.current = "flux"
        return pipe
    
    def get_vram_usage(self) -> dict:
        """Return current VRAM stats."""
        stats = {
            "status": "online" if torch.cuda.is_available() else "offline",
            "allocated_gb": 0.0,
            "reserved_gb": 0.0,
            "total_gb": 16.0,
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
