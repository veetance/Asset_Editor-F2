---
description: Migrate text encoder from safetensors to GGUF for space savings
---
# GGUF Text Encoder Migration Protocol

## Overview
Replace the 7.5GB FP16 Qwen3 text encoder shards with a 2-4GB GGUF quantized version.

## Current State
- `models/flux-klein/text_encoder/model-00001-of-00002.safetensors` (4.63GB)
- `models/flux-klein/text_encoder/model-00002-of-00002.safetensors` (2.87GB)
- **Total: ~7.5GB**

## Target Files
Source: `huggingface.co/worstplayer/Z-Image_Qwen_3_4b_text_encoder_GGUF`

| Option | File | Size | Quality |
|--------|------|------|---------|
| High | `Qwen_3_4b-Q8_0.gguf` | ~4GB | Best |
| Medium | `Qwen_3_4b-Q4_K_M.gguf` | ~2.5GB | Good |
| Low | `Qwen_3_4b-imatrix-IQ4_XS.gguf` | ~2GB | Acceptable |

## Prerequisites
```powershell
pip install llama-cpp-python
```

## Migration Steps

### Phase 1: Backup
```powershell
# Create backup folder
mkdir models/flux-klein/text_encoder_backup

# Move original shards to backup
Move-Item "models/flux-klein/text_encoder/model-*.safetensors" "models/flux-klein/text_encoder_backup/"
```

### Phase 2: Download GGUF
```powershell
# Download from HuggingFace (choose one)
# turbo
huggingface-cli download worstplayer/Z-Image_Qwen_3_4b_text_encoder_GGUF Qwen_3_4b-Q8_0.gguf --local-dir models/flux-klein/text_encoder/
```

### Phase 3: Modify Loader
Update `core/loaders/flux.py` to load GGUF instead of safetensors:

```python
from llama_cpp import Llama

# Load GGUF text encoder
gguf_path = os.path.join(flux_dir, "text_encoder", "Qwen_3_4b-Q8_0.gguf")
text_encoder = Llama(model_path=gguf_path, embedding=True, n_ctx=512)
```

### Phase 4: Custom Embedding Function
The pipeline needs a custom function to extract embeddings from GGUF:

```python
def get_text_embeddings(text_encoder, prompt, tokenizer):
    """Extract embeddings from GGUF Qwen3 model."""
    tokens = tokenizer.encode(prompt)
    # Run forward pass and extract hidden states
    embeddings = text_encoder.embed(prompt)
    return torch.tensor(embeddings)
```

### Phase 5: Test
1. Restart server
2. Load FLUX Klein 4B
3. Test generation with a known prompt
4. Compare output quality to safetensor version

### Phase 6: Cleanup (Only after successful test)
```powershell
# Remove backup if satisfied
Remove-Item -Recurse "models/flux-klein/text_encoder_backup/"
```

## Rollback
If GGUF quality is unacceptable:
```powershell
# Restore original shards
Move-Item "models/flux-klein/text_encoder_backup/model-*.safetensors" "models/flux-klein/text_encoder/"
```

## Warning
- GGUF runs on CPU (llama-cpp), not GPU tensor cores
- Text encoding may be 2-3x slower than GPU safetensors
- Quality degradation is possible with lower quantization
- This is an ADVANCED optimization - only do if space is critical

## Recommendation
Wait until llama-cpp supports CUDA acceleration for embeddings, OR diffusers adds native GGUF text encoder support.

---
**Status:** PENDING (Do not execute until space becomes critical)
