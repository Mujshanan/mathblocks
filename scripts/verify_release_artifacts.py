#!/usr/bin/env python3
"""Verify that wheel and sdist artifacts contain matching package assets."""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

REQUIRED_PACKAGE_FILES = {
    "mathblocks/__init__.py",
    "mathblocks/_version.py",
    "mathblocks/static/index.js",
    "mathblocks/static/frontend.css",
}
REQUIRED_SDIST_FILES = {
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "src/mathblocks/__init__.py",
    "src/mathblocks/_version.py",
    "src/mathblocks/static/index.js",
    "src/mathblocks/static/frontend.css",
}


def read_source_version(root: Path) -> str:
    source = (root / "src/mathblocks/_version.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', source, re.M)
    if match is None:
        raise ValueError("Could not find __version__ in src/mathblocks/_version.py")
    return match.group(1)


def check_wheel(path: Path, expected_version: str) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = REQUIRED_PACKAGE_FILES - names
        if missing:
            raise ValueError(f"{path.name} is missing wheel files: {sorted(missing)}")
        metadata_name = next(
            (name for name in names if name.endswith(".dist-info/METADATA")), None
        )
        if metadata_name is None:
            raise ValueError(f"{path.name} has no dist-info/METADATA")
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
        if metadata.get("Name", "").lower().replace("-", "_") != "mathblocks":
            raise ValueError(f"{path.name} has unexpected distribution name")
        if metadata.get("Version") != expected_version:
            raise ValueError(
                f"{path.name} metadata version {metadata.get('Version')!r} "
                f"does not match source version {expected_version!r}"
            )


def check_sdist(path: Path, expected_version: str) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = {member.name.split("/", 1)[-1] for member in archive.getmembers()}
        missing = REQUIRED_SDIST_FILES - names
        if missing:
            raise ValueError(f"{path.name} is missing sdist files: {sorted(missing)}")
        metadata_member = next(
            (member for member in archive.getmembers() if member.name.endswith("/PKG-INFO")),
            None,
        )
        if metadata_member is None:
            raise ValueError(f"{path.name} has no PKG-INFO")
        stream = archive.extractfile(metadata_member)
        if stream is None:
            raise ValueError(f"{path.name} PKG-INFO cannot be read")
        metadata = BytesParser().parsebytes(stream.read())
        if metadata.get("Version") != expected_version:
            raise ValueError(
                f"{path.name} metadata version {metadata.get('Version')!r} "
                f"does not match source version {expected_version!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    version = read_source_version(args.root)
    wheels = sorted(args.dist.glob("*.whl"))
    sdists = sorted(args.dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError(
            f"Expected exactly one wheel and one sdist in {args.dist}; "
            f"found {len(wheels)} wheel(s) and {len(sdists)} sdist(s)"
        )
    check_wheel(wheels[0], version)
    check_sdist(sdists[0], version)
    print(f"Release artifacts verified for mathblocks {version}")
    print(f"  wheel: {wheels[0]}")
    print(f"  sdist: {sdists[0]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(f"Release artifact verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
