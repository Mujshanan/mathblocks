"""Interactive graph plotting component."""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from .base import ComponentWidget


def _graph_series(series: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(series, (str, bytes)) or not isinstance(series, Sequence):
        raise TypeError("series must be a sequence of series objects")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(series):
        if not isinstance(item, Mapping):
            raise TypeError(f"series[{index}] must be a mapping")
        label = item.get("label", f"Series {index + 1}")
        points = item.get("points")
        if not isinstance(label, str):
            raise TypeError(f"series[{index}].label must be a string")
        if not isinstance(points, Sequence) or isinstance(points, (str, bytes)) or not points:
            raise ValueError(f"series[{index}].points must contain at least one [x, y] pair")
        normalized_points: list[list[float]] = []
        for point_index, point in enumerate(points):
            if (not isinstance(point, Sequence) or isinstance(point, (str, bytes))
                    or len(point) != 2):
                raise ValueError(f"series[{index}].points[{point_index}] must be an [x, y] pair")
            x, y = point
            if (isinstance(x, bool) or not isinstance(x, (int, float))
                    or isinstance(y, bool) or not isinstance(y, (int, float))
                    or not math.isfinite(x) or not math.isfinite(y)):
                raise TypeError("Graph coordinates must be finite numbers")
            normalized_points.append([float(x), float(y)])
        normalized.append({"label": label, "points": normalized_points})
    if not normalized:
        raise ValueError("Graph must contain at least one series")
    return normalized


class Graph(ComponentWidget):
    """Plot one or more labelled numeric series with an interactive SVG renderer."""

    def __init__(self, series: Sequence[Mapping[str, Any]], *, title: str | None = None,
                 x_label: str | None = None, y_label: str | None = None,
                 label: str | None = None) -> None:
        for name, value in (("title", title), ("x_label", x_label),
                            ("y_label", y_label), ("label", label)):
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be a string or None")
        super().__init__(component="graph", value=series,
                         title=title, x_label=x_label, y_label=y_label, label=label)

    def _validate_value(self, value: Any) -> list[dict[str, Any]]:
        return _graph_series(value)
