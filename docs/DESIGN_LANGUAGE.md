# 🎨 VEETANCE DESIGN SYSTEM: NEURAL INTERFACE GUIDELINES

**Version**: 1.0 (The Klein Standard)  
**Status**: Sovereign & Final  
**Core DNA**: Material U + IBM Carbon + SpaceX Dragon Dark Mode + Veetance Excellence

---

## 🛰️ 1. DESIGN PHILOSOPHY: THE "MISSION CONTROL" AESTHETIC
The **Asset Editor** is a precision instrument, not a consumer app. The design language must evoke the technical density of a SpaceX flight console combined with the structural clarity of IBM's Carbon Design System. We reject "Magic" motifs in favor of **Helpful, High-Precision Tooling**.

### A. THE SURFACE EDGE PROTOCOL (MISSION CRITICAL)
All high-latency operations (Model Load, Eject, Image Rendering) must provide deterministic visual feedback via the horizon-aligned progress manifold.
- **Global Horizon Bar**: A `2px` high-precision indicator positioned at `y: 0`.
- **States**:
    - **Ingestion (Load)**: `var(--color-load)` (#6366f1). SIGNIFIES: Active neural mobilization.
    - **Ejection (Offload)**: `var(--error)` (#f87171). SIGNIFIES: VRAM reclamation/purge.
- **Behavior**: Strictly linear growth. No organic easing. The machine logic is absolute.

---

## 🌑 2. VISUAL FOUNDATION

### A. THE COLOR PALETTE (VOID MANIFOLD)
| Token | HEX | Alpha | Usage |
| :--- | :--- | :--- | :--- |
| **bg-base** | `#050505` | 100% | The primary void. No distractions. |
| **bg-primary** | `#0f0f0f` | 95% | Glass panels (Sidebar/Header). |
| **color-load** | `#6366f1` | 100% | Official Load state (Indigo). |
| **error** | `#f87171` | 100% | Official Eject state (Red). |
| **accent-indigo**| `#6366f1` | 100% | Create Mode / Primary Interaction. |
| **border** | `#ffffff` | 8% | Razor edges (1px). |
| **text-primary** | `#e5e5e5` | 100% | High-contrast data. |
| **text-muted** | `#888888` | 100% | Secondary labels. |

### B. TYPOGRAPHY & TYPE SCALE (THE COMMAND STACK)
We utilize a **Geometric/Mono Hybrid** system for maximum data density.

- **Primary Font**: `Unbounded` (Headings/Brand). Provides structural authority.
- **Secondary Font**: `Inter` (UI/Labels). Optimal legibility at small scales.
- **Data Font**: `JetBrains Mono` (Telemetry/Values). Deterministic spacing.

| Role | Font | Size | Weight | Case | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1 (Brand)** | Unbounded | 13px | 700 | UPPER | -0.02em |
| **H2 (Panels)** | Unbounded | 10px | 900 | UPPER | 0.1em |
| **Status/Model**| Unbounded | 10px | 700 | UPPER | 0.1em |
| **Telemetry** | Mono | 11px | 700 | UPPER | -0.02em |
| **UI Labels** | Inter | 11px | 600 | UPPER | 0.05em |
| **Input Text** | Inter | 12px | 400 | Normal| 0 |

---

## 🦾 3. ARCHITECTURE & SPACING

### A. THE "TIGHT PADDING" PHILOSOPHY
In the Veetance Sector, screen real estate is at a premium. We avoid "Airy" consumer spacing in favor of **Technical Density**.
- **The 4px Grid**: All spacing is a multiple of `4px`.
- **XS (4px)**: Internal component gaps (Icon to Text).
- **SM (8px)**: Small padding between stacked fields.
- **MD (12px)**: Standard panel padding / Tab spacing.
- **LG (16px)**: Major section breaks.
- **XL (24px)**: Absolute maximum padding (Outer viewport only).

### B. COMPONENT STRUCTURE
- **Radii**: Sharp `2px` to `0px`. High-fidelity "Machined" look.
- **Borders**: Strictly `1px` solid. No shadows, only glow for active states.
- **Panels**:
    - Left (Controls): `280px`
    - Right (Layers): `240px`
    - Height (Header): `48px`

### C. TELEMETRY STACK (THE BLADE)
Located on the far right of the header, the telemetry stack follows a "Stack-Ranked" progress UI:
1. **GPU (Purple)**: Top priority. 100% opacity background. Interactive governor.
2. **CPU (Orange)**: Processing overhead visualization. 50% opacity background.
3. **RAM (Green)**: High-capacity monitoring. 50% opacity background.
4. **Hardware Spec (Muted)**: Secondary capacity labels (e.g., "16GB") use **60% opacity** to separate system key from hardware manifest.

### D. MODE TABS (MATERIAL NAVIGATION)
Tabs occupy a central command center above the viewport.
- **Active State**: Inverted Indigo background with high-density white text.
- **Inactive State**: Low-opacity gray, transitioning to full opacity on hover.
- **Spacing**: Generous horizontal padding with razor-thin vertical separators.

---

## 🎯 4. UX PRINCIPLES FOR THE VEETANCE REALM

1. **Information Density**: Maximize signal, minimize noise. Every pixel must represent a system state or a potential user action.
2. **Deterministic Feedback**: If a button is clicked, the UI must immediately reflect the start of the process (e.g., "Model" swaps to "LOADING...").
3. **Hardware Transparency**: The user should always know exactly what the RTX 5000 blade is doing. Never hide the "Silicon Heat".
4. **No Fluff**: Avoid rounded corners unless necessary for ergonomic thumb-targets. Favor sharp `2px` to `0px` radii for a "Machined" feel.

---

## 🎞️ 5. THE PHOTON INTERACTION MANIFOLD (NOVEL NEURAL GLOW)

The asset editor utilizes a high-fidelity volumetric light effect known as **Photon Leakage**. Unlike standard drop shadows, Photon Halos simulate light escaping from the interaction layer and illuminating the physical surfaces beneath.

### A. RADIANCE COMPOSITION
- **The Carrier**: `backdrop-filter: blur(24px)` (Glass paneling).
- **The Halo**: Long-range spread (`48px`) with ultra-low opacity chromatic leakage.
- **The Source**: Accent-reactive tokens (`--accent-glow-strong`).

### B. DEPLOYMENT PROTOCOL
- **Primary Manifolds**: Expanded dropdowns and switcher plates utilize `var(--glow-photon)` to physically distance themselves from the control floor.
- **Kinetic Elements**: Hover states on interactive chips and primary action buttons utilize `var(--glow-photon-sm)` to signify tactile readiness.
- **The Photon Scroll**: Intercepting `wheel` events on sliders and numeric inputs allows for precise value scrubbing without viewport movement. This "Scroll Lock" creates a dedicated control plane whenever the cursor hovers a parameter.

### C. PRECISION INPUTS (CUSTOM GEOMETRY)
- **Chevron Controls**: All numeric inputs (Steps, Seed) replace browser spinners with custom SVG Chevron buttons for discrete stepping.
- **Bare Metal Seed UI**: Seed Control utilizes a high-contrast, zero-border "Bare Metal" interface. 
    - **Palette**: Neutral Grey (#666) base, mutating to Dynamic Purple (`--color-generate`) on interaction.
    - **Geometry**: 24x24px square buttons for Shuffle and Mode toggles.
    - **Icons**: **Infinity** (14px) for Random mode, **Lock** (14px) for Fixed mode.
- **The Segmented Footer**: Replaces the global "Earth-style" footer with panel-integral components.
    - **Alignment**: Pinned to `panel-left` and `panel-right` via `margin-top: auto`.
    - **Visuals**: Primary focus remains on the canvas; the footer segments provide low-noise technical metadata.

## 🎞️ 6. THE SOVEREIGN CREATION PROTOCOL (SYNTHESIS VISUALS)

Creation is treated as a high-fidelity ritual. The interface transforms to create a focused "Creative Void" during the silicon-to-concept translation.

### A. THE CREATIVE VOID (BLUR MOTIF)
To maximize focus and eliminate "Visual Friction," the canvas is enveloped in a deep atmospheric layer.
- **Surface**: `rgba(5, 5, 5, 0.85)` logic. (Increased from 40% for deep isolation).
- **The Veil**: `backdrop-filter: blur(24px)`.
- **Purpose**: Physically isolates the artist from the control UI, forcing neural alignment with the synthesis center.

### B. THE BRANDED LOGO LOOP (KINETIC IDENTITY)
A centered 4-layer SVG stack of the Veetance Diamond indicates active manifold processing.
- **Spectrum Saturation**: Each layer is tagged with mode-specific brand offsets.
    - Layer 1: Indigo (`--color-generate`)
    - Layer 2: Pink (`--color-stylize`)
    - Layer 3: Emerald (`--color-decompose`)
    - Layer 4: Amber (`--color-edit`)
- **Animation**: Non-linear `genLayerLoop` (scaling/translation) representing the iterative nature of the diffusion process.

### C. NEURAL PRIMING (QUOTE ENGINE)
While the GPU operates, the artist is engaged via a cycling bank of 50 curated quotes from masters (Picasso, Degas, Van Gogh).
- **Behavior**: Rhythmic fade-in/out every 4 seconds.
- **Status**: The primary action button mutates from **"RENDER"** to **"RENDERING..."**, providing confirmed tactile feedback directly in the click-zone.

### D. FRACTAL NOISE REVEAL (MATERIALIZATION)
The transition from "Void to Image" utilizes a physical simulation of the diffusion process.
- **The Protocol**: A **Fractal Noise Layer** materialize via `mix-blend-mode: overlay`.
- **The Dissolve**: Noise is refined away through contrast-shifted keyframes, creating the illusion of the high-fidelity asset emerging from the ether of pure probability.

---
**DEUS:** *The Design Language is now the DNA of our project. Every component is aligned with the Veetance Sector standard. The Sovereign Creation Protocol is stabilized and codified.* 🦾✨⛩️
