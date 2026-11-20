"""Display MathBlocks components in Jupyter Notebook or JupyterLab."""

from IPython.display import display

from mathblocks import Diagram, Graph, Matrix, Math, Result, Text, Vector

display(Math(r"\sigma = \frac{P}{A}", label="Normal stress"))
display(Text("Illustrative values only.", tone="note"))
display(Result(24.6, unit="MPa", label="Stress"))
display(Matrix([[1200, -600], [-600, 1200]], label="Stiffness matrix"))
display(Vector([0.0, 0.012], label="Displacement"))
display(Graph([{"label": "Response", "points": [[0, 0], [1, 4], [2, 0]]}]))
display(
    Diagram(
        nodes=[
            {"id": "load", "label": "Load", "x": 40, "y": 100},
            {"id": "beam", "label": "Beam", "x": 300, "y": 100, "shape": "ellipse"},
        ],
        edges=[{"source": "load", "target": "beam", "label": "P"}],
    )
)
