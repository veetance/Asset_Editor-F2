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
        Engages the 4B Sovereign Speed V2 Manifold (Sequential Alpha).
        Strategy: Sequential Silicon Migration (TE -> TR -> VAE).
        """
        import time
        t0 = time.time()
        print("[CARRIER] Engaging 4B Sovereign Speed V2 (Sequential Alpha)...")
        
        # -------------------------------------------------------------
        # PATH 1: THE CACHE SENTINEL (TE BYPASS)
        # -------------------------------------------------------------
        prompt_embeds = None
        pooled_prompt_embeds = None
        
        if prompt == cls._last_prompt and cls._last_embeds is not None:
            print("[BRAIN] Prompt Cache Hit. ZERO-SHOT encoding.")
            prompt_embeds = cls._last_embeds
            pooled_prompt_embeds = cls._last_pooled
        else:
            print("[BRAIN] Prompt Cache Miss. Mobilizing Text Encoder...")
            t_enc = time.time()
            
            # MIGRATE TE
            pipe.text_encoder.to(device)
            torch.cuda.synchronize()
            
            try:
                with torch.no_grad():
                    prompt_embeds, pooled_prompt_embeds = pipe.encode_prompt(
                        prompt=prompt,
                        device=torch.device(device)
                    )
            except Exception as e:
                print(f"[ERROR] Encoding failure: {e}")
                pipe.text_encoder.to("cpu") # Safety eject
                raise e

            # EJECT TE
            pipe.text_encoder.to("cpu")
            torch.cuda.empty_cache() # HARD PURGE
            
            # CACHE
            cls._last_prompt = prompt
            cls._last_embeds = prompt_embeds
            cls._last_pooled = pooled_prompt_embeds
            
            print(f"[PROFILE] TE Logic: {time.time() - t_enc:.2f}s")

        # -------------------------------------------------------------
        # PATH 2: NATIVE BF16 MIGRATION (THE CORE)
        # -------------------------------------------------------------
        print("[CARRIER] Migrating Transformer (BF16) to Silicon...")
        t_tr = time.time()
        
        # Prepare Inputs on Silicon
        prompt_embeds = prompt_embeds.to(device, dtype=torch.bfloat16)
        pooled_prompt_embeds = pooled_prompt_embeds.to(device, dtype=torch.bfloat16)
        
        # MIGRATE TR
        # NATIVE MIGRATION: No casting. Speed = PCIe Gen4 Bandwidth.
        pipe.transformer.to(device) 
        torch.cuda.synchronize()
        
        # Protective Shim
        _te = pipe.text_encoder
        _tok = pipe.tokenizer
        pipe.text_encoder = None
        pipe.tokenizer = None
        
        try:
            print("[CARRIER] Executing Inference Loop (Frozen BF16)...")
            with torch.inference_mode():
                 # PATH 3: ADAPTIVE SHIFT (Handled by generator.py set_scheduler)
                latents = pipe(
                    prompt=None,
                    prompt_embeds=prompt_embeds,
                    # pooled_prompt_embeds=pooled_prompt_embeds, # REJECTED by Pipeline Signature
                    output_type="latent",
                    return_dict=False,
                    **kwargs
                )[0]
        finally:
            # Restore Shim
            pipe.text_encoder = _te
            pipe.tokenizer = _tok
            
            # EJECT TR
            print("[CARRIER] Purging Transformer...")
            pipe.transformer.to("cpu")
            torch.cuda.empty_cache() # HARD PURGE
            
        print(f"[PROFILE] Transformer Logic: {time.time() - t_tr:.2f}s")
        
        # -------------------------------------------------------------
        # PATH 4: SURGICAL PIXEL ASSEMBLY (VAE)
        # -------------------------------------------------------------
        print("[CARRIER] Mobilizing VAE for Decode...")
        t_vae = time.time()
        
        # MIGRATE VAE
        pipe.vae.to(device)
        torch.cuda.synchronize()
        
        latents = latents.detach().to(dtype=torch.float32)
        image = pipe.vae.decode(latents, return_dict=False)[0]
        image = image.detach()
        image = pipe.image_processor.postprocess(image, output_type="pil")
        
        # EJECT VAE
        pipe.vae.to("cpu")
        torch.cuda.empty_cache() # HARD PURGE
        
        print(f"[PROFILE] VAE Logic: {time.time() - t_vae:.2f}s")
        print(f"[PROFILE] Total Sovereign Time: {time.time() - t0:.2f}s")

        class Result:
            def __init__(self, images):
                self.images = images
        
        return Result(image)

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
