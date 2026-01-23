/**
 * ASSET EDITOR - Reducers
 * Pure functions for state transitions.
 */

export const rootReducer = (state, action) => {
    switch (action.type) {
        case 'SET_MODE':
            return { ...state, currentMode: action.payload };

        case 'SET_SOURCE_FILE':
            return { ...state, sourceFile: action.payload };

        case 'UPDATE_VRAM_LIMIT':
            return { ...state, vramUserLimit: action.payload };

        case 'SET_LOADED_MODEL':
            return { ...state, loadedModel: action.payload };

        case 'SET_CANNY':
            return { ...state, cannyEdges: action.payload };

        case 'UPDATE_GUIDANCE_SCALE':
            return { ...state, guidanceScale: Number(action.payload) };

        default:
            return state;
    }
};

export const initialState = {
    currentMode: 'generate',
    sourceFile: null,
    cannyEdges: false,
    vramUserLimit: 8,
    loadedModel: null,
    guidanceScale: 3.5, // FLUX.2 Klein Distilled Sweet Spot
    inferenceSteps: 20
};
