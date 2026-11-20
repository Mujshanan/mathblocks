import pytest

from mathblocks.core.serialization import StateContractError, make_state_envelope
from mathblocks.core.state import StateStore


def test_store_creates_candidate_without_mutating_accepted_state() -> None:
    store = StateStore()
    candidate = store.create_update({"value": 3})

    assert store.revision == 0
    assert store.data == {}
    assert candidate["revision"] == 1


def test_store_accepts_newer_updates_and_returns_detached_values() -> None:
    store = StateStore()
    candidate = store.create_update({"value": 3}, actor="view:one")

    assert store.accept(candidate) is True
    assert store.revision == 1

    data = store.data
    data["value"] = 100
    assert store.data == {"value": 3}


def test_store_rejects_stale_and_equal_versions() -> None:
    store = StateStore()
    winner = make_state_envelope({"value": "winner"}, revision=2, actor="view:z")
    loser = make_state_envelope({"value": "loser"}, revision=2, actor="view:a")

    assert store.accept(winner) is True
    assert store.accept(loser) is False
    assert store.accept(winner) is False
    assert store.data == {"value": "winner"}


def test_store_rejects_invalid_envelopes() -> None:
    store = StateStore()

    with pytest.raises(StateContractError):
        store.accept({"schema_version": 99})
