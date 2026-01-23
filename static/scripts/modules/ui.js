/**
 * ASSET EDITOR - Generic UI Controls
 */
import { State } from './state.js';

export const UI = {
    init() {
        this.initTabs();
        this.initSliders();
        this.initDropdowns();
        this.initFileUpload();
        this.initToggles();
        this.initGovernor();
        this.initSeedControl();
        this.initStepsControl();
        this.initWheelControls();
        this.syncFromState();
    },

    initWheelControls() {
        // Handle Numeric Inputs (Steps, Seed)
        const numericWraps = ['.seed-input-group', '.steps-input-group'];
        numericWraps.forEach(selector => {
            const wrap = document.querySelector(selector);
            if (!wrap) return;

            wrap.addEventListener('wheel', (e) => {
                const input = wrap.querySelector('input');
                if (!input) return;

                e.preventDefault();
                e.stopPropagation();

                const delta = e.deltaY > 0 ? -1 : 1;
                let val = parseInt(input.value) || 0;

                // Special handling for Seed mode
                if (input.id === 'genSeed') {
                    const modeToggle = document.getElementById('genSeedMode');
                    this.updateSeedMode(modeToggle, 'fixed');
                    input.value = val + delta;
                } else if (input.id === 'genSteps') {
                    input.value = Math.max(1, Math.min(50, val + delta));
                } else {
                    input.value = val + delta;
                }

                // Trigger change event for any listeners
                input.dispatchEvent(new Event('input'));
            }, { passive: false });
        });

        // Handle Sliders (Width, Height, Adherence, Strength, etc.)
        document.querySelectorAll('.slider-wrap').forEach(wrap => {
            wrap.addEventListener('wheel', (e) => {
                const slider = wrap.querySelector('input[type="range"]');
                if (!slider) return;

                e.preventDefault();
                e.stopPropagation();

                const step = parseFloat(slider.step) || 1;
                const delta = e.deltaY > 0 ? -step : step;
                const min = parseFloat(slider.min);
                const max = parseFloat(slider.max);

                let val = parseFloat(slider.value) + delta;
                slider.value = Math.max(min, Math.min(max, val));

                // Trigger change event
                slider.dispatchEvent(new Event('input'));

                // If it's the Guidance slider, we need to handle the chip specifically 
                // because the mouseenter handler might not be active if purely scrolling
                if (slider.id === 'genGuidance') {
                    const chip = document.getElementById('canvasChip');
                    if (chip) {
                        chip.classList.remove('hidden');
                        this.updateGuidanceHint(parseFloat(slider.value));
                    }
                }
            }, { passive: false });
        });
    },

    initSeedControl() {
        const seedInput = document.getElementById('genSeed');
        const shuffleBtn = document.getElementById('shuffleSeedBtn');
        const modeBtn = document.getElementById('genSeedMode');
        const incBtn = document.getElementById('seedInc');
        const decBtn = document.getElementById('seedDec');

        const setMode = (mode) => {
            this.updateSeedMode(modeBtn, mode);
        };

        if (shuffleBtn) {
            shuffleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const newSeed = Math.floor(Math.random() * 2147483647);
                seedInput.value = newSeed;
                // Force mode to Fixed when shuffling manually
                setMode('fixed');
            });
        }

        if (modeBtn) {
            modeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const current = modeBtn.dataset.value;
                const next = (current === 'random') ? 'fixed' : 'random';
                setMode(next);
            });
        }

        if (incBtn) {
            incBtn.addEventListener('click', (e) => {
                e.preventDefault();
                seedInput.value = parseInt(seedInput.value) + 1;
                setMode('fixed');
            });
        }

        if (decBtn) {
            decBtn.addEventListener('click', (e) => {
                e.preventDefault();
                seedInput.value = Math.max(0, parseInt(seedInput.value) - 1);
                setMode('fixed');
            });
        }
    },

    initStepsControl() {
        const stepsInput = document.getElementById('genSteps');
        const incBtn = document.getElementById('stepsInc');
        const decBtn = document.getElementById('stepsDec');

        if (incBtn) {
            incBtn.addEventListener('click', (e) => {
                e.preventDefault();
                stepsInput.value = Math.min(50, parseInt(stepsInput.value) + 1);
            });
        }

        if (decBtn) {
            decBtn.addEventListener('click', (e) => {
                e.preventDefault();
                stepsInput.value = Math.max(1, parseInt(stepsInput.value) - 1);
            });
        }
    },

    updateSeedMode(btn, mode) {
        if (!btn) return;
        btn.dataset.value = mode;

        // Icon Toggling
        const iconRandom = btn.querySelector('.icon-random');
        const iconFixed = btn.querySelector('.icon-fixed');

        if (mode === 'random') {
            if (iconRandom) iconRandom.classList.remove('hidden');
            if (iconFixed) iconFixed.classList.add('hidden');
        } else {
            if (iconRandom) iconRandom.classList.add('hidden');
            if (iconFixed) iconFixed.classList.remove('hidden');
        }

        // Toast Feedback
        const toast = document.getElementById('seedToast');
        if (toast) {
            toast.textContent = mode.toUpperCase();
            toast.classList.add('visible');

            // Clear previous timer if exists
            if (btn._toastTimer) clearTimeout(btn._toastTimer);

            btn._toastTimer = setTimeout(() => {
                toast.classList.remove('visible');
            }, 1500);
        }
    },

    syncFromState() {
        // Ensure VRAM budget displays match State
        const gb = State.vramUserLimit;
        const bar = document.getElementById('vramProgress');
        const valText = document.getElementById('vramValue');

        if (bar) bar.style.width = `${(gb / 16) * 100}%`;
        if (valText) valText.textContent = `${gb.toFixed(0)}GB`;
    },

    initTabs() {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => State.setMode(tab.dataset.mode));
        });
    },

    initToggles() {
        document.querySelectorAll('[data-canny]').forEach(btn => {
            btn.addEventListener('click', () => {
                State.cannyEdges = btn.dataset.canny === 'on';
                document.querySelectorAll('[data-canny]').forEach(b => b.classList.toggle('active', b === btn));
            });
        });
    },

    initSliders() {
        // Helper
        const bind = (id, valId, fmt = v => v) => {
            const el = document.getElementById(id);
            const val = document.getElementById(valId);
            if (el && val) el.addEventListener('input', () => val.textContent = fmt(el.value));
        };

        bind('layerCount', 'layerCountValue');
        bind('editStrength', 'editStrengthValue', v => `${v}%`);
        bind('genWidth', 'genWidthValue');
        bind('genHeight', 'genHeightValue');


        // Guidance Special Logic
        const gSlider = document.getElementById('genGuidance');
        const gVal = document.getElementById('genGuidanceValue');
        const chip = document.getElementById('canvasChip');

        if (gSlider) {
            const updateChip = () => {
                const v = parseFloat(gSlider.value);
                if (gVal) gVal.textContent = v.toFixed(1);
                if (chip) {
                    chip.classList.remove('hidden');
                    this.updateGuidanceHint(v);
                }
            };
            gSlider.addEventListener('input', updateChip);
            gSlider.addEventListener('mouseenter', updateChip);
            gSlider.addEventListener('mouseleave', () => chip.classList.add('hidden'));
        }
    },

    updateGuidanceHint(val) {
        const hintEl = document.getElementById('chipDesc');
        if (!hintEl) return;
        let tip = "", desc = "";

        if (val <= 1.0) { tip = "Loose:"; desc = "Photoreal focus."; }
        else if (val <= 3.0) { tip = "Balanced:"; desc = "Standard prompt."; }
        else if (val <= 4.0) { tip = "Distilled:"; desc = "Optimal Flux State."; }
        else { tip = "Strict:"; desc = "Aggressive enforcement."; }

        hintEl.innerHTML = `<span class="guidance-tip">${tip}</span> ${desc}`;
    },

    initDropdowns() {
        const selects = document.querySelectorAll('.custom-select');
        selects.forEach(select => {
            const trigger = select.querySelector('.select-trigger');
            const current = select.querySelector('.select-current');

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const isActive = select.classList.contains('active');
                selects.forEach(s => s.classList.remove('active')); // Close others
                if (!isActive) {
                    select.classList.add('active');
                    setTimeout(() => {
                        select.querySelector('.select-dropdown').scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 100);
                }
            });

            select.querySelectorAll('.select-option').forEach(opt => {
                opt.addEventListener('click', (e) => {
                    e.stopPropagation();
                    select.dataset.value = opt.dataset.value;
                    current.textContent = opt.textContent;
                    select.querySelectorAll('.select-option').forEach(o => o.classList.remove('active'));
                    opt.classList.add('active');
                    select.classList.remove('active');
                });
            });
        });
        document.addEventListener('click', () => selects.forEach(s => s.classList.remove('active')));
    },

    initFileUpload() {
        const zone = document.getElementById('uploadZone');
        const input = document.getElementById('imageInput');
        if (!zone) return;

        zone.addEventListener('click', () => input.click());
        zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('dragover');
            if (e.dataTransfer.files[0]) this.handleFile(e.dataTransfer.files[0]);
        });
        input.addEventListener('change', () => {
            if (input.files[0]) this.handleFile(input.files[0]);
        });
    },

    handleFile(file) {
        State.sourceFile = file;
        document.getElementById('uploadZone').innerHTML = `<span class="dropzone-text">✓ ${file.name}</span>`;
    },

    initGovernor() {
        const gov = document.getElementById('vramGovernor');
        const bar = document.getElementById('vramProgress');
        const val = document.getElementById('vramValue');

        if (!gov || !bar || !val) return;

        gov.addEventListener('mousedown', (e) => {
            e.preventDefault(); // Prevent text selection

            const move = (ev) => {
                const rect = gov.getBoundingClientRect();
                // Calculate percentage (clamped 0-1)
                const pct = Math.max(0, Math.min((ev.clientX - rect.left) / rect.width, 1));

                // 1. Tactile Visual Feedback (The Cheat)
                // Update DOM immediately without waiting for State/React cycles
                const gb = pct * 16.0;
                bar.style.width = `${pct * 100}%`;
                val.textContent = `${gb.toFixed(0)}GB`;

                // 2. State Update (For Logic)
                State.vramUserLimit = gb;

            };

            const up = () => {
                window.removeEventListener('mousemove', move);
                window.removeEventListener('mouseup', up);
            };

            window.addEventListener('mousemove', move);
            window.addEventListener('mouseup', up);

            // Initial snap
            move(e);
        });
    }
};
