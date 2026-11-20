# First components

MathBlocks Phase 2 provides three Python-facing components. Each is an independent AnyWidget with a versioned JSON state object; Python can inspect or update the value through the widget's `.value` property.

## Math

```python
from mathblocks import Math

editable = Math(r"\sigma = \frac{P}{A}", label="Normal stress")
static = Math(r"\int_0^1 x^2\,dx = \frac{1}{3}", read_only=True)
```

- Editable mode uses MathLive and syncs LaTeX source back to Python.
- `read_only=True` uses KaTeX for static rendering.
- The `value` property always contains the LaTeX source.

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

Every component syncs a JSON object with `schemaVersion: 1`, a `type` discriminator, and a `value`. Additional fields are component-specific. The browser owns transient editing details (focus, selection, and virtual keyboard state); Python owns the synchronized component value. MathLive input changes are sent through the AnyWidget model, and Python-originated state changes rerender the view.

## Examples and installation

Run `python examples/first_components.py` in an environment with an AnyWidget-compatible display, or copy its cell contents into Jupyter. Install the development checkout with `python -m pip install -e ".[dev]"`; build the frontend first with `npm install && npm run build`. End users will not need Node.js once the wheel is built and published.
