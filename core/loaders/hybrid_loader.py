import os
import torch
import torch.nn as nn
from transformers import Qwen2Config, AutoModel, AutoTokenizer
from diffusers.pipelines.flux2.pipeline_flux2_klein import Flux2KleinPipeline
from diffusers import (
    Flux2Transformer2DModel, 
    AutoencoderKLFlux2, 
    FlowMatchEulerDiscreteScheduler
)
from diffusers.pipelines.flux2.pipeline_flux2_klein import Qwen3ForCausalLM
import logging
import warnings
from core.vram import governor
import psutil

# --- SHUT UP WARNINGS ---
warnings.filterwarnings("ignore", category=FutureWarning, module="diffusers")
warnings.filterwarnings("ignore", message=".*torch_dtype.*") 
warnings.filterwarnings("ignore", message=".*`torch_dtype` is deprecated.*")

logger = logging.getLogger(__name__)

def patch_qwen_attention():
    try:
        from transformers.models.qwen2.modeling_qwen2 import Qwen2Attention, Qwen2RMSNorm, apply_rotary_pos_emb, ALL_ATTENTION_FUNCTIONS, eager_attention_forward
    except ImportError: return
    
    if getattr(Qwen2Attention, "_sovereign_patched", False): return
    
    _original_init = Qwen2Attention.__init__
    def patched_init(self, config, layer_idx=None, *args, **kwargs):
        _original_init(self, config, layer_idx, *args, **kwargs)
        # Re-inject the Norms that Qwen3 expects but Qwen2 class lacks
        self.q_norm = Qwen2RMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.k_norm = Qwen2RMSNorm(self.head_dim, eps=config.rms_norm_eps)

    def sovereign_attention_forward(self, hidden_states, position_embeddings=None, attention_mask=None, **kwargs):
        bsz, q_len, _ = hidden_states.size()
        
        query_states = self.q_proj(hidden_states).view(bsz, q_len, self.num_attention_heads, self.head_dim).transpose(1, 2)
        key_states = self.k_proj(hidden_states).view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = self.v_proj(hidden_states).view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        
        # Apply the Norms
        query_states = self.q_norm(query_states)
        key_states = self.k_norm(key_states)
        
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        
        attn_if = ALL_ATTENTION_FUNCTIONS.get(self.config._attn_implementation, eager_attention_forward)
        attn_output, attn_weights = attn_if(self, query_states, key_states, value_states, attention_mask, scaling=self.scaling, **kwargs)
        
        attn_output = attn_output.reshape(bsz, q_len, -1).contiguous()
        return self.o_proj(attn_output), attn_weights

    Qwen2Attention.__init__ = patched_init
    Qwen2Attention.forward = sovereign_attention_forward
    Qwen2Attention._sovereign_patched = True
    logger.info("[SYSTEM] SIGNAL RESTORED: Qwen Q/K Norms Patched.")

def patch_flux_nuclear_stability():
    # 1. Device Alignment Guard (CPU->CUDA Teleport)
    if not getattr(Flux2Transformer2DModel, "_sovereign_device_patched", False):
        _orig_trans_forward = Flux2Transformer2DModel.forward
        def aligned_forward(self, *args, **kwargs):
            try:
                target_device = next(self.parameters()).device
            except:
                target_device = torch.device("cuda")

            # Teleport keyword args (Targeted Strike)
            for k in ["timestep", "guidance", "pooled_projections", "hidden_states", "encoder_hidden_states", "img_ids", "txt_ids"]:
                v = kwargs.get(k)
                if torch.is_tensor(v) and v.device != target_device:
                    kwargs[k] = v.to(target_device)

            return _orig_trans_forward(self, *args, **kwargs)
        
        Flux2Transformer2DModel.forward = aligned_forward
        Flux2Transformer2DModel._sovereign_device_patched = True


def patch_flux_pipeline():
    # Patch the Klein pipeline specifically
    from diffusers.pipelines.flux2.pipeline_flux2_klein import Flux2KleinPipeline
    
    Flux2KleinPipeline.format_input = lambda prompts, **k: [[{"role": "user", "content": p}] for p in ([prompts] if isinstance(prompts, str) else prompts)]
    
    if not getattr(Flux2KleinPipeline, "_sovereign_patched_call", False):
        _orig_call = Flux2KleinPipeline.__call__
        def sovereign_call(self, *a, **k):
            # SAMPLING ALIGNMENT: 
            # If is_distilled is True, the pipeline usually ignores guidance_scale.
            # We will use k.get("guidance_scale") as the 'guidance' scalar for the transformer.
            gs = k.get("guidance_scale", 1.0)
            
            # FORCE SINGLE-PASS (CFG OFF)
            k["guidance_scale"] = 1.0 
            
            # Use our custom guidance logic: pass gs to the transformer via a patch
            self._sovereign_gs = gs

            # OPTIMIZATION: Clear internal IDs on fresh strike
            if k.get("prompt_embeds") is None:
                self._current_ids = None

            # FIXED: Flux2KleinPipeline does NOT support these as keyword arguments.
            k.pop("pooled_projections", None)
            k.pop("text_ids", None)
            if k.get("prompt_embeds") is not None: k["prompt"] = None
            return _orig_call(self, *a, **k)

        
        _orig_encode = Flux2KleinPipeline.encode_prompt
        def robust_encode(self, prompt=None, prompt_embeds=None, **k):
            # INSTANT STRIKE: If embeddings are provided AND we have cached IDs, skip.
            t_ids = getattr(self, "_current_ids", None)
            if prompt_embeds is not None and t_ids is not None: 
                return prompt_embeds, t_ids
            
            # For distilled models strike, we bypass internal dual-encoding if possible
            res = _orig_encode(self, prompt=prompt, prompt_embeds=prompt_embeds, **k)

            if isinstance(res, tuple):
                e, ids = res[0], res[1]
                td = len(self.transformer.config.axes_dims_rope)
                if ids.shape[-1] != td:
                    n_ids = torch.zeros((*ids.shape[:-1], td), device=ids.device, dtype=ids.dtype); n_ids[..., :ids.shape[-1]] = ids; ids = n_ids
                # Cache for optimization
                self._current_ids = ids
                return e, ids
            return res
            
        _orig_latents = Flux2KleinPipeline.prepare_latents
        def robust_latents(self, *a, **k):
            k["device"], k["dtype"] = torch.device("cuda"), torch.float16
            res = _orig_latents(self, *a, **k)
            l, ids = res[0], res[1]
            td = len(self.transformer.config.axes_dims_rope)
            if ids.shape[-1] != td:
                n_ids = torch.zeros((*ids.shape[:-1], td), device=ids.device, dtype=ids.dtype); n_ids[..., :ids.shape[-1]] = ids; ids = n_ids
            return l, ids
            

        Flux2KleinPipeline.__call__, Flux2KleinPipeline.encode_prompt, Flux2KleinPipeline.prepare_latents = sovereign_call, robust_encode, robust_latents
        Flux2KleinPipeline._sovereign_patched_call = True

    # NOTE: Custom RMSNorm patch was removed. The official _get_qwen3_prompt_embeds
    # stacks raw hidden states without normalization. Our RMSNorm patch was causing noise.

class HybridLoader:
    def __init__(self): self.pipeline, self.base_path = None, "models/flux-klein"
    def build_franklin_pipeline(self, model_id="4b", precision="fp16", sampler_type="flow_euler", scheduler_type="linear"):
        variant, target_dtype = ("klein-4b" if "4b" in model_id.lower() else "klein-9b"), torch.float16
        logger.info(f"[ENGINE] Initiating Hardware Override (TURING) | Target: {model_id.upper()} | Sampler: {sampler_type.upper()} | Scheduler: {scheduler_type.upper()}")
        try:
            # Load Transformer using from_single_file for proper BFL→diffusers weight conversion
            # CRITICAL: from_pretrained loads zeros due to weight naming mismatch
            trans_base = os.path.join(self.base_path, "transformer", variant, "safetensors")
            trans_weights = os.path.join(trans_base, "diffusion_pytorch_model-large.safetensors")
            trans_config = os.path.join(trans_base, "config.json")
            transformer = Flux2Transformer2DModel.from_single_file(trans_weights, config=trans_config, torch_dtype=target_dtype, low_cpu_mem_usage=True).to("cpu")
            import gc; gc.collect()
            torch.cuda.empty_cache()
            enc_path = os.path.join(self.base_path, "text_encoder")
            
            # Use native Qwen3ForCausalLM for noise suppression
            from transformers.models.qwen3.modeling_qwen3 import Qwen3ForCausalLM
            text_encoder = Qwen3ForCausalLM.from_pretrained(enc_path, torch_dtype=torch.float16, low_cpu_mem_usage=True).to("cpu")
            
            # --- TOKENIZER & VAE (FP16 for all components) ---
            tok_path = os.path.join(self.base_path, "tokenizer")
            tokenizer = AutoTokenizer.from_pretrained(tok_path)
            vae = AutoencoderKLFlux2.from_pretrained(os.path.join(self.base_path, "vae"), torch_dtype=torch.float16, low_cpu_mem_usage=True).to("cpu")
            import gc; gc.collect()
            torch.cuda.empty_cache()

            # --- SCHEDULER MANIFOLD (DECOUPLED) ---
            from diffusers import FlowMatchEulerDiscreteScheduler, FlowMatchHeunDiscreteScheduler
            
            # 1. Select Sampler Class
            sch_class = FlowMatchEulerDiscreteScheduler
            if "heun" in sampler_type.lower():
                sch_class = FlowMatchHeunDiscreteScheduler
            
            # 2. Load Config Base
            sch_path = os.path.join(self.base_path, "scheduler")
            sch = sch_class.from_pretrained(sch_path)
            
            # 3. Apply Schedule Overrides
            if scheduler_type.lower() == "beta":
                sch.register_to_config(use_beta_sigmas=True)
            elif scheduler_type.lower() == "karras":
                sch.register_to_config(use_karras_sigmas=True)
            elif scheduler_type.lower() == "simple":
                sch.register_to_config(shift=1.0)
            # 'linear' is the default shift=3.0 in the config

            
            self.pipeline = Flux2KleinPipeline(scheduler=sch, text_encoder=text_encoder, tokenizer=tokenizer, transformer=transformer, vae=vae, is_distilled=True)
            
            # --- GUIDANCE PROXY: Inject guidance into transformer call ---
            _orig_trans_forward = self.pipeline.transformer.forward
            def sovereign_trans_forward(*a, **k):
                if hasattr(self.pipeline, "_sovereign_gs"):
                    # For Klein 4B, guidance is often passed as a scaled tensor
                    # Even if guidance_embeds is False, the forward accepts it
                    k["guidance"] = torch.tensor([self.pipeline._sovereign_gs], device=k["hidden_states"].device, dtype=k["hidden_states"].dtype)
                return _orig_trans_forward(*a, **k)
            self.pipeline.transformer.forward = sovereign_trans_forward

            # --- SCHEDULER CONTEXT TRACKING (for hot-swap) ---

            self._current_sampler = sampler_type
            self._current_scheduler = scheduler_type
            
            # --- ANCHOR CHAT TEMPLATE ---
            template_path = os.path.join(tok_path, "chat_template.jinja")
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    tokenizer.chat_template = f.read()
                    logger.info("[DATA] Tokenizer Voice Anchored: chat_template.jinja loaded.")
            
            logger.info(f"[SUCCESS] MIRACLE CALIBRATION: {sampler_type.upper()} + {scheduler_type.upper()} Active (Shift: {sch.config.shift})")
            logger.info(f"Manifold Residency: {psutil.virtual_memory().used / 1e9:.1f}GB / {psutil.virtual_memory().total / 1e9:.1f}GB System RAM")
            return self.pipeline
        except Exception as e: logger.error(f"Override Fault: {e}"); raise e
    
    def hot_swap_scheduler(self, sampler_type="flow_euler", scheduler_type="linear"):

        """
        Hot-swap scheduler without rebuilding pipeline.
        Returns True if swap occurred, False if already at target config.
        """
        if self.pipeline is None:
            logger.warning("Hot-swap aborted: No pipeline loaded.")
            return False
        
        # Check if swap is needed
        current_s = getattr(self, '_current_sampler', None)
        current_sch = getattr(self, '_current_scheduler', None)
        if current_s == sampler_type and current_sch == scheduler_type:
            return False  # Already at target config
        
        from diffusers import FlowMatchEulerDiscreteScheduler, FlowMatchHeunDiscreteScheduler
        
        # 1. Select Sampler Class
        sch_class = FlowMatchHeunDiscreteScheduler if "heun" in sampler_type.lower() else FlowMatchEulerDiscreteScheduler
        
        # 2. Load from config
        sch_path = os.path.join(self.base_path, "scheduler")
        sch = sch_class.from_pretrained(sch_path)
        
        # 3. Apply Schedule Overrides
        if scheduler_type.lower() == "beta":
            sch.register_to_config(use_beta_sigmas=True)
        elif scheduler_type.lower() == "karras":
            sch.register_to_config(use_karras_sigmas=True)
        elif scheduler_type.lower() == "simple":
            sch.register_to_config(shift=1.0)
        
        # 4. Swap
        self.pipeline.scheduler = sch
        self._current_sampler = sampler_type
        self._current_scheduler = scheduler_type
        
        logger.info(f"[SUCCESS] HOT-SWAP: {sampler_type.upper()} + {scheduler_type.upper()} (Shift: {sch.config.shift})")
        return True

patch_qwen_attention()
patch_flux_nuclear_stability()
patch_flux_pipeline()
hybrid_loader = HybridLoader()
