/**
 * ASSET EDITOR - Main App
 * Mode switching and event orchestration
 */

const App = {
    currentMode: 'generate',
    sourceFile: null,
    cannyEdges: false,

    init() {
        CanvasStack.init();
        Masking.init();
        this.setMode('generate'); // Set initial mode

        // Mode tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => this.setMode(tab.dataset.mode));
        });

        // Toggles
        document.querySelectorAll('[data-mask]').forEach(btn => {
            btn.addEventListener('click', () => Masking.setMode(btn.dataset.mask));
        });

        document.querySelectorAll('[data-canny]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.cannyEdges = btn.dataset.canny === 'on';
                document.querySelectorAll('[data-canny]').forEach(b => b.classList.toggle('active', b === btn));
            });
        });

        // File upload
        const uploadZone = document.getElementById('uploadZone');
        const imageInput = document.getElementById('imageInput');

        uploadZone.addEventListener('click', () => imageInput.click());
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            if (e.dataTransfer.files[0]) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });
        imageInput.addEventListener('change', () => {
            if (imageInput.files[0]) {
                this.handleFile(imageInput.files[0]);
            }
        });

        // Sliders
        this.bindSlider('layerCount', 'layerCountValue');
        this.bindSlider('editStrength', 'editStrengthValue', v => `${v}%`);
        this.bindSlider('genWidth', 'genWidthValue');
        this.bindSlider('genHeight', 'genHeightValue');
        this.bindSlider('genGuidance', 'genGuidanceValue', v => {
            const val = parseFloat(v);
            this.updateGuidanceHint(val);
            return val.toFixed(1);
        });

        // Action buttons
        document.getElementById('decomposeBtn').addEventListener('click', () => this.decompose());
        document.getElementById('editBtn').addEventListener('click', () => this.applyEdit());
        document.getElementById('generateBtn').addEventListener('click', () => this.generate());

        // Model Picker
        this.initModelPicker();
    },

    initModelPicker() {
        const picker = document.getElementById('modelPicker');
        const trigger = document.getElementById('pickerTrigger');
        const dropdown = document.getElementById('pickerDropdown');

        if (!picker || !trigger) return;

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            picker.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            picker.classList.remove('active');
        });

        dropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        document.querySelectorAll('.btn-picker').forEach(btn => {
            btn.addEventListener('click', async () => {
                const model = btn.dataset.model;
                const isEject = btn.textContent.trim() === 'EJECT';
                await this.executeModelAction(model, isEject, btn);
            });
        });
    },

    async executeModelAction(model, isEject, btn) {
        const vramText = document.querySelector('#vramStatus .vram-text');
        const originalText = btn.textContent;
        const picker = document.getElementById('modelPicker');

        btn.disabled = true;
        btn.textContent = '...';

        try {
            // Close picker immediately for better UX
            picker.classList.remove('active');

            if (isEject) {
                if (vramText) vramText.textContent = `VRAM: Ejecting...`;
                await API.offload();
                this.showStatus('Model ejected to CPU');
            } else {
                if (vramText) vramText.textContent = `VRAM: Loading ${model.toUpperCase()}...`;
                await API.preload(model);
                this.showStatus(`${model.toUpperCase()} energized`);
            }
            await this.checkHealth();
        } catch (err) {
            console.error('[DEUS] Manifold failure:', err);
            this.showStatus('Action failure', 'error');
        } finally {
            btn.disabled = false;
        }
    },

    bindSlider(sliderId, valueId, formatter = v => v) {
        const slider = document.getElementById(sliderId);
        const value = document.getElementById(valueId);
        if (slider && value) {
            slider.addEventListener('input', () => {
                value.textContent = formatter(slider.value);
            });
        }
    },

    setMode(mode) {
        this.currentMode = mode;

        // Update app container for CSS-driven colors
        document.querySelector('.app').dataset.mode = mode;

        // Update tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });

        // Update control panels
        document.querySelectorAll('.mode-controls').forEach(panel => {
            panel.classList.add('hidden');
        });
        document.getElementById(`${mode}Controls`).classList.remove('hidden');

        // Update action buttons
        document.getElementById('generateBtn').classList.toggle('hidden', mode !== 'generate');
        document.getElementById('stylizeBtn').classList.toggle('hidden', mode !== 'stylize');
        document.getElementById('decomposeBtn').classList.toggle('hidden', mode !== 'decompose');
        document.getElementById('editBtn').classList.toggle('hidden', mode !== 'edit');
    },

    handleFile(file) {
        this.sourceFile = file;
        const dropzone = document.getElementById('uploadZone');
        dropzone.innerHTML = `<span class="dropzone-text">✓ ${file.name}</span>`;
    },

    async decompose() {
        if (!this.sourceFile) {
            this.showStatus('No image selected', 'error');
            return;
        }

        const layers = parseInt(document.getElementById('layerCount').value);

        this.showStatus('Decomposing image...', 'loading');
        GenerationAnim.start();

        try {
            const result = await API.decompose(this.sourceFile, layers);

            CanvasStack.clear();

            for (let i = 0; i < result.layers.length; i++) {
                await CanvasStack.addLayer(result.layers[i], i);
            }

            this.showStatus(`Created ${result.count} layers`);

            // Auto-switch to edit mode
            setTimeout(() => this.setMode('edit'), 500);
        } catch (err) {
            console.error('[DEUS] Decompose failure:', err);
            this.showStatus('Deconstruction failed', 'error');
        }
    },

    async applyEdit() {
        const layer = CanvasStack.getSelectedLayer();
        if (!layer) {
            this.showStatus('Select a layer to edit', 'error');
            return;
        }

        const prompt = document.getElementById('editPrompt').value.trim();
        if (!prompt) {
            this.showStatus('Enter an edit prompt', 'error');
            return;
        }

        const strength = parseInt(document.getElementById('editStrength').value) / 100;

        this.showStatus('Editing layer...', 'loading');
        ComparisonSlider.disable(); // Reset previous comparison
        GenerationAnim.start();

        try {
            const imageBlob = await CanvasStack.getLayerBlob(layer.index);
            const maskBlob = Masking.mode === 'manual' ? await Masking.getMaskBlob() : null;
            const useAlphaMask = Masking.mode === 'auto';

            const result = await API.inpaint(imageBlob, maskBlob, prompt, strength, useAlphaMask);

            // Create a new layer for the "after" comparison
            const afterCanvas = await CanvasStack.addLayer(result.image, layer.index + 1);
            ComparisonSlider.enable(afterCanvas);

            this.saveToHistory('edit', prompt, result.image);
            this.showStatus('Edit applied');
        } catch (err) {
            console.error('[DEUS] Edit failure:', err);
            this.showStatus('Edit failed', 'error');
        }
    },

    async generate() {
        const prompt = document.getElementById('genPrompt').value.trim();
        if (!prompt) {
            this.showStatus('Enter a prompt', 'error');
            return;
        }

        const width = parseInt(document.getElementById('genWidth').value);
        const height = parseInt(document.getElementById('genHeight').value);
        const guidance = parseFloat(document.getElementById('genGuidance').value);
        const sampler = document.getElementById('genSampler').value;

        this.showStatus('Generating image...', 'loading');
        ComparisonSlider.disable();
        GenerationAnim.start();

        try {
            const result = await API.txt2img(prompt, width, height, guidance, sampler);

            CanvasStack.clear();
            await CanvasStack.addLayer(result.image, 0);

            this.saveToHistory('generate', prompt, result.image);
            this.showStatus('Image generated');
        } catch (err) {
            console.error('[DEUS] Generation failure:', err);
            this.showStatus('Generation failed', 'error');
        }
    },

    saveToHistory(mode, prompt, imageUrl) {
        const entry = {
            timestamp: new Date().toISOString(),
            mode,
            prompt,
            imageUrl
        };
        console.log('History Entry Saved:', entry);
        // In a real scenario, we'd POST this to /api/history
    },

    updateGuidanceHint(val) {
        const hintEl = document.getElementById('genGuidanceHint');
        if (!hintEl) return;

        let tip = "";
        let desc = "";

        if (val <= 2.0) {
            tip = "Creative:";
            desc = "Model ignores prompt nuance for aesthetics.";
        } else if (val <= 3.5) {
            tip = "Artistic:";
            desc = "High flexibility, flows with lighting.";
        } else if (val <= 5.0) {
            tip = "Balanced:";
            desc = "The Sweet Spot. High adherence & quality.";
        } else if (val <= 7.5) {
            tip = "Literal:";
            desc = "Follows prompt strictly. Can look 'stiff'.";
        } else {
            tip = "Strict:";
            desc = "Extreme adherence. High risk of over-exposure.";
        }

        hintEl.innerHTML = `<span class="guidance-tip">${tip}</span> ${desc}`;
    },

    showStatus(message, type = '') {
        const statusBar = document.getElementById('statusBar');
        statusBar.textContent = message;
        statusBar.className = `status mt-md ${type}`;
        statusBar.classList.remove('hidden');

        if (type !== 'loading') {
            setTimeout(() => statusBar.classList.add('hidden'), 3000);
        }
    },

    async checkHealth() {
        try {
            const health = await API.health();
            const vramText = document.querySelector('#vramStatus .vram-text');
            const vramProgress = document.getElementById('vramProgress');
            const pickerButtons = document.querySelectorAll('.btn-picker');

            if (health.vram) {
                const currentModel = health.vram.current_model;

                // Get friendly name
                let modelInfo = '';
                if (currentModel) {
                    const item = document.querySelector(`.picker-item[data-model="${currentModel}"] .model-name`);
                    const modelLabel = item ? item.textContent : currentModel.toUpperCase();
                    modelInfo = ` | ${modelLabel}`;
                }

                vramText.textContent = `VRAM: ${health.vram.allocated_gb}GB / 16GB${modelInfo}`;

                // Update Progress Bar
                const totalVram = 16.0;
                const percent = Math.min((health.vram.allocated_gb / totalVram) * 100, 100);
                if (vramProgress) {
                    vramProgress.style.width = `${percent}%`;
                }

                pickerButtons.forEach(btn => {
                    const modelId = btn.dataset.model;
                    if (currentModel === modelId) {
                        btn.textContent = 'EJECT';
                        btn.classList.add('btn-active');
                    } else {
                        btn.textContent = 'LOAD';
                        btn.classList.remove('btn-active');
                    }
                });

                if (currentModel) {
                    const item = document.querySelector(`.picker-item[data-model="${currentModel}"] .model-name`);
                    if (item) {
                        document.getElementById('currentModelName').textContent = item.textContent;
                    }
                }
            }
        } catch (err) {
            const vramText = document.querySelector('#vramStatus .vram-text');
            if (vramText) vramText.textContent = 'VRAM: offline';
        }
    },
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', async () => {
    App.init();

    // Check initial health
    await App.checkHealth();

    // Hide splash screen
    const splash = document.getElementById('splash');
    if (splash) {
        // Short delay for aesthetics
        setTimeout(() => splash.classList.add('hidden'), 500);
    }

    // Continue health polling
    setInterval(() => App.checkHealth(), 10000);
});
