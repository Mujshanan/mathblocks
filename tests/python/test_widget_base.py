import pytest
from traitlets import TraitError

from mathblocks.core.serialization import StateContractError, make_state_envelope
from mathblocks.widgets import MathBlocksWidget


def test_widget_exposes_versioned_anywidget_state() -> None:
    widget = MathBlocksWidget()

    assert widget.schema_version == 1
    assert widget.revision == 0
    assert widget.component_state == {}
    assert widget.state == {
        "schema_version": 1,
        "revision": 0,
        "actor": "python",
        "data": {},
    }


def test_widget_can_be_initialized_with_explicit_state() -> None:
    initial = make_state_envelope({"value": "provided"}, revision=4, actor="python")
    widget = MathBlocksWidget(state=initial)

    assert widget.component_state == {"value": "provided"}
    assert widget.revision == 4


def test_python_updates_publish_new_detached_revisions() -> None:
    widget = MathBlocksWidget()

    source = {"value": 12, "nested": {"items": [1, 2]}}
    widget.component_state = source
    source["nested"]["items"].append(3)

    assert widget.component_state == {"value": 12, "nested": {"items": [1, 2]}}
    assert widget.revision == 1

    returned = widget.component_state
    returned["value"] = 99
    assert widget.component_state["value"] == 12

    widget.set_component_state({"value": 13})
    assert widget.revision == 2
    assert widget.component_state == {"value": 13}


def test_widget_instances_do_not_share_state() -> None:
    first = MathBlocksWidget()
    second = MathBlocksWidget()

    first.component_state = {"value": 12}

    assert first.component_state == {"value": 12}
    assert second.component_state == {}
    assert second.revision == 0


def test_frontend_originated_update_is_accepted() -> None:
    widget = MathBlocksWidget()

    widget.state = make_state_envelope(
        {"value": "from browser"},
        revision=1,
        actor="view:alpha",
    )

    assert widget.component_state == {"value": "from browser"}
    assert widget.revision == 1


def test_stale_concurrent_frontend_update_is_rejected_deterministically() -> None:
    widget = MathBlocksWidget()

    widget.state = make_state_envelope(
        {"value": "winner"},
        revision=1,
        actor="view:zeta",
    )
    widget.state = make_state_envelope(
        {"value": "stale"},
        revision=1,
        actor="view:alpha",
    )

    assert widget.component_state == {"value": "winner"}
    assert widget.state["actor"] == "view:zeta"


def test_python_wins_equal_revision_conflict() -> None:
    widget = MathBlocksWidget()

    widget.state = make_state_envelope(
        {"value": "python"},
        revision=2,
        actor="python",
    )
    widget.state = make_state_envelope(
        {"value": "browser"},
        revision=2,
        actor="view:zeta",
    )

    assert widget.component_state == {"value": "python"}
    assert widget.state["actor"] == "python"


@pytest.mark.parametrize(
    "invalid_state",
    [
        {"schema_version": 2, "revision": 0, "actor": "python", "data": {}},
        {"schema_version": 1.0, "revision": 0, "actor": "python", "data": {}},
        {"schema_version": 1, "revision": True, "actor": "python", "data": {}},
        {"schema_version": 1, "revision": -1, "actor": "python", "data": {}},
        {"schema_version": 1, "revision": 0, "actor": "", "data": {}},
        {"schema_version": 1, "revision": 0, "actor": "python", "data": []},
        {"schema_version": 1, "revision": 0, "actor": "python", "data": {}, "extra": 1},
    ],
)
def test_invalid_wire_state_is_rejected(invalid_state: dict) -> None:
    widget = MathBlocksWidget()

    with pytest.raises(TraitError):
        widget.state = invalid_state


def test_non_json_values_are_rejected() -> None:
    widget = MathBlocksWidget()

    with pytest.raises(StateContractError):
        widget.component_state = {"not_json": object()}


def test_unsafe_integers_and_cyclic_values_are_rejected() -> None:
    widget = MathBlocksWidget()

    with pytest.raises(StateContractError):
        widget.component_state = {"unsafe": 2**53}

    cyclic: dict = {}
    cyclic["self"] = cyclic
    with pytest.raises(StateContractError):
        widget.component_state = cyclic


def test_widget_has_frontend_module() -> None:
    widget = MathBlocksWidget()

    assert "as default" in widget._esm
    assert "change:state" in widget._esm


def test_synchronized_state_rejects_in_place_mutation() -> None:
    widget = MathBlocksWidget(
        state=make_state_envelope({"nested": {"items": [1, 2]}}, revision=1)
    )

    with pytest.raises(TypeError, match="read-only"):
        widget.state["data"]["nested"]["value"] = "bypass"

    with pytest.raises(TypeError, match="read-only"):
        widget.state["data"]["nested"]["items"].append(3)

    assert widget.component_state == {"nested": {"items": [1, 2]}}
    assert widget.revision == 1
