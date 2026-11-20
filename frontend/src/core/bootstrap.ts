import {
  attachStateSync,
  commitState,
  createViewActorId,
} from "./synchronization";
import type { AnyWidgetModel, JsonObject } from "./model";

/** Initialize one independently managed MathBlocks frontend view. */
export function renderMathBlocks(
  root: HTMLElement,
  model: AnyWidgetModel,
): () => void {
  root.classList.add("mathblocks-root");
  root.dataset.mathblocksReady = "true";

  const panel = document.createElement("section");
  panel.className = "mathblocks-state-panel";

  const heading = document.createElement("h3");
  heading.className = "mathblocks-state-title";
  heading.textContent = "MathBlocks · synchronized state";

  const description = document.createElement("p");
  description.className = "mathblocks-state-description";
  description.textContent =
    "Edit this JSON object and apply it. Changes synchronize with Python and other views.";

  const editor = document.createElement("textarea");
  editor.className = "mathblocks-state-editor";
  editor.setAttribute("aria-label", "Component state JSON");
  editor.spellcheck = false;

  const actions = document.createElement("div");
  actions.className = "mathblocks-state-actions";

  const applyButton = document.createElement("button");
  applyButton.className = "mathblocks-state-apply";
  applyButton.type = "button";
  applyButton.textContent = "Apply state";

  const status = document.createElement("output");
  status.className = "mathblocks-state-status";
  status.setAttribute("aria-live", "polite");

  actions.append(applyButton, status);
  panel.append(heading, description, editor, actions);
  root.replaceChildren(panel);

  const actor = createViewActorId();
  const unsubscribe = attachStateSync(model, (data, envelope) => {
    editor.value = JSON.stringify(data, null, 2);
    status.textContent = `Synced · revision ${envelope.revision}`;
    status.dataset.state = "synced";
  });

  const apply = (): void => {
    try {
      const parsed: unknown = JSON.parse(editor.value);
      if (
        typeof parsed !== "object" ||
        parsed === null ||
        Array.isArray(parsed)
      ) {
        throw new TypeError("The component state must be a JSON object.");
      }
      commitState(model, parsed as JsonObject, actor);
      status.textContent = "Update sent";
      status.dataset.state = "synced";
    } catch (error) {
      status.textContent =
        error instanceof Error ? error.message : "Unable to apply state.";
      status.dataset.state = "error";
    }
  };

  applyButton.addEventListener("click", apply);

  return () => {
    unsubscribe();
    applyButton.removeEventListener("click", apply);
    root.replaceChildren();
    root.classList.remove("mathblocks-root");
    delete root.dataset.mathblocksReady;
  };
}

/** AnyWidget frontend module entry point. */
export default {
  render({
    el,
    model,
  }: {
    el: HTMLElement;
    model: AnyWidgetModel;
  }): () => void {
    return renderMathBlocks(el, model);
  },
};
