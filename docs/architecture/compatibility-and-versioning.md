# Compatibility and versioning policy

MathBlocks is pre-1.0. The public Python API and the Python-to-frontend wire
contract are both versioned, but they have different compatibility concerns.

## Package version

MathBlocks follows semantic-versioning conventions with an explicit
pre-1.0 policy:

- **Patch release:** compatible bug fixes, documentation corrections, and
  internal improvements. No intentional public API or wire-format breakage.
- **Minor release:** may introduce new APIs and, before 1.0, may contain
  breaking changes. Breaking changes must be documented with migration notes.
- **Major release:** reserved for the 1.0 stability boundary and later
  incompatible public API changes.

The Python package version is the release version users install. Frontend
assets are built and shipped as part of that same release; they are not
independently versioned at runtime.

## Component state versioning

The AnyWidget model exposes one synchronized field named `state`. It is an
atomic envelope with four fields:

- `schema_version`: integer version of the envelope contract.
- `revision`: non-negative, JavaScript-safe logical revision.
- `actor`: `python` or a unique frontend view identifier.
- `data`: the JSON-compatible component payload.

Version 1 is the initial contract. The full envelope and conflict-resolution
rules are specified in [the state contract](state-contract.md).

- Compatible additions that existing readers can safely ignore do not
  necessarily require a schema version increment.
- Changes that alter the meaning, required shape, or interpretation of the
  envelope require a schema version increment.
- Readers must reject unsupported future schema versions with a clear error;
  they must not silently reinterpret unknown data.
- Component payloads are JSON objects containing only losslessly
  interoperable JSON values. Non-finite numbers, unsafe integers, unsupported
  Python objects, and cyclic values are rejected.
- Python exposes the payload through the detached `component_state`
  convenience property; the envelope itself remains the synchronized trait.

## Python and frontend compatibility

The Python package and bundled frontend are built and released together.
A wheel must never combine Python code from one MathBlocks release with
frontend assets from another release.

AnyWidget is the transport and lifecycle adapter. Component semantics and
wire-format definitions belong to MathBlocks, not to a specific notebook host.
MathBlocks requires AnyWidget 0.11 or newer for the per-view AbortSignal
lifecycle API used by its frontend adapter.

## Supported environments

The declared Python minimum is 3.11. CI tests Python 3.11, 3.12, and 3.13.
The frontend toolchain uses Node.js 22.12+ for development and packaging only;
end users installing a built wheel do not need Node.js or npm.
