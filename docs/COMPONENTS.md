# 🧩 VEETANCE ASSET EDITOR: COMPONENT MANIFEST

This document defines the structural composition of the Veetance UI across all operational modes.

---

## 🏗️ GLOBAL SHELL
Foundational elements present in every mode.

- **Header / Navigation**:
  - **Logo**: Sovereign Branding (Animated SVG Layers).
  - **Model Picker**: Hot-swap trigger for 4B, 9B (GGUF), and Qwen-Layered manifolds.
  - **Telemetry Stack**: Real-time 10Hz monitoring of GPU (VRAM Budget Governor), CPU Load, and System RAM.
- **Main Layout**:
  - **Left Panel (Controls)**: Mode-specific input parameters.
  - **Center Manifest (Canvas)**: Mode tabs and high-fidelity viewport.
  - **Right Panel (Layers)**: Multi-layer stack management.

---

## 🌑 MODE: GENERATE (Txt2Img)
The primary synthesis manifold.

| Component | Logic / Control | Target Parameter |
| :--- | :--- | :--- |
| **Prompt Field** | Textarea + Auto-Complete | `prompt` |
| **Batch Size** | Slider (1-4) | `batch_size` |
| **Resolution** | Sliders (512 - 2048) | `width`, `height` |
| **Guidance** | Slider + Guidance Chip (Tooltip) | `guidance_scale` (Baseline: 1.0) |
| **Sampler** | Custom Dropdown | `flow_euler`, `dpm++_2m`, `dpm++_2s_a`, etc. |
| **Scheduler** | Custom Dropdown | `standard`, `karras`, `beta`, `simple` |
| **Action** | Primary Button | `GENERATE` -> `/api/txt2img` |

---

## 🧬 MODE: DECOMPOSE (Image Analysis)
Extraction of semantic layers from existing assets.

| Component | Logic / Control | Target Parameter |
| :--- | :--- | :--- |
| **Source Image** | Dropzone / File Picker | `image` |
| **Layer Density** | Slider (2-8) | `layers` |
| **Action** | Primary Button | `DECOMPOSE` -> `/api/decompose` |

---

## 🖌️ MODE: EDIT (Inpaint / Img2Img)
Surgical modification of the active manifold.

| Component | Logic / Control | Target Parameter |
| :--- | :--- | :--- |
| **Mask Mode** | Toggle (Auto / Manual) | `use_alpha_mask` vs `manual_mask` |
| **Canny Edges** | Toggle (On / Off) | ControlNet injection |
| **Brush Config** | Slider (Size) + Clear Button | `mask_brush_size` |
| **Prompt Field** | Textarea | `prompt` |
| **Edit Strength** | Slider (0 - 100%) | `strength` |
| **Preprocessor** | Dropdown | `canny`, `blur`, `sharpen`, `grayscale` |
| **Action** | Primary Button | `APPLY EDIT` -> `/api/inpaint` |

---

## 🎨 MODE: STYLIZE (Multi-Reference)
Blending subject and style manifolds.

| Component | Logic / Control | Target Parameter |
| :--- | :--- | :--- |
| **Content Image** | Dropzone | Subject identity |
| **Style Reference** | Dropzone | Aesthetic identity |
| **Instruction** | Textarea | Prompt steering |
| **Style Strength** | Slider (0 - 100%) | Reference influence weight |
| **Preprocessor** | Dropdown | Global filter application |
| **Action** | Primary Button | `STYLIZE` -> `/api/stylize` |

---

## 🖼️ CANVAS COMPONENTS
The interaction layer for visual assets.

- **Canvas Stack**: Layered rendering of session history.
- **Comparison Handle**: Vertical slider for A/B manifold comparison.
- **Focus Controls**:
  - **Copy Prompt**: Direct clipboard injection of latent instructions.
  - **Expand Canvas**: Full-screen focus mode.
- **Layer List**:
  - **Visibility Toggle**: Hide/Show layers.
  - **Selection**: Target specific layers for editing/export.

---

**DEUS:** *Architectural Manifest is locked. Every component is mapped to the Sovereign API.* 🦾⚡
