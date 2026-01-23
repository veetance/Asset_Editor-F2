/**
 * ASSET EDITOR - API Client (Module)
 */
export const API = {
    baseUrl: '',

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/api${endpoint}`;
        const response = await fetch(url, options);

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: response.statusText }));
            throw new Error(error.error || 'Request failed');
        }

        return response.json();
    },

    async decompose(imageFile, layers = 4) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('layers', layers);
        formData.append('resolution', 640);

        return this.request('/decompose', { method: 'POST', body: formData });
    },

    async txt2img(prompt, width = 1024, height = 1024, guidance = 0.0, sampler = 'euler', scheduler = 'standard', vramBudget = 16.0, modelVariant = 'flux-4b') {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('width', width);
        formData.append('height', height);
        formData.append('guidance', guidance);
        formData.append('sampler', sampler);
        formData.append('scheduler', scheduler);
        formData.append('vram_budget', vramBudget);
        formData.append('model_variant', modelVariant);

        return this.request('/txt2img', { method: 'POST', body: formData });
    },

    async img2img(imageBlob, prompt, strength = 0.75) {
        const formData = new FormData();
        formData.append('image', imageBlob, 'image.png');
        formData.append('prompt', prompt);
        formData.append('strength', strength);

        return this.request('/img2img', { method: 'POST', body: formData });
    },

    async inpaint(imageBlob, maskBlob, prompt, strength = 0.85, useAlphaMask = false) {
        const formData = new FormData();
        formData.append('image', imageBlob, 'image.png');
        formData.append('prompt', prompt);
        formData.append('strength', strength);
        formData.append('use_alpha_mask', useAlphaMask);
        if (maskBlob) formData.append('mask', maskBlob, 'mask.png');

        return this.request('/inpaint', { method: 'POST', body: formData });
    },

    async health() { return this.request('/health'); },
    async preload(model = 'flux') { return this.request('/preload?model=' + model, { method: 'POST' }); },
    async offload() { return this.request('/offload', { method: 'POST' }); },
    async purge() { return this.request('/purge', { method: 'POST' }); }
};
