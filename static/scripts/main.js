/**
 * ASSET EDITOR - Main Entry
 */
import { AppStore } from './modules/state/index.js';
import { UI } from './modules/ui.js';
import { Models } from './modules/models.js';
import { Generator } from './modules/generator.js';

document.addEventListener('DOMContentLoaded', async () => {
    // AppStore is initialized via index.js (window.AppStore)
    UI.init();
    Models.init();
    Generator.init();

    // Sovereign Boot Ritual: Ensure at least one full splash cycle completes
    if (window.Splash && window.Splash.cycleComplete) {
        console.log("[DEUS] Sovereign Boot Ritual: Awaiting Splash cycle completion...");
        await window.Splash.cycleComplete;
    }

    // Hide Splash with aggressive, high-fidelity transition
    setTimeout(() => {
        const splash = document.getElementById('splash');
        if (splash) splash.classList.add('hidden');
    }, 200); // Tight buffer for snappiness

    console.log("DEUS: System Online. Modules Loaded.");
});
