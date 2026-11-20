# Architecture notes

MathBlocks is a Python-first AnyWidget component library. Architecture decisions are recorded in [decisions/](decisions/).

## Accepted decisions

- [ADR-001: AnyWidget component architecture](decisions/ADR-001-anywidget-component-architecture.md)
- [ADR-002: Canonical mathematical expression representation](decisions/ADR-002-expression-representation.md)
- [ADR-004: State synchronization and component lifecycle](decisions/ADR-004-state-synchronization-and-lifecycle.md)

## Existing contracts

- [Python–frontend state contract](state-contract.md)
- [Compatibility and versioning policy](compatibility-and-versioning.md)

These accepted decisions establish the architectural direction for subsequent implementation. Implementation must still satisfy each ADR's acceptance criteria; they do not authorize merging or releasing the current pull request.
