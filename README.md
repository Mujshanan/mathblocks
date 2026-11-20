# MathBlocks

**Reusable mathematical interface components for Python.**

MathBlocks is a Python-first toolkit for building interactive mathematical and scientific interfaces. Its TypeScript frontend is bundled inside the Python package through AnyWidget.

> Project status: Phases 0–5 are implemented in the development branch. The API and release checks are in place, but MathBlocks remains a pre-release development project and has not yet been published to PyPI.

## Installation

The intended installation after publication is:

```bash
pip install mathblocks
```

The development branch is not yet available from PyPI. To work from a source checkout, build the frontend assets and install the project locally as described in [Development](#development).

No Node.js or frontend build tools are required by end users installing a built wheel or source distribution. The distribution includes the compiled frontend assets. Node.js is a development/build requirement only.

For Marimo, install the optional extra after release:

```bash
pip install "mathblocks[marimo]"
```

## Quick start

```python
from IPython.display import display
from mathblocks import Diagram, Graph, Math, Matrix, Result, Text, Vector

display(Math(r"\sigma = \frac{P}{A}"))
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

## Host integrations

- **Jupyter Notebook / JupyterLab:** display components directly with IPython's display function.
- **Marimo:** use the optional `as_marimo(widget)` adapter for reactive Marimo UI elements.
- **Other AnyWidget hosts:** use the components directly as AnyWidget instances.

See [Host integrations](docs/development/host-integrations.md) for examples, requirements, and the host compatibility boundary.

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

## Architecture and compatibility

Python owns the public API, domain state, validation, and serialization. AnyWidget provides transport and view lifecycle. The bundled TypeScript frontend provides editing, plotting, SVG rendering, and interaction.

The versioned state envelope remains the single synchronization contract. Component data is stored in `data`; focus, selection, pointer state, and hover remain transient browser state. Browser edits use the existing per-view actor and revision policy. Python wins equal-revision conflicts. There is no CRDT or component-specific revision mechanism.

Marimo's adapter wraps the same AnyWidget instance and does not create a parallel component state store.

- [Public Python API](docs/architecture/public-api.md)
- [Compatibility and versioning policy](docs/architecture/compatibility-and-versioning.md)
- [State contract](docs/architecture/state-contract.md)

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

To test the optional Marimo integration:

```bash
python -m pip install -e ".[dev,marimo]"
pytest tests/integration
```

For package verification and the release procedure, see [Release readiness](docs/development/release.md).

CI builds the frontend, checks TypeScript, runs Python tests on 3.11–3.13, verifies wheel and source-distribution contents, smoke-tests both install formats, and separately tests the Marimo host adapter.

## Milestones

- [x] Phase 0 — package and CI foundation
- [x] Phase 1 — AnyWidget state and lifecycle foundation
- [x] Phase 2 — Math, Text, and Result
- [x] Phase 3 — Matrix, Vector, Graph, Diagram, validation, and serialization tests
- [x] Phase 4 — Jupyter/AnyWidget and Marimo host integrations
- [x] Phase 5 — stability and release readiness (PyPI publication deferred)

Phases 1–5 are proposed in a dependency-ordered series of draft pull requests. They remain unmerged. Phase 5 prepares release artifacts and procedures; it does not publish to PyPI.
