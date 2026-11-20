import {
  attachStateSync,
  commitState,
  createViewActorId,
} from "./synchronization";
import type { AnyWidgetModel, JsonObject } from "./model";
import { mountMath } from "../components/math";
import { mountText } from "../components/text";
import { mountResult } from "../components/result";
import { mountMatrix } from "../components/matrix";
import { mountVector } from "../components/vector";
import { mountGraph } from "../components/graph";
import { mountDiagram } from "../components/diagram";

export function renderMathBlocks(root: HTMLElement, model: AnyWidgetModel): () => void {
  root.classList.add("mathblocks-root");
  root.dataset.mathblocksReady = "true";
  const actor = createViewActorId();
  let currentData: JsonObject = {};
  let localCommitInProgress = false;
  let cleanupComponent: (() => void) | undefined;

  const publish = (next: JsonObject): void => {
    currentData = next;
    localCommitInProgress = true;
    try { commitState(model, next, actor); }
    finally { localCommitInProgress = false; }
  };

  const renderComponent = (data: JsonObject): void => {
    cleanupComponent?.();
    cleanupComponent = undefined;
    currentData = data;
    const label = stringValue(data.label);
    const component = data.component;

    if (component === "math") {
      cleanupComponent = mountMath(root, {
        value: stringValue(data.value) ?? "",
        readOnly: data.read_only === true,
        label,
        onChange: (value) => publish({ ...currentData, value } as JsonObject),
      }).destroy;
    } else if (component === "text") {
      mountText(root, { value: stringValue(data.value) ?? "", label, tone: textTone(data.tone) });
    } else if (component === "result") {
      mountResult(root, {
        value: data.value, unit: stringValue(data.unit), error: stringValue(data.error),
        diagnostics: Array.isArray(data.diagnostics)
          ? data.diagnostics.filter((item): item is string => typeof item === "string") : undefined,
        label,
      });
    } else if (component === "matrix") {
      mountMatrix(root, {
        value: matrixValue(data.value), readOnly: data.read_only === true, label,
        onChange: (value) => publish({ ...currentData, value } as JsonObject),
      });
    } else if (component === "vector") {
      mountVector(root, {
        value: vectorValue(data.value), readOnly: data.read_only === true, label,
        onChange: (value) => publish({ ...currentData, value } as JsonObject),
      });
    } else if (component === "graph") {
      mountGraph(root, {
        value: graphValue(data.value), title: stringValue(data.title),
        xLabel: stringValue(data.x_label), yLabel: stringValue(data.y_label), label,
      });
    } else if (component === "diagram") {
      mountDiagram(root, {
        value: diagramValue(data.value), readOnly: data.read_only === true, label,
        onChange: (value) => publish({ ...currentData, value } as JsonObject),
      });
    } else {
      root.replaceChildren();
      const message = document.createElement("p");
      message.setAttribute("role", "status");
      message.textContent = "Unsupported MathBlocks component state.";
      root.append(message);
    }
  };

  const unsubscribe = attachStateSync(model, (data) => {
    if (localCommitInProgress) { currentData = data; return; }
    renderComponent(data);
  });
  return () => {
    unsubscribe();
    cleanupComponent?.();
    root.replaceChildren();
    root.classList.remove("mathblocks-root");
    delete root.dataset.mathblocksReady;
  };
}

export default {
  render({ el, model, signal }: { el: HTMLElement; model: AnyWidgetModel; signal: AbortSignal }): void {
    const cleanup = renderMathBlocks(el, model);
    if (signal.aborted) { cleanup(); return; }
    signal.addEventListener("abort", cleanup, { once: true });
  },
};

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}
function textTone(value: unknown): "default" | "muted" | "note" | "warning" {
  if (value === "muted" || value === "note" || value === "warning") return value;
  return "default";
}
function matrixValue(value: unknown): unknown[][] {
  return Array.isArray(value) ? value.filter(Array.isArray) as unknown[][] : [[]];
}
function vectorValue(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}
function graphValue(value: unknown): { label: string; points: [number, number][] }[] {
  if (!Array.isArray(value)) return [];
  return value.filter((series): series is { label: string; points: [number, number][] } =>
    typeof series === "object" && series !== null && "label" in series && "points" in series
    && Array.isArray(series.points));
}
function diagramValue(value: unknown): {
  nodes: { id: string; label: string; x: number; y: number; shape?: "rect" | "ellipse" }[];
  edges: { source: string; target: string; label?: string }[];
} {
  if (typeof value !== "object" || value === null || !("nodes" in value) || !("edges" in value)) {
    return { nodes: [], edges: [] };
  }
  const candidate = value as { nodes: unknown; edges: unknown };
  return {
    nodes: Array.isArray(candidate.nodes) ? candidate.nodes as {
      id: string; label: string; x: number; y: number; shape?: "rect" | "ellipse";
    }[] : [],
    edges: Array.isArray(candidate.edges) ? candidate.edges as {
      source: string; target: string; label?: string;
    }[] : [],
  };
}
