"""Tests for MathBlocks' supported package-root API."""

from __future__ import annotations

import re
from importlib.metadata import version

import mathblocks


def test_public_component_exports_are_explicit_and_importable() -> None:
    expected = {
        "Diagram",
        "Graph",
        "Math",
        "Matrix",
        "Result",
        "Text",
        "Vector",
        "__version__",
    }
    assert set(mathblocks.__all__) == expected
    for name in expected:
        assert getattr(mathblocks, name) is not None


def test_package_version_is_pep440_and_matches_distribution_metadata() -> None:
    assert re.fullmatch(
        r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+|\.post\d+|\.dev\d+)?",
        mathblocks.__version__,
    )
    assert version("mathblocks") == mathblocks.__version__


def test_optional_marimo_adapter_is_not_loaded_by_package_import() -> None:
    # Importing the package root must not make the optional host dependency
    # mandatory. The adapter is imported explicitly from mathblocks.integrations.
    assert "marimo" not in __import__("sys").modules
