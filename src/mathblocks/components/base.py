"""Shared base for Python-facing MathBlocks components."""
from __future__ import annotations

from typing import Any

from mathblocks.core.serialization import make_state_envelope
from mathblocks.widgets import MathBlocksWidget


class ComponentWidget(MathBlocksWidget):
    """AnyWidget component whose domain fields live inside the Phase 1 state envelope."""

    def __init__(self, *, component: str, value: Any, **fields: Any) -> None:
        data = {"component": component, "value": self._validate_value(value), **fields}
        super().__init__(state=make_state_envelope(data))

    def _validate_value(self, value: Any) -> Any:
        """Normalize/validate a component value before publishing it."""
        return value

    @property
    def value(self) -> Any:
        """Current component value, including accepted browser-originated edits."""
        return self.component_state.get("value")

    @value.setter
    def value(self, value: Any) -> None:
        self.set_component_state({**self.component_state, "value": self._validate_value(value)})
