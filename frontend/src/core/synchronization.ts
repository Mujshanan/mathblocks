import type {
  AnyWidgetModel,
  ComponentStateEnvelope,
  JsonObject,
  JsonValue,
} from "./model";

export const STATE_SCHEMA_VERSION = 1;
const PYTHON_ACTOR = "python";

function normalizeJsonValue(
  value: unknown,
  ancestors: Set<object>,
  path: string,
): JsonValue {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value) || (!Number.isSafeInteger(value) && Number.isInteger(value))) {
      throw new TypeError(`${path} contains a non-finite or unsafe integer.`);
    }
    return value;
  }
  if (Array.isArray(value)) {
    if (ancestors.has(value)) throw new TypeError(`${path} contains a circular reference.`);
    // JSON.stringify silently converts sparse slots to null and ignores custom
    // array properties. Reject both so the wire payload is never changed.
    if (Object.keys(value).length !== value.length) {
      throw new TypeError(`${path} must be a dense array without extra properties.`);
    }
    if (Object.getOwnPropertySymbols(value).length > 0 || Reflect.ownKeys(value).length !== value.length + 1) {
      throw new TypeError(`${path} contains non-JSON array properties.`);
    }
    ancestors.add(value);
    const normalized: JsonValue[] = [];
    for (let index = 0; index < value.length; index += 1) {
      if (!Object.prototype.hasOwnProperty.call(value, index)) {
        throw new TypeError(`${path} contains a sparse array slot at index ${index}.`);
      }
      normalized.push(normalizeJsonValue(value[index], ancestors, `${path}[${index}]`));
    }
    ancestors.delete(value);
    return normalized;
  }
  if (typeof value === "object" && value !== null) {
    const prototype = Object.getPrototypeOf(value);
    if (prototype !== Object.prototype && prototype !== null) {
      throw new TypeError(`${path} must contain only plain JSON objects.`);
    }
    if (ancestors.has(value)) throw new TypeError(`${path} contains a circular reference.`);
    if (Reflect.ownKeys(value).length !== Object.keys(value).length) {
      throw new TypeError(`${path} contains non-enumerable or symbol-keyed properties.`);
    }
    ancestors.add(value);
    const normalized = Object.create(null) as JsonObject;
    for (const key of Object.keys(value)) {
      const descriptor = Object.getOwnPropertyDescriptor(value, key);
      if (!descriptor?.enumerable || !("value" in descriptor)) {
        throw new TypeError(`${path}.${key} must be an enumerable data property.`);
      }
      normalized[key] = normalizeJsonValue(descriptor.value, ancestors, `${path}.${key}`);
    }
    ancestors.delete(value);
    return normalized;
  }
  throw new TypeError(`${path} contains a value that is not JSON-compatible.`);
}

function normalizeJsonObject(value: unknown): JsonObject {
  if (
    typeof value !== "object" ||
    value === null ||
    Array.isArray(value) ||
    (Object.getPrototypeOf(value) !== Object.prototype &&
      Object.getPrototypeOf(value) !== null)
  ) {
    throw new TypeError("Component state must be a plain JSON object.");
  }
  return normalizeJsonValue(value, new Set<object>(), "data") as JsonObject;
}

/** Validate the synchronized state envelope and detach its JSON payload. */
export function readStateEnvelope(
  value: unknown,
): ComponentStateEnvelope {
  if (
    typeof value !== "object" ||
    value === null ||
    Array.isArray(value) ||
    (Object.getPrototypeOf(value) !== Object.prototype &&
      Object.getPrototypeOf(value) !== null)
  ) {
    throw new TypeError("MathBlocks state must be a JSON object.");
  }

  const envelope = value as Record<string, unknown>;
  const keys = Object.keys(envelope).sort();
  if (
    keys.join(",") !== "actor,data,revision,schema_version" ||
    envelope.schema_version !== STATE_SCHEMA_VERSION ||
    !Number.isSafeInteger(envelope.revision) ||
    (envelope.revision as number) < 0 ||
    typeof envelope.actor !== "string" ||
    envelope.actor.trim().length === 0
  ) {
    throw new TypeError("Invalid or unsupported MathBlocks state envelope.");
  }

  return {
    schema_version: STATE_SCHEMA_VERSION,
    revision: envelope.revision as number,
    actor: envelope.actor,
    data: normalizeJsonObject(envelope.data),
  };
}

/** Compare revisions deterministically; Python wins ties against browser views. */
export function compareStateVersions(
  left: ComponentStateEnvelope,
  right: ComponentStateEnvelope,
): number {
  if (left.revision !== right.revision) {
    return left.revision < right.revision ? -1 : 1;
  }
  const leftPriority = left.actor === PYTHON_ACTOR ? 1 : 0;
  const rightPriority = right.actor === PYTHON_ACTOR ? 1 : 0;
  if (leftPriority !== rightPriority) {
    return leftPriority < rightPriority ? -1 : 1;
  }
  if (left.actor === right.actor) return 0;
  return left.actor < right.actor ? -1 : 1;
}

/** Create a per-view actor identifier for deterministic concurrent updates. */
export function createViewActorId(): string {
  const randomId =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
  return `view:${randomId}`;
}

/** Subscribe to state changes and return a deterministic unsubscriber. */
export function attachStateSync(
  model: AnyWidgetModel,
  onState: (state: JsonObject, envelope: ComponentStateEnvelope) => void,
): () => void {
  let active = true;

  const update = (): void => {
    if (!active) return;
    const envelope = readStateEnvelope(model.get("state"));
    onState(envelope.data, envelope);
  };

  model.on("change:state", update);
  update();

  return () => {
    if (!active) return;
    active = false;
    model.off("change:state", update);
  };
}

/** Publish a frontend-originated domain-state update through AnyWidget. */
export function commitState(
  model: AnyWidgetModel,
  data: JsonObject,
  actor: string,
): ComponentStateEnvelope {
  if (!actor || actor === PYTHON_ACTOR) {
    throw new TypeError("Frontend updates require a non-Python actor ID.");
  }
  const current = readStateEnvelope(model.get("state"));
  if (current.revision >= Number.MAX_SAFE_INTEGER) {
    throw new RangeError("MathBlocks state revision has reached its safe integer limit.");
  }
  const next: ComponentStateEnvelope = {
    schema_version: STATE_SCHEMA_VERSION,
    revision: current.revision + 1,
    actor,
    data: normalizeJsonObject(data),
  };

  model.set("state", next);
  model.save_changes();
  return next;
}
