# Architecture Decision Records

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
