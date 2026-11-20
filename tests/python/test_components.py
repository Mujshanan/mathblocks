import pytest

from mathblocks import Math, Result, Text


def test_math_component_exposes_editable_latex_state():
    widget = Math(r"x^2 + y^2 = z^2", label="Pythagorean theorem")
    assert widget.state == {
        "schemaVersion": 1,
        "type": "math",
        "value": r"x^2 + y^2 = z^2",
        "readOnly": False,
        "label": "Pythagorean theorem",
    }
    widget.value = r"\frac{a}{b}"
    assert widget.state["value"] == r"\frac{a}{b}"


def test_math_can_be_static():
    assert Math(r"\int_0^1 x\,dx", read_only=True).state["readOnly"] is True


def test_text_state_and_tone_validation():
    assert Text("A note", tone="note").state["tone"] == "note"
    with pytest.raises(ValueError):
        Text("bad tone", tone="loud")


def test_result_keeps_units_errors_and_diagnostics():
    widget = Result(12.5, unit="kN", diagnostics=["Within limit"], label="Shear")
    assert widget.state["value"] == 12.5
    assert widget.state["unit"] == "kN"
    assert widget.state["diagnostics"] == ["Within limit"]
    assert Result(error="Not converged").state["error"] == "Not converged"


def test_component_values_must_be_json_serializable():
    with pytest.raises(TypeError, match="JSON serializable"):
        MathBlockWidgetForTest([object()])


def MathBlockWidgetForTest(value):
    from mathblocks.widgets.base import MathBlockWidget
    return MathBlockWidget(component="text", value=value)
