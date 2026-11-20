import type {
  AnyWidgetModel,
  ComponentStateEnvelope,
  JsonObject,
} from "./model";

export const STATE_SCHEMA_VERSION = 1;
const PYTHON_ACTOR = "python";

function isJsonObject(value: unknown): value is JsonObject {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    (Object.getPrototypeOf(value) === Object.prototype ||
      Object.getPrototypeOf(value) === null)
  );
}

/** Validate the synchronized state envelope without mutating the model value. */
export function readStateEnvelope(
  value: unknown,
): ComponentStateEnvelope {
  if (!isJsonObject(value)) {
    throw new TypeError("MathBlocks state must be a JSON object.");
  }

  const keys = Object.keys(value).sort();
  if (
    keys.join(",") !== "actor,data,revision,schema_version" ||
    value.schema_version !== STATE_SCHEMA_VERSION ||
    !Number.isSafeInteger(value.revision) ||
    (value.revision as number) < 0 ||
    typeof value.actor !== "string" ||
    value.actor.length === 0 ||
    !isJsonObject(value.data)
  ) {
    throw new TypeError("Invalid or unsupported MathBlocks state envelope.");
  }

  return {
    schema_version: STATE_SCHEMA_VERSION,
    revision: value.revision as number,
    actor: value.actor,
    data: value.data,
  };
}

/** Compare revisions deterministically; Python wins ties against browser views. */
export function compareStateVersions(
  left: ComponentStateEnvelope,
  right: ComponentStateEnvelope,
): number {
  const leftPriority = left.actor === PYTHON_ACTOR ? 1 : 0;
  const rightPriority = right.actor === PYTHON_ACTOR ? 1 : 0;
  const leftKey = [left.revision, leftPriority, left.actor] as const;
  const rightKey = [right.revision, rightPriority, right.actor] as const;

  for (let index = 0; index < leftKey.length; index += 1) {
    if (leftKey[index] < rightKey[index]) return -1;
    if (leftKey[index] > rightKey[index]) return 1;
  }
  return 0;
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
  const detachedData = JSON.parse(JSON.stringify(data)) as JsonObject;
  const next: ComponentStateEnvelope = {
    schema_version: STATE_SCHEMA_VERSION,
    revision: current.revision + 1,
    actor,
    data: detachedData,
  };

  model.set("state", next);
  model.save_changes();
  return next;
}
