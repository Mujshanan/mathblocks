"""Computed value, unit, and diagnostic display component."""
from __future__ import annotations

from typing import Any, Sequence

from ..widgets.base import MathBlockWidget


class Result(MathBlockWidget):
    """Display a value with an optional unit, error, and diagnostics."""

    def __init__(self, value: Any = None, *, unit: str | None = None, error: str | None = None,
                 diagnostics: Sequence[str] | None = None, label: str | None = None) -> None:
        if unit is not None and not isinstance(unit, str):
            raise TypeError("unit must be a string or None")
        if error is not None and not isinstance(error, str):
            raise TypeError("error must be a string or None")
        if diagnostics is not None and not all(isinstance(item, str) for item in diagnostics):
            raise TypeError("diagnostics must contain only strings")
        super().__init__(component="result", value=value, unit=unit, error=error,
                         diagnostics=list(diagnostics) if diagnostics is not None else [], label=label)
