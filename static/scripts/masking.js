/**
 * ASSET EDITOR - Masking Module
 * Auto (alpha) and Manual (brush) mask modes
 */

const Masking = {
    mode: 'auto', // 'auto' | 'manual'
    maskCanvas: null,
    maskCtx: null,
    brushSize: 30,
    isDrawing: false,

    init() {
        this.bindEvents();
    },

    bindEvents() {
        // Mode toggle
        document.querySelectorAll('[data-mask]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setMode(btn.dataset.mask);
                document.querySelectorAll('[data-mask]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Brush size slider
        const brushSlider = document.getElementById('brushSize');
        const brushValue = document.getElementById('brushSizeValue');
        if (brushSlider) {
            brushSlider.addEventListener('input', () => {
                this.brushSize = parseInt(brushSlider.value);
                brushValue.textContent = this.brushSize;
            });
        }

        // Clear mask button
        const clearBtn = document.getElementById('clearMaskBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearMask());
        }

        // Listen for layer selection
        window.addEventListener('layerSelected', (e) => {
            this.onLayerSelected(e.detail);
        });
    },

    setMode(mode) {
        this.mode = mode;
        const brushControls = document.getElementById('brushControls');

        if (mode === 'manual') {
            brushControls.classList.remove('hidden');
            this.enableDrawing();
        } else {
            brushControls.classList.add('hidden');
            this.disableDrawing();
        }
    },

    onLayerSelected(detail) {
        if (this.mode === 'manual' && detail.layer) {
            this.createMaskCanvas(detail.layer.canvas);
        }
    },

    createMaskCanvas(sourceCanvas) {
        // Remove existing mask canvas
        if (this.maskCanvas) {
            this.maskCanvas.remove();
        }

        // Create new mask canvas overlaying the source
        this.maskCanvas = document.createElement('canvas');
        this.maskCanvas.id = 'mask-canvas';
        this.maskCanvas.width = sourceCanvas.width;
        this.maskCanvas.height = sourceCanvas.height;
        this.maskCanvas.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1000;
      cursor: crosshair;
    `;

        this.maskCtx = this.maskCanvas.getContext('2d');
        this.maskCtx.fillStyle = 'rgba(255, 0, 0, 0.4)';

        document.getElementById('canvasContainer').appendChild(this.maskCanvas);
        this.enableDrawing();
    },

    enableDrawing() {
        if (!this.maskCanvas) return;

        this.maskCanvas.addEventListener('mousedown', this.startDraw.bind(this));
        this.maskCanvas.addEventListener('mousemove', this.draw.bind(this));
        this.maskCanvas.addEventListener('mouseup', this.stopDraw.bind(this));
        this.maskCanvas.addEventListener('mouseleave', this.stopDraw.bind(this));
    },

    disableDrawing() {
        if (this.maskCanvas) {
            this.maskCanvas.remove();
            this.maskCanvas = null;
            this.maskCtx = null;
        }
    },

    startDraw(e) {
        this.isDrawing = true;
        this.draw(e);
    },

    draw(e) {
        if (!this.isDrawing || !this.maskCtx) return;

        const rect = this.maskCanvas.getBoundingClientRect();
        const scaleX = this.maskCanvas.width / rect.width;
        const scaleY = this.maskCanvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;

        this.maskCtx.beginPath();
        this.maskCtx.arc(x, y, this.brushSize * scaleX, 0, Math.PI * 2);
        this.maskCtx.fill();
    },

    stopDraw() {
        this.isDrawing = false;
    },

    clearMask() {
        if (this.maskCtx) {
            this.maskCtx.clearRect(0, 0, this.maskCanvas.width, this.maskCanvas.height);
        }
    },

    getMaskBlob() {
        return new Promise(resolve => {
            if (!this.maskCanvas) {
                resolve(null);
                return;
            }

            // Convert red overlay to black/white mask
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = this.maskCanvas.width;
            tempCanvas.height = this.maskCanvas.height;
            const tempCtx = tempCanvas.getContext('2d');

            // Fill with black (areas to keep)
            tempCtx.fillStyle = '#000000';
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

            // Get painted areas and make them white (areas to inpaint)
            const imageData = this.maskCtx.getImageData(0, 0, this.maskCanvas.width, this.maskCanvas.height);
            const maskData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);

            for (let i = 0; i < imageData.data.length; i += 4) {
                if (imageData.data[i + 3] > 0) { // If pixel has alpha (was painted)
                    maskData.data[i] = 255;     // R
                    maskData.data[i + 1] = 255; // G
                    maskData.data[i + 2] = 255; // B
                    maskData.data[i + 3] = 255; // A
                }
            }

            tempCtx.putImageData(maskData, 0, 0);
            tempCanvas.toBlob(resolve, 'image/png');
        });
    },

    async getAutoMaskFromLayer(layerIndex) {
        // For auto mode, the mask comes from the layer's alpha channel
        // The backend handles this - we just need to send use_alpha_mask=true
        return null;
    }
};
