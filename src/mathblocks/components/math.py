"""Editable or statically rendered mathematical expressions."""
from __future__ import annotations

from .base import ComponentWidget


class Math(ComponentWidget):
    """A mathematical expression editor backed by MathLive.

    Set ``read_only=True`` to render the expression statically with KaTeX.
    The value is LaTeX source and remains available as ``.value``.
    """

    def __init__(self, value: str = "", *, read_only: bool = False, label: str | None = None) -> None:
        if not isinstance(value, str):
            raise TypeError("Math value must be a LaTeX string")
        if not isinstance(read_only, bool):
            raise TypeError("read_only must be a bool")
        if label is not None and not isinstance(label, str):
            raise TypeError("label must be a string or None")
        super().__init__(component="math", value=value, read_only=read_only, label=label)
