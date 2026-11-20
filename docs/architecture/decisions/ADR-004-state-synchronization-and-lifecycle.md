# ADR-004: State synchronization and component lifecycle

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owners:** MathBlocks maintainers
- **Scope:** Python–frontend state ownership, synchronization, update consistency, component identity, and widget/view lifecycle
- **Related decisions:** ADR-001 (AnyWidget Component Architecture), ADR-002 (Canonical Mathematical Expression Representation), ADR-003 (accepted expression evaluation contract; single-expression evaluation only)

## Context

MathBlocks exposes Python components backed by AnyWidget, with TypeScript views and Jotai for frontend interaction state. Python traits, frontend model replicas, and frontend atoms must not become competing sources of truth.

The project already defines a version-1 atomic state envelope and a deterministic revision/actor conflict policy in the [Python–frontend state contract](../state-contract.md). This ADR makes the architectural rules explicit and establishes the intended behavior for multiple frontend views and component lifecycle events.

## Decision

### 1. Three categories of state

MathBlocks MUST distinguish three categories of state.

**Synchronized component state** is the public, persistent mathematical content and configuration of a component. Examples include expression source and structured expression data, matrix/vector contents, graph/diagram document data, and component configuration. It is transported through the component's synchronized AnyWidget state trait.

**Frontend-local interaction state** is temporary state used to operate a particular view. Examples include cursor and selection, focus, open menus, hover, temporary drag operations, panel visibility, and uncommitted editor interaction. It remains local to that frontend view unless a component contract explicitly requires synchronization.

**External computation state** consists of values and diagnostics supplied by an external computation engine or host application. MathBlocks may validate and present these values, but it does not calculate them. Computation ownership is defined by ADR-003.

### 2. Ownership and authority

- Python defines the public component API, synchronized trait definitions, and validation boundary.
- The synchronized component state is the shared logical state of the component instance.
- JavaScript maintains a frontend replica of synchronized state for rendering and interaction; it does not create a separate persistent domain model.
- Jotai manages frontend-local interaction state and derived presentation state.
- The MathBlocks core owns framework-independent data contracts and validation.
- External computation engines own evaluation and computation semantics.
- The host application coordinates components and external engines.

The DOM is a rendering target, never the source of truth.

### 3. Atomic snapshot synchronization

The initial synchronization protocol MUST use complete, atomic component-state snapshots rather than partial patches.

AnyWidget SHALL transport one synchronized trait named `state`, containing a versioned envelope with:

- `schema_version`: synchronized state contract version.
- `revision`: non-negative logical revision.
- `actor`: update origin, `python` or a unique `view:<id>` frontend view identifier.
- `data`: component-owned JSON object.

The exact version-1 envelope is documented in [state-contract.md](../state-contract.md).

A state update is validated and accepted as one logical transition. Separate synchronized traits for payload and revision MUST NOT be used if they could expose an intermediate inconsistent combination.

Partial patches, field-level merges, and CRDT operations are outside the initial protocol.

### 4. Revision and conflict handling

The initial protocol SHALL use the deterministic revision/actor ordering defined in the state contract:

1. A higher revision wins.
2. At the same revision, a Python-originated update wins over a frontend-view update.
3. If two frontend views have the same revision, actor identifiers are compared lexicographically; the greater actor identifier wins.

Each frontend view has a unique actor identifier. A view creates its next update from the latest revision it has observed. Python-originated updates use actor `python`.

Stale or losing envelopes MUST be rejected, and the previously accepted state MUST be retained. The losing view MUST be reconciled to the accepted state rather than continuing to present its rejected snapshot as authoritative.

This is deterministic whole-snapshot conflict resolution, not collaborative editing. MathBlocks MUST NOT automatically merge concurrent component payloads. Domain-specific merge behavior, if ever required, must be introduced through a separately specified operation or contract.

### 5. Validation and atomicity

Synchronized payloads MUST be JSON-compatible and validated at trust boundaries.

- Invalid updates MUST NOT corrupt or replace the last accepted valid state.
- Nested Python mutation MUST NOT bypass Traitlets observation; callers must publish changes through the supported detached-state or setter API.
- The frontend MUST validate incoming envelopes before exposing their data to component views.
- Unsupported schema versions and malformed envelopes MUST produce explicit errors.
- Unknown fields MUST follow the documented versioned-contract policy.
- Non-JSON runtime objects and engine-native objects MUST NOT be placed directly in synchronized state.
- Mathematical structures whose fields must agree, such as LaTeX source and canonical expression data, MUST be validated and committed together.

An invalid update SHOULD produce a structured diagnostic. The frontend MUST NOT silently replace valid content with an invalid representation.

### 6. Frontend state and Jotai

Frontend code MUST distinguish:

1. Synchronized state received from the AnyWidget model.
2. Per-view local interaction state.
3. Derived presentation state.

Jotai atoms are frontend state-management mechanisms, not a second persistent data model. Derived atoms MUST NOT be treated as independently authoritative.

When synchronized state changes externally, affected views and derived state MUST update. Receiving a model update MUST NOT trigger an identical write-back loop.

Uncommitted editor interaction remains local to the view. A component may publish a validated domain-state update when its documented commit condition is met.

### 7. Component and view identity

A Python component instance has stable identity for its lifetime. Its identity is distinct from expression identity, state revision, DOM identity, and an individual frontend view's actor identifier.

Multiple frontend views of the same Python component instance MUST observe and update the same synchronized component state through the shared AnyWidget model. Each view MAY maintain its own transient interaction state and MUST use its own actor identifier for update ordering.

Ordinary state updates and frontend rerenders MUST NOT change the Python component identity.

### 8. Computation results and freshness

Computation results are externally supplied state. Their presence does not prove that they correspond to the current expression or inputs.

Where result freshness matters, the host or computation integration SHOULD associate a result with the expression/input revision for which it was produced. A view MUST NOT present a known-stale asynchronous result as the result of newer inputs.

Detailed request identifiers, cancellation, and asynchronous computation lifecycle are deferred to the computation integration contract; this ADR does not define an evaluator.

## Component lifecycle

### Construction and initialization

1. Python validates public constructor arguments.
2. The component establishes its initial synchronized state and stable identity.
3. The frontend initializes from the current state envelope when a view is created.
4. Frontend-local interaction state is initialized independently for that view.

A component MUST have a valid initial state before frontend interaction begins.

### Display and reconnection

Displaying or reconnecting a component MUST NOT create a second authoritative component state.

A newly created or reconnected view initializes from the current synchronized model state. It MUST NOT assume that any previous view's transient state is authoritative or reset valid Python-side state.

### Multiple views

All views attached to the same component instance share synchronized domain state. Transient interaction state and actor identity are per-view. Concurrent writes are resolved by the deterministic whole-snapshot ordering above; no automatic merge is performed.

### Disposal

Disposing a frontend view releases that view's event listeners, subscriptions, DOM resources, and transient interaction state using AnyWidget's supported lifecycle mechanism.

Disposing a view MUST NOT, by itself, delete the Python component or its synchronized state. Python-object lifetime and frontend-view lifetime are separate.

### Recovery

If a view encounters malformed or unsupported synchronized state, it MUST NOT silently overwrite the last accepted state. It SHOULD expose a recoverable error and reinitialize from the current accepted model state when possible.

## Compatibility and migration

- The synchronized state envelope is versioned independently of component-specific data schemas.
- Incompatible envelope changes require a new schema version and explicit migration support.
- Python and frontend assets ship together in the MathBlocks distribution and must agree on supported envelope versions.
- State migrations MUST preserve valid component data or report explicitly why migration cannot proceed.

## Alternatives considered

1. **Independent Python and JavaScript persistent state models.** Rejected: creates competing sources of truth and synchronization ambiguity.
2. **Partial patches as the initial transport.** Rejected: increases validation and conflict complexity; atomic snapshots are simpler to reason about and test.
3. **Automatic merging of concurrent snapshots.** Rejected: generic merging is unsafe for mathematical structures and does not define domain semantics.
4. **A single global frontend actor.** Rejected: multiple views need distinguishable origins for deterministic conflict ordering.
5. **Synchronizing all UI interaction state.** Rejected: cursor, focus, hover, and similar state are view-specific and should not be persisted by default.

## Consequences

### Positive

- A clear boundary between synchronized domain state and per-view interaction state.
- Consistent Python and frontend representations.
- Deterministic handling of concurrent whole-snapshot updates.
- Multiple views can share one component's domain state.
- Reconnection does not discard Python-owned component state.
- The initial protocol remains straightforward to validate and test.

### Trade-offs

- Whole-snapshot updates may transfer more data than patches.
- Concurrent edits are resolved by deterministic winner selection rather than merged.
- Components must validate internally consistent data before publishing it.
- Per-view interaction state is not automatically available to Python.

## Acceptance criteria

- [ ] Every public component documents its synchronized state and frontend-local state.
- [ ] Synchronized state uses the documented atomic versioned envelope.
- [ ] Python-side updates propagate to all views of the same component.
- [ ] Frontend-side accepted updates propagate to Python and sibling views.
- [ ] Invalid and stale updates do not corrupt previously accepted state.
- [ ] Concurrent snapshots follow deterministic revision/actor ordering.
- [ ] No automatic payload merge is performed.
- [ ] Nested Python mutation cannot bypass the synchronization contract.
- [ ] Jotai does not become a second persistent domain model.
- [ ] Reconnection initializes from the current accepted synchronized state.
- [ ] Disposing a view cleans up view resources without deleting the Python component state.
- [ ] Component identity remains stable across ordinary updates.
- [ ] Tests cover Python, frontend, multiple-view, and host lifecycle behavior.

## Deferred decisions

- Partial updates and patch protocols.
- Collaborative editing, CRDTs, and multi-user conflict resolution.
- Persistent document storage and cross-session identity.
- Detailed asynchronous computation request lifecycle.
- State migration tooling beyond the versioned compatibility contract.
- Whether specific high-volume components require measured optimizations to snapshot transport.

## References

- [ADR-001: AnyWidget component architecture](ADR-001-anywidget-component-architecture.md)
- [ADR-002: Canonical mathematical expression representation](ADR-002-expression-representation.md)
- [Python–frontend state contract](../state-contract.md)
- [AnyWidget documentation](https://anywidget.dev/)
- [Jotai documentation](https://jotai.org/)
