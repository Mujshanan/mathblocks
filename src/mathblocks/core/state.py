"""Framework-independent state storage and revision handling."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .serialization import (
    PYTHON_ACTOR,
    compare_state_versions,
    make_state_envelope,
    validate_state_envelope,
)


class StateStore:
    """Own one component's accepted domain-state envelope.

    The store does not know about AnyWidget, browser models, or DOM views.
    Adapters ask it to create candidate updates and accept/reject incoming
    envelopes according to the shared deterministic revision policy.
    """

    def __init__(self, initial_state: dict[str, Any] | None = None) -> None:
        self._state = validate_state_envelope(
            initial_state if initial_state is not None else make_state_envelope({})
        )

    @property
    def envelope(self) -> dict[str, Any]:
        """Return a detached copy of the complete state envelope."""
        return deepcopy(self._state)

    @property
    def data(self) -> dict[str, Any]:
        """Return a detached copy of component domain data."""
        return deepcopy(self._state["data"])

    @property
    def revision(self) -> int:
        """Return the currently accepted logical revision."""
        return self._state["revision"]

    def create_update(
        self,
        data: dict[str, Any],
        *,
        actor: str = PYTHON_ACTOR,
    ) -> dict[str, Any]:
        """Create the next candidate envelope without mutating accepted state."""
        return make_state_envelope(
            data,
            revision=self._state["revision"] + 1,
            actor=actor,
        )

    def accept(self, candidate: dict[str, Any]) -> bool:
        """Accept a newer candidate; return False for stale or losing updates."""
        normalized = validate_state_envelope(candidate)
        if compare_state_versions(normalized, self._state) <= 0:
            return False
        self._state = normalized
        return True
