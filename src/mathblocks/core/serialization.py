"""JSON serialization and versioned state-envelope helpers."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from typing import Any

SCHEMA_VERSION = 1
PYTHON_ACTOR = "python"
MAX_SAFE_INTEGER = 2**53 - 1


class StateContractError(ValueError):
    """Raised when component state violates the public wire contract."""


def _validate_json_value(value: Any, path: str = "data") -> None:
    """Reject Python values that cannot be represented losslessly in JavaScript JSON."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise StateContractError(f"{path} contains an integer outside JavaScript's safe range.")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise StateContractError(f"{path} contains a non-finite number.")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise StateContractError(f"{path} contains a non-string object key.")
            _validate_json_value(item, f"{path}.{key}")
        return
    raise StateContractError(f"{path} contains unsupported value type {type(value).__name__}.")


def normalize_json_object(value: Any) -> dict[str, Any]:
    """Return a detached JSON-compatible object with finite, safe numeric values."""
    if not isinstance(value, dict):
        raise StateContractError("Component state must be a JSON object.")
    _validate_json_value(value)
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        normalized = json.loads(encoded)
    except (TypeError, ValueError, RecursionError) as exc:
        raise StateContractError(f"Component state is not JSON-compatible: {exc}") from exc
    if not isinstance(normalized, dict):
        raise StateContractError("Component state must serialize to a JSON object.")
    return normalized


def make_state_envelope(
    data: dict[str, Any],
    *,
    revision: int = 0,
    actor: str = PYTHON_ACTOR,
) -> dict[str, Any]:
    """Build a detached version-1 state envelope."""
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise StateContractError("State revision must be a non-negative integer.")
    if not isinstance(actor, str) or not actor.strip():
        raise StateContractError("State actor must be a non-empty string.")
    return {
        "schema_version": SCHEMA_VERSION,
        "revision": revision,
        "actor": actor,
        "data": normalize_json_object(data),
    }


def validate_state_envelope(value: Any) -> dict[str, Any]:
    """Validate and detach a state envelope received from Python or the frontend."""
    if not isinstance(value, dict):
        raise StateContractError("State envelope must be a JSON object.")
    required = {"schema_version", "revision", "actor", "data"}
    if set(value) != required:
        raise StateContractError(
            "State envelope must contain exactly: schema_version, revision, actor, data."
        )
    schema_version = value["schema_version"]
    if isinstance(schema_version, bool) or schema_version != SCHEMA_VERSION:
        raise StateContractError(
            f"Unsupported state schema version: {schema_version!r}; "
            f"expected {SCHEMA_VERSION}."
        )
    return make_state_envelope(
        value["data"],
        revision=value["revision"],
        actor=value["actor"],
    )


def compare_state_versions(left: dict[str, Any], right: dict[str, Any]) -> int:
    """Compare Lamport-style versions; Python wins equal-revision conflicts."""
    def key(envelope: dict[str, Any]) -> tuple[int, int, str]:
        actor = envelope["actor"]
        priority = 1 if actor == PYTHON_ACTOR else 0
        return envelope["revision"], priority, actor

    left_key = key(left)
    right_key = key(right)
    return (left_key > right_key) - (left_key < right_key)


def clone_state_envelope(value: dict[str, Any]) -> dict[str, Any]:
    """Return a detached copy suitable for traitlets and caller-facing APIs."""
    return deepcopy(validate_state_envelope(value))
