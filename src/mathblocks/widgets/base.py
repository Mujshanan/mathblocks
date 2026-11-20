"""Shared AnyWidget adapter base for all MathBlocks components."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anywidget
from traitlets import Dict

_STATIC = Path(__file__).resolve().parents[1] / "static"


class MathBlockWidget(anywidget.AnyWidget):
    """Base widget with a versioned, JSON-compatible state contract."""

    _esm = _STATIC / "index.js"
    _css = _STATIC / "index.css"
    state = Dict(default_value={}).tag(sync=True)

    def __init__(self, *, component: str, value: Any, **options: Any) -> None:
        state = {"schemaVersion": 1, "type": component, "value": value, **options}
        try:
            json.dumps(state)
        except (TypeError, ValueError) as exc:
            raise TypeError("MathBlocks component state must be JSON serializable") from exc
        super().__init__(state=state)

    @property
    def value(self) -> Any:
        return self.state.get("value")

    @value.setter
    def value(self, value: Any) -> None:
        state = {**self.state, "value": value}
        try:
            json.dumps(state)
        except (TypeError, ValueError) as exc:
            raise TypeError("MathBlocks component state must be JSON serializable") from exc
        self.state = state
