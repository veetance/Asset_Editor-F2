/**
 * ASSET EDITOR - State Management
 */
export const State = {
    currentMode: 'generate',
    sourceFile: null,
    cannyEdges: false,
    vramUserLimit: 13, // GB
    loadedModel: null, // Track currently active model identity

    // UI References
    statusBar: null,

    init() {
        this.statusBar = document.getElementById('statusBar');
    },

    setMode(mode) {
        this.currentMode = mode;
        document.querySelector('.app').dataset.mode = mode;

        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });

        document.querySelectorAll('.mode-controls').forEach(panel => {
            panel.classList.add('hidden');
        });
        document.getElementById(`${mode}Controls`).classList.remove('hidden');

        // Toggle Actions
        document.getElementById('generateBtn').classList.toggle('hidden', mode !== 'generate');
        document.getElementById('stylizeBtn').classList.toggle('hidden', mode !== 'stylize');
        document.getElementById('decomposeBtn').classList.toggle('hidden', mode !== 'decompose');
        document.getElementById('editBtn').classList.toggle('hidden', mode !== 'edit');
    },

    showStatus(message, type = '') {
        if (!this.statusBar) return;
        this.statusBar.textContent = message;
        this.statusBar.className = `status mt-md ${type}`;
        this.statusBar.classList.remove('hidden');

        if (type !== 'loading') {
            setTimeout(() => this.statusBar.classList.add('hidden'), 3000);
        }
    }
};
