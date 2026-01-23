import torch
import gc

class SovereignCarrier:
    """
    The Universal Carrier: Exercises polymorphic control over different neural manifolds.
    Automatically assigns the optimal execution strategy based on the requisitioned model.
    """
    
    def dispatch(self, model_id, pipe, **kwargs):
        """Standard entry point for all generation passes."""
        model_id_lower = model_id.lower()
        
        if "flux-4b" in model_id_lower:
            # SCM Protocol for highly efficient 16GB operation
            return self.execute_flux_4b(pipe, **kwargs)
        elif "flux-9b" in model_id_lower:
            # Managed Offload for heavy 48/64GB architectures
            return self.execute_flux_managed(pipe, **kwargs)
        elif "qwen" in model_id_lower:
            # Specialized pass for VLM/Deconstruction manifolds
            return self.execute_qwen(pipe, **kwargs)
        else:
            # Standard Fallback: Managed Offload (Stability over Speed)
            print(f"[CARRIER] Unknown manifold {model_id}. Using Managed Fallback.")
            return self.execute_flux_managed(pipe, **kwargs)

    # CACHE LAYER (Static Class Variables)
    _last_prompt = None
    _last_embeds = None
    _last_pooled = None

    @classmethod
    def execute_flux_4b(cls, pipe, prompt, device="cuda", **kwargs):
        """
        Engages the 4B Sovereign Speed Manifold.
        Optimized for 16GB VRAM: Full Residency + Prompt Caching.
        """
        import time
        t0 = time.time()
        print("[CARRIER] Engaging 4B Sovereign Speed Manifold...")
        
        # 1. BRAIN RESIDENCY: Keep everything on GPU
        # We only move if absolutely necessary (first run)
        if pipe.text_encoder.device.type != "cuda":
            print("[BRAIN] Pinning Text Encoder to Silicon...")
            from accelerate.hooks import remove_hook_from_module
            remove_hook_from_module(pipe.text_encoder, recurse=True)
            pipe.text_encoder.to(device)
            
        if pipe.transformer.device.type != "cuda":
            print("[BRAIN] Pinning Transformer to Silicon (Standby: FP8)...")
            # Move and enforce FP8 to ensure we fit in the 16GB bucket along with other components
            pipe.transformer.to(device=device, dtype=torch.float8_e4m3fn)
            
        if pipe.vae.device.type != "cuda":
            # Just verify logic, we will move it during decode
            pipe.vae.disable_tiling()
            pipe.vae.disable_slicing()
        else:
            # Move to CPU to clear space for Inference
            pipe.vae.to("cpu")
            torch.cuda.empty_cache()

        torch.cuda.synchronize()

        # 2. PROMPT CACHING LAYER
        if prompt == cls._last_prompt and cls._last_embeds is not None:
            print("[BRAIN] Prompt Cache Hit. Skipping encoding pass.")
            prompt_embeds = cls._last_embeds
            pooled_prompt_embeds = cls._last_pooled
            # Safety: Ensure TE is offloaded even on cache hits if it was left there
            if pipe.text_encoder.device.type == "cuda":
                pipe.text_encoder.to("cpu")
                torch.cuda.empty_cache()
        else:
            print("[BRAIN] Prompt Cache Miss. Executing Sovereign Ignition...")
            t_enc_start = time.time()
            try:
                with torch.no_grad():
                    prompt_embeds, pooled_prompt_embeds = pipe.encode_prompt(
                        prompt=prompt,
                        device=torch.device(device)
                    )
                torch.cuda.synchronize()
                print(f"[PROFILE] Prompt Encoding Time: {time.time() - t_enc_start:.2f}s")
                
                # Update Cache
                cls._last_prompt = prompt
                cls._last_embeds = prompt_embeds
                cls._last_pooled = pooled_prompt_embeds

                # TRITON FIX: Offload TE back to CPU immediately to free ~2.6GB
                # This prevents hitting the 16GB limit and triggering Shared Memory slowness.
                print("[BRAIN] Vacating Text Encoder silicon to provide inference headroom...")
                pipe.text_encoder.to("cpu")
                torch.cuda.empty_cache()

            except Exception as e:
                print(f"[ERROR] Encoding failure: {e}")
                raise e

        # 3. Silicon Checksum
        prompt_embeds = prompt_embeds.to(device, dtype=torch.bfloat16)
        pooled_prompt_embeds = pooled_prompt_embeds.to(device, dtype=torch.bfloat16)

        # 4. Sovereign Execution
        print("[CARRIER] Executing Inference Loop...")
        t_inf_start = time.time()
        
        # Protect components
        _te = pipe.text_encoder
        _tok = pipe.tokenizer
        pipe.text_encoder = None
        pipe.tokenizer = None

        try:
            # SILICON BREATHING: Expand to BF16 for math
            print("[BRAIN] Expanding Transformer to BF16 for high-velocity math...")
            pipe.transformer.to(dtype=torch.bfloat16)
            torch.cuda.synchronize()

            with torch.inference_mode():
                latents = pipe(
                    prompt=None,
                    prompt_embeds=prompt_embeds,
                    output_type="latent",
                    return_dict=False,
                    **kwargs
                )[0]
            torch.cuda.synchronize()
            print(f"[PROFILE] Inference Time: {time.time() - t_inf_start:.2f}s")
            
            # SILICON BREATHING: Contract back to FP8 to vacate space for VAE
            print("[BRAIN] Contracting Transformer to FP8 to vacate silicon...")
            pipe.transformer.to(dtype=torch.float8_e4m3fn)
            torch.cuda.empty_cache()
            
            # 5. Precision Decode (Direct GPU)
            t_dec_start = time.time()
            print("[CARRIER] Mobilizing VAE for Decode (Silicon)...")
            pipe.vae.to(device)
            torch.cuda.synchronize()
            
            print("[CARRIER] Decoding Latents...")
            latents = latents.detach().to(dtype=torch.float32)
            image = pipe.vae.decode(latents, return_dict=False)[0]
            image = image.detach()
            image = pipe.image_processor.postprocess(image, output_type="pil")
            torch.cuda.synchronize()
            print(f"[PROFILE] VAE Decode Time: {time.time() - t_dec_start:.2f}s")
            
            print(f"[PROFILE] Total Sovereign Time: {time.time() - t0:.2f}s")

            class Result:
                def __init__(self, images):
                    self.images = images
            
            return Result(image)

        finally:
            pipe.text_encoder = _te
            pipe.tokenizer = _tok
            # No offload. No Vacate. Pure Residency.

    @staticmethod
    def execute_flux_managed(pipe, **kwargs):
        """Executes the Manifold with standard Managed Offloading."""
        print("[CARRIER] Engaging Managed Execution pass...")
        if hasattr(pipe, "enable_model_cpu_offload"):
            pipe.enable_model_cpu_offload()
        
        with torch.inference_mode():
            return pipe(**kwargs)

    @staticmethod
    def execute_qwen(pipe, **kwargs):
        """Executes the Qwen deconstruction manifold."""
        print("[CARRIER] Engaging Qwen Deconstruction Pass...")
        # Placeholder for specialized Qwen logic (e.g., vision tower handling)
        with torch.inference_mode():
            if hasattr(pipe, "__call__"):
                return pipe(**kwargs)
            return None

carrier = SovereignCarrier()
