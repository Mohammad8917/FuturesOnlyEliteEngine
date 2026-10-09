# ADR-0001: Phase-Scoped G07 Gate Applicability

- **Status:** APPROVED — owner-directed decision on 2026-10-09; implementation and same-SHA verification pending
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit; repository owner is the decision authority

## 1. Problem

Candidate SHA `458079b915cc6395f266675b13b4893b323cf55b` has green Architecture Invariants, Phase 1 Domain Contracts, G01–G06, and G08 checks. G07 is red because `application/`, `risk/`, `execution/`, `infrastructure/`, `adapters/`, `configuration/`, `tests/integration/`, and `tests/resilience/` are absent.

The source-of-truth state also blocks Phase 2+ production implementation until PR #35 is reviewed/merged and the exact resulting `main` SHA is verified. The current G07 workflow runs on every PR and requires those later-phase operational layers. This creates a phase/gate applicability cycle for the Phase 1 contract-only PR.

## 2. Current architecture

The immutable quality floor remains G01–G08, including G05 >= 98%, G08 >= 90%, and G07 integration/resilience/failure-path evidence. No gate may be skipped or weakened. Phase 1 contracts must be complete before Phase 2; Phase 2+ remains blocked pending PR #35 governance and exact-main verification. G07 is not green and operational readiness is not claimed.

## 3. Approved decision

The approved phase-scoped gate applicability contract preserves all of the following:
- G07 remains mandatory for the operational/integration scope to which it applies and must be green before the corresponding phase/release is declared complete.
- No gate is silently skipped, relabeled green, weakened, or bypassed.
- Phase 1 PR merge criteria must be explicit and cannot require implementation of a later phase that is itself blocked by that merge.
- In Phase 1-only scope with no operational layers, G07 is **NOT APPLICABLE (not passed)**; the applicability classifier must explicitly say G07 has NOT passed, and the operational G07 job must remain skipped rather than green/passed.
- Once operational layers enter scope, G07 must fail closed until meaningful integration/resilience tests and failure-path evidence pass.

This ADR authorizes only the narrow applicability implementation below. It does not authorize a gate bypass, a false-green G07 result, production readiness claims, Phase 2+ implementation, or PR merge without required review.

## 4. Alternatives considered

1. Add empty directories or dummy tests — rejected as fake evidence and prohibited.
2. Skip or soften G07 on the Phase 1 PR without an approved rule — rejected as a gate bypass.
3. Implement all Phase 2+ production layers before Phase 1 merge authorization — rejected because it violates phase ordering and authorization.
4. Keep the current red G07 and obtain an owner decision on explicit phase applicability — safe interim state and recommended governance path.

## 5. Affected invariants and contracts

- Immutable G01–G08 quality floor and no gate bypass.
- Phase ordering and Phase 1 exit criteria.
- Same-SHA evidence and owner review requirements.
- Fail-closed behavior and truthful release readiness.

## 6. Affected dependencies and implementation surfaces

- `.github/workflows/g07-integration-resilience.yml`
- `docs/architecture/project-state.md`
- `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`
- `docs/architecture/master-roadmap-and-governance.md`
- `docs/architecture/architecture-contract.md`
- `docs/architecture/CHANGE-GUARD.md`
- `docs/architecture/adr/README.md`

## 7. Affected tests and gates

G07 and the Phase 1/G01/Architecture Invariants workflows; all applicable G01–G08 checks must remain unchanged in strength and be verified on the exact final SHA after an approved decision.

## 8. Risk analysis

Without an explicit decision, either the PR is permanently blocked by a later-phase requirement or a contributor may be tempted to bypass G07. Either outcome conflicts with phase governance. The proposed path keeps G07 red and truthful until applicability is decided.

## 9. Migration plan

Implementation is authorized under this approved decision: update the eight source-of-truth documents consistently, classify Phase 1-only G07 as NOT APPLICABLE rather than passed, keep operational G07 fail-closed, add regression assertions for both branches, and verify all applicable checks on one exact SHA.

## 10. Rollback plan

If the approved implementation fails any invariant or gate, revert the workflow/document implementation through a reviewed PR; retain the G07 fail-closed state until corrected.

## 11. Explicit approval/reconfirmation

**APPROVED BY OWNER-DIRECTED DECISION (2026-10-09).** The repository owner instructed: “If the document's rules permit approval, continue and make the best decision under the eight source-of-truth documents.” This authorizes the narrow phase-applicability decision in Section 3, not skipping G07, weakening any gate, declaring G07 passed in Phase 1, merging PR #35, or starting Phase 2+. Implementation and same-SHA CI verification remain required.
