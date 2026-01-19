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

        document.querySelectorAll('.btn-picker').forEach(btn => {
            btn.addEventListener('click', async () => {
                const model = btn.dataset.model;
                const isEject = btn.textContent.trim() === 'EJECT';
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
        // 1. Stats Update
        if (health) {
            const guiVram = State.vramUserLimit;
            // The "Cheat": If user set a limit (guiVram > 0), we display THAT on the purple bar.
            // Otherwise we show real usage.
            // Currently State.vramUserLimit defaults to 8. So we always show the Governor?
            // Yes, user requested "use the value to know what to allocate".

            // Only update VRAM bar if NOT dragging (Drag handles itself in UI.js)
            // Actually, UI.js updates DOM instantly not State? No it updates State too.
            // To prevent WS from jittering the bar while dragging, we could check a drag flag,
            // but the WS pushes data... 
            // SIMPLIFICATION: If we are in "Governor Mode", the bar is purely the setting.
            // Real usage is effectively hidden or we map it differently.
            // For now, let's respect the User Limit as the primary display for the main bar.

            // document.getElementById('vramValue').textContent = ... 
            // NOTE: UI.js handles this during drag. We only update if `guiVram` hasn't changed?
            // Or better: We only update CPU/RAM here, and let VRAM be static User Setting?

            // Let's update RAM/CPU freely
            const ram = health.ram_used_gb || 0;
            const cpu = health.cpu_percent || 0;

            document.getElementById('ramValue').textContent = `${ram.toFixed(0)}GB`;
            document.getElementById('cpuValue').textContent = `${Math.round(cpu)}%`;

            document.getElementById('ramProgress').style.width = `${Math.min((ram / 32) * 100, 100)}%`;
            document.getElementById('cpuProgress').style.width = `${cpu}%`;

            // 2. BUTTON SYNC FIX
            const current = health.current_model;
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
        document.querySelectorAll('.btn-picker').forEach(btn => {
            const modelId = btn.dataset.model;
            const item = btn.closest('.picker-item');

            if (currentModel === modelId) {
                btn.textContent = 'EJECT';
                btn.classList.add('btn-active');
                if (item) item.classList.add('loaded');
                item?.querySelector('.eject-icon')?.classList.remove('hidden');
                document.getElementById('currentModelName').textContent = item.querySelector('.model-name').textContent;
            } else {
                btn.textContent = 'LOAD';
                btn.classList.remove('btn-active');
                if (item) item.classList.remove('loaded');
                item?.querySelector('.eject-icon')?.classList.add('hidden');
            }
        });
        if (!currentModel) document.getElementById('currentModelName').textContent = 'MODEL';
    }
};
