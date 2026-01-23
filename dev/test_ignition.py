
import os
import torch
import sys
# Add parent dir to path to import core
sys.path.append(os.getcwd())

from core.loaders.flux import build_flux_pipeline

def test_ignite():
    print("🔥 SOVEREIGN IGNITION TEST: 4B")
    try:
        # We don't need to load weights into GPU for the test, 
        # but build_4b_pipeline already has enable_model_cpu_offload() 
        # which will handle the initial meta-shell load.
        pipe = build_flux_pipeline(variant="4b")
        if pipe:
            print("🚀 SUCCESS: 4B Pipeline Built and Ready.")
        else:
            print("❌ FAILURE: Pipeline returned None.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR during ignition: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ignite()
