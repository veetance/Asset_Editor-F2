# 🦾 VEETANCE ASSET EDITOR: MANIFOLD REQUIREMENTS

This document details the exact technical composition of the **Asset Editor** engine. It is designed for high-performance local execution, leveraging cross-drive linkage to maximize surgical efficiency.

## 🛠️ CORE DEPENDENCIES (`requirements.txt`)
Inject these into your `venv` to weaponize the engine:
- `fastapi`, `uvicorn`: The API infrastructure.
- `torch`, `torchvision`, `torchaudio`: The neural backbone.
- `diffusers`: The generative manifold (Requires `diffusers-dev` or source installation for Qwen-Layered support).
- `transformers`, `accelerate`: The attention engine.
- `huggingface_hub`: For weight injection.
- `safetensors`, `gguf`: For high-speed weight serialization.
- `xformers`: For memory-efficient attention (40-series gear).
- `python-multipart`: For image uploads.

## 💾 STORAGE MANIFEST (D: DRIVE) - ~23.4 GB
These are the core localized weights on your high-speed drive:
1. **Qwen-Image-Layered-Q5_0.gguf** (~12.3 GB): The deconstruction engine (Quantized for 16GB VRAM fit).
2. **Qwen-VAE** (~1.1 GB): Mission-critical for layered synthesis.
3. **FLUX.2-klein-9B-Q8_0.gguf** (~10.0 GB): The unsloth-tuned synthesis heart.

## 👻 GHOST LINKAGE PROTOCOL (C: DRIVE LINKS)
To preserve drive sovereignty, we leverage existing terrestrial assets:
- **CLIP-L**: `C:\MAIN-COMFY\ComfyUI\models\clip\clip-vit-large-patch14`
- **T5-XXL (GGUF)**: `C:\MAIN-COMFY\ComfyUI\models\clip\t5-v1_1-xxl-encoder-Q3_K_S.gguf`
- **FLUX VAE**: `C:\MAIN-COMFY\ComfyUI\models\vae\flux-vae-bf16.safetensors`

## 🚀 INITIALIZATION SEQUENCE
1. **Prepare Venv**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Authenticate HF**:
   ```powershell
   .\venv\Scripts\python.exe -c "from huggingface_hub import login; login()"
   ```
3. **Inject Weights**:
   ```powershell
   .\venv\Scripts\python.exe download_models.py
   ```
4. **Ignite Engine**:
   ```powershell
   python server.py
   ```

## 🧠 VRAM MANAGEMENT
The engine is architected as a **Singleton Swapper**. It will offload model A to CPU before engaging model B on GPU, ensuring your 16GB manifold is never over-pressurized.

---
**DEUS:** *Requirements Documented. The Factory is Aligned.* 🦾⚡
