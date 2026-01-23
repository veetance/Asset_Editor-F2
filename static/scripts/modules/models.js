/**
 * ASSET EDITOR - Model Logic & Health
 */
import { API } from './api.js';
import { State } from './state.js';

export const Models = {
    init() {
        this.initPicker();
        this.connectWS();
    },

    initPicker() {
        const picker = document.getElementById('modelPicker');
        const trigger = document.getElementById('pickerTrigger');
        const dropdown = document.getElementById('pickerDropdown');
        if (!picker) return;

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            picker.classList.toggle('active');
        });
        document.addEventListener('click', () => picker.classList.remove('active'));
        dropdown.addEventListener('click', e => e.stopPropagation());

        document.querySelectorAll('.picker-item').forEach(item => {
            item.addEventListener('click', async (e) => {
                // Ignore if clicking the button (it has its own listener)
                if (e.target.classList.contains('btn-picker')) return;

                const btn = item.querySelector('.btn-picker');
                if (!btn) return;

                const model = btn.dataset.model;
                const isEject = btn.textContent.trim() === 'EJECT';
                console.log(`[UI] Item Clicked: ${model} (Action: ${isEject ? 'Eject' : 'Load'})`);
                await this.executeAction(model, isEject, btn);
            });
        });

        document.querySelectorAll('.btn-picker').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation(); // Stop row click from firing
                const model = btn.dataset.model;
                const isEject = btn.textContent.trim() === 'EJECT';
                console.log(`[UI] Button Clicked: ${model} (Action: ${isEject ? 'Eject' : 'Load'})`);
                await this.executeAction(model, isEject, btn);
            });
        });
    },

    connectWS() {
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${proto}//${window.location.host}/ws/telemetry`);

        ws.onopen = () => {
            console.log("[DEUS] Telemetry Socket: LOCKED");
        };

        ws.onmessage = (event) => {
            try {
                const health = JSON.parse(event.data);
                this.updateInterface(health);
            } catch (e) { console.error(e); }
        };

        ws.onclose = () => {
            console.warn("[DEUS] Socket Lost. Reconnecting...");
            setTimeout(() => this.connectWS(), 2000);
        };
    },

    updateInterface(health) {
        if (health) {
            // Stats Update
            const ram = health.ram_used_gb || 0;
            const ramTotal = health.ram_total_gb || 64;
            const vramTotal = health.total_gb || 16;
            const cpu = health.cpu_percent || 0;

            document.getElementById('ramValue').textContent = `${ram.toFixed(1)}GB`;
            document.getElementById('cpuValue').textContent = `${Math.round(cpu)}%`;

            // Labelling
            const ramLabel = document.getElementById('totalRamLabel');
            if (ramLabel) ramLabel.textContent = `${ramTotal.toFixed(0)}GB`;
            const vramLabel = document.getElementById('totalVramLabel');
            if (vramLabel) vramLabel.textContent = `${vramTotal.toFixed(0)}GB`;

            // RAM Bar: Calculate based on real total (64GB)
            document.getElementById('ramProgress').style.width = `${Math.min((ram / ramTotal) * 100, 100)}%`;
            document.getElementById('cpuProgress').style.width = `${cpu}%`;

            // BUTTON SYNC
            const current = health.model;
            this.syncButtons(current);
        }
    },

    async executeAction(model, isEject, btn) {
        btn.disabled = true;
        btn.textContent = '...';

        const bars = [document.getElementById('headerLoadingBar'), document.getElementById('globalLoadingBar')];
        bars.forEach(b => { if (b) b.className = isEject ? 'header-loading-bar offload' : 'header-loading-bar active'; });

        try {
            document.getElementById('modelPicker').classList.remove('active');
            if (isEject) {
                await API.offload();
                State.showStatus('Model ejected');
                this.syncButtons(null);  // Immediate sync - no model loaded
            } else {
                const result = await API.preload(model);
                State.showStatus(`${model.toUpperCase()} energized`);
                this.syncButtons(result.model || model);  // Immediate sync with loaded model
            }
        } catch (e) {
            console.error(e);
            State.showStatus('Action Failed', 'error');
        } finally {
            btn.disabled = false;
            bars.forEach(b => b.className = 'header-loading-bar complete');
        }
    },

    syncButtons(currentModel) {
        const picker = document.getElementById('modelPicker');
        const headerName = document.getElementById('currentModelName');

        // Update Global State Identity
        if (currentModel !== 'loading...') {
            State.loadedModel = currentModel;
        }

        // If loading, don't reset button texts to avoid flicker
        if (currentModel === 'loading...') return;

        document.querySelectorAll('.btn-picker').forEach(btn => {
            const modelId = btn.dataset.model;
            const item = btn.closest('.picker-item');

            if (currentModel === modelId) {
                btn.textContent = 'EJECT';
                btn.classList.add('btn-active');
                if (item) {
                    item.classList.add('loaded');
                    item.querySelector('.eject-icon')?.classList.remove('hidden');
                    headerName.textContent = item.querySelector('.model-name').textContent;
                }
            } else {
                btn.textContent = 'LOAD';
                btn.classList.remove('btn-active');
                if (item) {
                    item.classList.remove('loaded');
                    item.querySelector('.eject-icon')?.classList.add('hidden');
                }
            }
        });

        if (!currentModel) headerName.textContent = 'MODEL';
    }
};
