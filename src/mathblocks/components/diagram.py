"""Portable node-and-edge diagram component."""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from .base import ComponentWidget


def _diagram(nodes: Sequence[Mapping[str, Any]],
             edges: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    if isinstance(nodes, (str, bytes)) or not isinstance(nodes, Sequence):
        raise TypeError("nodes must be a sequence")
    if isinstance(edges, (str, bytes)) or not isinstance(edges, Sequence):
        raise TypeError("edges must be a sequence")
    normalized_nodes: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, Mapping):
            raise TypeError(f"nodes[{index}] must be a mapping")
        node_id, label = node.get("id"), node.get("label")
        x, y = node.get("x"), node.get("y")
        shape = node.get("shape", "rect")
        if not isinstance(node_id, str) or not node_id or node_id in identifiers:
            raise ValueError("Diagram node IDs must be unique non-empty strings")
        if not isinstance(label, str):
            raise TypeError(f"nodes[{index}].label must be a string")
        if (isinstance(x, bool) or not isinstance(x, (int, float))
                or isinstance(y, bool) or not isinstance(y, (int, float))
                or not math.isfinite(x) or not math.isfinite(y)):
            raise TypeError(f"nodes[{index}] coordinates must be finite numbers")
        if not isinstance(shape, str) or shape not in ("rect", "ellipse"):
            raise ValueError("Node shape must be 'rect' or 'ellipse'")
        identifiers.add(node_id)
        normalized_nodes.append({"id": node_id, "label": label, "x": float(x),
                                 "y": float(y), "shape": shape})
    normalized_edges: list[dict[str, Any]] = []
    for index, edge in enumerate(edges):
        if not isinstance(edge, Mapping):
            raise TypeError(f"edges[{index}] must be a mapping")
        source, target = edge.get("source"), edge.get("target")
        edge_label = edge.get("label", "")
        if source not in identifiers or target not in identifiers:
            raise ValueError(f"edges[{index}] must reference existing node IDs")
        if not isinstance(edge_label, str):
            raise TypeError(f"edges[{index}].label must be a string")
        normalized_edges.append({"source": source, "target": target, "label": edge_label})
    return {"nodes": normalized_nodes, "edges": normalized_edges}


class Diagram(ComponentWidget):
    """Editable node-and-edge diagram with standalone SVG export."""

    def __init__(self, nodes: Sequence[Mapping[str, Any]],
                 edges: Sequence[Mapping[str, Any]] = (), *,
                 read_only: bool = False, label: str | None = None) -> None:
        if not isinstance(read_only, bool):
            raise TypeError("read_only must be a bool")
        if label is not None and not isinstance(label, str):
            raise TypeError("label must be a string or None")
        super().__init__(component="diagram", value={"nodes": nodes, "edges": edges},
                         read_only=read_only, label=label)

    def _validate_value(self, value: Any) -> dict[str, list[dict[str, Any]]]:
        if not isinstance(value, Mapping) or "nodes" not in value or "edges" not in value:
            raise ValueError("Diagram value must contain nodes and edges")
        return _diagram(value["nodes"], value["edges"])
