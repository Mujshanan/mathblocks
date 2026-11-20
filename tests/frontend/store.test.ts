import { describe, expect, it } from "vitest";
import { atom } from "jotai/vanilla";
import { createMathBlocksStore } from "../../frontend/src/core/store";
import {
  attachStateSync,
  commitState,
  compareStateVersions,
  readStateEnvelope,
} from "../../frontend/src/core/synchronization";
import type { AnyWidgetModel, ComponentStateEnvelope } from "../../frontend/src/core/model";

class FakeModel implements AnyWidgetModel {
  private listeners = new Map<string, Set<() => void>>();
  private values: Record<string, unknown>;
  saveCount = 0;

  constructor(initial: ComponentStateEnvelope) {
    this.values = { state: initial };
  }

  get(name: string): unknown {
    return this.values[name];
  }

  set(name: string, value: unknown): void {
    this.values[name] = value;
    for (const listener of this.listeners.get(`change:${name}`) ?? []) {
      listener();
    }
  }

  save_changes(): void {
    this.saveCount += 1;
  }

  on(event: string, callback: () => void): void {
    const listeners = this.listeners.get(event) ?? new Set<() => void>();
    listeners.add(callback);
    this.listeners.set(event, listeners);
  }

  off(event: string, callback: () => void): void {
    this.listeners.get(event)?.delete(callback);
  }

  listenerCount(event: string): number {
    return this.listeners.get(event)?.size ?? 0;
  }
}

const initialState: ComponentStateEnvelope = {
  schema_version: 1,
  revision: 0,
  actor: "python",
  data: { value: 1 },
};

describe("MathBlocks state store", () => {
  it("keeps state isolated between component instances", () => {
    const countAtom = atom(0);
    const first = createMathBlocksStore();
    const second = createMathBlocksStore();

    first.set(countAtom, 3);

    expect(first.get(countAtom)).toBe(3);
    expect(second.get(countAtom)).toBe(0);
  });
});

describe("AnyWidget state synchronization", () => {
  it("publishes initial state and receives Python-originated updates", () => {
    const model = new FakeModel(initialState);
    const received: number[] = [];
    const dispose = attachStateSync(model, (data) => {
      received.push(data.value as number);
    });

    model.set("state", {
      schema_version: 1,
      revision: 1,
      actor: "python",
      data: { value: 7 },
    });

    expect(received).toEqual([1, 7]);
    dispose();
  });

  it("commits frontend changes as a new revision and saves them", () => {
    const model = new FakeModel(initialState);

    const next = commitState(model, { value: 2 }, "view:test");

    expect(next).toEqual({
      schema_version: 1,
      revision: 1,
      actor: "view:test",
      data: { value: 2 },
    });
    expect(readStateEnvelope(model.get("state"))).toEqual(next);
    expect(model.saveCount).toBe(1);
  });

  it("notifies all active views attached to the same widget model", () => {
    const model = new FakeModel(initialState);
    const first: number[] = [];
    const second: number[] = [];
    const disposeFirst = attachStateSync(model, (data) => first.push(data.value as number));
    const disposeSecond = attachStateSync(model, (data) => second.push(data.value as number));

    commitState(model, { value: 9 }, "view:writer");

    expect(first).toEqual([1, 9]);
    expect(second).toEqual([1, 9]);

    disposeFirst();
    expect(model.listenerCount("change:state")).toBe(1);
    disposeSecond();
    expect(model.listenerCount("change:state")).toBe(0);
  });

  it("stops delivering updates after deterministic cleanup", () => {
    const model = new FakeModel(initialState);
    const received: number[] = [];
    const dispose = attachStateSync(model, (data) => {
      received.push(data.value as number);
    });

    dispose();
    model.set("state", {
      schema_version: 1,
      revision: 1,
      actor: "python",
      data: { value: 4 },
    });

    expect(received).toEqual([1]);
    expect(model.listenerCount("change:state")).toBe(0);
  });

  it("rejects unsupported or malformed state envelopes", () => {
    expect(() => readStateEnvelope({ schema_version: 2 })).toThrow(
      "Invalid or unsupported MathBlocks state envelope",
    );
  });

  it("resolves equal-revision conflicts deterministically with Python priority", () => {
    const python: ComponentStateEnvelope = {
      schema_version: 1,
      revision: 3,
      actor: "python",
      data: {},
    };
    const view: ComponentStateEnvelope = {
      schema_version: 1,
      revision: 3,
      actor: "view:z",
      data: {},
    };

    expect(compareStateVersions(python, view)).toBeGreaterThan(0);
    expect(compareStateVersions(view, python)).toBeLessThan(0);
  });
});
