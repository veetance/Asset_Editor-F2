/**
 * ASSET EDITOR - Main App
 * Mode switching and event orchestration
 */

const App = {
    currentMode: 'generate',
    sourceFile: null,
    cannyEdges: false,

    vramUserLimit: 8, // Default budget in GB

    init() {
        CanvasStack.init();
        Masking.init();
        this.setMode('generate');

        // VRAM Governor Drag Logic
        const governor = document.getElementById('vramGovernor');
        if (governor) {
            governor.addEventListener('mousedown', (e) => {
                const moveHandler = (moveEvent) => {
                    const rect = governor.getBoundingClientRect();
                    const x = Math.max(0, Math.min(moveEvent.clientX - rect.left, rect.width));
                    const pct = x / rect.width;
                    this.vramUserLimit = pct * 16.0; // Assuming 16GB total
                    this.checkHealth(); // Instant visual update
                };

                const upHandler = () => {
                    window.removeEventListener('mousemove', moveHandler);
                    window.removeEventListener('mouseup', upHandler);
                };

                window.addEventListener('mousemove', moveHandler);
                window.addEventListener('mouseup', upHandler);
                moveHandler(e);
            });
        }

        // Batch Size Slider
        const batchSlider = document.getElementById('genBatchSize');
        const batchVal = document.getElementById('genBatchSizeValue');
        if (batchSlider && batchVal) {
            batchSlider.addEventListener('input', () => {
                batchVal.textContent = batchSlider.value;
            });
        }

        // Guidance Chip Logic
        const guidanceSlider = document.getElementById('genGuidance');
        const chip = document.getElementById('canvasChip');
        const chipVal = document.getElementById('chipValue');

        if (guidanceSlider && chip) {
            const showChip = () => {
                const val = parseFloat(guidanceSlider.value);
                chip.classList.remove('hidden');
                chipVal.textContent = val.toFixed(1);
                this.updateGuidanceHint(val);
            };
            const hideChip = () => {
                chip.classList.add('hidden');
            };

            guidanceSlider.addEventListener('input', showChip);
            guidanceSlider.addEventListener('mouseenter', showChip);
            guidanceSlider.addEventListener('mouseleave', hideChip);
        }

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

        // Dropdowns
        this.initModelPicker();
        this.initCustomSelects();
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

    initCustomSelects() {
        const selects = document.querySelectorAll('.custom-select');

        selects.forEach(select => {
            const trigger = select.querySelector('.select-trigger');
            const current = select.querySelector('.select-current');
            const options = select.querySelectorAll('.select-option');

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();

                // Close others
                selects.forEach(s => { if (s !== select) s.classList.remove('active', 'drop-up'); });

                const isActive = select.classList.contains('active');
                if (!isActive) {
                    // Close others
                    selects.forEach(s => s.classList.remove('active'));
                    select.classList.add('active');

                    // Auto-Scroll Protocol: Ensure the expanded manifold is centered or aligned to bottom
                    setTimeout(() => {
                        const dropdown = select.querySelector('.select-dropdown');
                        dropdown.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 100); // Wait for grid expansion to begin
                } else {
                    select.classList.remove('active');
                }
            });

            options.forEach(option => {
                option.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const value = option.dataset.value;
                    const text = option.textContent;

                    // Update State
                    select.dataset.value = value;
                    current.textContent = text;

                    // Update UI
                    options.forEach(opt => opt.classList.remove('active'));
                    option.classList.add('active');
                    select.classList.remove('active');

                    console.log(`[DEUS] Select Update: ${select.id} -> ${value}`);
                });
            });
        });

        document.addEventListener('click', () => {
            selects.forEach(s => s.classList.remove('active'));
        });
    },

    async executeModelAction(model, isEject, btn) {
        const picker = document.getElementById('modelPicker');
        const headerBar = document.getElementById('headerLoadingBar');
        const globalBar = document.getElementById('globalLoadingBar');

        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = '...';

        // Prepare bars (2px top indicators)
        [headerBar, globalBar].forEach(bar => {
            if (!bar) return;
            bar.classList.remove('complete', 'active', 'offload');
            // Trigger reflow to restart transition
            void bar.offsetWidth;

            if (isEject) {
                bar.classList.add('offload');
            } else {
                bar.classList.add('active');
            }
        });

        try {
            // Close picker immediately for better UX
            picker.classList.remove('active');

            if (isEject) {
                await API.offload();
                this.showStatus('Model ejected to CPU');
            } else {
                await API.preload(model);
                this.showStatus(`${model.toUpperCase()} energized`);
            }
            await this.checkHealth();
        } catch (err) {
            console.error('[DEUS] Manifold failure:', err);
            this.showStatus('Action failure', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;

            [headerBar, globalBar].forEach(bar => {
                if (!bar) return;
                bar.classList.remove('active', 'offload');
                bar.classList.add('complete');
                setTimeout(() => {
                    bar.classList.remove('complete');
                    bar.style.width = ''; // Clear inline style
                }, 500);
            });
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
        const sampler = document.getElementById('genSampler').dataset.value;

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
        const hintEl = document.getElementById('chipDesc');
        if (!hintEl) return;

        let tip = "";
        let desc = "";

        if (val === 0) {
            tip = "Schnell Optimized:";
            desc = "Minimizes artifacting on distilled models.";
        } else if (val <= 2.0) {
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
            const vramVal = document.getElementById('vramValue');
            const ramVal = document.getElementById('ramValue');
            const cpuVal = document.getElementById('cpuValue');

            const vramBar = document.getElementById('vramProgress');
            const ramBar = document.getElementById('ramProgress');
            const cpuBar = document.getElementById('cpuProgress');
            const pickerButtons = document.querySelectorAll('.btn-picker');

            if (health.vram) {
                const currentModel = health.vram.current_model;
                const totalVramGb = health.vram.total_gb || 16.0;
                const totalRamGb = 32.0;

                const currentVram = health.vram.allocated_gb || 0;
                const currentRam = health.vram.ram_used_gb || 0;
                const currentCpu = health.vram.cpu_percent || 0;

                // Priority: Display either real-time allocated OR the user's manual limit
                const vramDisplay = this.vramUserLimit || currentVram;

                if (vramVal) vramVal.textContent = `${vramDisplay.toFixed(0)}GB`;
                if (ramVal) ramVal.textContent = `${currentRam.toFixed(0)}GB`;
                if (cpuVal) cpuVal.textContent = `${Math.round(currentCpu)}%`;

                if (vramBar) {
                    const vramPct = Math.min((vramDisplay / totalVramGb) * 100, 100);
                    vramBar.style.width = `${vramPct}%`;
                }
                if (ramBar) {
                    const ramPct = Math.min((currentRam / totalRamGb) * 100, 100);
                    ramBar.style.width = `${ramPct}%`;
                }
                if (cpuBar) {
                    cpuBar.style.width = `${currentCpu}%`;
                }

                // Update Picker Buttons and Eject Icons
                // Update Picker Buttons and Eject Icons
                const currentModelSpan = document.getElementById('currentModelName');
                // Fallback to raw ID or 'Choose Model' if no button match logic works
                let activeModelName = currentModel ? currentModel.toUpperCase() : 'MODEL';

                console.log(`[DEUS] Health Check - Current Model: ${currentModel}`);

                pickerButtons.forEach(btn => {
                    const modelId = btn.dataset.model;
                    const pickerItem = btn.closest('.picker-item');
                    const ejectIcon = pickerItem?.querySelector('.eject-icon');
                    // Get model name from the span
                    const modelName = pickerItem.querySelector('span:first-child').textContent;

                    if (currentModel === modelId) {
                        console.log(`[DEUS] Match Found: ${modelId}`);
                        btn.textContent = 'EJECT';
                        btn.classList.add('btn-active');
                        pickerItem?.classList.add('loaded');
                        ejectIcon?.classList.remove('hidden');
                        activeModelName = modelName; // Capture active name
                    } else {
                        btn.textContent = 'LOAD';
                        btn.classList.remove('btn-active');
                        pickerItem?.classList.remove('loaded');
                        ejectIcon?.classList.add('hidden');
                    }
                });

                // Update the main trigger text
                if (currentModelSpan && activeModelName) {
                    currentModelSpan.textContent = activeModelName;
                }

                // Update header model name
                if (currentModel) {
                    const item = document.querySelector(`.picker-item[data-model="${currentModel}"] .model-name`);
                    if (item) document.getElementById('currentModelName').textContent = item.textContent;
                } else {
                    document.getElementById('currentModelName').textContent = 'Model';
                }
            }
        } catch (err) {
            console.error('[DEUS] Health check failure:', err);
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
