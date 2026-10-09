# ADR-0002: Module-Level Import-Cycle Enforcement

- **Status:** PROPOSED — implementation is not authorized until the repository owner explicitly reconfirms this decision.
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit; repository owner is the decision authority.

## 1. Problem

The current `validation/architecture_dependency_validator.py` builds its cycle graph using architectural layer names. Its depth-first search can detect cycles between layers, but it cannot detect circular imports between modules in the same layer. Issue #39 records this verified enforcement coverage gap. This is not evidence that a production import cycle currently exists.

## 2. Current Architecture

The dependency validator enforces allowed layer direction, forbidden imports, Futures-only boundaries, and layer-level dependency cycles. The Source-of-Truth dependency rules describe a one-directional dependency graph and require architecture tests and CI to enforce dependency boundaries. Existing cycle detection does not represent individual Python modules as graph nodes.

## 3. Proposed Change

Extend architecture enforcement to construct a deterministic module-to-module import graph for repository-owned Python modules in governed layers, while retaining all current layer-level checks unchanged. Reject direct and indirect import cycles between modules, including cycles within one architectural layer. Report a stable, deterministic cycle path.

Resolve supported imports conservatively:
- absolute imports of repository-owned modules;
- relative imports, including package-relative imports;
- package `__init__.py` targets;
- `from package import module` forms where the target module can be resolved unambiguously.

Do not treat third-party or standard-library imports as repository module edges. Do not broadly exclude files to obtain a passing result. Unresolved imports must follow an explicit, tested policy and must not silently conceal an otherwise resolvable internal edge.

## 4. Why Current Architecture Is Insufficient

A graph whose nodes are only layer names collapses all modules within each layer into one node. A cycle such as `contracts.alpha -> contracts.beta -> contracts.alpha` therefore cannot appear in the layer graph, even though Python can encounter a runtime circular import.

## 5. Alternatives Considered

1. Keep layer-only cycle detection — rejected as insufficient to detect same-layer module cycles.
2. Add a module graph without regression tests — rejected because resolution edge cases and false positives would be unverified.
3. Ban all intra-layer imports — rejected because it is unnecessarily restrictive and changes valid dependency behavior.
4. Add module-level cycle detection alongside existing layer rules and prove it with focused fixtures — proposed.

## 6. Affected Invariants

- The dependency graph remains deterministic and one-directional.
- Existing layer direction and single-owner rules remain unchanged.
- No architecture validator false-green may be introduced.
- Futures-only boundaries, fail-closed behavior, and all G01–G08 quality floors remain unchanged.

## 7. Affected Contracts

- Existing dependency direction and ownership rules remain authoritative.
- This proposal adds enforcement granularity; it does not change allowed layer direction or assign new financial ownership.

## 8. Affected Dependencies

- `validation/architecture_dependency_validator.py`
- `tests/architecture/test_dependency_direction.py`
- Applicable architecture contract / dependency-rule documentation and architecture CI.

## 9. Affected Tests and Gates

Required regression coverage:
- direct same-layer module cycle is rejected;
- indirect same-layer module cycle is rejected;
- cross-layer cycle remains rejected;
- acyclic same-layer graph is accepted;
- absolute and relative imports resolve correctly;
- package `__init__.py` imports are covered;
- unresolved and ambiguous import behavior is explicit and deterministic;
- repeated runs produce stable diagnostics.

G01 and G04 enforcement evidence, Architecture Invariants, Phase 1 Domain Contracts, and all other applicable gates must pass on the exact resulting SHA. G05 must remain at least 98%; G08 must remain at least 90%. No skips, xfails, weakened assertions, or exclusions may be introduced.

## 10. Risk Analysis

Incorrect import resolution can produce false positives or false negatives. The implementation must be bounded to repository-owned Python modules, tested with isolated temporary repository fixtures, and preserve current enforcement. Dynamic imports that cannot be statically resolved remain a documented limitation and must not be misrepresented as statically verified.

## 11. Migration Plan

No production or validator implementation change is authorized by this proposal alone. After explicit owner reconfirmation, implement the module graph and regression fixtures, reconcile relevant Source-of-Truth documentation, run local targeted tests and all applicable CI gates, and record evidence for the exact resulting SHA.

## 12. Rollback Plan

If the implementation causes false positives, false negatives, or any existing boundary regression, revert the implementation through a reviewed pull request while preserving the existing layer-level checks. Do not weaken gates to restore green status.

## 13. Explicit Approval / Reconfirmation

**Pending repository-owner decision.** The owner must explicitly approve or reject this ADR before implementation begins. Repository write access, an issue report, or this proposal itself is not approval. Until approved, issue #39 remains open and no claim is made that module-level cycle enforcement is complete.
