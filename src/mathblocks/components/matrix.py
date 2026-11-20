"""Rectangular matrix and vector input components."""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from .base import ComponentWidget

Scalar = str | int | float | bool | None


def _scalar(value: Any, path: str) -> Scalar:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise TypeError(f"{path} must be a finite JSON scalar (string, number, bool, or None)")


def _matrix(value: Sequence[Sequence[Scalar]]) -> list[list[Scalar]]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise ValueError("Matrix value must contain at least one row")
    rows: list[list[Scalar]] = []
    width: int | None = None
    for row_index, row in enumerate(value):
        if isinstance(row, (str, bytes)) or not isinstance(row, Sequence) or not row:
            raise ValueError(f"Matrix row {row_index} must contain at least one cell")
        cells = [_scalar(cell, f"Matrix cell [{row_index}]") for cell in row]
        if width is None:
            width = len(cells)
        elif len(cells) != width:
            raise ValueError("Matrix rows must all have the same number of columns")
        rows.append(cells)
    return rows


class Matrix(ComponentWidget):
    """Editable rectangular matrix; values are JSON scalar cells."""

    def __init__(self, value: Sequence[Sequence[Scalar]], *, read_only: bool = False,
                 label: str | None = None) -> None:
        if not isinstance(read_only, bool):
            raise TypeError("read_only must be a bool")
        if label is not None and not isinstance(label, str):
            raise TypeError("label must be a string or None")
        super().__init__(component="matrix", value=value,
                         read_only=read_only, label=label)

    def _validate_value(self, value: Any) -> list[list[Scalar]]:
        return _matrix(value)


class Vector(ComponentWidget):
    """Editable one-dimensional vector; values are JSON scalar entries."""

    def __init__(self, value: Sequence[Scalar], *, read_only: bool = False,
                 label: str | None = None) -> None:
        if not isinstance(read_only, bool):
            raise TypeError("read_only must be a bool")
        if label is not None and not isinstance(label, str):
            raise TypeError("label must be a string or None")
        super().__init__(component="vector", value=value,
                         read_only=read_only, label=label)

    def _validate_value(self, value: Any) -> list[Scalar]:
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
            raise ValueError("Vector value must contain at least one entry")
        return [_scalar(item, f"Vector entry [{index}]") for index, item in enumerate(value)]
