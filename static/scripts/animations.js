/**
 * ASSET EDITOR - Splash Screen & Generation Animation
 */

const Splash = {
    element: null,
    duration: 1350,
    layers: [],
    currentLayer: 0,
    goLeft: true, // alternates each layer

    init() {
        this.element = document.getElementById('splash');
        this.layers = document.querySelectorAll('.splash-layer');

        if (this.element && this.layers.length) {
            this.startAnimation();
            setTimeout(() => this.hide(), this.duration);
        }
    },

    startAnimation() {
        this.animateLayer();
    },

    animateLayer() {
        if (!this.element || this.element.classList.contains('hidden')) return;

        const layer = this.layers[this.currentLayer];

        // Remove previous animation class
        layer.classList.remove('fall-left', 'fall-right');

        // Force reflow
        void layer.offsetWidth;

        // Add direction class - alternates each time
        layer.classList.add(this.goLeft ? 'fall-left' : 'fall-right');

        // Toggle direction for next layer
        this.goLeft = !this.goLeft;

        // Move to next layer
        this.currentLayer = (this.currentLayer + 1) % this.layers.length;

        // Schedule next layer
        setTimeout(() => this.animateLayer(), 300);
    },

    hide() {
        if (this.element) {
            this.element.classList.add('hidden');
        }
    }
};

const GenerationAnim = {
    overlay: null,
    gridSize: 16,

    init() {
        this.createOverlay();
    },

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'gen-overlay hidden';
        this.overlay.id = 'genOverlay';

        const totalCells = this.gridSize * this.gridSize;
        for (let i = 0; i < totalCells; i++) {
            const cell = document.createElement('div');
            cell.className = 'gen-cell';
            this.overlay.appendChild(cell);
        }

        const container = document.getElementById('canvasContainer');
        if (container) {
            container.appendChild(this.overlay);
        }
    },

    start() {
        if (!this.overlay) return;

        const cells = this.overlay.querySelectorAll('.gen-cell');
        cells.forEach(cell => cell.classList.remove('revealed'));

        this.overlay.classList.remove('hidden');
        this.revealCells(cells);
    },

    revealCells(cells) {
        const cellArray = Array.from(cells);
        const shuffled = this.shuffleArray([...cellArray]);

        let index = 0;
        const interval = setInterval(() => {
            for (let i = 0; i < 8 && index < shuffled.length; i++, index++) {
                shuffled[index].classList.add('revealed');
            }

            if (index >= shuffled.length) {
                clearInterval(interval);
                setTimeout(() => this.hide(), 200);
            }
        }, 50);
    },

    hide() {
        if (this.overlay) {
            this.overlay.classList.add('hidden');
        }
    },

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Splash.init();
    GenerationAnim.init();
});
