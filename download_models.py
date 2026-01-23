
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
        hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir=target_dir,
            local_dir_use_symlinks=False
        )
        # Move file out of nested download folder if present
        # hf_hub_download inside local_dir creates nested 'split_files/...'
        downloaded_path = os.path.join(target_dir, filename.replace('/', os.sep))
        if os.path.exists(downloaded_path) and downloaded_path != target_path:
            shutil.move(downloaded_path, target_path)
            # Cleanup residue
            parts = filename.split('/')
            if len(parts) > 1:
                residue = os.path.join(target_dir, parts[0])
                if os.path.isdir(residue): shutil.rmtree(residue)
        print(f"✨ {local_filename} Saturated.")
    except Exception as e:
        print(f"❌ Requisition Failed for {local_filename}: {e}")

def ignite_sovereign_download():
    print("🦾 VEETANCE BRAIN SYNC: INITIATING...")

    # 1. BRAIN MANIFEST
    # Qwen3-4B (2560-dim) for 4B Engine
    requisition_component(
        repo="Comfy-Org/flux2-klein-4B",
        filename="split_files/text_encoders/qwen_3_4b.safetensors",
        target_subpath="text_encoder/brain-4b",
        rename_as="model.safetensors"
    )
    
    # Qwen3-8B (4096-dim) for 9B Engine
    requisition_component(
        repo="Comfy-Org/flux2-klein-9B",
        filename="split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors",
        target_subpath="text_encoder/brain-8b",
        rename_as="model.safetensors"
    )

    # 2. CONFIG MANIFEST (Surgical Alignment)
    # Grab 8B config for the 8B brain
    requisition_component(
        repo="black-forest-labs/FLUX.2-klein-9b-fp8", # Assuming it exists here or root
        filename="text_encoder/config.json",
        target_subpath="text_encoder/brain-8b",
        rename_as="config.json"
    )
    # Note: If 9B repo is missing it, we will copy it from dev or Comfy-Org
    
    print("\n🚀 BRAIN MANIFOLD ALIGNED. 🦾⚡")

if __name__ == "__main__":
    ignite_sovereign_download()
