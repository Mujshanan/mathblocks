export interface VectorOptions {
  value: unknown[];
  readOnly?: boolean;
  label?: string;
  onChange?: (value: unknown[]) => void;
}

/** Render a one-dimensional vector as a labelled editable column. */
export function mountVector(container: HTMLElement, options: VectorOptions): void {
  container.replaceChildren();
  const root = document.createElement("section");
  root.className = "mb-vector";
  if (options.label) {
    const label = document.createElement("div");
    label.className = "mb-visual__label";
    label.textContent = options.label;
    root.append(label);
  }
  const values = [...options.value];
  const table = document.createElement("table");
  table.className = "mb-matrix__table mb-vector__table";
  table.setAttribute("aria-label", options.label ?? "Vector");
  const body = document.createElement("tbody");
  values.forEach((value, index) => {
    const row = document.createElement("tr");
    const heading = document.createElement("th");
    heading.scope = "row";
    heading.textContent = String(index + 1);
    const cell = document.createElement("td");
    const input = document.createElement("input");
    input.className = "mb-matrix__cell";
    input.value = value === null || value === undefined ? "" : String(value);
    input.readOnly = options.readOnly === true;
    input.setAttribute("aria-label", `Vector entry ${index + 1}`);
    input.addEventListener("input", () => {
      const text = input.value.trim();
      values[index] = text !== "" && Number.isFinite(Number(text)) ? Number(text) : input.value;
      options.onChange?.([...values]);
    });
    cell.append(input);
    row.append(heading, cell);
    body.append(row);
  });
  table.append(body);
  root.append(table);
  container.append(root);
}
