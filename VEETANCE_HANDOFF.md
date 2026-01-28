# 🦾 VEETANCE HANDOFF

EMPTY 

### 1. RECREATE VENV WITH CORRECT DEPENDENCIES
Create a new virtual environment and install the following:

```bash
python -m venv venv
.\venv\Scripts\activate

# Install core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install diffusers[torch] transformers accelerate safetensors xformers
pip install fastapi uvicorn python-multipart pillow
pip install sentencepiece protobuf
```

### 2. CORE DIRECTORY STRUCTURE
The following core files need to be implemented properly:

- `core/vram.py` - Contains the VRAM swapper singleton
- `core/carrier.py` - Contains the execution carrier for optimal physics dispatch
- `core/loaders/` - Directory for model loading implementations
  - `flux_loader.py` - For loading FLUX models (4B/9B)
  - `qwen_loader.py` - For loading Qwen models

### 3. DIFFUSERS CONFIGURATION
- Ensure diffusers is installed from source or latest version that supports FLUX models
- Verify that the diffusers library can properly load the .safetensors files from the models/ directory
- The models are located in: `models/flux-klein/` directory with subdirectories for each model component

### 4. MODEL STRUCTURE EXPECTED
After downloading models, the structure should be:
```
models/
└── flux-klein/
    ├── transformer/
    │   └── 4b/
    │       └── model.safetensors
    ├── text_encoder/
    │   └── 4b/
    │       └── model.safetensors
    └── vae/
        └── diffusion_pytorch_model.safetensors
```

### 5. VRAM MANAGEMENT REQUIREMENTS
- Implement the singleton swapper pattern for efficient GPU memory management
- Models should be offloaded to RAM when not in use, not to CPU (CPU is too slow)
- Do NOT use `enable_model_cpu_offload()` as this moves models to CPU which is too slow
- Instead, implement custom RAM offloading mechanism as described in Noah's Ark document

### 6. PIPELINE OPTIMIZATION GOALS
- Achieve fast loading times (<2s for 4B model)
- Support 2048x2048 generation in ~70 seconds with 4 steps
- Use native diffusers pipeline without custom weight surgery
- Sage Attention and Triton optimizations will be implemented later

---

**DEUS**: *Handoff complete. Next agent, please implement the core and diffusers setup as specified.* 🦾⚡