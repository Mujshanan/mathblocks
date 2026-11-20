# MathBlocks

**Reusable mathematical interface components for Python.**

MathBlocks is a Python-first toolkit for building interactive mathematical and scientific interfaces. Its TypeScript frontend is bundled inside the Python package through AnyWidget.

> Project status: Phase 3 structured and visual components are implemented on the phase-3 development branch. Math, Text, Result, Matrix, Vector, Graph, and Diagram are available in the proposed implementation.

## Installation

Once published on PyPI:

```bash
pip install mathblocks
```

No Node.js or frontend build tools are required by end users. The published wheel includes compiled frontend assets. Node.js is a development/build requirement only.

## Quick start

```python
from IPython.display import display
from mathblocks import Diagram, Graph, Math, Matrix, Result, Text, Vector

display(Math(r"\\sigma = \\frac{P}{A}"))
display(Text("Check the sign convention.", tone="note"))
display(Result(24.6, unit="MPa"))
display(Matrix([[1, 2], [3, 4]], label="Matrix"))
display(Vector([1, 2, 3], label="Vector"))
display(Graph([{"label": "Load", "points": [[0, 0], [1, 12], [2, 8]]}]))
display(Diagram(
    nodes=[{"id": "a", "label": "A", "x": 40, "y": 60},
           {"id": "b", "label": "B", "x": 280, "y": 60}],
    edges=[{"source": "a", "target": "b"}],
))
```

## Component guide

| Component | Purpose |
|---|---|
| Math | Editable MathLive input and static KaTeX rendering |
| Text | Safe explanatory annotations |
| Result | Values, units, errors, and diagnostics |
| Matrix | Rectangular structured data editing |
| Vector | One-dimensional structured data editing |
| Graph | Interactive SVG plotting and point inspection |
| Diagram | Editable node-and-edge surface with SVG export |

See [First components](docs/components/first-components.md) and [Structured and visual components](docs/components/structured-visual.md).

## Architecture

Python owns the public API, domain state, validation, and serialization. AnyWidget provides transport and view lifecycle. The bundled TypeScript frontend provides editing, plotting, SVG rendering, and interaction.

The versioned state envelope remains the single synchronization contract. Component data is stored in data; focus, selection, pointer state, and hover remain transient browser state. Browser edits use the existing per-view actor and revision policy. Python wins equal-revision conflicts. There is no CRDT or component-specific revision mechanism.

## Development

Requirements: Python 3.11+, Node.js 22.12+ and npm.

```bash
npm install
npm run build
npm run typecheck
npm test
python -m pip install -e ".[dev]"
pytest
```

CI builds the frontend, checks TypeScript, runs frontend tests, runs Python tests on 3.11–3.13, and verifies the wheel contains the compiled assets.

## Milestones

- [x] Phase 0 — package and CI foundation
- [x] Phase 1 — AnyWidget state and lifecycle foundation
- [x] Phase 2 — Math, Text, and Result
- [x] Phase 3 — Matrix, Vector, Graph, Diagram, validation, and serialization tests
- [ ] Phase 4 — host integrations
- [ ] Phase 5 — stability and release

Phase 3 implementation is proposed in a draft pull request. Existing Phase 1 and Phase 2 pull requests remain unmerged.
