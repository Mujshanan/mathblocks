# MathBlocks

**Reusable mathematical interface components for Python.**

MathBlocks is a Python-first toolkit for building interactive mathematical and scientific interfaces. Its components are implemented with TypeScript and distributed inside the Python package through [AnyWidget](https://anywidget.dev/).

The project takes inspiration from component libraries such as WigglyStuff: Python provides a clear, composable API while the browser handles rich interaction and rendering.

> **Project status:** Phase 2 first components are implemented on `feat/phase-2-components`. Math, Text, and Result are available; Matrix, Graph, and Diagram remain planned.

## Goals

- Provide reusable, focused mathematical widgets with a Python-first API.
- Keep the TypeScript frontend bundled with the Python distribution.
- Work in Jupyter and other AnyWidget-compatible environments.
- Offer an optional Marimo integration without making Marimo a core dependency.
- Keep mathematical components independently testable and composable.
- Separate persistent/domain data, transient UI state, and computed results.
- Make it straightforward to add new component types.

## Installation

Once MathBlocks is published on PyPI, install it with one command:

```bash
pip install mathblocks
```

No Node.js, npm, or frontend build tools will be required by end users. The published wheel will include the compiled frontend assets.

For development from source, clone the repository and build its frontend assets before installing the editable Python package. Node.js is a development/build requirement only; it will not be required when installing a published wheel.

## Quick start

The first components are available from the Python package API:

```python
from IPython.display import display
from mathblocks import Math, Result, Text

equation = Math(r"\sigma = \frac{P}{A}")
annotation = Text("Check the sign convention.", tone="note")
result = Result(24.6, unit="MPa")

display(equation)
display(annotation)
display(result)
```

In Jupyter, AnyWidget components are displayed by returning or displaying the widget. In Marimo, the optional adapter is intended to provide a concise integration:

```python
import marimo as mo
from mathblocks import Math

equation = Math(r"\int_0^1 x^2\,dx")
mo.ui.anywidget(equation)
```

See [First components](docs/components/first-components.md) and [the runnable example](examples/first_components.py) for the current API. Math is editable by default; use `read_only=True` for KaTeX rendering.

## Planned components

| Component | Purpose |
|---|---|
| Math | Editable mathematical notation and expression input |
| Text | Rich explanatory text and annotations |
| Result | Display of computed values, units, and diagnostics |
| Matrix | Interactive matrix and vector editing |
| Graph | Mathematical plots and graph interaction |
| Diagram | Extensible diagram and engineering-visualization surface |

Components should remain independently useful. A future worksheet or larger application may compose them, but MathBlocks is not limited to a single worksheet interface.

## Architecture

MathBlocks is distributed as **one Python package** containing the compiled frontend assets.

```text
Python application / notebook
          |
          v
    MathBlocks API
          |
          v
     AnyWidget adapter
          |
          v
 Bundled TypeScript frontend
          |
          +-- Editors
          +-- Renderers
          +-- Interaction
          +-- Component styles
```

### Responsibilities

- **Python core:** public component APIs, domain models, validation, serialization, and Python-side state.
- **Component layer:** focused Python wrappers and component-specific contracts.
- **AnyWidget adapter:** transport and lifecycle integration between Python and the browser.
- **TypeScript frontend:** editing, rendering, keyboard interaction, and local presentation state.
- **Host integrations:** optional conveniences for environments such as Marimo. Host-specific behavior must not leak into the core package.

### State ownership

The versioned synchronized envelope and its conflict policy are defined in [the state contract](docs/architecture/state-contract.md).

Keep three categories distinct:

1. **Domain state** — component data that Python users expect to inspect, serialize, or persist.
2. **Transient UI state** — focus, cursor position, selection, hover, and in-progress editing details.
3. **Computed state** — results, validation messages, and other outputs derived from inputs.

Do not use the DOM as the source of truth. Avoid syncing every keystroke or animation frame to Python when local frontend state is sufficient. External Python-side changes must still propagate to the frontend, and asynchronous responses must not overwrite newer edits.

## Repository structure

```text
mathblocks/
├── README.md
├── LICENSE
├── pyproject.toml
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── tsconfig.json
├── .gitignore
├── .editorconfig
├── docs/
│   ├── README.md
│   ├── architecture/
│   ├── development/
│   ├── components/
│   └── api/
├── src/
│   └── mathblocks/
│       ├── __init__.py
│       ├── _version.py
│       ├── core/
│       │   ├── models.py
│       │   ├── state.py
│       │   ├── events.py
│       │   └── serialization.py
│       ├── components/
│       │   ├── math.py
│       │   ├── text.py
│       │   ├── result.py
│       │   ├── matrix.py
│       │   ├── graph.py
│       │   └── diagram.py
│       ├── widgets/
│       │   ├── __init__.py
│       │   └── base.py
│       ├── integrations/
│       │   └── marimo.py
│       └── static/
├── frontend/
│   ├── dev/
│   │   ├── index.html
│   │   └── main.ts
│   └── src/
│       ├── index.ts
│       ├── core/
│       │   ├── bootstrap.ts
│       │   ├── model.ts
│       │   ├── store.ts
│       │   └── synchronization.ts
│       ├── components/
│       │   ├── math/
│       │   ├── text/
│       │   ├── result/
│       │   ├── matrix/
│       │   ├── graph/
│       │   └── diagram/
│       ├── editors/
│       ├── rendering/
│       ├── interaction/
│       ├── synchronization/
│       ├── styles/
│       │   ├── index.css
│       │   └── README.md
│       └── utils/
├── tests/
│   ├── frontend/
│   │   └── store.test.ts
│   ├── python/
│   │   ├── test_package_import.py
│   │   ├── test_state_store.py
│   │   └── test_widget_base.py
│   └── integration/
├── examples/
└── scripts/
```

The Python package lives under `src/mathblocks`. TypeScript source lives under `frontend/src`; the build copies bundled assets into `src/mathblocks/static`, which is included in the wheel. Generated bundles should not be edited by hand.

## Development setup

### Requirements

- Python 3.11 or newer
- Node.js 22.12 or newer and npm (development/build only)

### Install development dependencies

```bash
git clone https://github.com/Mujshanan/mathblocks.git
cd mathblocks
python -m venv .venv
# Activate the environment, then:
npm install
npm run build
python -m pip install -e ".[dev]"
```

### Frontend dependencies

The frontend toolchain is managed in `package.json`:

| Dependency | Role |
|---|---|
| TypeScript | Typed frontend implementation |
| Vite | Development server and production bundler |
| MathLive | Interactive mathematical input |
| KaTeX | Static mathematical rendering |
| Jotai (vanilla store) | Isolated per-widget frontend state |
| Vitest | Frontend unit tests |

MathLive and KaTeX serve different purposes: MathLive handles editable math fields; KaTeX renders non-editable expressions. Jotai is used through its framework-independent vanilla store, not React. AnyWidget is a Python runtime dependency and is installed automatically by pip.


### Build the frontend

```bash
npm run dev       # Start the frontend development server
npm run build     # Bundle frontend assets into src/mathblocks/static/
npm run typecheck
```

### Run tests

```bash
pytest
npm test
```

The CI workflow runs the frontend build, TypeScript checks, frontend tests, Python tests on Python 3.11–3.13, and a built-wheel smoke test.

## Development and implementation plan

Work is organized into milestones. Each milestone should have a working demonstration, tests, and documented contracts before the next layer depends on it.

### Phase 0 — Project foundation

- [x] Establish package metadata, supported Python versions, license, and development tooling.
- [x] Set up TypeScript compilation and bundle assets into the Python package.
- [x] Add CI for Python tests, frontend tests, type checking, and package builds.
- [x] Define versioning and compatibility policy for Python APIs and frontend assets.

The CI pipeline has passed frontend checks, Python 3.11–3.13 tests, wheel/source builds, and installed-wheel asset smoke tests. See [the Phase 0 workflow](docs/development/phase-0-foundation.md) and [compatibility policy](docs/architecture/compatibility-and-versioning.md).

**Exit criteria:** a clean environment can build and install the package, and the installed package can load a minimal AnyWidget with its bundled frontend.

### Phase 1 — AnyWidget foundation

- [x] Implement a reusable Python widget base with one atomic state trait.
- [x] Define the versioned Python-to-frontend data contract and JSON serialization rules.
- [x] Implement frontend initialization, model updates, and deterministic view cleanup.
- [x] Handle Python-originated and frontend-originated updates.
- [x] Test multiple widget instances, multiple views, conflict resolution, and cleanup.
- [x] Add a minimal interactive JSON state inspector as the synchronization demonstration.

See [the state contract](docs/architecture/state-contract.md) and [Phase 1 implementation guide](docs/development/phase-1-anywidget.md).

**Exit criteria:** a minimal interactive component synchronizes reliably in Jupyter without requiring users to build frontend assets.

### Phase 2 — First components

- [x] Implement Math input with MathLive.
- [x] Implement static mathematical rendering with KaTeX where appropriate.
- [x] Implement Text and Result components.
- [x] Define consistent component styling, themes, sizing, and accessibility behavior.
- [x] Publish runnable examples and component-level documentation.

**Exit criteria:** the Phase 1 widget contract supports the first independently usable Python components, with frontend and Python validation enforced by CI.

### Phase 3 — Structured and visual components

- [ ] Implement Matrix and Vector editing, including rectangular validation and clipboard support.
- [ ] Implement Graph plotting and interaction contracts.
- [ ] Implement the Diagram surface and a portable export format.
- [ ] Add validation, error display, and serialization tests for each component.

**Exit criteria:** structured data and visual components work independently and compose with the initial components.

### Phase 4 — Host integrations

- [ ] Verify standard Jupyter integration.
- [ ] Add an optional Marimo convenience adapter.
- [ ] Test asset loading and lifecycle behavior in supported hosts.
- [ ] Keep host-specific dependencies optional.

**Exit criteria:** the same component API works across documented AnyWidget hosts, with host adapters remaining thin.

### Phase 5 — Stability and release

- [ ] Finalize public API and compatibility guarantees.
- [ ] Add documentation, examples, and migration guidance.
- [ ] Test source distributions and wheels in clean environments.
- [ ] Publish to PyPI and document the one-line installation.
- [ ] Establish issue templates and contribution guidance.

**Exit criteria:** a user can install from PyPI, import a documented component, and use it without Node.js or a separate frontend setup.

## Engineering principles

1. **Python-first, not Python-only:** Python is the user-facing API; TypeScript provides rich browser interaction.
2. **One installable distribution:** compiled frontend assets ship inside the Python package.
3. **Small components, shared foundations:** components are independent at the API level but reuse common lifecycle, styling, and synchronization infrastructure.
4. **Explicit state contracts:** distinguish domain data, transient interaction, and computed output.
5. **Host independence:** AnyWidget is the browser integration layer; Marimo is an optional host integration.
6. **Accessible interaction:** keyboard navigation, focus management, semantic controls, and readable diagnostics are part of component quality.
7. **Test behavior, not just rendering:** cover synchronization, lifecycle, serialization, edge cases, and host integration.

## Contributing

The project is in its early development stage. Start by reading the architecture and development notes in `docs/`. Before adding a component, define its Python API, data contract, frontend responsibilities, serialization behavior, and tests.

Please open an issue to discuss substantial API or architectural changes before submitting a pull request.

## License

MathBlocks is released under the MIT License. See [LICENSE](LICENSE).
