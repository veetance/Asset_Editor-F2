/**
 * ASSET EDITOR - Canvas Stack
 * Layer rendering and management
 */

const CanvasStack = {
    container: null,
    layers: [],
    selectedIndex: -1,

    init() {
        this.container = document.getElementById('canvasStackWrapper');
    },

    clear() {
        this.container.innerHTML = '';
        this.layers = [];
        this.selectedIndex = -1;
        this.updateLayerList();

        const controls = document.getElementById('focusControls');
        if (controls) controls.classList.add('hidden');
    },

    async addLayer(imageUrl, index) {
        // Show focus controls when first image enters
        if (index === 0) {
            const controls = document.getElementById('focusControls');
            if (controls) controls.classList.remove('hidden');
        }

        const canvas = document.createElement('canvas');
        canvas.id = `layer-${index}`;
        canvas.className = 'layer-canvas';
        canvas.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: ${index};
    `;

        const ctx = canvas.getContext('2d');
        const img = new Image();

        await new Promise((resolve, reject) => {
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;

                // Update container size to match first layer
                if (index === 0) {
                    this.container.style.width = `${img.width}px`;
                    this.container.style.height = `${img.height}px`;
                }

                ctx.drawImage(img, 0, 0);
                resolve();
            };
            img.onerror = reject;
            img.src = imageUrl;
        });

        this.container.appendChild(canvas);

        this.layers.push({
            index,
            url: imageUrl,
            canvas,
            visible: true
        });

        this.updateLayerList();
        return canvas;
    },

    selectLayer(index) {
        this.selectedIndex = index;
        this.updateLayerList();

        // Dispatch event for masking module
        window.dispatchEvent(new CustomEvent('layerSelected', {
            detail: { index, layer: this.layers[index] }
        }));
    },

    toggleVisibility(index) {
        const layer = this.layers[index];
        if (layer) {
            layer.visible = !layer.visible;
            layer.canvas.style.opacity = layer.visible ? '1' : '0';
            this.updateLayerList();
        }
    },

    getSelectedLayer() {
        return this.layers[this.selectedIndex] || null;
    },

    getLayerBlob(index) {
        const layer = this.layers[index];
        if (!layer) return null;

        return new Promise(resolve => {
            layer.canvas.toBlob(resolve, 'image/png');
        });
    },

    updateLayerList() {
        const listEl = document.getElementById('layerList');

        if (this.layers.length === 0) {
            listEl.innerHTML = '<div class="empty-state">EMPTY</div>';
            return;
        }

        listEl.innerHTML = this.layers.map((layer, i) => `
      <div class="layer-item ${i === this.selectedIndex ? 'selected' : ''}" 
           data-index="${i}">
        <img class="layer-thumb" src="${layer.url}" alt="Layer ${i}">
        <span class="layer-name">Layer ${i}</span>
        <button class="layer-toggle ${layer.visible ? 'visible' : ''}" 
                data-toggle="${i}" title="Toggle visibility">
          ${layer.visible ? '👁' : '○'}
        </button>
      </div>
    `).join('');

        // Bind events
        listEl.querySelectorAll('.layer-item').forEach(el => {
            el.addEventListener('click', (e) => {
                if (!e.target.classList.contains('layer-toggle')) {
                    this.selectLayer(parseInt(el.dataset.index));
                }
            });
        });

        listEl.querySelectorAll('.layer-toggle').forEach(el => {
            el.addEventListener('click', () => {
                this.toggleVisibility(parseInt(el.dataset.toggle));
            });
        });
    },

    async replaceLayer(index, imageUrl) {
        const layer = this.layers[index];
        if (!layer) return;

        const img = new Image();
        await new Promise(resolve => {
            img.onload = resolve;
            img.src = imageUrl;
        });

        const ctx = layer.canvas.getContext('2d');
        ctx.clearRect(0, 0, layer.canvas.width, layer.canvas.height);
        ctx.drawImage(img, 0, 0);
        layer.url = imageUrl;

        this.updateLayerList();
    }
};
