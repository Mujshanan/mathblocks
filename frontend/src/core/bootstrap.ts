import type { AnyWidgetRenderContext, ComponentState } from "./model";
import { mountMath } from "../components/math";
import { mountText } from "../components/text";
import { mountResult } from "../components/result";
const SCHEMA_VERSION = 1;
export function renderMathBlocks({ model, el }: AnyWidgetRenderContext): () => void {
  el.replaceChildren(); const root = document.createElement("div"); root.className = "mathblocks-root";
  root.setAttribute("data-mathblocks", "true"); el.append(root);
  let destroyed = false; let cleanup: (() => void) | undefined; let localUpdate: unknown;
  const render = () => {
    if (destroyed) return; cleanup?.(); cleanup = undefined;
    const raw = model.get("state"); const state = isComponentState(raw) ? raw : fallbackState(raw);
    const onChange = (value: string) => {
      const current = model.get("state"); const latest = isComponentState(current) ? current : state;
      const next = { ...latest, value }; localUpdate = next; model.set("state", next); model.save_changes();
    };
    if (state.type === "math") {
      cleanup = mountMath(root, { value: String(state.value ?? ""), readOnly: Boolean(state.readOnly),
        label: asString(state.label), onChange }).destroy;
    } else if (state.type === "text") {
      mountText(root, { value: String(state.value ?? ""), label: asString(state.label),
        tone: isTone(state.tone) ? state.tone : "default" });
    } else if (state.type === "result") {
      mountResult(root, { value: state.value, unit: asString(state.unit), error: asString(state.error),
        diagnostics: Array.isArray(state.diagnostics) ? state.diagnostics.filter((v): v is string => typeof v === "string") : undefined,
        label: asString(state.label) });
    } else { root.textContent = "Unsupported MathBlocks component."; root.setAttribute("role", "status"); }
  };
  const handleStateChange = () => {
    // Ignore our own synchronous model event: remounting would reset MathLive's cursor.
    if (localUpdate !== undefined && model.get("state") === localUpdate) { localUpdate = undefined; return; }
    render();
  };
  model.on("change:state", handleStateChange); render();
  return () => { destroyed = true; model.off("change:state", handleStateChange); cleanup?.(); root.remove(); };
}
function isComponentState(value: unknown): value is ComponentState<Record<string, unknown>> {
  if (!value || typeof value !== "object") return false; const candidate = value as Record<string, unknown>;
  return candidate.schemaVersion === SCHEMA_VERSION && ["math", "text", "result"].includes(String(candidate.type));
}
function fallbackState(value: unknown): ComponentState { return { schemaVersion: 1, type: "text", value: String(value ?? "") }; }
function asString(value: unknown): string | undefined { return typeof value === "string" ? value : undefined; }
function isTone(value: unknown): value is "default" | "muted" | "note" | "warning" {
  return value === "default" || value === "muted" || value === "note" || value === "warning";
}
