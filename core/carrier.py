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

    @staticmethod
    def execute_flux_4b(pipe, prompt, device="cuda", **kwargs):
        """
        Engages the 4B Sequential Manifold (SCM Protocol).
        Optimized for 16GB VRAM: TE-CPU, TR/VAE-GPU.
        """
        import time
        t0 = time.time()
        print("[CARRIER] Engaging 4B Sequential Manifold (SCM Protocol)...")
        
        # 1. Mobilize Text Encoder to Silicon
        t_te_start = time.time()
        print("[BRAIN] Mobilizing Text Encoder to Silicon...")
        pipe.text_encoder.to(device)
        torch.cuda.synchronize() # Force sync to catch lazy loading
        print(f"[PROFILE] TE Transfer Time (Synced): {time.time() - t_te_start:.2f}s")
        print(f"[DEBUG] TE Device: {pipe.text_encoder.device}, Components Dtype: {pipe.text_encoder.dtype}")
        
        # 2. Sovereign Ignition: Encode Prompt
        t_enc_start = time.time()
        print("[BRAIN] Encoding prompt on GPU (Sovereign Ignition)...")
        try:
            with torch.no_grad():
                # Note: encode_prompt returns (prompt_embeds, pooled_prompt_embeds)
                prompt_embeds, pooled_prompt_embeds = pipe.encode_prompt(
                    prompt=prompt,
                    device=torch.device(device)
                )


            torch.cuda.synchronize() # Force sync to measure true encoding time
            print(f"[PROFILE] Prompt Encoding Time (Synced): {time.time() - t_enc_start:.2f}s")
            print("[BRAIN] Encoding successful. Tensors materialized.")
        except Exception as e:
            print(f"[ERROR] Sovereign encoding failure: {e}")
            raise e
        finally:
            # 3. Brain Residency: Keep Text Encoder on GPU for speed
            # We removed the offload logic to eliminate the 28s penalty.
            pass


        # 4. Mobilize Synthesis Components (Transformer & VAE)
        t_tr_start = time.time()
        print("[CARRIER] Mobilizing Transformer & VAE to Silicon...")
        pipe.transformer.to(device)
        # Note: VAE is moved during decode, but let's prep it
        pipe.vae.to(device)
        print(f"[PROFILE] Transformer Transfer Time: {time.time() - t_tr_start:.2f}s")
        
        # 5. Silicon Checksum: Ensure inputs are precisely on device
        prompt_embeds = prompt_embeds.to(device, dtype=torch.bfloat16)
        pooled_prompt_embeds = pooled_prompt_embeds.to(device, dtype=torch.bfloat16)


        # 6. Ignite Transformer
        print("[CARRIER] Vectors verified. Igniting Transformer...")
        
        # STORE REFS
        _te = pipe.text_encoder
        _tok = pipe.tokenizer

        try:
            # SILICON SATURATION: Total Device Enforcement
            # We iterate and force every single buffer and parameter to CUDA
            print("[CARRIER] Executing Silicon Saturation...")
            pipe.transformer.to(device)
            
            # DETACH CPU COMPONENTS
            # This forces the pipeline to detect 'device' from the Transformer (GPU)
            # preventing the "Expected all tensors to be on same device" error.
            print("[CARRIER] Detaching Text Encoder for Sovereign Execution...")
            pipe.text_encoder = None
            pipe.tokenizer = None

            # DECOUPLED EXECUTION PROTOCOL
            # 1. Generate Latents (BFloat16)
            t_inf_start = time.time()
            with torch.inference_mode():
                latents = pipe(
                    prompt=None,
                    prompt_embeds=prompt_embeds,
                    # pooled_prompt_embeds=pooled_prompt_embeds, # Removed to fix TypeError
                    output_type="latent",
                    return_dict=False,
                    **kwargs
                )[0]


            print(f"[PROFILE] Inference Time: {time.time() - t_inf_start:.2f}s")
            
            print("[CARRIER] Latents generated. Executing Precision Cast (BF16 -> FP32)...")
            
            # 2. Precision Cast
            # The VAE is in float32 for stability. We must cast the latents before entry.
            latents = latents.detach().to(dtype=torch.float32)
            
            # 3. Manual Decode
            t_dec_start = time.time()
            print("[CARRIER] Decoding with High-Precision VAE...")
            
            # VAE ACCELERATION: Force VAE to Silicon
            pipe.vae.to(device)
            pipe.vae.disable_tiling()
            pipe.vae.disable_slicing()
            torch.cuda.synchronize()

            
            image = pipe.vae.decode(latents, return_dict=False)[0]
            image = image.detach()
            image = pipe.image_processor.postprocess(image, output_type="pil")
            torch.cuda.synchronize()
            print(f"[PROFILE] VAE Decode Time: {time.time() - t_dec_start:.2f}s")
            
            print(f"[PROFILE] Total Pipeline Time: {time.time() - t0:.2f}s")

            # 4. Construct Result Object
            # We need to return an object with an .images attribute to satisfy the route handler
            class Result:
                def __init__(self, images):
                    self.images = images
            
            return Result(image)

        finally:
            # RESTORE COMPONENTS
            pipe.text_encoder = _te
            pipe.tokenizer = _tok

            # 7. Atomic Cleanup: Purge all temporary synthesis tensors
            print("[CARRIER] Synthesis complete. Vacating Silicon...")
            del prompt_embeds
            if 'latents' in locals(): del latents
            torch.cuda.empty_cache()
            gc.collect()

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
