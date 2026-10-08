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
- Current phase: Phase 1 — Domain Contracts
- Current gate: Phase 1 Domain Contracts
- Implementation phase authorized: YES — Phase 1 Domain Contracts
- Current HEAD: repository HEAD on `main`; this state document must not pin a mutable SHA as authoritative state.
- Last verified SHA: 8c0e2da70cb49fa6c8863d5d1ba1e4a348bcaacf; verified by current GitHub Actions same-SHA evidence.
- Completed phases: Phase 0 — Architecture Baseline / Governance Final Audit
- Active work: Phase 1 Domain Contracts — instrument identity, multiplier/contract specification, settlement asset/settlement semantics, and margin asset/margin semantics are implemented and evidenced; leverage vocabulary and contract-level constraints are implemented and evidenced; initial margin semantics are now the first incomplete contract.
- Blocked work: Phase 2+ production implementation remains blocked until each preceding phase exit criteria is evidenced.
- Next authorized action: define and implement leverage vocabulary and contract-level constraints from the canonical baseline; preserve explicit Linear/Inverse semantics and the mandatory implementation unit protocol.
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
- open architecture questions: None identified in the bounded Phase 0 deep audit.
- evidence references: Phase 0 closure control applied on 3efc4b90f49790db65e07387d37fa7ed52a11f9a; deep-audit baseline verified through 497b8b7ac3dabc5d3da9fd35a9a7025d23381fca; instrument identity implementation and contract CI evidenced on main SHA 53bf816e49d5025f0ca6df2a671d590fb3770e6a; master index at docs/architecture/ARCHITECTURE-MASTER-INDEX.md
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


## Phase 0 closure control

The final audit is explicitly bounded. Findings must be classified as FIX NOW, DEFER TO PHASE N, or NOT AN ARCHITECTURE GAP. Once exit criteria are evidenced and the exit decision is recorded, Phase 0 is closed and must not be reopened for documentation completeness alone. A later phase may stop only for a genuine architecture gap; implementation details and optimizations stay in their owning phase.


## Phase 0 exit decision

**CLOSED — authorized to proceed to Phase 1 Domain Contracts.** The bounded deep audit found and closed the identified Phase 0 architecture gaps. Cross-document ownership, dependency direction, Futures-only scope, Linear/Inverse semantics, fail-closed behavior, configuration/security boundary, state authority, idempotency, concurrency/recovery, execution halt, trusted time, audit integrity, release provenance, phase/gate evidence, and anti-cycle controls are aligned on the verified pre-snapshot SHA. This state snapshot records the closure decision; the snapshot commit itself becomes the new repository HEAD and must be treated as the next current HEAD for subsequent work.

## Security requirement added during Phase 0 final audit

The final audit identified and closed two classes of genuine Phase 0 gaps: (1) explicit anti-hardcoding/configuration-security governance; and (2) explicit financial-state authority, idempotency, concurrency, restart/recovery, execution-halt, trusted-clock/skew, audit-integrity, configuration-provenance, and release-provenance requirements. These are now represented in the authoritative architecture path. Production enforcement, implementation, tests, and security scanning remain future-phase/G06 work and are not claimed complete by these documentation changes.

## Phase 1 multiplier / contract-specification evidence

The multiplier/contract-specification cursor is closed with same-SHA CI evidence. The active cursor is now **leverage vocabulary and contract-level constraints**.

The canonical semantic lock is:
- quantity unit = CONTRACTS;
- exact finite positive Decimal multiplier/contract size;
- Linear = base units per contract, quote notional = quantity × multiplier × price;
- Inverse = quote-price-denomination units per contract, quote notional = quantity × multiplier;
- base exposure is explicit and family-specific;
- quote denomination is bound to the canonical symbol;
- invalid, zero, negative, non-finite, contradictory, ambiguous, or unsupported specifications fail closed;
- margin/settlement are not inferred by this unit.

No downstream Phase 1 cursor advance is authorized until production implementation, contract tests, CI, and same-SHA evidence are green.

## Phase 1 cursor transition — multiplier closed

- Verified implementation SHA: `8c0e2da70cb49fa6c8863d5d1ba1e4a348bcaacf`
- Current documentation cursor snapshot is maintained on the current main HEAD and must be re-verified after every state change.
- Multiplier / contract specification: COMPLETE — production implementation, contract tests, Phase 1 CI, Architecture Invariants CI, and G01 CI are green on the same merge SHA.
- Active work: Phase 1 Domain Contracts — leverage vocabulary and contract-level constraints.
- Next authorized action: define and implement the initial margin semantics contract.
- Forbidden action: do not bypass settlement semantics, reinterpret multiplier meaning, weaken tests/gates, lower G05/G08, or skip the first incomplete Phase 1 contract.
\n## Phase 1 settlement implementation evidence

The active cursor is **initial margin semantics**.

The implementation contract is frozen:
- settlement unit = ASSET;
- settlement asset must equal the canonical instrument settlement asset;
- source asset is explicit;
- same-asset settlement has no conversion rate;
- cross-asset settlement requires an explicit positive finite Decimal conversion rate;
- conversion rate is settlement-asset units per source-asset unit;
- no exchange/network/scheduling/persistence/account mutation is permitted in the domain contract;
- invalid, zero, negative, non-finite, contradictory, or ambiguous settlement terms fail closed.

Production boundary: `contracts/futures/settlement.py`.
Test boundary: `tests/contracts/test_settlement.py`.
CI boundary: `.github/workflows/phase1-domain-contracts.yml`.
\n## Phase 1 cursor transition — settlement closed

- Settlement asset and settlement semantics: COMPLETE — production implementation, contract tests, Phase 1 CI, Architecture Invariants CI, and G01 CI are green on same SHA `164dcb97c38271ab29f79f8e9b8068bcc8a55234`.
- Active work: Phase 1 Domain Contracts — margin asset and margin semantics.
- Next authorized action: define and implement initial margin semantics.
- Forbidden action: bypass margin semantics, redefine settlement/multiplier meaning, weaken tests/gates, lower G05/G08, or skip the first incomplete Phase 1 contract.


## Phase 1 margin implementation contract

The active cursor is margin asset and margin semantics.

The implementation contract is frozen:
- authoritative margin asset = FuturesInstrumentIdentity.margin_asset;
- margin unit = ASSET;
- source asset is explicit;
- same-asset margin has no conversion rate;
- cross-asset margin requires an explicit positive finite Decimal conversion rate;
- rate direction = margin-asset units per source-asset unit;
- margin asset is independent from settlement asset and is never inferred from it;
- leverage, initial margin, maintenance margin, liquidation, and exchange-specific collateral policy are not inferred by this unit;
- invalid, zero, negative, non-finite, contradictory, or ambiguous terms fail closed.

Production boundary: contracts/futures/margin.py.
Test boundary: tests/contracts/test_margin.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.


## Phase 1 margin closure evidence

Margin asset and margin semantics are COMPLETE on main merge SHA f2c30bf3da77f56b2dd2d9350af7bb1376f47797:
- production boundary: contracts/futures/margin.py
- test boundary: tests/contracts/test_margin.py
- CI enforcement: .github/workflows/phase1-domain-contracts.yml
- Architecture Invariants CI: green on the same SHA
- G01 CI: green on the same SHA
- Phase 1 contract CI: green on the same SHA

## Phase 1 current cursor — initial margin

Current cursor: initial margin semantics.

Next authorized action: define and implement leverage vocabulary and contract-level constraints. No Phase 2+ work is authorized, and no threshold/test/gate weakening is permitted.

## Phase 1 leverage implementation contract

The active implementation unit is leverage vocabulary and contract-level constraints.

Frozen semantics:
- leverage unit = RATIO;
- requested/minimum/maximum leverage are explicit finite positive Decimal values;
- minimum <= maximum;
- requested leverage must be within inclusive bounds;
- all supported Futures markets and Linear/Inverse families are covered;
- no leverage default is inferred from exchange, margin, notional, or account state;
- leverage does not calculate margin, liquidation, risk, or position sizing;
- invalid or ambiguous leverage terms fail closed.

Production boundary: contracts/futures/leverage.py.
Test boundary: tests/contracts/test_leverage.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.
