import os
from huggingface_hub import snapshot_download

# Define local storage
MODEL_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# List of essential components for FLUX + Qwen
# Note: You may need to accept the license on HuggingFace for FLUX.1 models
models = [
    {"repo": "black-forest-labs/FLUX.1-schnell", "folder": "flux-core"},
    {"repo": "openai/clip-vit-large-patch14", "folder": "text_encoder_clip"},
    {"repo": "google/t5-v1_1-xxl", "folder": "text_encoder_t5"}
]

print("🦾 INITIALIZING DOWNLOAD SEQUENCE...")

for m in models:
    try:
        print(f"📥 Pulling {m['repo']} into models/{m['folder']}...")
        snapshot_download(
            repo_id=m['repo'],
            local_dir=os.path.join(MODEL_DIR, m['folder']),
            local_dir_use_symlinks=False
        )
    except Exception as e:
        print(f"❌ Error downloading {m['repo']}: {e}")

print("🚀 MANIFOLD DOWNLOAD COMPLETE. VRAM Swapper ready for initialization.")
