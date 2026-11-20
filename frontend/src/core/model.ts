/** JSON values allowed across the Python/TypeScript component boundary. */
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export type JsonObject = { [key: string]: JsonValue };

/** Versioned, atomic state payload synchronized by AnyWidget. */
export interface ComponentStateEnvelope<T extends JsonObject = JsonObject> {
  schema_version: 1;
  revision: number;
  actor: string;
  data: T;
}

/** Minimal Backbone-model surface provided to AnyWidget render functions. */
export interface AnyWidgetModel {
  get(name: string): unknown;
  set(name: string, value: unknown): void;
  save_changes(): void;
  on(event: string, callback: () => void): void;
  off(event: string, callback: () => void): void;
}
