# First components

Phase 2 adds the first user-facing components while preserving the Phase 1 versioned state envelope and conflict policy. Each component is a Python `MathBlocksWidget`; its domain fields are stored in `component_state` and synchronized through the shared envelope.

## Math

```python
from mathblocks import Math

editable = Math(r"\sigma = \frac{P}{A}", label="Normal stress")
static = Math(r"\int_0^1 x^2\,dx = \frac{1}{3}", read_only=True)
```

- Editable mode uses MathLive and publishes LaTeX changes through `commitState` and the existing revision policy.
- `read_only=True` uses KaTeX for static rendering.
- `value` contains LaTeX source. Assigning to it creates a Python-originated state revision.
- The editor stays mounted for its own keystrokes so cursor position and virtual-keyboard state are not reset.

## Text

```python
from mathblocks import Text

annotation = Text("Verify the support conditions.", tone="note", label="Design note")
```

Supported tones are `default`, `muted`, `note`, and `warning`. Content is inserted as text, not interpreted as HTML.

## Result

```python
from mathblocks import Result

result = Result(
    24.6,
    unit="MPa",
    label="Concrete compressive stress",
    diagnostics=["Below the specified limit"],
)
failure = Result(error="Calculation did not converge")
```

A result can show a value and unit, an error message, and zero or more diagnostic messages. Errors use an assertive live region; ordinary results use a polite live region.

## State contract

The Phase 1 envelope remains authoritative:

- `schema_version`, `revision`, `actor`, and `data` remain owned by the shared synchronization layer.
- Component-specific fields live inside `data`; the discriminator is `component`.
- Python updates use `MathBlocksWidget.set_component_state` and increment the shared revision.
- Browser edits use `commitState` with a per-view actor ID; the existing deterministic conflict policy remains in force.
- Focus, selection, and virtual-keyboard state remain transient browser state.

The component layer does not introduce a second state format, its own revision counter, or a separate synchronization mechanism.

## Examples and development

Run `examples/first_components.py` in a Jupyter environment with the frontend assets built. For frontend-only work, `npm run dev` starts a MathLive playground using the same component renderer.
