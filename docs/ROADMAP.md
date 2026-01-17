# ASSET EDITOR - Roadmap

## ✅ Completed

### Phase 0: Foundation
- [x] Project structure created
- [x] `model_manager.py` - VRAM Swapper with lazy loading and singleton pattern
- [x] `server.py` - FastAPI with route mounting and static file serving
- [x] `requirements.txt` - Python dependencies

### Phase 1: Backend Endpoints
- [x] `/api/decompose` - Qwen-Image-Layered RGBA extraction
- [x] `/api/txt2img` - FLUX text-to-image
- [x] `/api/img2img` - FLUX image-to-image
- [x] `/api/inpaint` - FLUX inpaint with auto/manual mask support
- [x] `/api/health` - VRAM status monitoring

### Phase 2: Frontend UI
- [x] 3-column layout (Controls | Canvas | Layers)
- [x] Full-width tabs: Generate → Decompose → Edit
- [x] Gray/black translucent theme with pop colors per mode
  - Indigo (#6366f1) - Generate
  - Emerald (#10b981) - Decompose  
  - Amber (#f59e0b) - Edit
- [x] Canvas layer stack with selection and visibility
- [x] Dual masking: Auto (alpha) + Manual (brush)

### Phase 3: Ralph PRD Loop
- [x] `prd.json` task manifest
- [x] `progress.txt` execution log

---

## 🔄 Current Status

**UI Refinement Complete** - Theme updated, tabs full-width, mode colors applied.

---

## 🚀 Road Ahead

### Phase 4: Integration Testing
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Accept HuggingFace FLUX license
- [ ] First model download (~25GB)
- [ ] Test VRAM swap cycle (Qwen → FLUX → Qwen)

### Phase 5: Full Workflow Test
- [ ] Upload image → Decompose → Verify layers
- [ ] Select layer → Apply edit → Verify update
- [ ] Text prompt → Generate → Verify output

### Phase 6: Core Persistence & Stability
- [ ] **Generation History**: PERSISTENCE - `gen-history.json` to store images + prompt metadata.
- [ ] **CSS Fragmentation**: Break heavy styles into focused modules.
- [ ] Canny edge detection for structural edits
- [ ] Undo/redo layer history
- [ ] Export composite image
- [ ] Keyboard shortcuts

---

## Quick Start

```bash
cd d:\FLUX-2-KLIEN
pip install -r requirements.txt
python server.py
# Open http://localhost:8000
```
