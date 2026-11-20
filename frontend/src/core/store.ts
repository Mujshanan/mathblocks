import { atom, createStore } from "jotai/vanilla";

/** Per-widget-instance state store; never share mutable stores across instances. */
export const createMathBlocksStore = () => createStore();

export { atom };
