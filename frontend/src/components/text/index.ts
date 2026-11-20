export interface TextComponentOptions { value: string; label?: string; tone?: "default" | "muted" | "note" | "warning"; }
export function mountText(container: HTMLElement, options: TextComponentOptions): HTMLElement {
  const element = document.createElement("div"); element.className = `mb-text mb-text--${options.tone ?? "default"}`;
  if (options.label) { const label = document.createElement("div"); label.className = "mb-text__label"; label.textContent = options.label; element.append(label); }
  const content = document.createElement("p"); content.className = "mb-text__content"; content.textContent = options.value;
  element.append(content); container.replaceChildren(element); return element;
}
