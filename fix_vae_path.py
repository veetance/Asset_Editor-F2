import os
import shutil

# Path to the nested file
nested_path = r"d:\FLUX-2-KLIEN\models\qwen-layered\vae\vae\diffusion_pytorch_model.safetensors"
# Target path
target_path = r"d:\FLUX-2-KLIEN\models\qwen-layered\vae\diffusion_pytorch_model.safetensors"

if os.path.exists(nested_path):
    print(f"Moving VAE to correct manifold location...")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.move(nested_path, target_path)
    print("✅ VAE Corrected.")
else:
    print("❌ Nested VAE not found or already moved.")
