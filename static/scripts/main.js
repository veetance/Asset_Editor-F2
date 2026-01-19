/**
 * ASSET EDITOR - Main Entry
 */
import { State } from './modules/state.js';
import { UI } from './modules/ui.js';
import { Models } from './modules/models.js';
import { Generator } from './modules/generator.js';

document.addEventListener('DOMContentLoaded', () => {
    State.init();
    UI.init();
    Models.init();
    Generator.init();

    // Hide Splash
    setTimeout(() => {
        const splash = document.getElementById('splash');
        if (splash) splash.classList.add('hidden');
    }, 500);

    console.log("DEUS: System Online. Modules Loaded.");
});
