# Release readiness and procedure

MathBlocks is currently a pre-1.0 development package. Phase 5 prepares the
project for a release; it does not publish to PyPI or create a GitHub release.
The current `0.1.0.dev0` version is not a stable release.

## Release invariants

- Users install one Python distribution: `pip install mathblocks`.
- The wheel and source distribution include the compiled frontend assets.
- Installing either distribution must not require Node.js or npm.
- Python code and frontend assets are built and shipped together.
- Marimo remains optional and is installed with
  `pip install "mathblocks[marimo]"`.
- `src/mathblocks/_version.py` is the single source of the package version;
  Hatchling reads it for distribution metadata.
- No release is considered complete until the exact artifacts to be published
  pass the checks below.

## Before a release

1. Review the public API reference and compatibility policy.
2. Review every public component constructor, assignment behavior, and
   documented host integration for unintended changes.
3. Update `CHANGELOG.md` with user-visible changes and migration notes.
4. Set the intended PEP 440 version in `src/mathblocks/_version.py`.
5. Confirm the Python version range and runtime dependencies in
   `pyproject.toml`.
6. Run the full frontend and Python test suites.
7. Build both wheel and source distribution with `python -m build`.
8. Run `python scripts/verify_release_artifacts.py`.
9. Install the wheel and source distribution into clean target directories
   and verify imports and bundled assets.
10. Test the optional Marimo extra in a Marimo-capable environment.
11. Inspect the generated metadata, archive contents, license, README, and
    changelog before publication.

## Local verification

Development/build prerequisites: Python 3.11+, Node.js 22.12+, and npm.

```bash
npm install
npm run build
npm run typecheck
npm test
python -m pip install -e ".[dev]"
pytest
python -m build
python scripts/verify_release_artifacts.py
```

To verify installation from the source distribution (this step needs Python
build isolation dependencies, but not Node.js or npm):

```bash
python -m pip install --no-deps --target /tmp/mathblocks-sdist dist/*.tar.gz
PYTHONPATH=/tmp/mathblocks-sdist python -c "import mathblocks; from pathlib import Path; p = Path(mathblocks.__file__).parent / 'static'; assert (p / 'index.js').is_file(); assert (p / 'frontend.css').is_file()"
```

For the optional host integration:

```bash
python -m pip install -e ".[dev,marimo]"
pytest tests/integration
```

## Publication checklist

Publication is a separate, explicitly authorized action. Before publishing:

- [ ] Confirm the release version and changelog.
- [ ] Confirm the target Git tag points to the reviewed release commit.
- [ ] Confirm all required CI checks pass on that exact commit.
- [ ] Build and inspect the final wheel and source distribution.
- [ ] Publish the artifacts to PyPI using the project's authorized publishing
      credentials or trusted-publishing configuration.
- [ ] Verify the uploaded files and metadata on PyPI.
- [ ] Create the matching GitHub release with release notes.
- [ ] Install the published version in a clean environment and run a smoke
      test.

This repository work does not publish artifacts, create a tag, or create a
GitHub release. Those actions require separate authorization.
