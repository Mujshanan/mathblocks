"""Host-neutral AnyWidget integration smoke tests."""

from __future__ import annotations

import anywidget

from mathblocks import Diagram, Graph, Math, Matrix, Result, Text, Vector


def test_all_public_components_are_native_anywidgets() -> None:
    components = [
        Math(r"\sigma = \frac{P}{A}"),
        Text("Annotation"),
        Result(12.5, unit="MPa"),
        Matrix([[1, 2], [3, 4]]),
        Vector([1, 2, 3]),
        Graph([{"label": "series", "points": [[0, 0], [1, 1]]}]),
        Diagram([{"id": "a", "label": "A", "x": 10, "y": 20}]),
    ]

    assert all(isinstance(component, anywidget.AnyWidget) for component in components)


def test_widget_has_bundled_frontend_assets_and_synchronized_state() -> None:
    widget = Matrix([[1, 2], [3, 4]])

    assert "render" in widget._esm
    assert widget._css
    assert widget.state["schema_version"] == 1
    assert widget.component_state["component"] == "matrix"
