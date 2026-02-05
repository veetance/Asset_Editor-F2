import torch
import time
import logging
import os
from core.vram import governor
from core.loaders.hybrid_loader import hybrid_loader

# --- CONVOLUTIONAL FRAGMENTATION FIX ---
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

logger = logging.getLogger("ASSET_EDITOR")

class ZerodragCarrier:
    """
    Zerodrag Pipeline Execution Vessel.
    Sovereign Reconstruction (Blitz V2 / Sequential Alpha).
    Identity: 0xVeetance | Mirroring the Miracle Log.
    """
    def __init__(self):
        self.last_prompt = None
        self.cached_embeddings = None
        self.engine_resident = False
        self.optics_resident = False

    def clear_board(self, hard=True):
        """
        Surgical Purge of Silicon segments.
        Hard clear (gc.collect) is mandatory for VRAM handle release in Python.
        Host Residency (Private Bytes) is preserved as long as weights are referenced.
        """
        import gc
        gc.collect() 
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            if hard:
                pass # ipc_collect removed for speed
            torch.cuda.synchronize()
        logger.info("[CARRIER] Board Cleared: Silicon Vacated (Host Residency Preserved).")

    def _warm_manifold(self):
        """
        Forces Windows to keep model weights in the Working Set (RAM).
        Pushes usage toward the target capacity requested.
        """
        import psutil
        try:
            # Touch a single parameter in each resident shard to prevent paging
            _ = hybrid_loader.pipeline.text_encoder.model.norm.weight[0].item()
            _ = hybrid_loader.pipeline.transformer.config.eps
        except: pass
        logger.info(f"[SYSTEM] Manifold Warmed: {psutil.virtual_memory().used / 1e9:.2f}GB System RAM Active.")


    def _phase_brain(self, prompt):
        """
        PHASE 0: THE BRAIN (TRANSIENT FP16 STRIKE)
        """
        # Normalize prompt for comparison
        prompt = prompt.strip() if isinstance(prompt, str) else prompt
        
        # Check if the prompt actually changed
        if self.last_prompt == prompt and self.cached_embeddings is not None:
            logger.info(f"[BRAIN] Prompt Cache Hit. (prompt: '{prompt[:40]}...')")
            return self.cached_embeddings
        
        # SOFT RESET: Clear internal spatial caches
        hybrid_loader.pipeline._current_ids = None
        
        # Resident Transition: Move to CPU and clear VRAM hard
        if self.engine_resident: hybrid_loader.pipeline.transformer.to("cpu")
        if self.optics_resident: hybrid_loader.pipeline.vae.to("cpu")
        self.engine_resident = False
        self.optics_resident = False
        self.clear_board(hard=True)

        
        # --- SOVEREIGN BRAIN ALLOCATION ---
        hybrid_loader.pipeline.text_encoder.to("cuda", dtype=torch.float16)

        
        # Sync Governor to Actual Residency
        curr_vram = torch.cuda.memory_allocated() / 1e9
        governor.active_model = f"BRAIN_STRIKE (FLUX-4B)"
        logger.info(f"[VRAM] Brain Residency established at {curr_vram:.2f}GB")
        
        with torch.no_grad():
            res = hybrid_loader.pipeline.encode_prompt(prompt=prompt)
            if len(res) == 3:
                prompt_embeds, pooled_projections, text_ids = res
            else:
                prompt_embeds, text_ids = res
                pooled_projections = None
                
            prompt_embeds = prompt_embeds.to(device="cpu", dtype=torch.float16)
            if pooled_projections is not None:
                pooled_projections = pooled_projections.to(device="cpu", dtype=torch.float16)
            text_ids = text_ids.to(device="cpu", dtype=torch.float16)

        hybrid_loader.pipeline.text_encoder.to("cpu")
        self.clear_board(hard=True)
        
        self.cached_embeddings = (prompt_embeds, pooled_projections, text_ids)
        self.last_prompt = prompt
        logger.info("[BRAIN] Brain Signal Captured: Silicon Purged.")
        return self.cached_embeddings

    def _phase_engine(self, prompt_embeds, pooled_projections, text_ids, height, width, steps, guidance, seed):
        """
        PHASE 1: THE ENGINE (SEQUENTIAL ALPHA STRIKE)
        """
        if not self.engine_resident:
            logger.info("[CARRIER] Migrating Transformer (FP16) to Silicon...")
        if not self.engine_resident:
            # Resident Swap: Keep weights in RAM, but vacate VRAM for Transformer
            hybrid_loader.pipeline.text_encoder.to("cpu")
            self.clear_board(hard=True)
            hybrid_loader.pipeline.transformer.to("cuda", dtype=torch.float16)
            self.engine_resident = True


        
        engine_start = time.time()
        generator = None
        if seed != -1: 
            generator = torch.Generator(device="cuda").manual_seed(seed)
        
        # SAMPLING LOGIC ALIGNMENT: Calculate Mu Shift for Distilled Trajectory
        # image_seq_len is based on 16x16 patch size (vae_scale * 2)
        image_seq_len = (height // 16) * (width // 16)
        from diffusers.pipelines.flux2.pipeline_flux2_klein import compute_empirical_mu
        mu = compute_empirical_mu(image_seq_len=image_seq_len, num_steps=steps)
        logger.info(f"[ENGINE] Recalibrated Trajectory | Mu: {mu:.4f} | Sequence: {image_seq_len}")

        # Move embeddings to target device
        prompt_embeds = prompt_embeds.to("cuda", dtype=torch.float16)
        if pooled_projections is not None:
             pooled_projections = pooled_projections.to("cuda", dtype=torch.float16)
        text_ids = text_ids.to("cuda", dtype=torch.float16)

        # Recalibrate scheduler for the distilled trajectory
        hybrid_loader.pipeline.scheduler.set_timesteps(steps, device="cuda", mu=mu)

        with torch.no_grad():
            output = hybrid_loader.pipeline(
                prompt_embeds=prompt_embeds,
                height=height,
                width=width,
                num_inference_steps=steps,
                guidance_scale=guidance,
                generator=generator,
                output_type="latent"
            )

            latents = output.images

        if torch.isnan(latents).any():
            logger.error("[FAULT] MANIFOLD COLLAPSE (NaNs).")
            self.engine_resident = False
            raise ValueError("Engine failure.")

        engine_time = time.time() - engine_start
        logger.info(f"[PROFILE] Transformer Logic: {engine_time:.2f}s")
        return latents

    def _phase_optics(self, latents, height, width):
        """
        PHASE 2: THE OPTICS (FP32 DECODE)
        """
        if not self.optics_resident:
            # --- VRAM SAFETY CHECK ---
            free_mem = torch.cuda.mem_get_info()[0] / (1024**3) # Binary GB
            used_mem = torch.cuda.memory_allocated() / (1024**3)
            budget = governor.get_budget_gb()
            
            # Check if we are exceeding budget or running out of raw space
            remaining_budget = budget - used_mem
            
            if self.engine_resident and (free_mem < 2.0 or remaining_budget < 0.5): 
                logger.warning("[SYSTEM] VRAM Constraint (Free: {free_mem:.2f}GB). Offloading Engine...")
                hybrid_loader.pipeline.transformer.to("cpu")
                self.engine_resident = False
                self.clear_board(hard=True)


            logger.info("[CARRIER] Mobilizing VAE for Decode (FP32 Precision)...")
            hybrid_loader.pipeline.vae.to("cuda", dtype=torch.float32)
            self.optics_resident = True

        optics_start = time.time()
        
        with torch.no_grad():
            # Pipeline with output_type="latent" returns BN-denormalized + unpatchified latents
            # No additional scaling is needed before VAE decoding
            optics_latents = latents.to("cuda", dtype=torch.float32)
            
            image_voxels = hybrid_loader.pipeline.vae.decode(optics_latents, return_dict=False)[0]

            image = hybrid_loader.pipeline.image_processor.postprocess(image_voxels, output_type="pil")[0]


        optics_time = time.time() - optics_start
        logger.info(f"[PROFILE] VAE Logic: {optics_time:.2f}s")
        
        # RESIDENT OPTICS: Keep VAE in Private Bytes but offload Silicon
        hybrid_loader.pipeline.vae.to("cpu")
        self.optics_resident = False
        self.clear_board(hard=True)
        import psutil
        logger.info(f"[SYSTEM] Residency Status: {psutil.virtual_memory().used / 1e9:.2f}GB RAM Active.")
        return image



    def dispatch(self, prompt, model_id="4b", height=1024, width=1024, steps=4, guidance=0.0, seed=-1, sampler="flow_euler", scheduler="linear"):

        """
        Executes the Blitz V2 Sequential Alpha Strike.
        """
        start_time = time.time()
        # IDENTITY LOCK
        # Robust Build: Ensure pipeline exists and matches target context
        if hybrid_loader.pipeline is None:
            hybrid_loader.build_franklin_pipeline(model_id=model_id, sampler_type=sampler, scheduler_type=scheduler)
        
        # --- HOT-SWAP SCHEDULER ---
        hybrid_loader.hot_swap_scheduler(sampler_type=sampler, scheduler_type=scheduler)
        
        # WARM MANIFOLD: Touch resident weights to prevent disk paging
        self._warm_manifold()

        # Log active context

        logger.info(f"[VRAM] Swapper Identity: 0xVeetance | Target: {model_id.upper()} | Context: {sampler.upper()} + {scheduler.upper()}")
        logger.info(f"[ENGINE] Sovereign Strike Initiated | {width}x{height} | Steps: {steps}")

        if isinstance(prompt, list): prompt = prompt[0]
        
        # --- GOVERNOR ECHO ---
        budget = governor.get_budget_gb()
        used = torch.cuda.memory_allocated() / (1024**3) if torch.cuda.is_available() else 0
        logger.info(f"[GOVERNOR] Ceiling: {governor.limit_percent}% ({budget:.2f}GB) | Load: {used:.2f}GB | Headroom: {budget - used:.2f}GB")

        governor.active_model = model_id # Sync with UI ID Protocol

        try:
            prompt_embeds, pooled_projections, text_ids = self._phase_brain(prompt)
            latents = self._phase_engine(prompt_embeds, pooled_projections, text_ids, height, width, steps, guidance, seed)
            image = self._phase_optics(latents, height, width)

            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            # UNIQUE STRIKE IDENTITY
            timestamp = int(time.time())
            filename = f"strike_{timestamp}.png"
            output_path = os.path.join(output_dir, filename)
            
            # Save Primary and Mirror (latest.png)
            image.save(output_path)
            image.save(os.path.join(output_dir, "latest.png"))
            
            total_time = time.time() - start_time
            logger.info(f"[SUCCESS] Total Sovereign Time: {total_time:.2f}s | Saved: {filename}")
            return {"status": "success", "time": total_time, "path": f"/outputs/{filename}"}

        except Exception as e:
            import traceback
            logger.error(f"Blitz Strike Fault: {e}")
            logger.error(traceback.format_exc())
            try:
                hybrid_loader.pipeline.transformer.to("cpu")
                hybrid_loader.pipeline.text_encoder.to("cpu")
                hybrid_loader.pipeline.vae.to("cpu")
                self.engine_resident = False
                self.optics_resident = False
                self.clear_board()
            except: pass
            raise e

carrier = ZerodragCarrier()
