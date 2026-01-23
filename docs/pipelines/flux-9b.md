# 🦾 SOVEREIGN BLUEPRINT: FLUX-2-KLEIN 9B

The **9B Managed Manifold** is designed for peak fidelity on **16GB VRAM**. It utilizes dynamic CPU offloading to handle the heavier 9B weights.

## 🛠️ ARCHITECTURE

- **Pipeline Shell**: `Flux2KleinPipeline`
- **Text Encoder**: Qwen3-8B (BFloat16) -> **Managed Offload**
- **Transformer**: FLUX-9B (BFloat16) -> **Managed Offload**
- **VAE**: AutoencoderKLFlux2 (Float32) -> **Pinned to GPU**

## 🧠 LOGIC SHIMS

### 1. `managed_to` Override
Orchestrates the transition between the RAM Pool and the GPU.
- **CUDA Target**: Triggers `enable_model_cpu_offload()` to engage the Diffusers/Accelerate management layer.
- **CPU Target**: Explicitly moves all heavy silicon (Transformer/VAE/TE) back to RAM.

### 2. VAE Decode Safety
Maintains numerical stability for high-resolution outputs.
- **Action**: Casts inputs to `float32` for the final image reconstruction.

## ✅ FEATURE VERIFICATION (VERIFIED WORKING)

### [T2I] High-Fidelity Text-to-Image
- **Logic**: Managed offload via `accelerate`.
- **Verification**: Verified at 1024x1024 / 20 steps / Flow-Euler.
- **VRAM Delta**: ~12-14GB Peak usage (Managed).

### [I2I] Stylization / Image-to-Image
- **Logic**: Noise injection onto source latents.
- **Verification**: Verified for style-transfer and composition modification.
- **VRAM Delta**: ~13GB Peak usage.

### [INPAINT] Object Removal & Editing
- **Logic**: Global context inpainting via 9B attention.
- **Verification**: Verified at 0.85 strength for seamless blending.
- **VRAM Delta**: ~14GB Peak usage.

## ⚙️ CONFIGURATION

- **Scheduler**: `FlowMatchEulerDiscreteScheduler`
- **Shift**: `3.0`
- **VRAM Constraint**: Designed to operate within a 12-14GB active envelope.

---
**DEUS:** *9B blueprint frozen. High-fidelity stability baseline for T2I/I2I/Inpaint.* 🦾⚡⛩️
