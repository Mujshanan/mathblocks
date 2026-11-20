export interface DiagramNode { id: string; label: string; x: number; y: number; shape?: "rect" | "ellipse"; }
export interface DiagramEdge { source: string; target: string; label?: string; }
export interface DiagramDocument { nodes: DiagramNode[]; edges: DiagramEdge[]; }
export interface DiagramOptions {
  value: DiagramDocument;
  readOnly?: boolean;
  label?: string;
  onChange?: (value: DiagramDocument) => void;
}
const NS = "http://www.w3.org/2000/svg";

/** SVG node-and-edge editor with drag interaction and standalone SVG download. */
export function mountDiagram(container: HTMLElement, options: DiagramOptions): void {
  container.replaceChildren();
  const root = document.createElement("section");
  root.className = "mb-diagram";
  if (options.label) {
    const label = document.createElement("div");
    label.className = "mb-visual__label";
    label.textContent = options.label;
    root.append(label);
  }
  const documentModel: DiagramDocument = {
    nodes: options.value.nodes.map((node) => ({ ...node })),
    edges: options.value.edges.map((edge) => ({ ...edge })),
  };
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", "0 0 800 500");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", options.label ?? "Diagram editor");
  svg.classList.add("mb-diagram__surface");
  const nodeWidth = 132, nodeHeight = 54;
  const render = () => {
    svg.replaceChildren();
    documentModel.edges.forEach((edge) => {
      const source = documentModel.nodes.find((node) => node.id === edge.source);
      const target = documentModel.nodes.find((node) => node.id === edge.target);
      if (!source || !target) return;
      const line = document.createElementNS(NS, "line");
      line.setAttribute("x1", String(source.x + nodeWidth / 2));
      line.setAttribute("y1", String(source.y + nodeHeight / 2));
      line.setAttribute("x2", String(target.x + nodeWidth / 2));
      line.setAttribute("y2", String(target.y + nodeHeight / 2));
      line.setAttribute("class", "mb-diagram__edge");
      svg.append(line);
      if (edge.label) {
        const text = document.createElementNS(NS, "text");
        text.setAttribute("x", String((source.x + target.x + nodeWidth) / 2));
        text.setAttribute("y", String((source.y + target.y + nodeHeight) / 2 - 6));
        text.setAttribute("class", "mb-diagram__edge-label");
        text.textContent = edge.label;
        svg.append(text);
      }
    });
    documentModel.nodes.forEach((node) => {
      const group = document.createElementNS(NS, "g");
      group.setAttribute("transform", `translate(${node.x} ${node.y})`);
      group.setAttribute("class", "mb-diagram__node");
      group.setAttribute("data-node-id", node.id);
      if (node.shape === "ellipse") {
        const shape = document.createElementNS(NS, "ellipse");
        shape.setAttribute("cx", String(nodeWidth / 2)); shape.setAttribute("cy", String(nodeHeight / 2));
        shape.setAttribute("rx", String(nodeWidth / 2)); shape.setAttribute("ry", String(nodeHeight / 2));
        shape.setAttribute("class", "mb-diagram__shape"); group.append(shape);
      } else {
        const shape = document.createElementNS(NS, "rect");
        shape.setAttribute("width", String(nodeWidth)); shape.setAttribute("height", String(nodeHeight));
        shape.setAttribute("rx", "8"); shape.setAttribute("class", "mb-diagram__shape"); group.append(shape);
      }
      const text = document.createElementNS(NS, "text");
      text.setAttribute("x", String(nodeWidth / 2)); text.setAttribute("y", String(nodeHeight / 2 + 5));
      text.setAttribute("text-anchor", "middle"); text.setAttribute("class", "mb-diagram__node-label");
      text.textContent = node.label; group.append(text);
      if (!options.readOnly) {
        group.setAttribute("tabindex", "0");
        group.setAttribute("role", "button");
        group.setAttribute("aria-label", `Move node ${node.label}`);
        let start: { x: number; y: number; nodeX: number; nodeY: number } | undefined;
        group.addEventListener("pointerdown", (event) => {
          start = { x: event.clientX, y: event.clientY, nodeX: node.x, nodeY: node.y };
          group.setPointerCapture(event.pointerId);
        });
        group.addEventListener("pointermove", (event) => {
          if (!start) return;
          const rect = svg.getBoundingClientRect();
          const scaleX = 800 / Math.max(rect.width, 1), scaleY = 500 / Math.max(rect.height, 1);
          node.x = Math.max(0, Math.min(800 - nodeWidth, start.nodeX + (event.clientX - start.x) * scaleX));
          node.y = Math.max(0, Math.min(500 - nodeHeight, start.nodeY + (event.clientY - start.y) * scaleY));
          group.setAttribute("transform", `translate(${node.x} ${node.y})`);
        });
        group.addEventListener("pointerup", () => {
          if (!start) return;
          start = undefined;
          render();
          options.onChange?.({ nodes: documentModel.nodes.map((item) => ({ ...item })),
            edges: documentModel.edges.map((item) => ({ ...item })) });
        });
        group.addEventListener("pointercancel", () => { start = undefined; });
      }
      svg.append(group);
    });
  };
  render();
  root.append(svg);
  if (!options.readOnly) {
    const exportButton = document.createElement("button");
    exportButton.type = "button"; exportButton.className = "mb-visual__action";
    exportButton.textContent = "Export SVG";
    exportButton.addEventListener("click", () => {
      const clone = svg.cloneNode(true) as SVGSVGElement;
      clone.setAttribute("xmlns", NS);
      const style = document.createElementNS(NS, "style");
      style.textContent = ".mb-diagram__edge{stroke:#777;stroke-width:2}.mb-diagram__edge-label{fill:#333;font-size:12px}.mb-diagram__shape{fill:#eef4fc;stroke:#3978c5;stroke-width:1.7}.mb-diagram__node-label{fill:#17202a;font-size:13px}";
      clone.insertBefore(style, clone.firstChild);
      const blob = new Blob([new XMLSerializer().serializeToString(clone)], { type: "image/svg+xml" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url; anchor.download = "mathblocks-diagram.svg";
      anchor.click(); URL.revokeObjectURL(url);
    });
    root.append(exportButton);
  }
  container.append(root);
}
