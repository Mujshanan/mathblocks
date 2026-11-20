"""Real Jupyter-kernel integration tests for MathBlocks widget display.

These tests execute notebook cells in a separate IPython kernel and inspect
the widget-view MIME messages emitted by the kernel. They verify the actual
Jupyter display protocol and model identity across repeated displays. Browser
DOM rendering is intentionally covered separately by frontend tests.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from ipykernel.kernelspec import install as install_kernel_spec
from nbclient import NotebookClient

WIDGET_VIEW_MIME = "application/vnd.jupyter.widget-view+json"
KERNEL_NAME = "mathblocks-integration"


def _execute_notebook(cells: list[str]) -> nbformat.NotebookNode:
    """Execute cells in an isolated, real IPython kernel."""
    install_kernel_spec(
        user=True,
        kernel_name=KERNEL_NAME,
        display_name="MathBlocks integration test",
    )
    notebook = nbformat.v4.new_notebook(
        metadata={
            "kernelspec": {
                "display_name": "MathBlocks integration test",
                "language": "python",
                "name": KERNEL_NAME,
            }
        },
        cells=[nbformat.v4.new_code_cell(source) for source in cells],
    )
    client = NotebookClient(
        notebook,
        timeout=90,
        kernel_name=KERNEL_NAME,
        resources={"metadata": {"path": str(Path.cwd())}},
        allow_errors=False,
    )
    return client.execute()


def _widget_view_model_ids(cell: nbformat.NotebookNode) -> list[str]:
    """Extract model IDs from real Jupyter widget-view display messages."""
    model_ids: list[str] = []
    for output in cell.outputs:
        if output.output_type not in {"display_data", "execute_result"}:
            continue
        data = output.get("data", {})
        descriptor = data.get(WIDGET_VIEW_MIME)
        if descriptor is not None:
            model_id = descriptor.get("model_id")
            assert isinstance(model_id, str) and model_id
            model_ids.append(model_id)
    return model_ids


def test_notebook_displays_multiple_views_of_one_widget_model() -> None:
    notebook = _execute_notebook(
        [
            (
                "from IPython.display import display\n"
                "from mathblocks import Matrix\n"
                "widget = Matrix([[1, 2], [3, 4]], label='Shared matrix')\n"
                "display(widget)\n"
                "display(widget)"
            ),
            (
                "widget.set_component_state({**widget.component_state, "
                "'value': [[5, 6], [7, 8]]})\n"
                "assert widget.component_state['value'] == [[5, 6], [7, 8]]\n"
                "display(widget)"
            ),
        ]
    )

    first_cell_ids = _widget_view_model_ids(notebook.cells[0])
    updated_cell_ids = _widget_view_model_ids(notebook.cells[1])

    assert len(first_cell_ids) == 2
    assert first_cell_ids[0] == first_cell_ids[1]
    assert updated_cell_ids == [first_cell_ids[0]]


def test_notebook_kernel_preserves_widget_state_between_cells() -> None:
    notebook = _execute_notebook(
        [
            (
                "from mathblocks import Text\n"
                "widget = Text('initial')\n"
                "widget.set_component_state({**widget.component_state, "
                "'value': 'updated in kernel'})"
            ),
            (
                "assert widget.value == 'updated in kernel'\n"
                "print(widget.value)"
            ),
        ]
    )

    output_text = "".join(
        output.text
        for output in notebook.cells[1].outputs
        if output.output_type == "stream"
    )
    assert "updated in kernel" in output_text
