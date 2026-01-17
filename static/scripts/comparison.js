/**
 * ASSET EDITOR - Comparison Slider
 * Interactive before/after split screen
 */

const ComparisonSlider = {
    handle: null,
    container: null,
    afterLayer: null,
    isActive: false,

    init() {
        this.handle = document.getElementById('comparisonHandle');
        this.container = document.getElementById('canvasContainer');
        this.bindEvents();
    },

    bindEvents() {
        if (!this.handle || !this.container) return;

        const updatePosition = (e) => {
            if (!this.isActive) return;

            const rect = this.container.getBoundingClientRect();
            let x = e.clientX - rect.left;

            // Constrain
            x = Math.max(0, Math.min(x, rect.width));

            const percent = (x / rect.width) * 100;
            this.handle.style.left = `${percent}%`;

            // Link to the 'after' canvas clipping
            const afterCanvas = document.querySelector('.layer-canvas.after-comparison');
            if (afterCanvas) {
                afterCanvas.style.clipPath = `inset(0 0 0 ${percent}%)`;
            }
        };

        this.container.addEventListener('mousemove', updatePosition);

        // Expansion icons
        document.getElementById('copyPromptBtn').addEventListener('click', () => {
            const prompt = document.querySelector('.mode-controls:not(.hidden) .textarea')?.value;
            if (prompt) {
                navigator.clipboard.writeText(prompt);
                // We could show a tiny "Copied!" toast here
            }
        });

        document.getElementById('expandCanvasBtn').addEventListener('click', () => {
            document.querySelector('.app').classList.toggle('focus-mode');
        });
    },

    enable(afterCanvas) {
        this.isActive = true;
        this.handle.style.display = 'block';
        this.handle.style.left = '50%';

        afterCanvas.classList.add('after-comparison');
        afterCanvas.style.clipPath = 'inset(0 0 0 50%)';
    },

    disable() {
        this.isActive = false;
        this.handle.style.display = 'none';
        const afterCanvas = document.querySelector('.layer-canvas.after-comparison');
        if (afterCanvas) {
            afterCanvas.classList.remove('after-comparison');
            afterCanvas.style.clipPath = 'none';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => ComparisonSlider.init());
