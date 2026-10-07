# Project State — FuturesOnlyEliteEngine

## Purpose

This file is the persistent handoff state. It prevents a new AI, engineer, or session from guessing where the project is or choosing an unauthorized next step.

This is project state, not the architectural contract. Architectural rules remain governed by the architecture documents, especially architecture-invariants.md.

## Current authoritative state

- Repository: Mohammad8917/FuturesOnlyEliteEngine
- Default branch: main
- Product: Elite Futures-Only Professional Trading Engine
- Python runtime: 3.13
- Supported deployment: Windows Server, Linux Server, Windows Home/Desktop
- Supported markets: CRYPTO Futures, FOREX Futures, GOLD Futures — 100% Futures
- Operational capabilities: automated Futures trading + Telegram/email signal and operational notifications
- Architecture status: FROZEN BY DEFAULT
- Operational Spot: FORBIDDEN
- Current phase: Phase 0 — Architecture Baseline / Governance Completion
- Current gate: Architecture baseline governance
- Implementation phase authorized: NO — until governance baseline is finalized
- Active work: Establish immutable architecture invariants, persistent project state, and controlled ADR process
- Blocked work: Production implementation until the architecture governance baseline is complete
- Next authorized action: Verify governance documents, then begin Phase 1 — Domain Contracts
- Forbidden action: Do not redesign architecture, reintroduce operational Spot, bypass Linear/Inverse semantics, bypass risk/execution boundaries, lower G05/G08, weaken tests, or skip the first incomplete phase/gate

## Required state fields for every update

Whenever this file is updated, record:
- current phase
- current gate
- current HEAD
- last verified SHA
- completed phases
- active work
- blocked work
- next authorized action
- forbidden actions
- open architecture questions
- evidence references

## State transition rule

A phase or gate may be marked complete only with evidence.

A new AI/session must not infer completion from old conversation messages, old CI runs, old commits, assumptions, or partially implemented code.

Current repository evidence and same-SHA verification control.

## Handoff rule

The next AI/session must read this file before changing production code.

If state is ambiguous or inconsistent with repository evidence:

STOP → REPORT CONFLICT → RECONCILE STATE → CONTINUE

Do not guess.

## Architecture-change state

Any proposed architecture change must be represented through the ADR process before project state can authorize implementation.

Owner requests that conflict with an invariant must trigger the critical architecture warning defined in architecture-invariants.md.
