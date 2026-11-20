import "mathlive";
import katex from "katex";

export interface MathComponentOptions {
  value: string;
  readOnly?: boolean;
  label?: string;
  onChange?: (value: string) => void;
}

export interface MountedComponent {
  destroy(): void;
}

/** Mount editable MathLive input or a static KaTeX expression. */
export function mountMath(container: HTMLElement, options: MathComponentOptions): MountedComponent {
  container.replaceChildren();
  const wrapper = document.createElement("div");
  wrapper.className = "mb-math";

  if (options.readOnly) {
    const output = document.createElement("div");
    output.className = "mb-math__static";
    output.setAttribute("role", "math");
    output.setAttribute("aria-label", options.label ?? "Mathematical expression");
    katex.render(options.value, output, { throwOnError: false, strict: "warn", trust: false });
    wrapper.append(output);
    container.append(wrapper);
    return { destroy: () => wrapper.remove() };
  }

  const field = document.createElement("math-field") as HTMLElement & {
    value: string;
    readOnly: boolean;
  };
  field.className = "mb-math__field";
  field.setAttribute("aria-label", options.label ?? "Mathematical expression");
  field.setAttribute("virtual-keyboard-mode", "manual");
  field.value = options.value;
  field.readOnly = false;

  const handleInput = () => options.onChange?.(field.value);
  field.addEventListener("input", handleInput);
  wrapper.append(field);
  container.append(wrapper);

  return {
    destroy: () => {
      field.removeEventListener("input", handleInput);
      wrapper.remove();
    },
  };
}
