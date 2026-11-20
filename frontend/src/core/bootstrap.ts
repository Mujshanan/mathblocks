/** Initialize one MathBlocks frontend view. */
export function renderMathBlocks(root: HTMLElement): void {
  root.classList.add("mathblocks-root");
  root.dataset.mathblocksReady = "true";
  root.textContent = "MathBlocks widget is ready.";
}

/** AnyWidget front-end module entry point. */
export default {
  render({ el }: { el: HTMLElement }): void {
    renderMathBlocks(el);
  },
};
