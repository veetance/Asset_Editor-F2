/**
 * ASSET EDITOR - Generator Logic
 */
import { API } from './api.js';
import { State } from './state.js';

export const Generator = {
    init() {
        document.getElementById('generateBtn').addEventListener('click', () => this.generate());
        document.getElementById('decomposeBtn').addEventListener('click', () => this.decompose());
        document.getElementById('editBtn').addEventListener('click', () => this.edit());
    },

    async generate() {
        const prompt = document.getElementById('genPrompt').value.trim();
        if (!prompt) return State.showStatus('Enter prompt', 'error');
        if (prompt.length < 3 && !prompt.includes(' ')) return State.showStatus('Prompt too short', 'error');

        const width = parseInt(document.getElementById('genWidth').value);
        const height = parseInt(document.getElementById('genHeight').value);
        const guidance = parseFloat(document.getElementById('genGuidance').value);
        const steps = parseInt(document.getElementById('genSteps').value);
        const sampler = document.getElementById('genSampler').dataset.value;
        const scheduler = document.getElementById('genScheduler').dataset.value;
        const vramBudget = State.vramUserLimit || 16.0;

        // Seed Logic
        const seedInput = document.getElementById('genSeed');
        const seedMode = document.getElementById('genSeedMode').dataset.value;
        let seed = parseInt(seedInput.value);

        if (seedMode === 'random') {
            seed = Math.floor(Math.random() * 2147483647);
            seedInput.value = seed;
        } else if (seedMode === 'increment') {
            seed = seed + 1;
            seedInput.value = seed;
        } else if (seedMode === 'decrement') {
            seed = seed - 1;
            seedInput.value = seed;
        }

        State.showStatus('Rendering...', 'loading');

        // Button Feedback
        const btn = document.getElementById('generateBtn');
        const originalText = btn.textContent;
        btn.textContent = 'RENDERING...';
        btn.disabled = true;

        const targetModel = State.loadedModel || 'flux-4b';
        console.log(`[RENDERER] Target: ${targetModel} | Prompt: ${prompt.slice(0, 30)}... | Steps: ${steps} | Seed: ${seed}`);
        if (window.GenerationAnim) window.GenerationAnim.start();

        try {
            const res = await API.txt2img(prompt, width, height, guidance, sampler, scheduler, vramBudget, targetModel, steps, seed);
            if (window.CanvasStack) {
                window.CanvasStack.clear();
                window.CanvasStack.addLayer(res.image, 0);
            }
            State.showStatus(`Rendered using ${res.model || 'FLUX'} (${res.vram_used}GB VRAM)`);
        } catch (e) {
            console.error(e);
            State.showStatus('Render Failed', 'error');
        } finally {
            if (window.GenerationAnim) window.GenerationAnim.stop();
            // Restore Button
            btn.textContent = originalText;
            btn.disabled = false;
        }
    },

    async decompose() {
        if (!State.sourceFile) return State.showStatus('No file', 'error');

        State.showStatus('Decomposing...', 'loading');
        if (window.GenerationAnim) window.GenerationAnim.start();

        try {
            const layers = parseInt(document.getElementById('layerCount').value);
            const res = await API.decompose(State.sourceFile, layers);

            if (window.CanvasStack) {
                window.CanvasStack.clear();
                res.layers.forEach((l, i) => window.CanvasStack.addLayer(l, i));
            }
            State.showStatus(`Decomposed ${res.count} layers`);
            setTimeout(() => State.setMode('edit'), 500);
        } catch (e) {
            console.error(e);
            State.showStatus('Failed', 'error');
        } finally {
            if (window.GenerationAnim) window.GenerationAnim.stop();
        }
    },

    async edit() {
        const prompt = document.getElementById('editPrompt').value.trim();
        if (!prompt) return State.showStatus('No prompt', 'error');

        // Legacy Canvas Interaction
        if (!window.CanvasStack) return;
        const layer = window.CanvasStack.getSelectedLayer();
        if (!layer) return State.showStatus('Select layer', 'error');

        State.showStatus('Editing...', 'loading');
        if (window.GenerationAnim) window.GenerationAnim.start();

        try {
            const blob = await window.CanvasStack.getLayerBlob(layer.index);
            // Masking check
            const maskBlob = (window.Masking && window.Masking.mode === 'manual')
                ? await window.Masking.getMaskBlob() : null;

            const res = await API.inpaint(blob, maskBlob, prompt, 0.75, false);

            window.CanvasStack.addLayer(res.image, layer.index + 1);
            State.showStatus('Edit applied');
        } catch (e) {
            console.error(e);
            State.showStatus('Edit failed', 'error');
        } finally {
            if (window.GenerationAnim) window.GenerationAnim.stop();
        }
    }
};
