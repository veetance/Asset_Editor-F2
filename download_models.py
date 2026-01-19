import os
from huggingface_hub import hf_hub_download

# Define local storage
MODEL_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def create_link_manifest(folder_name, source_path):
    """Create a folder with a text file documenting the external link."""
    target_dir = os.path.join(MODEL_DIR, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    manifest_path = os.path.join(target_dir, "LINK_MANIFEST.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(f"🦾 ASSET LINKAGE ACTIVE\n")
        f.write(f"This component is symlinked or direct-pointed to save space on D: drive.\n")
        f.write(f"SOURCE_PATH: {source_path}\n")
    print(f"✅ Created linkage manifest for {folder_name}")

def download_manifold():
    print("🦾 INITIALIZING ELITE LEAN DOWNLOAD SEQUENCE...")
    
    # 1. Create Linkage Placemarkers (The "Ghost" Folders)
    linkage_map = {
        "clip-large": r"C:\MAIN-COMFY\ComfyUI\models\clip\clip-vit-large-patch14",
        "t5-xxl": r"C:\MAIN-COMFY\ComfyUI\models\clip\t5-v1_1-xxl-encoder-Q3_K_S.gguf",
        "vae": r"C:\MAIN-COMFY\ComfyUI\models\vae\flux-vae-bf16.safetensors"
    }
    
    for folder, path in linkage_map.items():
        create_link_manifest(folder, path)

    # 2. Qwen-Image-Layered (Quantized Q5_0 GGUF) - ~12.3GB
    # High-speed selection for 16GB VRAM manifolds.
    qwen_repo = "QuantStack/Qwen-Image-Layered-GGUF"
    qwen_file = "Qwen_Image_Layered-Q5_0.gguf"
    qwen_dir = os.path.join(MODEL_DIR, "qwen-layered")
    os.makedirs(qwen_dir, exist_ok=True)
    qwen_path = os.path.join(qwen_dir, qwen_file)

    if not os.path.exists(qwen_path):
        print(f"📥 Pulling {qwen_repo} (Q5_0 - ~12.3GB)...")
        try:
            hf_hub_download(repo_id=qwen_repo, filename=qwen_file, local_dir=qwen_dir)
        except Exception as e:
            print(f"❌ Qwen Error: {e}")
    else:
        print(f"✅ {qwen_file} detected.")

    # 3. Qwen VAE (Mission Critical for Layered Architecture) - ~1GB
    qwen_vae_repo = "Qwen/Qwen-Image-Layered"
    qwen_vae_file = "vae/diffusion_pytorch_model.safetensors"
    qwen_vae_dir = os.path.join(MODEL_DIR, "qwen-layered", "vae")
    os.makedirs(qwen_vae_dir, exist_ok=True)
    qwen_vae_local_path = os.path.join(qwen_vae_dir, "diffusion_pytorch_model.safetensors")

    if not os.path.exists(qwen_vae_local_path):
        print(f"📥 Pulling {qwen_vae_repo} VAE (~1GB)...")
        try:
            hf_hub_download(repo_id=qwen_vae_repo, filename=qwen_vae_file, local_dir=qwen_vae_dir)
        except Exception as e:
            print(f"❌ Qwen VAE Error: {e}")
    else:
        print(f"✅ Qwen VAE detected.")

    # 4. FLUX.2-klein-4B Safetensors (Official BFL - Diffusers Compatible) - ~8GB
    from huggingface_hub import snapshot_download
    flux_repo = "black-forest-labs/FLUX.2-klein-4B"
    flux_dir = os.path.join(MODEL_DIR, "flux-klein-4b")
    flux_marker = os.path.join(flux_dir, "transformer", "diffusion_pytorch_model.safetensors")
    
    if not os.path.exists(flux_marker):
        print(f"[DOWNLOAD] Pulling {flux_repo} (safetensors - ~8GB)...")
        try:
            snapshot_download(
                repo_id=flux_repo,
                local_dir=flux_dir,
                ignore_patterns=["*.md", "*.txt", "*.jpg", "*.png"]
            )
            print(f"[DOWNLOAD] FLUX.2-klein-4B complete.")
        except Exception as e:
            print(f"[ERROR] FLUX Download Failed: {e}")
    else:
        print(f"[OK] FLUX.2-klein-4B detected.")

    print("🚀 CORE WEIGHTS INJECTED & LINKAGE MAPPED.")

if __name__ == "__main__":
    download_manifold()
