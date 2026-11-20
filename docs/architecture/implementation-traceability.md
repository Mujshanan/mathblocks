# ADR-to-implementation traceability

- **Status:** Working implementation audit
- **Last reviewed:** 2026-11-20
- **Architecture baseline:** `foundation/phase-0-ci-packaging`
- **Implementation candidate reviewed:** cumulative Phase 1–5 pull-request stack, ending at PR #5 head `78584e7de99612e2c9918ffae869528607d46c3d`, plus P0 foundation changes through commit `12e878649056938e09b02bc984afa4f7caf8876e` on this branch.
- **Scope:** Trace accepted ADR-001 through ADR-005 requirements to implementation evidence, tests, and remaining work.

> This matrix distinguishes accepted architectural decisions from implemented behavior. The phase pull requests are still open and unmerged. “Implemented” means evidence exists in the reviewed candidate branch; it does not mean that code has been merged or released. “Not verified” means the available code or tests do not establish the requirement.

## Status vocabulary

| Status | Meaning |
|---|---|
| **Implemented** | Code and relevant tests/evidence are present in the reviewed candidate. |
| **Partial** | Some of the requirement exists, but important acceptance criteria or integration evidence remain. |
| **Not implemented** | No implementation evidence was found in the reviewed candidate. |
| **Not verified** | A claim may be true in a particular environment, but the available repository evidence does not prove it. |

## Executive summary

| ADR | Decision area | Status | Main finding |
|---|---|---|---|
| [ADR-001](decisions/ADR-001-anywidget-component-architecture.md) | AnyWidget component architecture | **Partial** | Shared AnyWidget base, public components, bundled assets, lockfile-based CI, real Jupyter-kernel display checks, and AFM view lifecycle tests exist; browser-host end-to-end verification remains incomplete. |
| [ADR-002](decisions/ADR-002-expression-representation.md) | Canonical expression representation | **Not implemented** | The Math component still stores LaTeX as its value; no MathBlocks-owned canonical expression envelope/operator validator was found. |
| [ADR-003](decisions/ADR-003-expression-evaluation-contract.md) | Single-expression evaluation boundary | **Partial** | Result presentation primitives exist, but no request/response schema, capability contract, or evaluator adapter exists. |
| [ADR-004](decisions/ADR-004-state-synchronization-and-lifecycle.md) | State synchronization and lifecycle | **Partial** | Versioned atomic state, deterministic conflict policy, detached Python state, real notebook-kernel display checks, and per-view abort/reconnect tests exist; browser-host lifecycle verification remains incomplete. |
| [ADR-005](decisions/ADR-005-component-identity-document-model-and-persistence.md) | Component identity, document model, persistence | **Not implemented** | Components have typed payloads, but no ordered document model, stable component/document IDs, registry, or document serialization/migration layer was found. |

The most substantial completed foundation is the shared AnyWidget/state transport layer. The largest unimplemented domain foundations are canonical expression data and persistent document identity/modeling.

## Detailed traceability

### ADR-001 — AnyWidget component architecture

**Decision intent:** Every public component is itself an AnyWidget, with a shared base; framework-independent core contracts remain separate from host adapters; Python distributions ship the compiled frontend assets without requiring Node.js at user runtime.

| Requirement | Implementation evidence | Tests / verification | Status | Remaining work |
|---|---|---|---|---|
| Shared `MathBlocksWidget` derives from AnyWidget and owns synchronized transport | `src/mathblocks/widgets/base.py` | `tests/python/test_widget_base.py`; `tests/integration/test_anywidget_hosts.py` | **Implemented** | Keep component classes on this shared base. |
| Public component classes are directly displayable widgets; no nested widget wrapper | Component classes inherit through `ComponentWidget` → `MathBlocksWidget` | `tests/integration/test_anywidget_hosts.py`; `tests/integration/test_jupyter_kernel.py` verifies the base widget's real notebook display MIME | **Implemented** | Keep the public component classes directly displayable. |
| Components, core contracts, widgets, and host integrations have separate modules | `components/`, `core/`, `widgets/`, `integrations/` | Import and component tests | **Partial** | Core mathematical/document models are still mostly absent; module layout alone does not satisfy those contracts. |
| Jupyter/AnyWidget host compatibility | AnyWidget components; notebook cells execute in a real IPython kernel and emit widget-view MIME descriptors | `tests/integration/test_anywidget_hosts.py`; `tests/integration/test_jupyter_kernel.py`; `tests/frontend/bootstrap-lifecycle.test.ts` | **Partial** | Add a browser-host end-to-end test in JupyterLab or Notebook to verify actual DOM rendering, output removal, reconnect, and disposal. |
| Optional Marimo adapter wraps the same component instance | `src/mathblocks/integrations/marimo.py` | `tests/integration/test_marimo.py` | **Implemented** | Preserve optional/lazy import behavior. |
| Frontend assets are built into wheel and sdist; end-user install does not require Node.js | Phase 5 build and artifact verification workflow; `scripts/verify_release_artifacts.py` | PR #5 CI run [44754371500](https://github.com/Mujshanan/mathblocks/actions/runs/44754371500) reports artifact and clean-install smoke tests passing on implementation commit | **Implemented in candidate CI** | Re-run on the final integrated commit after the stacked PRs are reconciled. |
| CSS is isolated from the host page | Frontend styles scoped under the MathBlocks root in the component implementation | Frontend tests/build | **Implemented in candidate** | Include a regression test against host-level selectors and multiple widget instances. |
| Reproducible dependency installation through a committed lockfile | `package-lock.json` (lockfile v3) is committed; CI uses `npm ci` in frontend and Python build jobs | CI run [44769265930](https://github.com/Mujshanan/mathblocks/actions/runs/44769265930) passed frontend checks and Python 3.11/3.12/3.13 build/test jobs | **Implemented** | Keep `package-lock.json` in sync with `package.json`; retain `npm ci` in CI. |

### ADR-002 — Canonical mathematical expression representation

**Decision intent:** A versioned, validated MathJSON-compatible expression is canonical; original LaTeX is retained as source metadata. MathLive and KaTeX are replaceable adapters, not owners of the domain model.

| Requirement | Implementation evidence | Tests / verification | Status | Remaining work |
|---|---|---|---|---|
| MathBlocks-owned expression envelope with schema/version | No expression model or schema found in `src/mathblocks/core/` | No expression schema tests found | **Not implemented** | Define Python types and JSON Schema for the ADR-002 envelope. |
| Explicit supported operator catalogue and operand validation | No operator catalogue or canonical expression validator found | No operator validation tests found | **Not implemented** | Specify operator names, arity, operand constraints, extension rules, and invalid-node diagnostics. |
| Preserve LaTeX source alongside canonical expression | `Math` currently stores a LaTeX string in its generic `value` field (`src/mathblocks/components/math.py`) | `tests/python/test_components.py` verifies the string value | **Not implemented** | Replace LaTeX-only domain storage with a validated canonical expression plus preserved source metadata. |
| MathLive adapter converts editor output into canonical data | MathLive is part of the frontend component workflow, but no canonical expression conversion boundary was found | No canonical conversion tests found | **Not implemented** | Implement editor adapter and invalid/unsupported conversion behavior. |
| Deterministic canonical serialization/deserialization | Existing `core/serialization.py` serializes generic component state, not expression trees | State serialization tests do not establish expression serialization | **Not implemented** | Add expression-specific normalization, validation, round-trip, and migration tests. |
| Unknown extension nodes are preserved only when structurally verifiable and are not treated as understood | No expression extension registry or opaque-node handling found | No tests found | **Not implemented** | Implement explicit namespaced extension registration and opaque preservation policy. |
| Renderer consumes canonical expression or documented source fallback without corrupting state | Math component supports editable/static rendering, but its stored domain value remains LaTeX | Component/frontend tests do not prove canonical rendering boundary | **Partial** | Make renderer adapter consume the canonical model and test fallback/error behavior. |

### ADR-003 — Expression evaluation contract

**Decision intent:** MathBlocks validates and presents single-expression evaluation requests/results but never evaluates. An external engine evaluates one canonical expression against an explicit context. Worksheet execution belongs to a separate engine-level contract.

| Requirement | Implementation evidence | Tests / verification | Status | Remaining work |
|---|---|---|---|---|
| Versioned single-expression request schema | No request model or schema found | No evaluator contract tests found | **Not implemented** | Define request ID, canonical expression, explicit context, and correlation metadata. |
| Explicit context rather than implicit worksheet lookup | No evaluation-context contract found | No tests found | **Not implemented** | Define portable binding/context envelope and reject hidden implicit dependencies. |
| Engine capability checks for expression versions/operators | No engine capability declaration or negotiation layer found | No tests found | **Not implemented** | Define capability reporting and unsupported-expression outcomes. |
| Structured success value and structured failure/unsupported diagnostics | `Result` accepts a generic value, optional unit/error, and string diagnostics | `tests/python/test_components.py` covers display fields only | **Partial** | Define typed result-value and diagnostic schemas; distinguish success, failure, and unsupported states. |
| Correlate result to expression/context revision and prevent stale result display | No request correlation/freshness metadata found in result component | No stale-result tests found | **Not implemented** | Add correlation metadata and stale-result handling. |
| External evaluator adapter; MathBlocks does not compute | No evaluator adapter found; no computation code was found in core | No adapter contract tests found | **Not implemented** | Implement a minimal test adapter only after the request/result schemas are agreed. |
| Worksheet execution remains outside MathBlocks | Current components do not provide a worksheet interpreter | Scope inspection | **Implemented as a boundary decision; no engine implementation implied** | Keep worksheet sequencing, variable state, dependencies, scopes, and control flow in a separate engine contract. |

### ADR-004 — State synchronization and component lifecycle

**Decision intent:** One atomic versioned state envelope is shared by Python and frontend views. Updates are validated and resolved deterministically; per-view interaction state remains local.

| Requirement | Implementation evidence | Tests / verification | Status | Remaining work |
|---|---|---|---|---|
| One atomic versioned state envelope | `core/serialization.py` and `widgets/base.py` define and transport `schema_version`, `revision`, `actor`, and `data` | `tests/python/test_widget_base.py`; `tests/frontend/store.test.ts` | **Implemented** | Maintain a single synchronized trait. |
| Framework-independent state store and deterministic revision/actor ordering | `core/state.py`, `core/serialization.py` | `tests/python/test_state_store.py`, widget conflict tests, frontend store tests | **Implemented** | Add cross-language conformance vectors so Python and TypeScript always choose the same winner. |
| Invalid/stale updates do not replace accepted state | Python trait validation and rejected-update restoration in `widgets/base.py` | Invalid envelope and stale-update tests | **Implemented** | Add browser-to-Python and multi-client integration coverage. |
| Python nested mutation cannot bypass observation; getters return detached data | `component_state` returns detached data; updates pass through validated setter | `tests/python/test_widget_base.py` | **Implemented** | Continue to keep raw synchronized envelope immutable to callers. |
| Frontend state separates synchronized data from per-view transient interaction state | Frontend store implementation and component views | `tests/frontend/store.test.ts` | **Partial** | Audit each component for accidental persistence of cursor, selection, focus, hover, and temporary editing state. |
| Multiple views share state while keeping per-view actors/transient state | Shared model subscriptions and per-view lifecycle cleanup are exercised | `tests/frontend/bootstrap-lifecycle.test.ts` mounts two independent views against one model, verifies propagation, aborts one view, and reconnects another; `tests/integration/test_jupyter_kernel.py` verifies repeated notebook displays use the same model ID | **Partial** | Add browser-host coverage for two simultaneously rendered views and view-local interaction state. |
| Reconnection and disposal follow AnyWidget lifecycle; disposal does not destroy Python state | AFM render hooks bind cleanup to each host-provided `AbortSignal`; Python widget state remains independent of view cleanup | `tests/frontend/bootstrap-lifecycle.test.ts` verifies independent abort, cleanup, reconnect, and preserved model state; notebook-kernel test verifies kernel-side state persists across cells | **Partial** | Verify actual browser-host output removal/reconnection and frontend disposal in JupyterLab or Notebook. |
| External results are not presented as current when their inputs have changed | ADR describes freshness; current `Result` has no correlation fields | No tests found | **Not implemented** | Coordinate with ADR-003 result correlation implementation. |

### ADR-005 — Component identity, document model, and persistence

**Decision intent:** V1 documents are ordered component collections. Document/component identities survive save/restore; copying creates new identities; unknown components are preserved; MathBlocks serializes documents but the host owns storage.

| Requirement | Implementation evidence | Tests / verification | Status | Remaining work |
|---|---|---|---|---|
| Ordered document model containing component records | No document model found; components currently expose independent state payloads | No document model tests found | **Not implemented** | Define document envelope, ordered component collection, and document schema version. |
| Stable opaque document and component IDs | No document/component identity fields or identity service found | No identity tests found | **Not implemented** | Define UUID identity generation, validation, copy/move semantics, and identity lifecycle. |
| Component registry with stable type IDs and schema versions | Components use string discriminator values such as `math`, `matrix`, and `graph`; no registry/migration system found | No registry tests found | **Partial** | Formalize registry entries, per-type schema versions, migrations, and duplicate/unknown type behavior. |
| Unknown structurally valid component records are preserved | No document loader/unknown-component preservation path found | No tests found | **Not implemented** | Add opaque record preservation and user-visible diagnostics. |
| JSON document serialization/deserialization | Existing serialization is for synchronized state envelopes only | State tests do not cover document round-trips | **Not implemented** | Implement deterministic document serialization, validation, and round-trip tests. |
| Host application owns file/database/cloud storage | No storage backend found; package has no file persistence service | Architectural boundary in ADR only | **Implemented as an architectural boundary** | Keep filesystem/database/cloud persistence out of MathBlocks core. |
| Copy/move/save/restore identity semantics | No document operations found | No tests found | **Not implemented** | Add tests: move preserves IDs; component copy regenerates component ID; document copy regenerates document and component IDs; save/restore preserves IDs. |
| Explicit conversion between live component state and persisted document records | No conversion adapter found | No tests found | **Not implemented** | Define conversion boundaries; do not persist live AnyWidget transport envelopes as the document format. |

## Cross-ADR implementation dependencies

The following dependencies should guide implementation order:

1. **ADR-001 + ADR-004 foundation:** Finish synchronization conformance and real host lifecycle tests. Keep AnyWidget as transport and the framework-independent state store as the policy owner.
2. **ADR-002 expression domain model:** Implement the canonical expression envelope, operator catalogue, source preservation, validation, and deterministic serialization. ADR-003 cannot be implemented correctly before this boundary exists.
3. **ADR-005 document model:** Define document/component identity, registry, ordered records, unknown-component preservation, and JSON persistence. Document records should embed versioned component domain data, not live AnyWidget state envelopes.
4. **ADR-003 evaluation contract:** Define concrete request/result schemas and freshness metadata against ADR-002 expressions. Add a small external adapter as a conformance fixture; do not introduce worksheet execution.
5. **Browser-host lifecycle validation:** Add a JupyterLab/Notebook browser test for actual DOM rendering, output removal, reconnect, and disposal. Then continue cross-host integration for expression edits, result updates, document save/restore, and multiple views across Python, Jupyter, and optional Marimo.

## Prioritized implementation backlog

| Priority | Work item | ADR coverage | Exit evidence |
|---|---|---|---|
| P0 | Commit the frontend dependency lockfile and verify deterministic CI install | ADR-001 | **Complete:** `package-lock.json` committed; CI uses `npm ci`; run [44769265930](https://github.com/Mujshanan/mathblocks/actions/runs/44769265930) passed. |
| P0 | Add kernel-backed notebook display and frontend view-lifecycle tests | ADR-001, ADR-004 | **Implemented:** notebook kernel emits real widget-view MIME descriptors; frontend test verifies two views, independent abort cleanup, reconnect, and retained model state. CI run [44769395392](https://github.com/Mujshanan/mathblocks/actions/runs/44769395392) is the validation run for this commit. |
| P1 | Implement canonical expression types, schema, operator catalogue, and validation | ADR-002 | Versioned expression fixtures; positive/negative validation and deterministic round-trip tests. |
| P1 | Implement component/document IDs, ordered document model, registry, and migrations | ADR-005 | Document save/restore, unknown component preservation, copy/move identity tests. |
| P2 | Specify request/result/diagnostic schemas and capability contract | ADR-003 | Versioned JSON schemas and conformance fixtures; stale-result tests. |
| P2 | Implement a minimal external evaluator adapter for contract tests | ADR-003 | Adapter consumes canonical expressions and explicit context; no evaluator dependency in MathBlocks core. |
| P3 | Complete end-to-end host tests across document, expression, evaluation, and state lifecycle | ADR-001–005 | Integrated notebook test suite and clean wheel/sdist smoke tests on final candidate commit. |

## Audit limitations and maintenance rules

- The implementation review used the cumulative Phase 1–5 candidate branch associated with open PR #5, not a merged release. PR #5 identifies implementation commit `6d28f3f564d977265d8ec851930ba081d317afbf` and final documentation-only head `78584e7de99612e2c9918ffae869528607d46c3d`.
- The ADR documents were authored on `foundation/phase-0-ci-packaging`; the phase PRs are a stacked, unmerged sequence. Reconcile/rebase the stack so the accepted ADRs and this matrix are present in the final integrated branch before treating this audit as a release baseline.
- CI success on a phase commit is evidence for that commit only. It does not prove that later documentation or implementation changes passed CI.
- Status is based on repository code and tests inspected for this audit. A documentation statement or a passing unrelated test is not evidence that an acceptance criterion is implemented.
- Update this matrix whenever an ADR, implementation, test, or phase boundary changes. Every **Implemented** row should retain a concrete code path and a test or CI reference.

## References

- [ADR-001: AnyWidget component architecture](decisions/ADR-001-anywidget-component-architecture.md)
- [ADR-002: Canonical mathematical expression representation](decisions/ADR-002-expression-representation.md)
- [ADR-003: Expression evaluation contract](decisions/ADR-003-expression-evaluation-contract.md)
- [ADR-004: State synchronization and component lifecycle](decisions/ADR-004-state-synchronization-and-lifecycle.md)
- [ADR-005: Component identity, document model, and persistence](decisions/ADR-005-component-identity-document-model-and-persistence.md)
- [Python–frontend state contract](state-contract.md)
- [Phase 5 pull request](https://github.com/Mujshanan/mathblocks/pull/5)
