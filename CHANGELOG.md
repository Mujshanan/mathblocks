# Changelog

All notable MathBlocks changes are documented here.

The project is currently pre-1.0. Until the 1.0 stability boundary, minor
releases may include documented breaking API changes; see
[Compatibility and versioning](docs/architecture/compatibility-and-versioning.md).

## Unreleased

### Added
- Public API reference and release-readiness checklist.
- Automated wheel and source-distribution content verification.
- Installed source-distribution smoke test in CI.

### Changed
- Make `src/mathblocks/_version.py` the single source of the Python package
  version; build metadata is derived from it.
- Clarify that the package is not yet published to PyPI and that the current
  development version is not a stable release.
