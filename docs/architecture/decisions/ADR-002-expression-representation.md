# ADR-002: Canonical mathematical expression representation

- **Status:** Proposed
- **Date:** 2026-11-20
- **Decision owners:** MathBlocks maintainers
- **Scope:** Mathematical expression data, editor interchange, serialization, and rendering

## Context

MathBlocks needs a mathematical expression representation that survives editing, serialization, inspection, and future interchange with external computation engines.

LaTeX is an excellent presentation and editing format, but it is not a sufficient canonical data model. It can encode visually similar expressions with different source strings, and a LaTeX string alone does not provide a validated, editor-independent expression tree.

MathLive can expose structured MathJSON output. MathBlocks should use that ecosystem where appropriate without making its entire internal data contract identical to an editor's current output.

## Decision

**MathBlocks MUST store a versioned, validated, MathJSON-compatible structured expression as the canonical mathematical representation. It MUST also preserve the original LaTeX source supplied or authored by the user as editor-source metadata.**

MathBlocks owns the supported expression subset, schema version, validation rules, and conversion boundary. MathLive is an editor adapter; KaTeX (or another renderer) is a presentation adapter. Neither editor nor renderer owns the canonical model.

The canonical representation is not an evaluation result. This ADR does not introduce an evaluator or define the semantics of variable binding, units, scopes, or numerical execution.

## Canonical envelope

The conceptual envelope is:

```json
{
  "schema": "mathblocks.expression",
  "version": 1,
  "format": "mathjson",
  "expression": ["Power", "x", 2],
  "source": {
    "format": "latex",
    "text": "x^2"
  }
}
```

This is an illustrative serialization shape. The final Python types and JSON Schema must be defined before implementation. The `source` field preserves the original LaTeX text; it is not authoritative for structural operations when a valid canonical expression is available.

The envelope version is controlled by MathBlocks. It is independent of MathLive versions and MathJSON specification revisions.

## Initial supported expression subset

Version 1 should define a deliberately bounded subset, including:

- Numeric literals and named symbols.
- Addition, subtraction, multiplication, division, and negation.
- Powers, roots, and supported elementary functions.
- Equality and ordered comparisons.
- Grouping and function application.
- Lists/tuples only where required by component contracts; matrix/vector domain structures remain separately typed rather than being inferred from arbitrary nested lists.

The initial operator catalogue must specify each operator's arity and operand constraints. Unsupported operators must not be silently dropped, rewritten, or accepted as if they had known semantics.

### Extension policy

- Core operators use the canonical MathJSON operator names and documented operand forms.
- Extension operators must be explicitly namespaced and registered with a MathBlocks extension identifier and version.
- Unknown extension nodes may be preserved as opaque serialized data only when their envelope and structural validity can be verified.
- Opaque nodes cannot be edited, rendered, transformed, or evaluated by a component that does not understand the extension. The component must report that limitation.
- A future core operator or incompatible schema change requires a documented compatibility and migration policy.

MathBlocks must not claim universal MathJSON compatibility in version 1.

## LaTeX source preservation and conversion

The component stores both:
1. The canonical structured expression, used for structural inspection and interchange.
2. The original LaTeX source, used to preserve author intent and editor fidelity.

Rules:

- Preserve the original source string even when conversion succeeds.
- Editing through MathLive produces a candidate LaTeX source and structured expression; both are validated before the new domain state is committed.
- A source edit that cannot be converted into the supported canonical subset must not silently replace the previous valid canonical expression.
- Unsupported input must produce a clear diagnostic and preserve the source so the user does not lose work.
- Converting canonical expressions back to LaTeX must preserve mathematical meaning for the supported subset. Exact source-string round-tripping is not required because formatting may change.
- Where source and canonical forms disagree, the state is invalid and must be reconciled explicitly; the implementation must not silently choose one.

Cursor, selection, focus, composition state, and other ephemeral editor details are transient UI state and do not belong in the canonical expression envelope.

## Responsibilities

### Core expression model — `src/mathblocks/core/`

- Define the MathBlocks-owned expression envelope and version.
- Validate the supported MathJSON-compatible subset.
- Provide deterministic serialization and deserialization.
- Preserve source metadata.
- Define structural equality and inspection behavior.
- Remain independent of MathLive, KaTeX, and AnyWidget.

### MathLive adapter

- Convert supported editor output into the canonical expression representation.
- Initialize the editor from canonical expression data and preserved source.
- Preserve source during editing and report unsupported conversions.
- Never make undocumented editor-internal state the persisted public contract.

### Renderer adapter

- Render supported canonical expressions or the preserved LaTeX source according to a documented fallback policy.
- Report rendering failures without corrupting canonical state.
- Remain replaceable independently of the editor.

### Future evaluator boundary

External evaluators consume the structured expression and an explicit evaluation context. They do not receive LaTeX as the primary input. Evaluation semantics are outside this ADR and belong to a separate computation-boundary decision.

## Alternatives considered

1. **LaTeX-only canonical storage.** Rejected: presentation text is insufficient for reliable structural inspection and interchange.
2. **MathLive editor state as the canonical model.** Rejected: couples persistence to a particular editor implementation.
3. **Unrestricted MathJSON as the complete MathBlocks contract.** Rejected: leaves supported semantics and compatibility undefined.
4. **MathBlocks-owned versioned MathJSON-compatible subset plus preserved LaTeX source.** Selected: structured interoperability with controlled semantics and protection against source loss.

## Consequences

- Result and future expression-bearing components can share one structured expression contract.
- External evaluators can consume structured data without parsing LaTeX.
- MathLive and the renderer can be replaced independently.
- The supported operator subset and conversion adapters require explicit tests and maintenance.
- Some LaTeX constructs will initially be unsupported or only preserved as source with diagnostics.
- Schema migration becomes a maintained responsibility.

## Acceptance criteria

- [ ] The expression envelope has a documented schema identifier and version.
- [ ] Version 1 has an explicit operator catalogue, arity rules, and operand constraints.
- [ ] Original LaTeX source is preserved alongside canonical expression data.
- [ ] Supported MathLive output converts into the canonical expression model.
- [ ] Supported canonical expressions serialize and deserialize deterministically.
- [ ] Unsupported expressions produce diagnostics and do not silently destroy source or prior valid canonical state.
- [ ] Supported expressions round-trip between canonical structure and editor input without semantic change.
- [ ] Core expression types do not depend on MathLive, KaTeX, AnyWidget, or notebook hosts.
- [ ] LaTeX is never the sole canonical representation for a valid structured expression.
- [ ] No mathematical evaluation behavior is implemented or implied by this ADR.

## References

- [MathLive](https://mathlive.io/)
- [MathJSON documentation](https://mathlive.io/math-json/)
- [KaTeX](https://katex.org/)
