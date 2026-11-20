import "../src/index";
import { renderMathBlocks } from "../src/core/bootstrap";
import type { AnyWidgetModel } from "../src/core/model";

class LocalModel implements AnyWidgetModel {
  private values: Record<string, unknown> = {
    state: {
      schema_version: 1,
      revision: 0,
      actor: "python",
      data: {
        component: "math",
        value: "\\sigma = \\frac{P}{A}",
        label: "Normal stress",
      },
    },
  };
  private listeners = new Map<string, Set<() => void>>();

  get(name: string): unknown { return this.values[name]; }

  set(name: string, value: unknown): void {
    this.values[name] = value;
    for (const listener of this.listeners.get(`change:${name}`) ?? []) listener();
  }

  save_changes(): void {
    // The local playground has no Python kernel to receive this update.
  }

  on(event: string, callback: () => void): void {
    const listeners = this.listeners.get(event) ?? new Set<() => void>();
    listeners.add(callback);
    this.listeners.set(event, listeners);
  }

  off(event: string, callback: () => void): void {
    this.listeners.get(event)?.delete(callback);
  }
}

const root = document.querySelector<HTMLElement>("#app");
if (root) {
  const cleanup = renderMathBlocks(root, new LocalModel());
  if (import.meta.hot) import.meta.hot.dispose(cleanup);
}
