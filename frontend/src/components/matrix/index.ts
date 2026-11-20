export interface MatrixOptions {
  value: unknown[][];
  readOnly?: boolean;
  label?: string;
  onChange?: (value: unknown[][]) => void;
}
export interface MountedMatrix { destroy(): void; }

/** Rectangular keyboard-editable table with TSV paste and copy support. */
export function mountMatrix(container: HTMLElement, options: MatrixOptions): MountedMatrix {
  container.replaceChildren();
  const root = document.createElement("section");
  root.className = "mb-matrix";
  if (options.label) {
    const label = document.createElement("div");
    label.className = "mb-visual__label";
    label.textContent = options.label;
    root.append(label);
  }
  const values = options.value.map((row) => [...row]);
  const table = document.createElement("table");
  table.className = "mb-matrix__table";
  table.setAttribute("aria-label", options.label ?? "Matrix");
  const body = document.createElement("tbody");
  const readOnly = options.readOnly === true;

  const publish = () => options.onChange?.(values.map((row) => [...row]));
  const render = (focus?: [number, number]) => {
    body.replaceChildren();
    values.forEach((row, rowIndex) => {
      const tr = document.createElement("tr");
      row.forEach((cell, columnIndex) => {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.className = "mb-matrix__cell";
        input.type = "text";
        input.value = cell === null || cell === undefined ? "" : String(cell);
        input.readOnly = readOnly;
        input.setAttribute("aria-label", `Row ${rowIndex + 1}, column ${columnIndex + 1}`);
        input.addEventListener("input", () => {
          values[rowIndex]![columnIndex] = parseCell(input.value);
          publish();
        });
        input.addEventListener("paste", (event) => {
          if (readOnly) return;
          const text = event.clipboardData?.getData("text/plain");
          if (!text || (!text.includes("\\t") && !text.includes("\\n"))) return;
          event.preventDefault();
          const pasted = text.replace(/\\r/g, "").split("\\n").filter((line) => line.length > 0)
            .map((line) => line.split("\\t").map(parseCell));
          pasted.forEach((pasteRow, rowOffset) => {
            const targetRow = rowIndex + rowOffset;
            while (!values[targetRow]) values.push(Array(values[0]?.length ?? 1).fill(""));
            pasteRow.forEach((item, columnOffset) => {
              const targetColumn = columnIndex + columnOffset;
              if (targetColumn < (values[0]?.length ?? 1)) values[targetRow]![targetColumn] = item;
            });
          });
          publish();
          render([rowIndex, columnIndex]);
        });
        td.append(input);
        tr.append(td);
      });
      body.append(tr);
    });
    if (focus) {
      const target = body.querySelectorAll("input")[focus[0] * (values[0]?.length ?? 1) + focus[1]];
      target?.focus();
    }
  };
  render();
  table.append(body);
  root.append(table);
  if (!readOnly) {
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "mb-visual__action";
    copy.textContent = "Copy TSV";
    copy.addEventListener("click", () => {
      const tsv = values.map((row) => row.map((cell) => String(cell ?? "")).join("\\t")).join("\\n");
      void navigator.clipboard?.writeText(tsv);
    });
    root.append(copy);
  }
  container.append(root);
  return { destroy: () => root.remove() };
}

function parseCell(value: string): string | number {
  const trimmed = value.trim();
  if (trimmed !== "" && Number.isFinite(Number(trimmed))) return Number(trimmed);
  return value;
}
