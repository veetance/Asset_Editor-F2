
import os
import shutil
from huggingface_hub import hf_hub_download

# Base Directions
BASE_MODEL_DIR = os.path.join(os.getcwd(), "models")
SOVEREIGN_FLUX_DIR = os.path.join(BASE_MODEL_DIR, "flux-klein")

def requisition_component(repo, filename, target_subpath, rename_as=None):
    """Surgical Injection with High-Velocity Check."""
    target_dir = os.path.join(SOVEREIGN_FLUX_DIR, target_subpath)
    os.makedirs(target_dir, exist_ok=True)

    local_filename = rename_as if rename_as else filename.split('/')[-1]
    target_path = os.path.join(target_dir, local_filename)

    if os.path.exists(target_path):
        print(f"✅ Component Saturated: {local_filename}")
        return

    print(f"📥 Requisitioning {local_filename} from {repo}...")
    try:
        downloaded_path = hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir=target_dir,
            local_dir_use_symlinks=False
        )
        # Move file to expected name if different
        if os.path.basename(downloaded_path) != local_filename:
            final_path = os.path.join(target_dir, local_filename)
            shutil.move(downloaded_path, final_path)
        print(f"✨ {local_filename} Saturated.")
    except Exception as e:
        print(f"❌ Requisition Failed for {local_filename}: {e}")

def ignite_sovereign_download():
    print("🦾 VEETANCE BRAIN SYNC: INITIATING...")

    # 1. VAE for 4B
    requisition_component(
        repo="Comfy-Org/flux2-dev",
        filename="split_files/vae/flux2-vae.safetensors",
        target_subpath="vae",
        rename_as="diffusion_pytorch_model.safetensors"
    )

    # 2. Text Encoder for 4B
    requisition_component(
        repo="Comfy-Org/flux2-klein-4B",
        filename="split_files/text_encoders/qwen_3_4b.safetensors",
        target_subpath="text_encoder/4b",
        rename_as="model.safetensors"
    )

    # 3. 4B Model Weights
    requisition_component(
        repo="black-forest-labs/FLUX.2-klein-4b-fp8",
        filename="flux-2-klein-4b-fp8.safetensors",
        target_subpath="transformer/4b",
        rename_as="model.safetensors"
    )

    # 4. 4B Config
    requisition_component(
        repo="black-forest-labs/FLUX.2-klein-4b-fp8",
        filename="config.json",
        target_subpath="transformer/4b",
        rename_as="config.json"
    )

    # 5. 4B Text Encoder Config
    requisition_component(
        repo="Comfy-Org/flux2-klein-4B",
        filename="text_encoder/config.json",
        target_subpath="text_encoder/4b",
        rename_as="config.json"
    )

    print("\n🚀 BRAIN MANIFOLD ALIGNED. 🦾⚡")

if __name__ == "__main__":
    ignite_sovereign_download()
