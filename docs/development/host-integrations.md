# Phase 4 — Host integrations

MathBlocks components are native AnyWidget instances. The AnyWidget protocol is
the host boundary; MathBlocks does not maintain separate Jupyter, JupyterLab,
or VS Code widget implementations.

## Installation

The standard installation contains the Python API and compiled frontend assets:

```bash
pip install mathblocks
```

For Marimo, install its optional integration extra:

```bash
pip install "mathblocks[marimo]"
```

End users do not need Node.js or npm. The frontend is compiled into the wheel
during package release/build.

## Jupyter Notebook and JupyterLab

Display components directly using IPython display:

```python
from IPython.display import display
from mathblocks import Matrix, Graph

matrix = Matrix([[1200, -600], [-600, 1200]], label="Stiffness matrix")
graph = Graph([{"label": "Response", "points": [[0, 0], [1, 4], [2, 0]]}])

display(matrix)
display(graph)
```

The Python kernel and the notebook server must use the environment in which
MathBlocks is installed. No Jupyter server extension or frontend labextension
is required by MathBlocks; AnyWidget supplies the widget transport.

## Marimo

Marimo supports AnyWidget and provides a reactive wrapper. MathBlocks includes
a small optional adapter so notebooks can use one explicit integration call:

```python
import marimo as mo
from mathblocks import Matrix
from mathblocks.integrations import as_marimo

matrix = as_marimo(Matrix([[1, 2], [3, 4]], label="Matrix"))
matrix
```

The returned Marimo UI element exposes the original AnyWidget as
`matrix.widget`. Read `matrix.value` in downstream Marimo cells to register
reactive dependencies; it is the synchronized trait snapshot, with component
data under `matrix.value["state"]["data"]`. The original widget's
`matrix.widget.component_state` property exposes the current Python-side
component data directly. The wrapper does not create a second component state
store or alter the MathBlocks versioned envelope.

A complete runnable example is in [marimo_app.py](../../examples/marimo_app.py):

```bash
marimo run examples/marimo_app.py
```

## Other AnyWidget hosts

In other compatible hosts, display or embed the component as a normal
AnyWidget. MathBlocks does not add host-specific code or dependencies for
these environments. Host compatibility depends on that host's AnyWidget
support and version.

AnyWidget documents support for Jupyter Notebook, JupyterLab, Google Colab,
VS Code, and Marimo. This is protocol-level compatibility, not a guarantee
that every host/version combination has been manually browser-tested by
MathBlocks.

## State and lifecycle contract

- Python remains authoritative for validation and accepted component state.
- The single versioned JSON envelope is the only synchronized state contract.
- Marimo wraps the original widget; it does not fork or mirror the component
  state inside MathBlocks.
- View-local focus, hover, and pointer state remain transient frontend state.
- Each host is responsible for mounting and disposing its widget view through
  the AnyWidget lifecycle contract.

## Validation

The integration tests verify that all public components are native AnyWidget
instances and that bundled assets are attached. When the optional Marimo
dependency is installed, tests also verify the Marimo adapter and wrapped
widget identity.

```bash
python -m pip install ".[dev,marimo]"
pytest
```

The release CI builds frontend assets, tests the Python package on supported
Python versions, runs a Marimo integration smoke test, and checks that the
wheel contains the frontend assets. Interactive browser testing across every
third-party host remains outside this milestone.
