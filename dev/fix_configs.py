
import os
from huggingface_hub import hf_hub_download, list_repo_files

REPO_4B = "black-forest-labs/FLUX.2-klein-4B"
TARGET_DIR = r"e:\Data-D-2\FLUX-2-KLEIN\models\flux-klein"

def download_missing_configs():
    print("💎 VEETANCE CONFIG REQUISITION...")
    
    files_in_repo = list_repo_files(REPO_4B)
    print(f"Repo Files: {files_in_repo}")

    # Standard Files to Grab
    manifest = [
        ("model_index.json", ""),
        ("text_encoder/config.json", "text_encoder"),
        ("tokenizer/tokenizer_config.json", "tokenizer"),
        ("tokenizer/tokenizer.json", "tokenizer"),
        ("tokenizer/vocab.json", "tokenizer"), # Qwen 3 might use different filenames
        ("vae/config.json", "vae"),
        ("scheduler/scheduler_config.json", "scheduler"),
        ("transformer/config.json", "transformer/klein-4b")
    ]

    for repo_file, sub_dir in manifest:
        if repo_file in files_in_repo:
            dest = os.path.join(TARGET_DIR, sub_dir)
            os.makedirs(dest, exist_ok=True)
            print(f"📥 Grabbing {repo_file}...")
            hf_hub_download(
                repo_id=REPO_4B,
                filename=repo_file,
                local_dir=dest,
                local_dir_use_symlinks=False
            )
        else:
            print(f"⚠️ {repo_file} not in repo. Checking root...")
            # Some repos put everything in root
            root_file = repo_file.split('/')[-1]
            if root_file in files_in_repo:
                 dest = os.path.join(TARGET_DIR, sub_dir)
                 os.makedirs(dest, exist_ok=True)
                 hf_hub_download(repo_id=REPO_4B, filename=root_file, local_dir=dest)
            else:
                 print(f"❌ {repo_file} totally missing from {REPO_4B}.")

if __name__ == "__main__":
    download_missing_configs()
