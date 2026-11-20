import { describe, expect, it } from "vitest";
import { atom } from "jotai/vanilla";
import { createMathBlocksStore } from "../../frontend/src/core/store";

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
