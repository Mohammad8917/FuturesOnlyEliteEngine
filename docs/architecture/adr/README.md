# Architecture Decision Records

**Navigation:** Start with `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`. This file governs ADR process only and does not create an alternative project path.

## Purpose

This directory contains the formal record of approved, rejected, and superseded architectural decisions.

## Mandatory rule

An ADR is required before changing an architectural invariant, ownership boundary, dependency direction, Futures-only boundary, Linear/Inverse semantics, exchange isolation, quality floor, pipeline ordering, fail-closed behavior, or release criteria.

A proposal is not approval.

## Status lifecycle

PROPOSED → APPROVED → implemented and verified

or

PROPOSED → REJECTED

An approved decision may later become SUPERSEDED only through another explicit architecture decision.

## Owner-request rule

The project owner may propose an architecture change.

If the proposal conflicts with an invariant, implementation must stop and issue:

CRITICAL ARCHITECTURE WARNING

The warning must explain the conflict, impact, risk, alternatives, and affected gates/contracts.

Owner intent does not authorize bypassing architecture governance.

## Minimum ADR structure

Every ADR must contain:
1. Status
2. Date
3. Proposer/Owner
4. Problem
5. Current Architecture
6. Proposed Change
7. Why Current Architecture Is Insufficient
8. Alternatives Considered
9. Affected Invariants
10. Affected Contracts
11. Affected Dependencies
12. Affected Tests/Gates
13. Risk Analysis
14. Migration Plan
15. Rollback Plan
16. Explicit Approval/Reconfirmation

## No silent architecture drift

No AI, agent, engineer, CI job, or implementation pressure may convert a proposed architecture change directly into code.

Required path:

PROPOSAL → WARNING → IMPACT ANALYSIS → ADR → EXPLICIT RECONFIRMATION → DOCUMENT UPDATE → IMPLEMENTATION → TEST → CI → SAME-SHA VERIFICATION

## Phase 1 implementation note — multiplier contract

The multiplier/contract-specification implementation does not change an architectural invariant or ownership boundary; it implements the already-approved Phase 1 contract. Its fixed semantic baseline is documented in the authoritative architecture documents and enforced by production contract tests and CI.

If a future change proposes different Linear/Inverse multiplier meaning, different financial formulas, different ownership, or different dependency direction, it becomes an Architecture Change Candidate and must use the ADR process above.

## Phase 1 multiplier closure

The multiplier/contract-specification implementation is a closed implementation of the approved architecture baseline and is evidenced by same-SHA CI. The Phase 1 cursor now advances to settlement asset and settlement semantics. Any future semantic change to multiplier meaning remains subject to the ADR process.
\n## Phase 1 settlement closure rule

Settlement asset and settlement semantics are an approved implementation of the existing Phase 1 contract baseline, not an architecture change. Any proposal to redefine settlement denomination, conversion direction, ownership, dependency direction, or fail-closed semantics must use the ADR process before implementation.
\n## Phase 1 settlement closure

Settlement asset and settlement semantics are a closed implementation of the approved Phase 1 baseline and are evidenced by same-SHA CI. The Phase 1 cursor now advances to margin asset and margin semantics. Any future semantic change to settlement denomination or conversion meaning remains subject to the ADR process.


## Phase 1 margin closure rule

Margin asset and margin semantics are an approved implementation of the existing Phase 1 contract baseline, not an architecture change. The canonical instrument identity already owns an explicit margin asset; this unit closes its denomination and conversion semantics without redefining leverage, initial/maintenance margin, liquidation, or exchange-specific collateral policy.

Any future proposal to redefine margin-asset ownership, equate margin with settlement, change conversion direction, introduce hidden defaults, alter dependency direction, or change fail-closed behavior is an Architecture Change Candidate and must use the ADR process before implementation.


## Phase 1 margin closure

Margin asset and margin semantics are a closed implementation of the approved Phase 1 baseline and are evidenced by same-SHA CI on main merge SHA f2c30bf3da77f56b2dd2d9350af7bb1376f47797. The Phase 1 cursor now advances to leverage vocabulary and contract-level constraints. Any future semantic change to margin-asset ownership, denomination, conversion direction, or fail-closed behavior remains subject to the ADR process.

