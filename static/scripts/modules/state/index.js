/**
 * ASSET EDITOR - Store Singleton
 */
import { createStore } from './store.js';
import { rootReducer, initialState } from './reducers.js';

export const AppStore = createStore(rootReducer, initialState);

// Attach to window for global access (DBS-CA Pattern)
window.AppStore = AppStore;
