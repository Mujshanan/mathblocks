import pytest

from mathblocks import Diagram, Graph, Matrix, Vector
from mathblocks.core.serialization import validate_state_envelope


def test_matrix_requires_a_non_empty_rectangular_shape() -> None:
    matrix = Matrix([[1, 2], [3, 4]], label="Stiffness matrix")
    assert matrix.component_state["component"] == "matrix"
    assert matrix.value == [[1, 2], [3, 4]]
    with pytest.raises(ValueError, match="same number of columns"):
        Matrix([[1, 2], [3]])
    with pytest.raises(ValueError):
        Matrix([])


def test_matrix_assignment_is_validated_before_revision() -> None:
    matrix = Matrix([[1, 2]])
    with pytest.raises(ValueError, match="same number of columns"):
        matrix.value = [[1, 2], [3]]
    assert matrix.revision == 0


def test_vector_is_one_dimensional_and_json_scalar_only() -> None:
    vector = Vector([1, 2.5, "x"], label="Displacement")
    assert vector.component_state["value"] == [1, 2.5, "x"]
    with pytest.raises(TypeError):
        Vector([1, object()])  # type: ignore[list-item]


def test_structured_component_edits_use_the_shared_revision() -> None:
    matrix = Matrix([[1]])
    matrix.value = [[2]]
    assert matrix.revision == 1
    assert matrix.state["actor"] == "python"


def test_graph_validates_series_and_finite_coordinates() -> None:
    graph = Graph([{"label": "Load", "points": [[0, 0], [1, 2]]}],
                  title="Load response", x_label="x", y_label="P")
    assert graph.component_state["component"] == "graph"
    assert graph.value[0]["points"] == [[0.0, 0.0], [1.0, 2.0]]
    with pytest.raises(ValueError):
        Graph([{"label": "Bad", "points": []}])
    with pytest.raises(TypeError):
        Graph([{"label": "Bad", "points": [[0, float("nan")]]}])


def test_graph_revalidates_python_side_assignments() -> None:
    graph = Graph([{"label": "Load", "points": [[0, 0]]}])
    with pytest.raises(TypeError):
        graph.value = [{"label": "Bad", "points": [[0, float("inf")]]}]
    assert graph.revision == 0


def test_diagram_references_must_resolve_and_ids_must_be_unique() -> None:
    nodes = [
        {"id": "a", "label": "Support", "x": 20, "y": 30},
        {"id": "b", "label": "Beam", "x": 240, "y": 30, "shape": "ellipse"},
    ]
    diagram = Diagram(nodes, [{"source": "a", "target": "b", "label": "reaction"}])
    assert diagram.component_state["component"] == "diagram"
    assert len(diagram.value["edges"]) == 1
    with pytest.raises(ValueError, match="unique"):
        Diagram([nodes[0], nodes[0]])
    with pytest.raises(ValueError, match="existing node IDs"):
        Diagram(nodes, [{"source": "a", "target": "missing"}])


def test_diagram_rejects_non_finite_node_coordinates() -> None:
    with pytest.raises(TypeError, match="finite numbers"):
        Diagram([{"id": "a", "label": "A", "x": float("inf"), "y": 0}])


@pytest.mark.parametrize(
    "widget",
    [
        Matrix([[1, 2], [3, 4]]),
        Vector([1, 2, 3]),
        Graph([{"label": "series", "points": [[0, 1], [1, 2]]}]),
        Diagram(
            [{"id": "n1", "label": "Node", "x": 10, "y": 20}],
            [],
        ),
    ],
)
def test_visual_components_round_trip_through_shared_json_envelope(widget) -> None:
    restored = validate_state_envelope(widget.state)
    assert restored["schema_version"] == 1
    assert restored["revision"] == 0
    assert restored["actor"] == "python"
    assert restored["data"] == widget.component_state
