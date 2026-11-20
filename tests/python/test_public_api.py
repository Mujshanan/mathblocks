"""Tests for MathBlocks' supported package-root API."""

from __future__ import annotations

import re
import subprocess
import sys
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


def test_importing_package_root_does_not_import_optional_marimo() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, mathblocks; "
            "assert 'marimo' not in sys.modules; "
            "assert hasattr(mathblocks, 'Math')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
