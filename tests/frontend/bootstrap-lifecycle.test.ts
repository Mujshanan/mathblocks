import { afterEach, describe, expect, it, vi } from "vitest";
import widgetModule from "../../frontend/src/core/bootstrap";
import type { AnyWidgetModel, ComponentStateEnvelope } from "../../frontend/src/core/model";

class FakeElement {
  children: FakeElement[] = [];
  className = "";
  dataset: Record<string, string> = {};
  value = "";
  textContent = "";
  spellcheck = true;
  type = "";
  attributes = new Map<string, string>();
  listeners = new Map<string, Set<EventListener>>();
  classes = new Set<string>();

  classList = {
    add: (name: string) => this.classes.add(name),
    remove: (name: string) => this.classes.delete(name),
    contains: (name: string) => this.classes.has(name),
  };

  append(...children: FakeElement[]): void {
    this.children.push(...children);
  }

  replaceChildren(...children: FakeElement[]): void {
    this.children = [...children];
  }

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }

  addEventListener(type: string, listener: EventListener): void {
    const listeners = this.listeners.get(type) ?? new Set<EventListener>();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }

  removeEventListener(type: string, listener: EventListener): void {
    this.listeners.get(type)?.delete(listener);
  }
}

class SharedWidgetModel implements AnyWidgetModel {
  private listeners = new Set<() => void>();

  constructor(public state: ComponentStateEnvelope) {}

  get(name: string): unknown {
    return name === "state" ? this.state : undefined;
  }

  set(name: string, value: unknown): void {
    if (name !== "state") return;
    this.state = value as ComponentStateEnvelope;
    for (const listener of this.listeners) listener();
  }

  save_changes(): void {}

  on(event: string, callback: () => void): void {
    if (event === "change:state") this.listeners.add(callback);
  }

  off(event: string, callback: () => void): void {
    if (event === "change:state") this.listeners.delete(callback);
  }

  listenerCount(): number {
    return this.listeners.size;
  }
}

function editorValue(root: FakeElement): string {
  return root.children[0]?.children[2]?.value ?? "";
}

function mountView(
  root: FakeElement,
  model: AnyWidgetModel,
  controller: AbortController,
): void {
  widgetModule.render({
    el: root as unknown as HTMLElement,
    model,
    signal: controller.signal,
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("AnyWidget frontend view lifecycle", () => {
  it("shares one model across views and cleans up independently on abort/reconnect", () => {
    vi.stubGlobal("document", {
      createElement: () => new FakeElement(),
    } as unknown as Document);

    const model = new SharedWidgetModel({
      schema_version: 1,
      revision: 0,
      actor: "python",
      data: { value: "initial" },
    });

    const firstRoot = new FakeElement();
    const secondRoot = new FakeElement();
    const firstController = new AbortController();
    const secondController = new AbortController();

    mountView(firstRoot, model, firstController);
    mountView(secondRoot, model, secondController);

    expect(JSON.parse(editorValue(firstRoot))).toEqual({ value: "initial" });
    expect(editorValue(secondRoot)).toBe(editorValue(firstRoot));
    expect(model.listenerCount()).toBe(2);

    model.set("state", {
      schema_version: 1,
      revision: 1,
      actor: "python",
      data: { value: "updated from kernel" },
    });

    expect(JSON.parse(editorValue(firstRoot))).toEqual({ value: "updated from kernel" });
    expect(editorValue(secondRoot)).toBe(editorValue(firstRoot));

    firstController.abort();
    expect(firstRoot.children).toHaveLength(0);
    expect(firstRoot.classList.contains("mathblocks-root")).toBe(false);
    expect(model.listenerCount()).toBe(1);

    model.set("state", {
      schema_version: 1,
      revision: 2,
      actor: "python",
      data: { value: "second view remains active" },
    });

    expect(firstRoot.children).toHaveLength(0);
    expect(JSON.parse(editorValue(secondRoot))).toEqual({
      value: "second view remains active",
    });

    const reconnectedRoot = new FakeElement();
    const reconnectedController = new AbortController();
    mountView(reconnectedRoot, model, reconnectedController);

    expect(JSON.parse(editorValue(reconnectedRoot))).toEqual({
      value: "second view remains active",
    });
    expect(model.listenerCount()).toBe(2);

    secondController.abort();
    reconnectedController.abort();

    expect(secondRoot.children).toHaveLength(0);
    expect(reconnectedRoot.children).toHaveLength(0);
    expect(model.listenerCount()).toBe(0);
    expect(model.state.data).toEqual({ value: "second view remains active" });
  });
});
