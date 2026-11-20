"""Editable or statically rendered mathematical expressions."""
from __future__ import annotations

from ..widgets.base import MathBlockWidget


class Math(MathBlockWidget):
    """A mathematical expression editor backed by MathLive.

    Set ``read_only=True`` to render the expression statically with KaTeX.
    The expression value is LaTeX source and remains available as ``.value``.
    """

    def __init__(self, value: str = "", *, read_only: bool = False, label: str | None = None) -> None:
        if not isinstance(value, str):
            raise TypeError("Math value must be a LaTeX string")
        if not isinstance(read_only, bool):
            raise TypeError("read_only must be a bool")
        super().__init__(component="math", value=value, readOnly=read_only, label=label)
