
"""
VEETANCE - Clean Qwen3 FP8 Loader
Unified logic for FP8Mixed text encoders.
"""
import torch
import os
from safetensors import safe_open
from transformers import AutoConfig, AutoModelForCausalLM

def load_qwen3_text_encoder(model_dir: str, target_dtype: torch.dtype = torch.bfloat16):
    """
    Loads the Qwen3-8B FP8Mixed text encoder with zero hacks.
    """
    checkpoint_path = os.path.join(model_dir, "model.safetensors")
    config_path = os.path.join(model_dir, "config.json")
    
    print(f"[BRAIN] Requisitioning Qwen3 Manifold from {model_dir}...")
    
    # 1. Load Config
    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=True)
    
    # 2. Build Empty Shell
    with torch.device("meta"):
        model = AutoModelForCausalLM.from_config(config, trust_remote_code=True)
    
    # 3. Handle FP8Mixed Dequantization
    # Since we are on 16GB VRAM, we can afford to dequantize to BF16 for speed.
    model = model.to_empty(device="cpu")
    sd = model.state_dict()
    
    with safe_open(checkpoint_path, framework="pt") as f:
        keys = f.keys()
        for k in sd.keys():
            if k in keys:
                tensor = f.get_tensor(k)
                
                # Check for FP8 components
                s_key = k.replace(".weight", ".weight_scale")
                if (tensor.dtype == torch.float8_e4m3fn or tensor.dtype == torch.float8_e5m2) and s_key in keys:
                    scale = f.get_tensor(s_key)
                    # Dequantize to BF16
                    v = (tensor.to(torch.float32) * scale.to(torch.float32)).to(target_dtype)
                    sd[k].copy_(v)
                else:
                    sd[k].copy_(tensor.to(target_dtype))
            else:
                 # Check for ComfyUI style packing if needed (not expected in official Klein)
                 pass

    print(f"[BRAIN] Qwen3 Brain Saturated.")
    return model.to(target_dtype)
