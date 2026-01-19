import torch
import os
import traceback
from core.loaders import build_flux_pipeline

def test_pipeline():
    try:
        print("--- INITIALIZING PIPELINE ---")
        pipe = build_flux_pipeline()
        
        print("\n--- STARTING GENERATION TEST ---")
        prompt = "a futuristic neon city, high quality, digital art"
        
        # We'll use a very small number of steps for the test
        # Note: Flux2-Klein-Distilled usually needs 1-4 steps
        result = pipe(
            prompt=prompt,
            num_inference_steps=1,
            guidance_scale=0.0,
            height=512,
            width=512,
            output_type="np"
        )
        
        print("GENERATION SUCCESS!")
        if result.images is not None and len(result.images) > 0:
            print(f"Generated image shape: {result.images[0].shape}")
        
    except Exception as e:
        print(f"\nFATAL ERROR DURING TEST: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
