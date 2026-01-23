/**
 * ASSET EDITOR - State Engine (VSE)
 * Pure JS Implementation of the Flux pattern.
 */

export const createStore = (reducer, initialState) => {
    let state = initialState;
    const listeners = new Set();

    const getState = () => state;

    const dispatch = (action) => {
        const nextState = reducer(state, action);
        if (nextState !== state) {
            state = nextState;
            listeners.forEach(listener => listener(state));
        }
    };

    const subscribe = (listener) => {
        listeners.add(listener);
        return () => listeners.delete(listener);
    };

    return { getState, dispatch, subscribe };
};
