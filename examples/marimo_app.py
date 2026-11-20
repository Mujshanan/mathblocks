"""Run with marimo run examples/marimo_app.py.

Install the optional host integration first:
    pip install "mathblocks[marimo]"
"""

import marimo as mo

from mathblocks import Diagram, Graph, Matrix, Result, Vector
from mathblocks.integrations import as_marimo

app = mo.App()


@app.cell
def _():
    matrix = as_marimo(Matrix([[1200, -600], [-600, 1200]], label="Stiffness matrix"))
    vector = as_marimo(Vector([0.0, 0.012], label="Displacement"))
    graph = as_marimo(
        Graph(
            [{"label": "Deflection", "points": [[0, 0], [1, 4], [2, 0]]}],
            title="Illustrative response",
            x_label="Span (m)",
            y_label="Deflection (mm)",
        )
    )
    diagram = as_marimo(
        Diagram(
            nodes=[
                {"id": "load", "label": "Load", "x": 40, "y": 100},
                {"id": "beam", "label": "Beam", "x": 300, "y": 100, "shape": "ellipse"},
            ],
            edges=[{"source": "load", "target": "beam", "label": "P"}],
            label="Load path",
        )
    )
    result = as_marimo(Result(24.6, unit="MPa", label="Stress"))
    mo.vstack([matrix, vector, graph, diagram, result])
    return matrix, vector, graph, diagram, result


@app.cell
def _(matrix, vector, graph, diagram, result):
    # Access the live AnyWidget-backed state from reactive Marimo cells.
    mo.md(
        f"""
        **Current matrix:** {matrix.widget.value}

        **Current vector:** {vector.widget.value}

        **Current graph data:** {graph.widget.value}

        **Current diagram data:** {diagram.widget.value}

        **Current result:** {result.widget.value}
        """
    )
    return


if __name__ == "__main__":
    app.run()
