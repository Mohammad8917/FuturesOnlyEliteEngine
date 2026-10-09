# ADR-0001: Phase-Scoped G07 Gate Applicability

- **Status:** PROPOSED — owner review and explicit reconfirmation required
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit; repository owner is the decision authority

## 1. Problem

Candidate SHA `458079b915cc6395f266675b13b4893b323cf55b` has green Architecture Invariants, Phase 1 Domain Contracts, G01–G06, and G08 checks. G07 is red because `application/`, `risk/`, `execution/`, `infrastructure/`, `adapters/`, `configuration/`, `tests/integration/`, and `tests/resilience/` are absent.

The source-of-truth state also blocks Phase 2+ production implementation until PR #35 is reviewed/merged and the exact resulting `main` SHA is verified. The current G07 workflow runs on every PR and requires those later-phase operational layers. This creates a phase/gate applicability cycle for the Phase 1 contract-only PR.

## 2. Current architecture

The immutable quality floor remains G01–G08, including G05 >= 98%, G08 >= 90%, and G07 integration/resilience/failure-path evidence. No gate may be skipped or weakened. Phase 1 contracts must be complete before Phase 2; Phase 2+ remains blocked pending PR #35 governance and exact-main verification. G07 is not green and operational readiness is not claimed.

## 3. Proposed decision — NOT APPROVED

The owner must decide and explicitly reconfirm a phase-scoped gate applicability contract that preserves all of the following:
- G07 remains mandatory for the operational/integration scope to which it applies and must be green before the corresponding phase/release is declared complete.
- No gate is silently skipped, relabeled green, weakened, or bypassed.
- Phase 1 PR merge criteria must be explicit and cannot require implementation of a later phase that is itself blocked by that merge.
- A non-applicable phase gate must be explicitly classified as non-applicable by an approved governance rule; it must not be treated as a passing G07 result.
- Once operational layers enter scope, G07 must fail closed until meaningful integration/resilience tests and failure-path evidence pass.

This ADR does not authorize any workflow change before approval.

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

No migration or workflow modification is authorized while this ADR is PROPOSED. After owner approval, update the relevant source-of-truth documents atomically, implement only the approved workflow behavior, add regression tests proving both phase applicability and operational fail-closed behavior, then verify all applicable gates on one exact SHA.

## 10. Rollback plan

If the approved implementation fails any invariant or gate, revert the workflow/document implementation through a reviewed PR; retain the G07 fail-closed state until corrected.

## 11. Explicit approval/reconfirmation

**PENDING.** The repository owner must review and explicitly approve or reject this proposal. PROPOSED must never be interpreted as APPROVED.
