# Structured and visual components

Phase 3 adds editable structured values and visual components. All components continue to use the Phase 1 versioned state envelope and the shared Python-authoritative revision policy.

## Matrix and Vector

```python
from mathblocks import Matrix, Vector

matrix = Matrix([[1, 2], [3, 4]], label="Stiffness matrix")
vector = Vector([0.0, 12.5, 0.0], label="Nodal displacement")
```

- Matrix values are non-empty rectangular rows of JSON scalar cells.
- Vector values are a non-empty one-dimensional sequence of JSON scalar entries.
- Both support read_only=True.
- Editable cells accept keyboard input. Matrix supports tab-separated clipboard paste and a Copy TSV action.
- Numeric text is normalized to a JSON number; other cell text remains a string.

## Graph

```python
from mathblocks import Graph

plot = Graph(
    [{"label": "Load", "points": [[0, 0], [1, 12], [2, 18], [3, 14]]}],
    title="Load response",
    x_label="Span (m)",
    y_label="Load (kN)",
)
```

A graph contains one or more labelled series, each with finite numeric [x, y] points. The frontend renders an SVG polyline plot. Legend buttons show or hide individual series, and each point can be inspected by hover or keyboard focus. Graphs are display components; plotting does not evaluate expressions or mutate series data.

## Diagram

```python
from mathblocks import Diagram

diagram = Diagram(
    nodes=[
        {"id": "support", "label": "Support", "x": 60, "y": 120},
        {"id": "beam", "label": "Beam", "x": 320, "y": 120, "shape": "ellipse"},
    ],
    edges=[{"source": "support", "target": "beam", "label": "reaction"}],
    label="Load path",
)
```

The diagram document is a portable JSON object with nodes and edges. Nodes have unique IDs, labels, coordinates, and a rect or ellipse shape. Edges refer to existing node IDs. Dragging nodes updates their coordinates through the common synchronized state contract. The Export SVG action downloads a standalone SVG representation.

## Serialization and validation

All values are JSON-compatible and are validated before entering the shared envelope. Matrices reject empty or ragged rows; vectors reject nested/non-scalar entries; graphs reject empty series and non-finite coordinates; diagrams reject duplicate IDs, unsupported shapes, and dangling edges. The shared state serializer also rejects non-finite numbers and values outside JavaScript's safe integer range.

The components do not add a new synchronization layer, revision counter, or CRDT. Browser-originated edits use the existing per-view actor and commitState; Python remains authoritative when revisions tie.
