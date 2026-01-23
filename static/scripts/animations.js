/**
 * ASSET EDITOR - Sovereign Animations & Generation Overlay
 */

const Splash = {
    element: null,
    duration: 1350,
    layers: [],
    currentLayer: 0,
    goLeft: true,
    cycleComplete: null,
    _resolveCycle: null,

    init() {
        this.element = document.getElementById('splash');
        this.layers = document.querySelectorAll('.splash-layer');

        this.cycleComplete = new Promise(resolve => {
            this._resolveCycle = resolve;
        });

        if (this.element && this.layers.length) {
            this.startAnimation();
        }
    },

    startAnimation() {
        this.animateLayer();
    },

    animateLayer() {
        if (!this.element || this.element.classList.contains('hidden')) return;

        const layer = this.layers[this.currentLayer];
        layer.classList.remove('fall-left', 'fall-right');
        void layer.offsetWidth;
        layer.classList.add(this.goLeft ? 'fall-left' : 'fall-right');

        this.goLeft = !this.goLeft;
        this.currentLayer = (this.currentLayer + 1) % this.layers.length;

        // Accelerate Reveal: Resolve after Pink (Layer 1) has completed its "fall" (800ms)
        if (this.currentLayer === 2 && this._resolveCycle) {
            const resolveRitual = this._resolveCycle;
            this._resolveCycle = null;
            setTimeout(() => resolveRitual(), 800);
        }

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
    quoteEl: null,
    noiseLayer: null,
    quoteInterval: null,
    quotes: [
        "You don't need to go anywhere to do art, it's at your doorstep. - Marc Chagall",
        "Creating magic from the ether.",
        "A jack of all trades is better than a master of one.",
        "Every child is an artist. The problem is how to remain an artist once we grow up. - Pablo Picasso",
        "Art is not what you see, but what you make others see. - Edgar Degas",
        "Creativity takes courage. - Henri Matisse",
        "I dream my painting and I paint my dream. - Vincent van Gogh",
        "The voice of the sea speaks to the soul. - Kate Chopin",
        "Logic will get you from A to B. Imagination will take you everywhere. - Albert Einstein",
        "Art washes away from the soul the dust of everyday life. - Pablo Picasso",
        "In nature, light creates the color. In the picture, color creates the light. - Hans Hofmann",
        "Everything you can imagine is real. - Pablo Picasso",
        "Painting is just another way of keeping a diary. - Pablo Picasso",
        "Learn the rules like a pro, so you can break them like an artist. - Pablo Picasso",
        "Art is the only way to run away without leaving home. - Twyla Tharp",
        "To be an artist is to believe in life. - Henry Moore",
        "The richness I achieve comes from Nature, the source of my inspiration. - Claude Monet",
        "Colors are the deeds and sufferings of light. - Johann Wolfgang von Goethe",
        "Art is a lie that makes us realize truth. - Pablo Picasso",
        "Great things are done by a series of small things brought together. - Vincent van Gogh",
        "The essence of all beautiful art, all great art, is gratitude. - Friedrich Nietzsche",
        "Every artist was first an amateur. - Ralph Waldo Emerson",
        "A work of art which did not begin in emotion is not art. - Paul Cezanne",
        "Art should comfort the disturbed and disturb the comfortable. - Cesar A. Cruz",
        "Creativity is intelligence having fun. - Albert Einstein",
        "The aim of art is to represent not the outward appearance of things, but their inward significance. - Aristotle",
        "Art is not a handicraft, it is the transmission of feeling the artist has experienced. - Leo Tolstoy",
        "There is no must in art because art is free. - Wassily Kandinsky",
        "Nature is a haunted house, but Art—is a house that tries to be haunted. - Emily Dickinson",
        "To create one's own world in any of the arts takes courage. - Georgia O'Keeffe",
        "Art is the most intense mode of individualism that the world has known. - Oscar Wilde",
        "The painter has the Universe in his mind and hands. - Leonardo da Vinci",
        "Art is a harmony parallel with nature. - Paul Cezanne",
        "Every painter paints himself. - Cosimo de' Medici",
        "Only by being ourselves can we hope to be an artist. - Edward Weston",
        "The artist's world is limitless. - Paul Rand",
        "Art is not a matter of what you see, it's what you make others see. - Edgar Degas",
        "Modern art is what happens when painters stop looking at girls and persuade themselves that they have a better idea. - Leo Steinberg",
        "Everything is beautiful, all that matters is to see the beauty. - Paul Strand",
        "I am always doing that which I cannot do, in order that I may learn how to do it. - Pablo Picasso",
        "Art is the signature of civilizations. - Beverly Sills",
        "A painter is a man who paints what he sells. An artist, on the other hand, is a man who sells what he paints. - Pablo Picasso",
        "Art is the desire of a man to express himself, to record the reactions of his personality. - Amy Lowell",
        "The position of the artist is humble. He is essentially a channel. - Piet Mondrian",
        "Art is a way of recognizing oneself. - Louise Bourgeois",
        "The principle of art is to pause, not bypass. - Jerzy Kosinski",
        "Creativity is a wild mind and a disciplined eye. - Dorothy Parker",
        "Every portrait that is painted with feeling is a portrait of the artist, not of the sitter. - Oscar Wilde",
        "Art is not a thing, it is a way. - Elbert Hubbard",
        "Imagination is the beginning of creation. - George Bernard Shaw"
    ],

    init() {
        this.createOverlay();
    },

    createOverlay() {
        // Main Overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'gen-overlay';
        this.overlay.id = 'genOverlay';

        // Animated Splash Loop
        const splashLoop = document.createElement('div');
        splashLoop.className = 'gen-splash-loop';

        for (let i = 0; i < 4; i++) {
            const layer = document.createElement('div');
            layer.className = 'gen-splash-layer';
            layer.innerHTML = `
                <svg viewBox="0 0 60 20" fill="none" stroke="currentColor">
                    <path d="M30 2L5 10L30 18L55 10L30 2Z" />
                </svg>
            `;
            splashLoop.appendChild(layer);
        }
        this.overlay.appendChild(splashLoop);

        // Text Stack
        const textStack = document.createElement('div');
        textStack.className = 'gen-text-stack';

        const status = document.createElement('div');
        status.className = 'gen-status';
        status.textContent = 'Generating...';
        textStack.appendChild(status);

        const quoteContainer = document.createElement('div');
        quoteContainer.className = 'gen-quote-container';
        this.quoteEl = document.createElement('div');
        this.quoteEl.className = 'gen-quote';
        quoteContainer.appendChild(this.quoteEl);
        textStack.appendChild(quoteContainer);

        this.overlay.appendChild(textStack);

        // Noise Layer (Reveal)
        this.noiseLayer = document.createElement('div');
        this.noiseLayer.className = 'noise-reveal-layer';

        const container = document.getElementById('canvasContainer');
        if (container) {
            container.appendChild(this.overlay);
            container.appendChild(this.noiseLayer);
        }
    },

    start() {
        if (!this.overlay) return;
        this.overlay.classList.add('active');
        this.cycleQuote();
        this.quoteInterval = setInterval(() => this.cycleQuote(), 8000);
    },

    cycleQuote() {
        if (!this.quoteEl) return;

        this.quoteEl.classList.remove('visible');

        setTimeout(() => {
            const randomIndex = Math.floor(Math.random() * this.quotes.length);
            this.quoteEl.textContent = this.quotes[randomIndex];
            this.quoteEl.classList.add('visible');
        }, 800);
    },

    stop() {
        if (!this.overlay) return;
        this.overlay.classList.remove('active');
        clearInterval(this.quoteInterval);

        // Trigger Noise Reveal
        this.revealFromNoise();
    },

    revealFromNoise() {
        if (!this.noiseLayer) return;

        this.noiseLayer.classList.remove('noise-revealing');
        void this.noiseLayer.offsetWidth; // force reflow
        this.noiseLayer.classList.add('noise-revealing');
    },

    hide() {
        // Legacy support
        this.stop();
    }
};

const InteractiveFX = {
    init() {
        document.addEventListener('mousemove', (e) => {
            const btns = document.querySelectorAll('.btn, .btn-primary');
            btns.forEach(btn => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                btn.style.setProperty('--mouse-x', `${x}px`);
                btn.style.setProperty('--mouse-y', `${y}px`);
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Splash.init();
    GenerationAnim.init();
    InteractiveFX.init();
});

window.GenerationAnim = GenerationAnim;
window.Splash = Splash;
