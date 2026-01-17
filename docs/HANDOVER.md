# VEETANCE MANIFOLD: HANDOVER PROTOCOL 🦾✨

**Project:** ASSET EDITOR (FLUX-2-KLIEN)
**Originator:** MrVee (The 3D Counterpart)
**Executant:** DEUS (Digital Sub-Agent)

---

## 💎 CURRENT RESONANCE (UI STATE)
The interface is now at a "Premium Minimalist" level. All interaction patterns are established but require backend wiring.

### 🎨 Visual Identity
- **Typography:** `Unbounded` for headers/logo/tabs, `Inter` for data/labels.
- **Color Palette:** Deep dark backgrounds (`#050505`) with translucent glass panels. 
- **Mode Accents:**
  - **Generate:** Indigo (#6366f1)
  - **Stylize:** Pink (#ec4899)
  - **Decompose:** Emerald (#10b981)
  - **Edit:** Amber (#f59e0b)

### 🧩 Atomic Components
- **Unified Prompt Box:** Integrated title header, borderless textarea, focus-aware glow.
- **Viewport:** Figma-style pannable/zoomable manifold with high-contrast dark checkers.
- **Comparison Slider:** Interactive "curtain" slider for original vs. edited image comparison.
- **Focus Mode:** One-click "Expand" to hide all panels and header for pure art focus.
- **Splash Screen:** 4-layer staggered animation (one color per mode).

---

## 🧪 UNTESTED FRONTIERS
The following features were implemented in the final hour and need immediate verification in a live browser session:
1. **Viewport Panning/Zooming:** Verify `viewport.js` correctly handles the `canvasStackWrapper` transform.
2. **Comparison Slider:** Test `comparison.js` clip-path logic on two superimposed canvases.
3. **Focus Mode:** Ensure all side panels and the top header disappear correctly when `.app.focus-mode` is toggled.

---

## 🚀 BACKEND ARCHITECTURE (NEXT STEPS)
The foundation for the "Power Layer" is laid.

### 1. Requirements & Weights
- `requirements.txt` has been weaponized with `xformers`, `bitsandbytes`, and `optimum`.
- `download_models.py` is ready to pull **FLUX.1-schnell**, **CLIP**, and **T5** encoders.
- **Target Location:** `d:/FLUX-2-KLIEN/models/`

### 2. VRAM Swapper (Priority)
Implement `model_manager.py`. It MUST rotate between **Qwen (Decomposition)** and **FLUX (Generation/Edit)** within the VRAM buffer. 
- **Purge Logic:** Use `torch.cuda.empty_cache()` and manual GC.
- **Lazy Loading:** Only move to VRAM when the mode-specific API endpoint is hit.

### 3. CSS Fragmentation
`main.css` is currently a monolith (>600 lines). 
- **Task:** Break it into `layout.css`, `canvas.css`, `panels.css`, and `modes.css`.
- **Reason:** Prevent truncation and corruption during high-density coding sessions.

---

## 🤖 RALPH DIRECTIVE
Ralph is the background PRD-loop engine (`prd.json` + `progress.txt`). He is to be used for autonomous refactors, memory-leak hunting, and stress testing. If MrVee says "RALPH:", switch to full autonomous execution.

---

**DEUS SIGN-OFF:** 
The UI is a work of art. The engine is primed. 
Next Agent: Feed the machine. 🦾✨
