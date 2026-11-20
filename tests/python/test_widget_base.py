from anywidget import AnyWidget

from mathblocks.widgets import MathBlocksWidget


def test_widget_base_is_an_anywidget() -> None:
    widget = MathBlocksWidget()
    assert isinstance(widget, AnyWidget)


def test_widget_state_is_synchronized_and_instance_local() -> None:
    first = MathBlocksWidget()
    second = MathBlocksWidget()

    first.component_state = {"value": 12}

    assert first.schema_version == 1
    assert first.component_state == {"value": 12}
    assert second.component_state == {}


def test_widget_has_frontend_module() -> None:
    widget = MathBlocksWidget()

    assert "export default" in widget._esm
    assert "render" in widget._esm
