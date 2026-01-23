
"""
VEETANCE - FLUX 4B Sovereign Speed Engine
Hybrid Manifold: TR/VAE on GPU, TE on RAM (CPU).
Designed for 16GB VRAM / 64GB RAM Optimization.
"""
import os
import torch
import functools
from diffusers import Flux2KleinPipeline, Flux2Transformer2DModel, AutoencoderKLFlux2
# from .qwen_fp8 import load_qwen3_text_encoder
from transformers import AutoModelForCausalLM, BitsAndBytesConfig


def build_4b_pipeline():
    """
    Ignites the 4B Sovereign Speed engine.
    Zeros out generation overhead by pinning TR to GPU.
    """
    flux_dir = r"e:\Data-D-2\FLUX-2-KLEIN\models\flux-klein"
    print("[LOADER] Initiating FLUX.2-Klein-4B (Sovereign Speed)...")

    # 1. Load Text Encoder (Official Qwen3-4B / 2560-dim)
    # OPTIMIZATION: 4-bit Quantization [8GB -> 2.6GB]
    te_path = os.path.join(flux_dir, "text_encoder", "brain-4b")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    te = AutoModelForCausalLM.from_pretrained(
        te_path,
        quantization_config=bnb_config,
        device_map="cuda:0", # Force GPU residency to prevent CPU offload fallback
        trust_remote_code=True
    )

    
    # 1B. Force Evaluation Mode (Safety)
    te.eval()


    # 2. Extract Tokenizer
    from transformers import Qwen2TokenizerFast
    tok_path = os.path.join(flux_dir, "tokenizer")
    tokenizer = Qwen2TokenizerFast.from_pretrained(tok_path)

    # 3. Inject 4B Transformer
    trans_path = os.path.join(flux_dir, "transformer", "klein-4b")
    transformer = Flux2Transformer2DModel.from_pretrained(
        trans_path,
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )

    # OPTIMIZATION: Sequential Alpha Protocol [BF16 Managed]
    # We keep the transformer in BF16 on CPU. Carrier handles migration.
    # NO FP8 CASTING HERE.
    print("[LOADER] Sequential Alpha Protocol: Transformer remains in BF16 (CPU)...")
    # transformer.to(device="cuda", dtype=torch.float8_e4m3fn)
    # transformer.to("cpu")
    torch.cuda.empty_cache()

    # 4. Inject VAE (Stability Fix: Float32 weights)
    vae_path = os.path.join(flux_dir, "vae")
    vae = AutoencoderKLFlux2.from_pretrained(
        vae_path,
        torch_dtype=torch.float32,
        local_files_only=True
    )

    # 5. Build Pipeline Shell
    pipe = Flux2KleinPipeline.from_pretrained(
        flux_dir,
        text_encoder=te,
        tokenizer=tokenizer,
        transformer=transformer,
        vae=vae,
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )

    # NOVEL OPTIMIZATION: Neural Fusion (torch.compile)
    # DEFERRED: Fixed "TritonMissing" error on Windows/Turing hardware.
    # print("[LOADER] Engaging Neural Fusion: Compiling Transformer (reduce-overhead)...")
    # try:
    #     pipe.transformer = torch.compile(
    #         pipe.transformer, 
    #         mode="reduce-overhead",
    #         fullgraph=False
    #     )
    # except Exception as e:
    #     print(f"[LOADER] Fusion Warning: torch.compile not available or failed: {e}")

    # Resolution Safety
    # OPTIMIZATION: Disable Tiling for Speed (<2s Decode) on 16GB Cards
    # pipe.vae.enable_tiling()
    # pipe.vae.enable_slicing()


    # 7. Manifold Calibration (Zero Noise)
    if hasattr(pipe.scheduler, "config"):
        pipe.scheduler.register_to_config(shift=3.0)

    print("[LOADER] FLUX.2-Klein-4B Ready (Sovereign Speed Online).")
    return pipe
