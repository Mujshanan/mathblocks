# Phase 0 — Project foundation

Phase 0 establishes a reproducible package and frontend build before
component-specific work begins.

## Local validation

From a clean checkout:

```bash
python -m pip install -e ".[dev]"
npm install
npm run build
npm run typecheck
npm test
pytest
python -m build
```

The frontend build writes the ESM module and stylesheet into
`src/mathblocks/static/`. The Python package reads those files when creating
an AnyWidget instance.

If the assets have not been built in a source checkout, the base widget uses
a small diagnostic frontend module. This fallback is for development
diagnostics only; release wheels must contain the generated bundle.

## CI requirements

The CI workflow must:

1. Build the frontend with the supported Node.js version.
2. Run TypeScript type checking and frontend tests.
3. Run Python tests on the supported Python versions.
4. Build both wheel and source distribution artifacts.
5. Install the wheel into an isolated target and verify that the package,
   AnyWidget base, JavaScript module, and stylesheet are present.

## Phase 0 exit criteria

- A clean environment can build the frontend and Python distributions.
- Python and frontend checks pass in CI.
- The built wheel imports without a source checkout.
- A minimal AnyWidget instance loads the bundled frontend assets.
