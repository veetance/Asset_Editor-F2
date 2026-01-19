
import json
from safetensors import safe_open

path = r"e:\Data-D-2\FLUX-2-KLEIN\models\flux-klein-4b\transformer\flux-2-klein-9b-fp8.safetensors"

try:
    with safe_open(path, framework="pt", device="cpu") as f:
        # Check a weight to see hidden dim
        # FLUX weight shape for QKV is (3 * hidden_dim, hidden_dim)
        # But for FP8 it might be different or packed.
        key = "double_blocks.0.img_attn.qkv.weight"
        if key in f.keys():
            t = f.get_tensor(key)
            print(f"{key} shape: {t.shape}")
        else:
            # Try single block
            key = "single_blocks.0.linear1.weight"
            if key in f.keys():
                t = f.get_tensor(key)
                print(f"{key} shape: {t.shape}")
            
except Exception as e:
    print(f"Error: {e}")
