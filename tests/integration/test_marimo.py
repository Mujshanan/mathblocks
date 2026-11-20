"""Optional Marimo host integration tests."""

from __future__ import annotations

import pytest

marimo = pytest.importorskip("marimo")

from mathblocks import Matrix, Math  # noqa: E402
from mathblocks.integrations import as_marimo  # noqa: E402


def test_as_marimo_wraps_mathblocks_widget_without_replacing_it() -> None:
    widget = Matrix([[1, 2], [3, 4]], label="Matrix")
    element = as_marimo(widget)

    assert element.widget is widget
    assert element.widget.component_state["value"] == [[1, 2], [3, 4]]


def test_as_marimo_supports_math_component() -> None:
    widget = Math(r"\sigma = \frac{P}{A}")
    element = as_marimo(widget)

    assert element.widget is widget
    assert element.widget.component_state["component"] == "math"


def test_as_marimo_rejects_non_mathblocks_objects() -> None:
    with pytest.raises(TypeError, match="MathBlocksWidget"):
        as_marimo(object())  # type: ignore[arg-type]
