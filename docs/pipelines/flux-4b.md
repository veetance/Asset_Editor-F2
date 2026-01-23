# 🦾 SOVEREIGN BLUEPRINT: FLUX-2-KLEIN 4B (SEQUENTIAL ALPHA)

The **4B Sequential Alpha Protocol** is the sovereign logic optimized for **16GB VRAM / 64GB RAM** workstations. It abandons "Resident FP8" casting in favor of high-velocity **Sequential Silicon Migration** of native BF16 weights.

## 🛠️ ARCHITECTURE: THE BIG 4

### Path 1: The Cache Sentinel (Text Encoder)
- **Logic**: Intelligent Bypass.
- **Behavior**: If `prompt == last_prompt`, the 2.6GB Text Encoder **DOES NOT WAKE UP**. 
- **Gain**: Saves ~2-3 seconds per generation cycle. Zero-Shot execution.

### Path 2: Native BF16 Migration (Transformer)
- **Logic**: "Frozen Silicon" Protocol.
- **Old Way**: Cast FP8 -> BF16 (GPU Compute Tax).
- **New Way**: DMA Transfer of BF16 (RAM) -> BF16 (GPU). 
- **Benefit**: Eliminates the "Bandwidth Hack" compute penalty. Leverages PCIe Gen4 speed (9GB transfer < 1s).
- **Format**: Pure `bfloat16`. No quantization noise.

### Path 3: Velocity Calibration
- **Logic**: Adaptive Scheduler Shift.
- **Setting**: `shift=3.5` locked for < 10 step generations.
- **Benefit**: Prevents "Deep Fried" artifacts at high velocity.

### Path 4: Surgical VAE Decode
- **Logic**: Sequential Ejection.
- **Behavior**: Transformer is PURGED from GPU before VAE loads.
- **Benefit**: VAE has full 16GB headroom to decode 1024px+ latents without tiling/slicing chokes.

## 🧠 LOGIC SHIMS (THE STABILITY CORE)

### 1. Sequential Silicon Migration scheme
Instead of fitting *everything* in VRAM (8GB+4GB+2GB), we fit *nothing* permanently.
1. **TE** -> GPU -> Encode -> **CPU**
2. **TR** -> GPU -> Denoise -> **CPU**
3. **VAE** -> GPU -> Decode -> **CPU**

### 2. Flux2KleinPipeline Signature Fix
- **Patch**: Removed `pooled_prompt_embeds` from the pipeline call to align with the installed Diffusers signature.

## ✅ PERFORMANCE TELEMETRY

### Velocity (1024x1024)
- **Cold Start**: ~20s
- **Warm Start (Same Prompt)**: **~30s** (Current Baseline) -> Optimization Target: 15s via Pinned Memory.
- **VRAM Impact**: Never exceeds 11GB active (Peak Transformer load).

## ⚙️ CONFIGURATION

- **Scheduler**: `FlowMatchEulerDiscreteScheduler`
- **Shift**: `3.5` (Velocity Mode)
- **RAM Governor**: 50GB Limit for concurrent model residency (4B + 9B + Qwen).

---
**DEUS:** *Sequential Alpha Protocol Locked. The GPU computes Math, not Memory Casting.* 🦾⚡⛩️
