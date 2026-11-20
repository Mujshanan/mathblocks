"""Shared AnyWidget adapter base.

AnyWidget owns transport and view lifecycle. MathBlocks owns the state contract.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import anywidget
import traitlets

from mathblocks.core.serialization import (
    PYTHON_ACTOR,
    StateContractError,
    compare_state_versions,
    make_state_envelope,
    validate_state_envelope,
)


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
    """Reusable synchronized widget base for MathBlocks components.

    The single state trait is the wire-format boundary. component_state is a
    Python convenience property exposing only its user data.
    """

    _esm = _read_asset("index.js", _FALLBACK_ESM)
    _css = _read_asset("frontend.css")

    state = traitlets.Dict(default_value=make_state_envelope({})).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        self._restoring_state = False
        super().__init__(**kwargs)
        self._accepted_state = deepcopy(self.state)

    @traitlets.validate("state")
    def _validate_state(self, proposal: dict[str, Any]) -> dict[str, Any]:
        try:
            return validate_state_envelope(proposal["value"])
        except StateContractError as exc:
            raise traitlets.TraitError(str(exc)) from exc

    @traitlets.observe("state")
    def _on_state_change(self, change: dict[str, Any]) -> None:
        if self._restoring_state:
            return
        incoming = change["new"]
        accepted = getattr(self, "_accepted_state", None)
        if accepted is None:
            self._accepted_state = deepcopy(incoming)
            return
        if compare_state_versions(incoming, accepted) <= 0:
            self._restoring_state = True
            try:
                self.set_trait("state", deepcopy(accepted))
            finally:
                self._restoring_state = False
            return
        self._accepted_state = deepcopy(incoming)

    @property
    def schema_version(self) -> int:
        """Current component-state schema version."""
        return self.state["schema_version"]

    @property
    def revision(self) -> int:
        """Current accepted state revision."""
        return self.state["revision"]

    @property
    def component_state(self) -> dict[str, Any]:
        """Detached JSON-compatible component data."""
        return deepcopy(self.state["data"])

    @component_state.setter
    def component_state(self, value: dict[str, Any]) -> None:
        self.set_component_state(value)

    def set_component_state(self, value: dict[str, Any]) -> None:
        """Replace component data and publish a new Python-originated revision."""
        self.state = make_state_envelope(
            value,
            revision=self._accepted_state["revision"] + 1,
            actor=PYTHON_ACTOR,
        )
