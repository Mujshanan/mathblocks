export interface GraphSeries { label: string; points: [number, number][]; }
export interface GraphOptions {
  value: GraphSeries[];
  title?: string;
  xLabel?: string;
  yLabel?: string;
  label?: string;
}

/** Accessible SVG plot with per-point hover/focus inspection and legend toggles. */
export function mountGraph(container: HTMLElement, options: GraphOptions): void {
  container.replaceChildren();
  const root = document.createElement("section");
  root.className = "mb-graph";
  if (options.title || options.label) {
    const heading = document.createElement("div");
    heading.className = "mb-visual__label";
    heading.textContent = options.title ?? options.label ?? "";
    root.append(heading);
  }
  const hidden = new Set<number>();
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 720 380");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", options.title ?? options.label ?? "Interactive graph");
  svg.classList.add("mb-graph__plot");
  const legend = document.createElement("div");
  legend.className = "mb-graph__legend";
  options.value.forEach((series, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "mb-graph__legend-item";
    button.textContent = series.label;
    button.setAttribute("aria-pressed", "true");
    button.addEventListener("click", () => {
      if (hidden.has(index)) hidden.delete(index); else hidden.add(index);
      button.setAttribute("aria-pressed", String(!hidden.has(index)));
      draw();
    });
    legend.append(button);
  });

  const draw = () => {
    svg.replaceChildren();
    const visible = options.value.filter((_, index) => !hidden.has(index));
    const points = visible.flatMap((series) => series.points);
    if (!points.length) return;
    const xs = points.map((p) => p[0]), ys = points.map((p) => p[1]);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const spanX = maxX - minX || 1, spanY = maxY - minY || 1;
    const px = (x: number) => 58 + ((x - minX) / spanX) * 620;
    const py = (y: number) => 320 - ((y - minY) / spanY) * 270;
    const axis = document.createElementNS(svg.namespaceURI, "path");
    axis.setAttribute("d", "M58 24 V320 H678");
    axis.setAttribute("class", "mb-graph__axis");
    svg.append(axis);
    const xTitle = document.createElementNS(svg.namespaceURI, "text");
    xTitle.setAttribute("x", "368"); xTitle.setAttribute("y", "365");
    xTitle.setAttribute("text-anchor", "middle"); xTitle.textContent = options.xLabel ?? "x";
    xTitle.setAttribute("class", "mb-graph__axis-label"); svg.append(xTitle);
    const yTitle = document.createElementNS(svg.namespaceURI, "text");
    yTitle.setAttribute("transform", "translate(18 185) rotate(-90)");
    yTitle.setAttribute("text-anchor", "middle"); yTitle.textContent = options.yLabel ?? "y";
    yTitle.setAttribute("class", "mb-graph__axis-label"); svg.append(yTitle);
    options.value.forEach((series, index) => {
      if (hidden.has(index)) return;
      const path = document.createElementNS(svg.namespaceURI, "polyline");
      path.setAttribute("points", series.points.map(([x,y]) => `${px(x)},${py(y)}`).join(" "));
      path.setAttribute("class", "mb-graph__line");
      path.setAttribute("data-series", String(index));
      svg.append(path);
      series.points.forEach(([x,y], pointIndex) => {
        const circle = document.createElementNS(svg.namespaceURI, "circle");
        circle.setAttribute("cx", String(px(x))); circle.setAttribute("cy", String(py(y)));
        circle.setAttribute("r", "5"); circle.setAttribute("tabindex", "0");
        circle.setAttribute("class", "mb-graph__point");
        circle.setAttribute("aria-label", `${series.label}, point ${pointIndex + 1}: (${x}, ${y})`);
        const title = document.createElementNS(svg.namespaceURI, "title");
        title.textContent = `${series.label}: (${x}, ${y})`;
        circle.append(title); svg.append(circle);
      });
    });
  };
  draw();
  root.append(legend, svg);
  container.append(root);
}
