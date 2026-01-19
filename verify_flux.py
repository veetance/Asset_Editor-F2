
import sys
import os
import torch

# Add current dir to path
sys.path.append(os.getcwd())

def test_variant(variant):
    try:
        from core.loaders import build_flux_pipeline
        print(f"\n[TEST] Testing FLUX-{variant.upper()}...")
        
        pipe = build_flux_pipeline(variant)
        if pipe:
            print(f"[TEST] Pipeline {variant.upper()} built successfully!")
            
            print(f"[TEST] Attempting inference for {variant.upper()}...")
            with torch.inference_mode():
                image = pipe(
                    prompt="A test image for " + variant,
                    height=512,
                    width=512,
                    num_inference_steps=1,
                    guidance_scale=0.0 if variant == "4b" else 3.5,
                    max_sequence_length=256
                ).images[0]
            print(f"[TEST] Inference for {variant.upper()} successful!")
            
            # Clean up for next test
            del pipe
            torch.cuda.empty_cache()
            import gc
            gc.collect()
        else:
            print(f"[TEST] Pipeline build for {variant.upper()} returned None.")
    except Exception as e:
        import traceback
        print(f"[TEST] FAILURE for {variant.upper()}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=str, default="4b", choices=["4b", "9b"])
    args = parser.parse_args()
    
    test_variant(args.variant)
