
import os
import shutil

ROOT = r"e:\Data-D-2\FLUX-2-KLEIN\models\flux-klein"

def cleanup():
    print("🧹 VEETANCE TOPOLOGY ALIGNMENT...")
    
    # [ (Nested Path , Parent Path) ]
    moves = [
        ("transformer/klein-4b/transformer/config.json", "transformer/klein-4b/config.json"),
        ("text_encoder/text_encoder/config.json", "text_encoder/config.json"),
        ("vae/vae/config.json", "vae/config.json"),
        ("scheduler/scheduler/scheduler_config.json", "scheduler/scheduler_config.json"),
        ("tokenizer/tokenizer/tokenizer_config.json", "tokenizer/tokenizer_config.json"),
        ("tokenizer/tokenizer/tokenizer.json", "tokenizer/tokenizer.json"),
        ("tokenizer/tokenizer/vocab.json", "tokenizer/vocab.json")
    ]

    for src_rel, dest_rel in moves:
        src = os.path.join(ROOT, src_rel)
        dest = os.path.join(ROOT, dest_rel)
        
        if os.path.exists(src):
            print(f"🚚 Moving {src_rel}...")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(src, dest)
        else:
            print(f"⚠️ Missing source: {src_rel}")

    # Remove empty nested dirs
    for sub in ["text_encoder", "vae", "scheduler", "tokenizer"]:
        nested = os.path.join(ROOT, sub, sub)
        if os.path.exists(nested):
            print(f"🗑️ Cleaning {nested}...")
            shutil.rmtree(nested)
            
    # Special case for 4B transformer
    nested_4b = os.path.join(ROOT, "transformer", "klein-4b", "transformer")
    if os.path.exists(nested_4b):
        shutil.rmtree(nested_4b)

    print("✨ Manifold Topology Aligned.")

if __name__ == "__main__":
    cleanup()
