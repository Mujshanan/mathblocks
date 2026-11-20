/** Versioned JSON contract shared by Python and the browser. */
export type ComponentKind = "math" | "text" | "result";
export interface ComponentState<T = unknown> { schemaVersion: 1; type: ComponentKind; value: T; [key: string]: unknown; }
export interface WidgetModel {
  get(name: string): unknown; set(name: string, value: unknown): void; save_changes(): void;
  on(event: string, callback: () => void): void; off(event: string, callback: () => void): void;
}
export interface AnyWidgetRenderContext { model: WidgetModel; el: HTMLElement; }
