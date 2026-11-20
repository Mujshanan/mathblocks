import pytest

from mathblocks import Math, Result, Text
from mathblocks.core.serialization import StateContractError


def test_math_component_uses_the_versioned_shared_state_envelope() -> None:
    widget = Math(r"x^2 + y^2 = z^2", label="Pythagorean theorem")

    assert widget.schema_version == 1
    assert widget.revision == 0
    assert widget.component_state == {
        "component": "math",
        "value": r"x^2 + y^2 = z^2",
        "read_only": False,
        "label": "Pythagorean theorem",
    }


def test_math_value_updates_use_the_python_revision_policy() -> None:
    widget = Math(r"x")
    widget.value = r"\frac{a}{b}"

    assert widget.value == r"\frac{a}{b}"
    assert widget.revision == 1
    assert widget.state["actor"] == "python"


def test_math_supports_static_rendering_and_validates_input() -> None:
    widget = Math(r"\int_0^1 x\,dx", read_only=True)

    assert widget.component_state["read_only"] is True
    with pytest.raises(TypeError):
        Math(42)  # type: ignore[arg-type]


def test_text_component_exposes_annotation_tone() -> None:
    widget = Text("Check the sign convention.", tone="note", label="Design note")

    assert widget.component_state == {
        "component": "text",
        "value": "Check the sign convention.",
        "label": "Design note",
        "tone": "note",
    }
    with pytest.raises(ValueError):
        Text("Unsupported tone", tone="loud")  # type: ignore[arg-type]


def test_result_component_supports_units_errors_and_diagnostics() -> None:
    result = Result(24.6, unit="MPa", diagnostics=["Within limit"], label="Stress")
    failure = Result(error="Calculation did not converge")

    assert result.component_state["value"] == 24.6
    assert result.component_state["unit"] == "MPa"
    assert result.component_state["diagnostics"] == ["Within limit"]
    assert failure.component_state["error"] == "Calculation did not converge"


def test_component_state_obeys_shared_json_validation() -> None:
    with pytest.raises(StateContractError):
        Result(object())
