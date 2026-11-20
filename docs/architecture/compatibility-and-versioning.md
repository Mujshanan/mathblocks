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

The shared AnyWidget model exposes two synchronized fields:

- `schema_version`: the integer version of the component payload contract.
- `component_state`: the JSON-compatible component payload.

Version 1 is the initial contract.

- Compatible additions that existing readers can safely ignore do not
  necessarily require a schema version increment.
- Changes that alter the meaning, required shape, or interpretation of
  existing component data require a schema version increment.
- Readers must reject unsupported future schema versions with a clear error;
  they must not silently reinterpret unknown data.
- Component-specific payloads must be validated at the Python boundary before
  being sent to the frontend.

## Python and frontend compatibility

The Python package and bundled frontend are built and released together.
A wheel must never combine Python code from one MathBlocks release with
frontend assets from another release.

AnyWidget is the transport and lifecycle adapter. Component semantics and
wire-format definitions belong to MathBlocks, not to AnyWidget or a specific
notebook host.

## Supported environments

The declared Python minimum is 3.11. CI tests the minimum and the current
supported Python minor versions. The frontend toolchain uses Node.js 22.12+
for development and packaging only; end users installing a built wheel do
not need Node.js or npm.
