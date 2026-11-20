# Phase 1 — AnyWidget foundation

Phase 1 implements the shared state and lifecycle layer used by all MathBlocks
components. It intentionally uses a JSON state inspector as a small
interactive demonstration; it does not introduce the MathLive editor or any
component-specific mathematical behavior.

## Implemented

- One atomic, versioned state envelope synchronized through AnyWidget.
- Python validation, JSON normalization, detached state access, and
  Python-originated revisions.
- Frontend model subscriptions and frontend-originated updates.
- Deterministic whole-state conflict resolution for concurrent views.
- Per-view actor identities and isolated frontend view lifecycle.
- Explicit cleanup of model subscriptions and DOM event handlers through AnyWidget's per-view AbortSignal.
- Python and TypeScript tests for validation, synchronization, conflicts,
  multiple views, multiple widget instances, and cleanup.

## Run the demonstration

MathBlocks requires AnyWidget 0.11 or newer for its AbortSignal-based view lifecycle.

Build the frontend and install the package in editable mode:

```bash
npm install
npm run build
python -m pip install -e ".[dev]"
```

In a Jupyter notebook:

```python
from IPython.display import display
from mathblocks.widgets import MathBlocksWidget

widget = MathBlocksWidget()
display(widget)
```

Edit the JSON object in the widget and apply it. The state is synchronized
back to Python:

```python
widget.component_state
widget.component_state = {"value": 42, "unit": "MPa"}
```

Multiple displays of the same widget share the synchronized model state.
Different widget instances do not share component state.

## Validation

```bash
npm run build
npm run typecheck
npm test
pytest
python -m build
```

## Phase 1 exit criteria

- [x] Define the Python-to-frontend data contract and serialization rules.
- [x] Implement frontend initialization, update handling, and cleanup.
- [x] Handle Python-originated updates and frontend-originated updates.
- [x] Test multiple widget instances and multiple views without shared mutable state.
- [x] Demonstrate a minimal interactive AnyWidget state editor.

## Known boundary

The conflict policy is deterministic whole-object last-writer-wins based on
logical revision and actor priority. It is not a CRDT and does not merge
simultaneous edits to different fields. A future collaborative component
must introduce an explicit merge strategy at its domain layer.
