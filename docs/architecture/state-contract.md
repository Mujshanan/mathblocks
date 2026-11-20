# Python–frontend state contract

Phase 1 defines the version-1 wire contract shared by MathBlocks Python
widgets and their TypeScript views.

## Atomic envelope

AnyWidget synchronizes one trait named `state`. It is an atomic envelope:

```json
{
  "schema_version": 1,
  "revision": 0,
  "actor": "python",
  "data": {}
}
```

| Field | Meaning |
|---|---|
| `schema_version` | Contract version. Version 1 is the initial format. |
| `revision` | Non-negative logical revision, increased for every accepted update. |
| `actor` | Origin identifier: `python` or a unique `view:<id>` frontend view. |
| `data` | Component-owned JSON object. |

The envelope is deliberately a single synchronized trait. Sending payload and
revision as separate traits could expose intermediate combinations to observers.

The Python-side revision and conflict rules live in the framework-independent
`mathblocks.core.StateStore`. The AnyWidget adapter only transports accepted
envelopes; it does not define component state semantics.

Python exposes `widget.component_state` as a detached convenience property.
Assigning it publishes a new Python-originated revision:

```python
widget.component_state = {"value": 12}
print(widget.component_state)
```

The frontend reads and writes the envelope through the AnyWidget Backbone
model. A frontend write updates the model's `state` attribute and calls
`save_changes()`. Python-originated trait updates are delivered through
AnyWidget's normal model-change event.

## Serialization rules

- The envelope and component payload must be JSON objects.
- Allowed payload values are JSON strings, finite numbers, booleans, null,
  arrays, and objects with string keys.
- NaN, positive/negative infinity, Python objects, cyclic structures, and
  non-object root payloads are rejected.
- Python validates and detaches values by JSON round-tripping before accepting
  them. The frontend validates the envelope before exposing it to a view.
- Unknown envelope keys and unsupported schema versions are rejected. A
  future incompatible contract must use a new schema version and explicit
  migration support; it must not be silently reinterpreted.

## Revision and conflict policy

Updates use a Lamport-style logical version ordered by:

1. Higher revision wins.
2. At the same revision, Python wins over a browser view.
3. If two browser views have the same revision, actor IDs are compared
   lexicographically; the greater actor ID wins.

This gives concurrent updates a deterministic winner on every client. It is
not a collaborative text-editing algorithm: simultaneous edits to the same
payload are resolved as whole-object last-writer-wins updates. Components
needing merge semantics must define a domain-specific operation rather than
changing the shared transport contract.

A frontend view increments the latest observed revision and uses its unique
actor ID. Python-originated updates increment the latest accepted revision
and use actor `python`. Stale or losing envelopes are rejected and the
previous accepted state is restored.

## State ownership

- **Domain state:** persisted component data in `state.data`; synchronized.
- **Transient UI state:** cursor, focus, selection, hover, and uncommitted
  editor text; local to a view and not synchronized by the base widget.
- **Computed state:** derived output; components should recompute it from
  domain inputs unless a component contract explicitly declares it persisted.

The DOM is a rendering target, never the source of truth. A view subscribes to
model changes and returns an unsubscribe function. AnyWidget's per-view
AbortSignal invokes that cleanup when the view is removed, removing model
listeners and DOM event handlers. Each widget instance owns its own state;
each rendered view owns its own transient UI state and actor identity.

## Compatibility

Python and frontend assets ship together in one distribution. The frontend
must reject unsupported envelope versions. The Python boundary validates
incoming frontend state before exposing it to application code.
