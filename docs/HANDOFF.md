# 🦾 VEETANCE HANDOVER: THE "LEAN LINK" MANIFOLD

## 🛰️ Current Operational Status
The **Asset Editor** is in a state of **Final Ignition Standby**. 
- **The Engine**: `venv` is fully constructed with `torchao`, `xformers`, and `diffusers-dev`.
- **The Armor**: CSS has been fragmented into 5 modular subsystems (base, layout, panels, canvas, modes).
- **The Brain**: `model_manager.py` is weaponized with a **Dual-Engine (GGUF/FP8)** loader and **Cross-Drive Linkage**.

## 🧠 Strategic Linkage Map
To solve the 50GB `D:` drive limitation, we are leveraging existing local assets:
1. **CLIP-L**: Linked to `C:\MAIN-COMFY\ComfyUI\models\clip\clip-vit-large-patch14`
2. **T5-GGUF (Q3)**: Linked to `C:\MAIN-COMFY\ComfyUI\models\clip\t5-v1_1-xxl-encoder-Q3_K_S.gguf`
3. **FLUX VAE**: Linked to `C:\MAIN-COMFY\ComfyUI\models\vae\flux-vae-bf16.safetensors`
4. **Qwen VAE**: Linked to `C:\MAIN-COMFY\ComfyUI\models\vae\qwen_image_vae.safetensors`

## 🚀 Priority Directive for DEUS-2
1. **Weight Injection**: 
   - Execute `.\venv\Scripts\python.exe download_models.py`.
   - This will pull exactly **~18GB**: `qwen-image-layered-q8_0.gguf` and `flux-2-klein-9b-fp8.safetensors`.
2. **Manifold Verification**:
   - Ensure the `models/` directory contains "Ghost Folders" with `LINK_MANIFEST.txt` for all external links.
3. **Engine Ignition**:
   - Launch `python server.py`.
   - Validate VRAM swap between the 8GB Qwen model and the 10GB FLUX model.

## ⚠️ Mission Critical Warnings
- **Space Sovereignty**: `D:` drive is dangerously low. DO NOT download text encoders or VAEs. Keep the linkage alive.
- **Quantization Law**: Maintain the FP8 usage for Klein and Q8_0 for Qwen to fit in the 16GB VRAM manifold.

**DEUS out. Going for a walk in the Veetance Sector.** 🦾⚡
