# Project State — FuturesOnlyEliteEngine

## Purpose

Start from `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`; this file is the persistent handoff state and controls only the currently authorized work. It prevents a new AI, engineer, or session from guessing where the project is or choosing an unauthorized next step.

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
- Current phase: Phase 0 — Architecture Baseline / Governance Final Audit
- Current gate: Architecture baseline governance
- Implementation phase authorized: NO — until the final governance audit is complete
- Current HEAD at last verification: 754307b53785f6dc2b62445360daca0cbdcc16f9
- Last verified SHA: 754307b53785f6dc2b62445360daca0cbdcc16f9
- Completed phases: None — Phase 0 remains open until its exit evidence is recorded
- Active work: Preserve the completed governance baseline and begin only the first authorized Phase 1 action after the Phase 0 exit decision is explicitly recorded
- Blocked work: Production implementation, Phase 1 domain-contract implementation, and all downstream phases
- Next authorized action: Record the Phase 0 exit decision after this evidence snapshot; if and only if all exit criteria remain satisfied, authorize Phase 1 — Domain Contracts
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
- evidence references: governance audit verified on 754307b53785f6dc2b62445360daca0cbdcc16f9; master index at docs/architecture/ARCHITECTURE-MASTER-INDEX.md
- master-index navigation reference: docs/architecture/ARCHITECTURE-MASTER-INDEX.md

## Phase 0 exit criteria

Phase 0 is complete only when all of the following are explicitly verified on the current repository HEAD:

- architecture invariants are complete and internally consistent;
- project-state fields are complete and consistent with repository evidence;
- ADR governance is defined and unambiguous;
- architecture contract, responsibility map, dependency rules, and roadmap agree on product scope and ownership;
- canonical terminology and boundary vocabulary are consistent;
- runtime, deployment, operational capability, security, observability, audit, reconciliation, and fail-closed requirements are explicitly owned;
- phase/gate entry and exit criteria are explicit;
- evidence requirements and same-SHA verification rules are explicit;
- architecture enforcement is defined as rule → contract → implementation → test → CI → evidence;
- no unresolved architecture contradiction or unowned critical requirement remains.

Only after these conditions are evidenced may `Implementation phase authorized` change to `YES — Phase 1 Domain Contracts`.

## State transition rule

A phase or gate may be marked complete only with evidence.

A new AI/session must not infer completion from old conversation messages, old CI runs, old commits, assumptions, or partially implemented code.

Current repository evidence and same-SHA verification control. Because updating this state file itself creates a new commit, the recorded HEAD is the exact SHA verified immediately before this state snapshot commit; the next session must refresh it before relying on state.

## Handoff rule

The next AI/session must read this file before changing production code.

If state is ambiguous or inconsistent with repository evidence:

STOP → REPORT CONFLICT → RECONCILE STATE → CONTINUE

Do not guess.

## Architecture-change state

Any proposed architecture change must be represented through the ADR process before project state can authorize implementation.

Owner requests that conflict with an invariant must trigger the critical architecture warning defined in architecture-invariants.md.
