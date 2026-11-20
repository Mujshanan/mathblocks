# ADR-001: AnyWidget component architecture

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owners:** MathBlocks maintainers
- **Scope:** Public Python API, widget ownership, frontend lifecycle, and host adapters
- **Architectural reference:** [WigglyStuff](https://github.com/koaning/wigglystuff)

## Context

MathBlocks is a Python-first mathematical UI component library built on AnyWidget. WigglyStuff is the project's architectural reference for building Python-facing interactive components with AnyWidget.

The initial design has separate `components/`, `widgets/base.py`, and `core/models.py` areas. These are useful only if their responsibilities are distinct. The public API must not make users guess whether a component is itself an AnyWidget or a wrapper around one.

Jupyter usage should display a component directly. Marimo usage should adapt that same component with `mo.ui.anywidget(component)`; the Marimo wrapper is a host integration object, not an inner widget exposed by MathBlocks.

## Decision

**Every public MathBlocks component MUST inherit from the shared `MathBlocksWidget` base, which itself inherits from `anywidget.AnyWidget`. A public component is the widget; it does not wrap another widget.**

The shared base is the only supported inheritance path for public components. Components must not inherit directly from AnyWidget, because doing so would bypass shared MathBlocks lifecycle and synchronization behavior.

Example:

```python
from mathblocks import Math

equation = Math(latex=r"x^2 + y^2 = z^2")
equation
```

Marimo adapts the same instance:

```python
import marimo as mo
from mathblocks import Math

equation = Math(latex=r"x^2 + y^2 = z^2")
mo_equation = mo.ui.anywidget(equation)
```

There is no public `.widget` property and no second MathBlocks widget instance.

## Responsibilities and package boundaries

### Public components — `src/mathblocks/components/`

- Define user-facing component classes and component-specific traits.
- Inherit from `MathBlocksWidget`.
- Validate component-specific inputs and expose a stable Python API.
- Declare the frontend component identity/configuration needed by the shared renderer.
- Avoid host-specific behavior and duplicated widget lifecycle code.

Examples include `Math`, `Text`, `Result`, `Matrix`, `Vector`, `Graph`, and `Diagram`. This list does not commit their implementation order.

### Shared widget base — `src/mathblocks/widgets/base.py`

- Inherit from `anywidget.AnyWidget`.
- Own the common AnyWidget trait and message boundary.
- Provide common initialization, synchronization, and lifecycle integration.
- Load packaged frontend assets.
- Delegate domain validation to framework-independent core contracts.

The base must remain small. It must not become a mathematical evaluator or a host abstraction framework.

### Core models — `src/mathblocks/core/`

- Define framework-independent domain and protocol data structures.
- Define validation, serialization, and versioned contracts.
- Avoid AnyWidget, Traitlets, notebook, and host-specific imports.
- Remain independently testable in ordinary Python processes.

### Host integrations — `src/mathblocks/integrations/`

- Provide optional host adapters only where the host offers value beyond direct AnyWidget support.
- Wrap the existing component instance; do not clone it or create a second MathBlocks component.
- Import optional host dependencies lazily.
- Keep AnyWidget direct display as the primary integration path.

The Marimo adapter should be equivalent to:

```python
def as_marimo(component):
    import marimo as mo
    return mo.ui.anywidget(component)
```

It must validate that the argument is a MathBlocks component and preserve object identity. Marimo's wrapper may expose Marimo-specific reactive values; those are not a replacement for the component's Python traits.

## Frontend packaging and loading

The frontend is the view and interaction layer for the Python component. The Python component remains the public object and owns the synchronized model.

The frontend packaging strategy (one shared bundle versus component-specific bundles) is intentionally not decided here. It must be selected through a separate measured decision that considers duplicated dependencies, custom-element registration, first-use loading cost, cacheability, and package size.

Regardless of bundle strategy:

- Runtime assets must be included in the Python distributions.
- End users must not need Node.js or npm.
- Required fonts and CSS must be locally available; runtime CDN dependencies are not permitted.
- Host theme integration and style isolation must be tested in supported notebook hosts.
- Per-view resources must be cleaned up using AnyWidget's supported lifecycle mechanism.

## Alternatives considered

1. **A Python wrapper containing an AnyWidget.** Rejected: creates two objects for one component and makes direct display and host adaptation inconsistent.
2. **Each component independently subclasses AnyWidget.** Rejected: duplicates shared lifecycle and synchronization behavior and permits inconsistent implementations.
3. **Every component inherits from a shared AnyWidget base.** Selected: one public object, one integration model, and one shared lifecycle boundary.
4. **Implement a custom `_repr_mimebundle_` instead of AnyWidget.** Rejected as the primary design: duplicates host display and lifecycle responsibilities already provided by AnyWidget.

## Consequences

- A component can be displayed directly in Jupyter and passed unchanged to a host adapter.
- The shared base becomes a stable internal dependency for all components.
- Component domain models remain independent of notebook infrastructure.
- The base class must be carefully kept generic and must not absorb component-specific behavior.
- AnyWidget's public lifecycle and synchronization APIs become explicit dependencies.

## Acceptance criteria

- [ ] Every public component inherits from `MathBlocksWidget`.
- [ ] `MathBlocksWidget` inherits from `anywidget.AnyWidget`.
- [ ] A component instance is directly displayable; no `.widget` property is required.
- [ ] The Marimo adapter wraps the same instance with `mo.ui.anywidget(component)`.
- [ ] The adapter does not clone the component or maintain a second synchronized state.
- [ ] Core models import without AnyWidget or notebook dependencies.
- [ ] Optional host dependencies are imported lazily.
- [ ] Packaged frontend assets load without Node.js on the user's machine.
- [ ] Real-host smoke tests cover direct display and interaction.

## References

- [WigglyStuff](https://github.com/koaning/wigglystuff) — architectural reference; source-level practices must be verified before being attributed to it.
- [AnyWidget documentation](https://anywidget.dev/)
- [Marimo AnyWidget integration](https://docs.marimo.io/api/inputs/anywidget/)
