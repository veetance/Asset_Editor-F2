/**
 * ASSET EDITOR - Selectors
 * Memoized access to state slices.
 */

export const selectState = (state) => state;

export const createSelector = (dependencies, transform) => {
    let lastArgs = [];
    let lastResult = null;

    return (state) => {
        const currentArgs = dependencies.map(dep => dep(state));
        const hasChanged = currentArgs.some((arg, i) => arg !== lastArgs[i]);

        if (hasChanged) {
            lastArgs = currentArgs;
            lastResult = transform(...currentArgs);
        }
        return lastResult;
    };
};

// Mode Selectors
export const selectCurrentMode = state => state.currentMode;
export const selectSourceFile = state => state.sourceFile;
export const selectVramLimit = state => state.vramUserLimit;
export const selectLoadedModel = state => state.loadedModel;
export const selectCanny = state => state.cannyEdges;
