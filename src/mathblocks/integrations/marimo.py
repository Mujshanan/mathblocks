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

    Read the synchronized trait snapshot through the returned element's
    .value property to establish Marimo reactive dependencies. The original
    AnyWidget is available as .widget; its component_state property exposes
    the current Python-side component data directly.
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
