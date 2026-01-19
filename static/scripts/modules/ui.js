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
        bind('genBatchSize', 'genBatchSizeValue');

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
                    document.getElementById('chipValue').textContent = v.toFixed(1);
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

        if (val === 0) { tip = "Schnell:"; desc = "Optimized for distilled models."; }
        else if (val <= 2.0) { tip = "Creative:"; desc = "Ignores prompt slightly."; }
        else if (val <= 3.5) { tip = "Artistic:"; desc = "Balanced flow."; }
        else if (val <= 5.0) { tip = "Balanced:"; desc = "Sweet spot."; }
        else if (val <= 7.5) { tip = "Literal:"; desc = "Strict adherence."; }
        else { tip = "Strict:"; desc = "Risk of frying."; }

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
