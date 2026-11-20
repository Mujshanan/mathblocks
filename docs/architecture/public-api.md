# Public Python API

This document defines the supported Python import surface for the current
pre-1.0 release line.

## Supported imports

The supported component imports are:

```python
from mathblocks import (
    Diagram,
    Graph,
    Math,
    Matrix,
    Result,
    Text,
    Vector,
    __version__,
)
```

The seven component classes are the supported user-facing component API.
Their documented constructor arguments, public `.value` property, and
AnyWidget behavior are covered by the component guides and tests.

The following integration is an optional host adapter:

```python
from mathblocks.integrations import as_marimo
```

It requires the `marimo` extra. Importing the base `mathblocks` package
must not import Marimo or require it to be installed.

## Internal implementation

Modules such as `mathblocks.core`, `mathblocks.widgets`, and
`mathblocks.components.*` contain implementation and contract types used
internally. They are not all promised as stable user-facing import paths.
The versioned state envelope is documented separately as an interoperability
contract for host integrations and component views.

## Compatibility policy

MathBlocks is pre-1.0. Public API changes may be made in minor releases, but
must be recorded in the changelog and accompanied by migration notes when
they affect existing user code. Patch releases are reserved for compatible
fixes. The 1.0 release will require an explicit API review and a compatibility
test suite for every supported public symbol.

## Stability rules

- Keep the top-level `mathblocks.__all__` deliberate and tested.
- Do not expose development helpers or frontend build internals from the
  package root.
- Keep Marimo optional and lazily imported.
- Ship the Python API and its matching compiled frontend assets together.
- Treat the version-1 state envelope and its conflict rules as a separate,
  documented compatibility contract.
