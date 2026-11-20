# ADR-003: Expression evaluation contract

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owners:** MathBlocks maintainers
- **Scope:** The boundary and data contract for evaluating one mathematical expression using an external computation engine
- **Related decisions:** ADR-001 (AnyWidget component architecture), ADR-002 (canonical mathematical expression representation), ADR-004 (state synchronization and component lifecycle), ADR-005 (component identity, document model, and persistence)

## Context

MathBlocks owns mathematical expression editing, validation, representation, and presentation. ADR-002 defines a versioned MathJSON-compatible canonical expression model while preserving the original LaTeX source. MathBlocks needs a stable boundary through which a host application can submit a supported expression to a computation engine and present the resulting value or diagnostic.

The expression editor and renderer must not become computation engines. Conversely, MathBlocks should not dictate the internal implementation, programming language, numerical algorithms, or execution model of an external engine.

A strict distinction is required between evaluating one expression and executing a worksheet. Expression evaluation answers a bounded request against an explicitly supplied context. Worksheet execution involves document traversal, statement sequencing, variable-state transitions, dependency resolution, scopes, and control flow; those are separate engine-level responsibilities and are outside this ADR.

## Decision

**MathBlocks SHALL define an implementation-independent contract for requesting evaluation of one canonical expression against an explicit evaluation context and for receiving a structured result from an external computation engine. MathBlocks itself SHALL NOT evaluate mathematical expressions.**

The host application coordinates MathBlocks components and the selected computation engine. The engine owns mathematical evaluation semantics and execution of the individual expression request.

### 1. Responsibilities and ownership

**MathBlocks core owns:**
- The canonical expression input contract defined by ADR-002.
- Structural validation of expression envelopes and evaluation request/result envelopes.
- Stable serialization of request data that conforms to the public contract.
- Presentation-facing result and diagnostic data contracts.
- Association of displayed results with the expression/input revision for which they were produced.

**The external computation engine owns:**
- Determining whether it supports the expression schema, operators, functions, and required capabilities.
- Parsing/consuming the canonical structured expression according to its declared semantics.
- Mathematical interpretation and evaluation of the expression.
- Interpretation of supplied variable bindings, functions, units, dimensions, numeric types, precision, and domain rules.
- Producing the evaluated value or structured diagnostics.
- Any engine-specific algorithms, optimizations, numerical methods, and internal state needed to perform that one request.

**The host application owns:**
- Selecting and configuring the computation engine.
- Supplying the explicit evaluation context.
- Dispatching requests and delivering responses.
- Coordinating asynchronous work, cancellation, retries, and engine lifecycle.
- Deciding when to request evaluation, including in response to user actions or host-level workflows.
- Any worksheet-level sequencing or state management, through a separate engine-level contract.

The MathBlocks frontend MAY initiate a host-defined evaluation action, but MUST NOT perform evaluation itself or treat editor/renderer behavior as computation.

### 2. Evaluation unit and input

The unit of work defined here is **one expression evaluation request**. It is not a document, worksheet, block sequence, program, or general execution session.

An evaluation request MUST contain, at minimum:

- A request identifier unique within the host's request lifecycle.
- The canonical expression envelope from ADR-002, including its schema identifier and version.
- An explicit evaluation context supplied by the host.
- A correlation token sufficient to associate the response with the expression and context revision that were submitted.

The context is an explicit input to the request. It MAY contain named variable bindings and other engine-defined inputs, but MathBlocks does not define their mathematical meaning or resolve them from document order. The context MUST be represented using the agreed portable data boundary; engine-native runtime objects MUST NOT be placed directly into MathBlocks synchronized state or persisted document records.

The engine MUST NOT assume that omitted variables or functions can be obtained from an implicit worksheet environment managed by MathBlocks. Any additional engine session or environment is an explicit host/engine integration concern and is outside this expression contract.

The engine MUST validate that it understands the expression schema and every operator or extension node it needs to evaluate. An unsupported or unknown expression construct MUST produce an explicit unsupported-capability diagnostic; it MUST NOT be silently ignored or assigned guessed semantics.

### 3. Evaluation result

The engine returns a structured response correlated to the originating request. The public result contract MUST distinguish:

- **Success:** an evaluated value is available.
- **Evaluation failure:** the engine understood the request but could not produce a value, for example because of a mathematical domain error or invalid input.
- **Unsupported:** the engine cannot evaluate the expression or a required construct under its declared capabilities.

A successful result MUST provide a JSON-compatible structured value using a documented result-value schema. The schema MUST be capable of representing the value without relying on arbitrary Python objects, JavaScript objects, executable payloads, or display-only text as the sole value representation.

A result MAY additionally include presentation metadata such as a formatted display string, unit/dimension information, precision information, or engine provenance. Such metadata MUST NOT replace the structured value where a value exists.

A non-success response MUST provide one or more structured diagnostics with stable machine-readable codes and human-readable messages. Diagnostics MAY include source/expression locations when the engine can provide reliable locations. A failure or unsupported response MUST NOT be represented as a successful result containing a fabricated numeric value.

The concrete result-value schema and diagnostic taxonomy are implementation deliverables that must be specified before the first public evaluator adapter is declared stable. This ADR establishes the required semantics and boundaries, not a particular numerical type system.

### 4. Result freshness and correlation

An evaluation result is valid only for the expression and explicit context submitted in its request.

The request/response correlation data MUST allow the host and MathBlocks component to determine which expression revision and context revision the result belongs to. A result known to belong to an older expression or context MUST NOT be presented as the current result.

MathBlocks MAY retain and display a stale result if it is clearly identified as stale; it MUST NOT silently associate that result with newer inputs. Request identifiers and revision/fingerprint correlation are metadata, not mathematical expression identity.

Detailed scheduling, cancellation, retries, streaming, and asynchronous request lifecycle are host/engine integration concerns. They are not defined as a worksheet execution protocol by this ADR.

### 5. Expression and result state in MathBlocks

MathBlocks components MAY store or synchronize:
- The canonical expression and preserved source defined by ADR-002.
- The correlation metadata needed to associate a displayed result with submitted inputs.
- A validated externally supplied structured result.
- Structured diagnostics and presentation metadata.

MathBlocks MUST NOT:
- Compute a result from the expression.
- Reinterpret an engine result using undocumented assumptions.
- Treat LaTeX source as the primary evaluator input when a canonical expression is available.
- Store engine-native executable objects in synchronized state or persisted documents.
- Claim that the presence of a result means it is current without checking its correlation metadata.

Result components are presentation components. They display externally computed values and diagnostics; they do not independently evaluate expressions.

### 6. Compatibility and capability negotiation

The expression schema version and supported operator set are governed by ADR-002. An engine integration MUST declare which expression schema versions and operators/extensions it supports.

A MathBlocks expression may be valid under ADR-002 but unsupported by a particular engine. Structural validity and engine evaluability are separate checks.

Incompatible request/result contract changes require explicit versioning and migration or adapter compatibility rules. Engine-specific extensions MUST be namespaced and MUST NOT silently redefine core MathBlocks expression semantics.

### 7. Explicit exclusion: worksheet execution

This ADR does NOT define or authorize MathBlocks to implement:
- Worksheet or document execution.
- Sequential statement/block traversal.
- Variable creation, assignment, mutation, versioning, or shared variable-state ownership.
- Dependency graphs, dependency resolution, or recalculation scheduling.
- Lexical/dynamic scopes, namespaces, or local environments.
- Conditional blocks, loops, functions as executable worksheet constructs, or control flow.
- Program execution, execution snapshots, or a worksheet interpreter.
- A persistent computation kernel or general-purpose evaluator service.

These responsibilities belong to a separate engine-level architecture and contract. That contract may define how an engine consumes ordered worksheet content and manages execution state. It MUST remain distinct from this single-expression evaluation boundary.

## Alternatives considered

1. **Implement evaluation inside MathBlocks.** Rejected: couples the UI/document component library to mathematical semantics and a particular computation implementation.
2. **Use LaTeX as the evaluator input.** Rejected: ADR-002 establishes a validated structured expression as canonical; LaTeX is preserved editor-source metadata.
3. **Allow implicit access to worksheet variables.** Rejected: makes expression evaluation depend on hidden document order and an unspecified execution environment.
4. **Define worksheet execution in this ADR.** Rejected: expression evaluation and worksheet interpretation are different responsibilities and require separate contracts.
5. **Let result components calculate their own values.** Rejected: presentation components must remain independent of evaluator implementation and semantics.

## Consequences

### Positive

- MathBlocks remains a portable mathematical UI and document-component library.
- External computation engines can be replaced without changing the expression editor or renderer contracts.
- A host can connect different engines while preserving one MathBlocks expression representation.
- Expression validity, engine capability, evaluation outcome, and result freshness are distinguishable.
- Worksheet execution can evolve in a separate engine architecture without leaking into MathBlocks component responsibilities.

### Trade-offs

- A host integration is required to connect MathBlocks to an evaluator.
- The result-value and diagnostic schemas require careful specification before a stable adapter can ship.
- Different engines may support different subsets or semantics; capability reporting and explicit diagnostics are necessary.
- Asynchronous result freshness requires correlation metadata and host coordination.

## Acceptance criteria

- [ ] MathBlocks defines versioned request and response envelope schemas for single-expression evaluation.
- [ ] Requests carry the ADR-002 canonical expression and an explicit context.
- [ ] Request correlation identifies the expression and context revision/fingerprint used.
- [ ] Engine capability checks distinguish structurally valid expressions from expressions an engine can evaluate.
- [ ] Unsupported constructs produce explicit diagnostics and are never silently ignored.
- [ ] Successful responses contain a structured JSON-compatible value.
- [ ] Failure and unsupported responses contain structured diagnostics and no fabricated success value.
- [ ] Result metadata can be correlated with the submitted expression/context so stale results are not shown as current.
- [ ] MathBlocks validates and presents externally supplied results without performing evaluation.
- [ ] No worksheet interpreter, statement sequencing, variable-state manager, dependency resolver, scope system, or control-flow execution is introduced under this ADR.
- [ ] Tests cover request/result validation, unsupported expressions, error diagnostics, serialization, and stale-result correlation.
- [ ] At least one external evaluator adapter demonstrates the contract without making the adapter or engine a dependency of the MathBlocks core.

## Deferred decisions

- The exact JSON schema for numeric, symbolic, matrix, vector, interval, and unit-bearing result values.
- A standardized diagnostic code catalogue and source-location mapping.
- Engine capability discovery transport and adapter registration API.
- Asynchronous request scheduling, cancellation, retries, streaming, and progress reporting.
- Caching and memoization policy.
- Engine process lifecycle, sandboxing, resource limits, and security isolation.
- Worksheet execution and variable-state semantics, which require a separate engine-level contract.

## References

- [ADR-001: AnyWidget component architecture](ADR-001-anywidget-component-architecture.md)
- [ADR-002: Canonical mathematical expression representation](ADR-002-expression-representation.md)
- [ADR-004: State synchronization and component lifecycle](ADR-004-state-synchronization-and-lifecycle.md)
- [ADR-005: Component identity, document model, and persistence](ADR-005-component-identity-document-model-and-persistence.md)
- [Python–frontend state contract](../state-contract.md)
