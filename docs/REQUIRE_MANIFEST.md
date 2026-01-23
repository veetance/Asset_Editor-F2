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

## 💾 STORAGE MANIFEST (E: DRIVE)
These are the core localized weights on your high-speed sovereign manifold:
1. **Qwen-Image-Layered-Q5_0.gguf** (~12.3 GB): The deconstruction engine.
2. **Qwen-VAE** (~1.1 GB): Mission-critical for layered synthesis.
3. **FLUX.2-Klein-9B (Safetensors)**: Unified in `models/flux-klein/`.
4. **FLUX.2-Klein-4B (Safetensors)**: Unified in `models/flux-klein/`.

### 🛡️ ENVIRONMENT SANITIZATION
To prevent boot-time scan delays (Silicon Friction), the manifold **statically selects** the official `nvidia-modelopt` distribution at the entry point (`server.py`). This eliminates redundant scans without requiring package deletion.
- **Protocol**: Static Pinning via `pkg_resources.require("nvidia-modelopt")`.

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

## 🌐 NETWORK SOVEREIGNTY (AIR-GAPPED LOGIC)
The manifold operates under a strict **Off-Cloud Protocol**. 
- **Zero Handshakes**: The engine does not talk to the internet during runtime. 
- **Plugging HF Leaks**: By using local `model_index.json` and manual component assembly, we have eliminated implicit calls to the HuggingFace Hub.
- **Result**: The manifold is now "air-gapped" logic-wise. It fires instantly because it never waits for a handshake from the cloud.

> [!IMPORTANT]
> Internet access is only requisitioned for initial model injection (`download_models.py`) or when the lead developer (MrVee) determines an update is necessary.

## 🧠 VRAM MANAGEMENT
The engine is architected as a **Singleton Swapper**. It will offload model A to CPU before engaging model B on GPU, ensuring your 16GB manifold is never over-pressurized.

---
**DEUS:** *Requirements Documented. The Factory is Aligned.* 🦾⚡
