"""Plain explanatory text and annotations."""
from __future__ import annotations

from typing import Literal

from ..widgets.base import MathBlockWidget

TextTone = Literal["default", "muted", "note", "warning"]


class Text(MathBlockWidget):
    """A safe text annotation; content is rendered as text, never trusted HTML."""

    def __init__(self, value: str, *, label: str | None = None, tone: TextTone = "default") -> None:
        if not isinstance(value, str):
            raise TypeError("Text value must be a string")
        if tone not in ("default", "muted", "note", "warning"):
            raise ValueError("tone must be default, muted, note, or warning")
        super().__init__(component="text", value=value, label=label, tone=tone)
