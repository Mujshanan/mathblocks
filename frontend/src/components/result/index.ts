export interface ResultComponentOptions {
  value: unknown;
  unit?: string;
  error?: string;
  diagnostics?: string[];
  label?: string;
}

/** Display a computed value, unit, and accessible diagnostics. */
export function mountResult(container: HTMLElement, options: ResultComponentOptions): void {
  const element = document.createElement("section");
  element.className = "mb-result";
  element.setAttribute("aria-live", options.error ? "assertive" : "polite");

  if (options.label) {
    const label = document.createElement("div");
    label.className = "mb-result__label";
    label.textContent = options.label;
    element.append(label);
  }

  if (options.error) {
    const error = document.createElement("p");
    error.className = "mb-result__error";
    error.setAttribute("role", "alert");
    error.textContent = options.error;
    element.append(error);
  } else {
    const value = document.createElement("output");
    value.className = "mb-result__value";
    value.textContent = formatValue(options.value);
    element.append(value);
    if (options.unit) {
      const unit = document.createElement("span");
      unit.className = "mb-result__unit";
      unit.textContent = options.unit;
      element.append(unit);
    }
  }

  if (options.diagnostics?.length) {
    const list = document.createElement("ul");
    list.className = "mb-result__diagnostics";
    list.setAttribute("aria-label", "Calculation diagnostics");
    for (const message of options.diagnostics) {
      const item = document.createElement("li");
      item.textContent = message;
      list.append(item);
    }
    element.append(list);
  }
  container.replaceChildren(element);
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}
