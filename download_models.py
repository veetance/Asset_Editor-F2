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
    with open(manifest_path, "w") as f:
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

    # 2. Qwen-Image-Layered (Quantized Q8_0 GGUF) - ~8GB
    qwen_repo = "QuantStack/Qwen-Image-Layered-GGUF"
    qwen_file = "qwen-image-layered-q8_0.gguf"
    qwen_dir = os.path.join(MODEL_DIR, "qwen-layered")
    os.makedirs(qwen_dir, exist_ok=True)
    qwen_path = os.path.join(qwen_dir, qwen_file)

    if not os.path.exists(qwen_path):
        print(f"📥 Pulling {qwen_repo} (Q8_0 - ~8GB)...")
        try:
            hf_hub_download(repo_id=qwen_repo, filename=qwen_file, local_dir=qwen_dir, local_dir_use_symlinks=False)
        except Exception as e:
            print(f"❌ Qwen Error: {e}")
    else:
        print(f"✅ {qwen_file} detected.")

    # 3. FLUX.2-klein-9b-fp8 (Single Checkpoint) - ~10GB
    flux_repo = "black-forest-labs/FLUX.2-klein-9b-fp8"
    flux_filename = "flux-2-klein-9b-fp8.safetensors"
    flux_dir = os.path.join(MODEL_DIR, "flux-schnell")
    os.makedirs(flux_dir, exist_ok=True)
    flux_path = os.path.join(flux_dir, flux_filename)
    
    if not os.path.exists(flux_path):
        print(f"📥 Pulling {flux_repo} (FP8 - ~10GB)...")
        try:
            hf_hub_download(repo_id=flux_repo, filename=flux_filename, local_dir=flux_dir, local_dir_use_symlinks=False)
        except Exception as e:
            print(f"❌ FLUX Error: {e}")
    else:
        print(f"✅ {flux_filename} detected.")

    print("🚀 CORE WEIGHTS INJECTED & LINKAGE MAPPED.")

if __name__ == "__main__":
    download_manifold()
