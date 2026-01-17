/**
 * ASSET EDITOR - Viewport Module
 * Handles Figma-style panning and zooming for the canvas stack
 */

const Viewport = {
    container: null,
    wrapper: null,

    scale: 1,
    offset: { x: 0, y: 0 },

    isPanning: false,
    startPos: { x: 0, y: 0 },

    init() {
        this.container = document.getElementById('canvasContainer');
        this.wrapper = document.getElementById('canvasStackWrapper');

        if (!this.container || !this.wrapper) return;

        this.bindEvents();
        this.updateTransform();
    },

    bindEvents() {
        // Panning
        this.container.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // Left click to pan
                this.isPanning = true;
                this.startPos = { x: e.clientX - this.offset.x, y: e.clientY - this.offset.y };
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (!this.isPanning) return;

            this.offset.x = e.clientX - this.startPos.x;
            this.offset.y = e.clientY - this.startPos.y;
            this.updateTransform();
        });

        window.addEventListener('mouseup', () => {
            this.isPanning = false;
        });

        // Zooming (Alt + Wheel or just Wheel if preferred)
        this.container.addEventListener('wheel', (e) => {
            e.preventDefault();

            const zoomSpeed = 0.001;
            const delta = -e.deltaY;
            const factor = Math.pow(1.1, delta / 100);

            this.scale *= factor;

            // Constrain zoom
            this.scale = Math.max(0.1, Math.min(this.scale, 5));

            this.updateTransform();
        }, { passive: false });
    },

    updateTransform() {
        if (!this.wrapper) return;
        this.wrapper.style.transform = `translate(${this.offset.x}px, ${this.offset.y}px) scale(${this.scale})`;
    },

    reset() {
        this.scale = 0.8; // default fit-ish
        this.offset = { x: 0, y: 0 };
        this.updateTransform();
    }
};

document.addEventListener('DOMContentLoaded', () => Viewport.init());
