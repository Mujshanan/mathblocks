"""Optional Marimo convenience integration.

Marimo natively supports AnyWidget. This adapter is deliberately thin: it
wraps an existing MathBlocks AnyWidget in Marimo's reactive UIElement without
introducing another state store or changing the widget's wire contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mathblocks.widgets import MathBlocksWidget


def as_marimo(widget: MathBlocksWidget) -> Any:
    """Wrap a MathBlocks widget as a reactive Marimo UI element.

    Marimo is an optional dependency. Install it with
    pip install mathblocks[marimo].

    The returned Marimo element exposes the wrapped AnyWidget as .widget.
    The MathBlocks component value remains available on
    element.widget.value / element.widget.component_state.
    """
    from mathblocks.widgets import MathBlocksWidget as _MathBlocksWidget

    if not isinstance(widget, _MathBlocksWidget):
        raise TypeError("as_marimo() expects a MathBlocksWidget instance")

    try:
        import marimo as mo
    except ImportError as exc:
        raise ImportError(
            'Marimo integration requires the optional dependency. '
            'Install it with: pip install "mathblocks[marimo]"'
        ) from exc

    return mo.ui.anywidget(widget)
