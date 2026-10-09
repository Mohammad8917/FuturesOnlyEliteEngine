# ADR-0002: Module-Level Import-Cycle Enforcement

- **Status:** PROPOSED — not approved; no implementation authorized
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit; repository owner is the decision authority

## 1. Problem

The current `validation/architecture_dependency_validator.py` constructs its cycle graph using architectural layer names. It detects cycles between layers, but cannot detect a cycle between two or more Python modules inside the same layer. Existing regression coverage demonstrates a cross-layer cycle only. This is an enforcement-coverage gap, not evidence that a production module cycle currently exists.

## 2. Current architecture

The approved source-of-truth documents freeze dependency direction and layer ownership. The validator is an enforcement mechanism and must not redefine layer ownership, dependency direction, or production responsibilities. Architecture enforcement changes are Architecture Change Candidates and must follow the ADR process.

## 3. Proposed decision — owner confirmation required

Extend the architecture validator to detect import cycles among repository-owned Python modules while retaining every existing layer-level dependency rule and cycle check unchanged.

If approved, the implementation must:
- construct a module-level directed graph for resolvable internal Python imports;
- correctly account for absolute imports, relative imports, package `__init__.py` modules, and `from package import submodule` forms;
- report a deterministic, actionable cycle path;
- preserve existing forbidden-import, layer-direction, Spot-boundary, order-call, and HTTP-call checks without exclusions or weaker enforcement;
- fail closed for relevant unresolved internal imports rather than silently treating them as external;
- include temporary-root regression tests for same-layer cycles, multi-module cycles, package imports, relative imports, non-cycles, and existing cross-layer-cycle behavior;
- prove tests and all applicable gates pass on the exact same SHA.

This proposal does not authorize moving financial logic, changing layer ownership, weakening any gate, adding ignore/skip/xfail rules, or merging PR #35.

## 4. Alternatives considered

1. Keep layer-only cycle detection — rejected as insufficient if module-level cycles are within the intended invariant.
2. Ban all imports within a layer — rejected because it would over-constrain valid internal module dependencies and change the architecture beyond the identified gap.
3. Add module-level cycle detection while retaining layer checks — proposed; preserves current rules and adds the narrowest enforceable coverage.
4. Add broad exclusions for package imports or unresolved modules — rejected because exclusions could hide real cycles.

## 5. Affected invariants and contracts

- One-directional dependency graph and frozen layer ownership.
- Architecture enforcement must be executable and CI-enforced.
- No silent architecture drift; all existing boundaries remain unchanged.
- No gate weakening or false-green reporting.

## 6. Affected implementation and tests

- `validation/architecture_dependency_validator.py`
- `tests/architecture/test_dependency_direction.py`
- Applicable Architecture Invariants, G01 dependency architecture, and full candidate CI.

No source-of-truth document is changed by this proposal. If approved, the owner-authorized decision and implementation must be reflected in the governed documents as required by the ADR process.

## 7. Risk analysis

Import resolution can misclassify package imports, relative imports, or namespace packages and produce false positives or miss cycles. The implementation must use deterministic resolution and focused regression tests. The current layer-level checks must remain active. A green test run alone does not establish absence of every dynamic-import cycle; the enforced scope must be stated accurately.

## 8. Migration plan

No migration is authorized while this ADR is PROPOSED. Following explicit owner approval/reconfirmation, update the required architecture records, implement the module graph and tests, run relevant tests and CI, then verify all evidence against the exact same candidate SHA.

## 9. Rollback plan

If an approved implementation causes false positives or breaks existing enforcement, stop the affected candidate and revert only through the normal reviewed PR process. Do not weaken checks or bypass gates to restore green CI.

## 10. Explicit approval / reconfirmation

**Pending.** Repository owner must explicitly approve or reject the proposed module-level import-cycle invariant before implementation. Owner intent to continue the project is not, by itself, approval of this specific architecture decision.
