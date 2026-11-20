/** Synced AnyWidget model fields shared by Python and the frontend. */
export interface ComponentModelState<T = unknown> {
  schema_version: number;
  component_state: T;
}
