"""Shared AnyWidget adapter base.

AnyWidget owns transport and view lifecycle. MathBlocks core owns state rules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import anywidget
import traitlets

from mathblocks.core.serialization import StateContractError, validate_state_envelope
from mathblocks.core.state import StateStore


_STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def _immutable(*args: Any, **kwargs: Any) -> None:
    raise TypeError("MathBlocks synchronized state is read-only; use component_state or set_component_state().")


class _FrozenDict(dict[str, Any]):
    """JSON-serializable dict that prevents unobserved in-place trait mutation."""

    def __init__(self, values: dict[str, Any]) -> None:
        dict.__init__(self, ((key, _freeze_json(item)) for key, item in values.items()))

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable


class _FrozenList(list[Any]):
    """JSON-serializable list that prevents unobserved in-place trait mutation."""

    def __init__(self, values: list[Any]) -> None:
        list.__init__(self, (_freeze_json(item) for item in values))

    __setitem__ = _immutable
    __delitem__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return _FrozenDict(value)
    if isinstance(value, list):
        return _FrozenList(value)
    return value


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

    # The default must already be immutable: traitlets may not replace an
    # equal mutable default when set_trait() compares values for equality.
    state = traitlets.Dict(default_value=_freeze_json(StateStore().envelope)).tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        self._restoring_state = False
        super().__init__(**kwargs)
        self._state_store = StateStore(self.state)

    @traitlets.validate("state")
    def _validate_state(self, proposal: dict[str, Any]) -> dict[str, Any]:
        try:
            return _freeze_json(validate_state_envelope(proposal["value"]))
        except StateContractError as exc:
            raise traitlets.TraitError(str(exc)) from exc

    @traitlets.observe("state")
    def _on_state_change(self, change: dict[str, Any]) -> None:
        if self._restoring_state or not hasattr(self, "_state_store"):
            return

        incoming = change["new"]
        accepted_before = self._state_store.envelope
        if self._state_store.accept(incoming):
            return
        if incoming == accepted_before:
            return

        self._restoring_state = True
        try:
            self.set_trait("state", accepted_before)
        finally:
            self._restoring_state = False

    @property
    def schema_version(self) -> int:
        """Current component-state schema version."""
        return self.state["schema_version"]

    @property
    def revision(self) -> int:
        """Current accepted state revision."""
        return self._state_store.revision

    @property
    def component_state(self) -> dict[str, Any]:
        """Detached JSON-compatible component data."""
        return self._state_store.data

    @component_state.setter
    def component_state(self, value: dict[str, Any]) -> None:
        self.set_component_state(value)

    def set_component_state(self, value: dict[str, Any]) -> None:
        """Replace component data and publish a new Python-originated revision."""
        self.state = self._state_store.create_update(value, actor="python")
