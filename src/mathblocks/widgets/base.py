"""Shared AnyWidget adapter base.

The adapter owns transport and lifecycle, not component semantics.
"""

from pathlib import Path

import anywidget
import traitlets


_STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def _read_asset(name: str, fallback: str = "") -> str:
    """Read a bundled frontend asset, with a useful source-checkout fallback."""
    path = _STATIC_DIR / name
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return fallback


_FALLBACK_ESM = """
function render({ el }) {
  el.classList.add("mathblocks-root");
  el.textContent = "MathBlocks frontend assets have not been built. Run npm install and npm run build.";
}
export default { render };
"""


class MathBlocksWidget(anywidget.AnyWidget):
    """Minimal shared widget base for MathBlocks components.

    component_state is the versioned JSON-compatible state envelope shared
    with the frontend. Component-specific Python classes can extend this base
    with validated traits as their contracts are defined.
    """

    _esm = _read_asset("index.js", _FALLBACK_ESM)
    _css = _read_asset("style.css")

    schema_version = traitlets.Int(1).tag(sync=True)
    component_state = traitlets.Dict(default_value={}).tag(sync=True)
