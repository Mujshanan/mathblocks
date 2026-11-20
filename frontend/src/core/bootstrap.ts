import {
  attachStateSync,
  commitState,
  createViewActorId,
} from "./synchronization";
import type { AnyWidgetModel, JsonObject } from "./model";
import { mountMath } from "../components/math";
import { mountText } from "../components/text";
import { mountResult } from "../components/result";

/** Render the component selected by the current synchronized domain state. */
export function renderMathBlocks(root: HTMLElement, model: AnyWidgetModel): () => void {
  root.classList.add("mathblocks-root");
  root.dataset.mathblocksReady = "true";

  const actor = createViewActorId();
  let currentData: JsonObject = {};
  let localCommitInProgress = false;
  let cleanupComponent: (() => void) | undefined;

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
        onChange: (value) => {
          const next = { ...currentData, value } as JsonObject;
          currentData = next;
          // commitState emits a synchronous Backbone change event. Do not
          // remount MathLive for our own keystroke: it would reset the caret.
          localCommitInProgress = true;
          try {
            commitState(model, next, actor);
          } finally {
            localCommitInProgress = false;
          }
        },
      }).destroy;
      return;
    }

    if (component === "text") {
      mountText(root, {
        value: stringValue(data.value) ?? "",
        label,
        tone: textTone(data.tone),
      });
      return;
    }

    if (component === "result") {
      mountResult(root, {
        value: data.value,
        unit: stringValue(data.unit),
        error: stringValue(data.error),
        diagnostics: Array.isArray(data.diagnostics)
          ? data.diagnostics.filter((item): item is string => typeof item === "string")
          : undefined,
        label,
      });
      return;
    }

    root.replaceChildren();
    const message = document.createElement("p");
    message.setAttribute("role", "status");
    message.textContent = "Unsupported MathBlocks component state.";
    root.append(message);
  };

  const unsubscribe = attachStateSync(model, (data) => {
    if (localCommitInProgress) {
      currentData = data;
      return;
    }
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

/** AnyWidget frontend module entry point; cleanup follows its per-view signal. */
export default {
  render({
    el,
    model,
    signal,
  }: {
    el: HTMLElement;
    model: AnyWidgetModel;
    signal: AbortSignal;
  }): void {
    const cleanup = renderMathBlocks(el, model);
    if (signal.aborted) {
      cleanup();
      return;
    }
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
