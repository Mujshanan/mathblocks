"""Runnable examples for MathBlocks structured and visual components."""
from IPython.display import display

from mathblocks import Diagram, Graph, Matrix, Vector

stiffness = Matrix([[1200, -600], [-600, 1200]], label="Stiffness matrix")
displacement = Vector([0.0, 0.012, 0.0], label="Nodal displacement")
response = Graph(
    [
        {"label": "Shear", "points": [[0, 0], [1, 12], [2, 0], [3, -12], [4, 0]]},
        {"label": "Moment", "points": [[0, 0], [1, 8], [2, 16], [3, 8], [4, 0]]},
    ],
    title="Illustrative beam response",
    x_label="Span (m)",
    y_label="Response",
)
load_path = Diagram(
    nodes=[
        {"id": "load", "label": "Applied load", "x": 40, "y": 90},
        {"id": "beam", "label": "Beam", "x": 320, "y": 90, "shape": "ellipse"},
        {"id": "support", "label": "Support", "x": 600, "y": 90},
    ],
    edges=[
        {"source": "load", "target": "beam", "label": "P"},
        {"source": "beam", "target": "support", "label": "R"},
    ],
    label="Load path",
)

for component in (stiffness, displacement, response, load_path):
    display(component)
