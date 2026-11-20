/** Shared frontend model contracts. Keep wire formats explicit and versioned. */
export interface ComponentState<T = unknown> {
  schemaVersion: number;
  value: T;
}
