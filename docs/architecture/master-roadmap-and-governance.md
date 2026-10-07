# Master Project Roadmap & Architecture Governance

## Status

**Authoritative project-control document.**

This document defines the permanent execution order, architecture freeze rules, runtime/deployment requirements, operational capabilities, phase gates, and handoff protocol for FuturesOnlyEliteEngine.

A future AI, engineer, or session must start at `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`, then follow the unified reading path defined there. This document remains authoritative for project-control execution order and governance; it does not replace the constitutional source-of-truth hierarchy.

## 1. Source-of-truth hierarchy

When documents or assumptions conflict, use this order:

1. `docs/architecture/architecture-invariants.md` — constitutional constraints.
2. Explicitly approved architectural decision recorded through the ADR process.
3. `docs/architecture/architecture-contract.md`
4. `docs/architecture/futures-responsibility-map.md`
5. `docs/architecture/dependency-rules.md`
6. `docs/architecture/master-roadmap-and-governance.md` for execution order and governance.
7. `docs/architecture/project-state.md` for current authorized work state.
8. Current production code, tests, CI, and repository state as implementation evidence.
9. Historical project material is reference only and cannot override the current architecture.

Historical Spot architecture, old repository decisions, old PRs, and old CI failures must not silently redefine this project.

## 2. Architecture freeze

The architecture baseline is **frozen by default**.

No AI or engineer may:
- change the product from Futures-only;
- reintroduce operational Spot;
- change CRYPTO/FOREX/GOLD scope;
- remove Linear or Inverse as first-class semantics;
- collapse Linear and Inverse formulas merely for reuse;
- change layer ownership;
- reverse dependency direction;
- move exchange-specific semantics into domain;
- replace independent exchange adapters with a generic adapter that erases meaningful differences;
- weaken fail-closed behavior;
- lower G05 below 98%;
- lower G08 below 90%;
- weaken, delete, skip, exclude, xfail, or bypass tests/gates to obtain green CI.

An architectural change is allowed only through the controlled ADR process. The project owner may propose a change, but owner intent does not bypass architectural governance. If an owner request conflicts with an invariant, implementation must stop and issue a **CRITICAL ARCHITECTURE WARNING**, followed by impact analysis, alternatives, risk analysis, ADR, explicit reconfirmation, document update, implementation, tests, CI enforcement, and same-SHA verification.

A code change is not an architecture change merely because it implements an already-approved contract.

## 3. Architecture-change firewall

Any change touching the Futures-only boundary, Spot boundary, market scope, Linear/Inverse semantics, financial accounting ownership, layer ownership, dependency direction, risk/execution boundary, exchange isolation, pipeline ordering, fail-closed behavior, quality thresholds, architecture enforcement, or release criteria is an Architecture Change Candidate and must stop for governance review before implementation.

There is no emergency bypass for architectural safety.

## 4. Runtime, deployment, and operational capability baseline

The permanent runtime baseline is **Python 3.13**.

Supported deployment environments are:
- Windows Server
- Linux Server
- Windows Home/Desktop

All three are first-class supported targets. Platform-specific code must remain isolated behind infrastructure boundaries and must not alter financial semantics or weaken safety controls.

The finished system must provide both:
- automated Futures trading through the complete risk-gated execution pipeline;
- signal and operational notifications through Telegram and email.

Telegram and email are delivery/observability channels. They cannot authorize execution, bypass risk, or convert notification failure into execution success.

The three supported markets are **100% Futures**:
- CRYPTO Futures
- FOREX Futures
- GOLD Futures

Operational Spot is permanently forbidden.

## 5. Governance baseline completeness

Phase 0 is not considered complete merely because the initial documents exist. The baseline is complete only when the following are explicit, internally consistent, and evidenced on the current HEAD:

- product identity, exact market scope, Futures-only boundary, and prohibited operational Spot behavior;
- Linear/Inverse semantic ownership and required financial/accounting vocabulary;
- layer ownership and dependency direction;
- exchange-adapter isolation and the exact adapter-count requirement;
- canonical terminology, contract naming, units, precision, UTC/time semantics, and validation expectations;
- risk, execution, order lifecycle, reconciliation, and audit ownership;
- data-quality, stale/contradictory-state, idempotency, and fail-closed behavior;
- configuration, secrets, credentials, security, and supply-chain ownership;
- observability, notifications, operational errors, and the rule that delivery failure never equals execution success;
- phase entry/exit criteria, gate entry/exit criteria, evidence requirements, and same-SHA verification;
- architecture-test and CI-enforcement expectations;
- ADR/change-control, owner-change protection, rollback, and migration expectations;
- persistent project state and handoff rules;
- no unresolved architectural contradiction, undefined critical owner, or ungoverned critical behavior.

**Phase 0 status:** OPEN — FINAL AUDIT REQUIRED.

Phase 1 and all production implementation remain blocked until this baseline has a recorded exit decision in `project-state.md`.



## 5.1 Phase 0 closure rule — prevent governance cycles

Phase 0 has a finite closure point. The purpose of the final audit is to establish an implementation-safe architecture, not to make governance documents indefinitely more complete.

The final audit is limited to these findings:

1. architecture contradiction;
2. unclear critical owner;
3. unclear or contradictory dependency direction;
4. missing critical contract;
5. dangerous or unowned failure/fallback behavior;
6. phase/gate without a usable entry or exit criterion;
7. critical requirement without an enforcement path;
8. inconsistent terminology that can change implementation meaning;
9. contradictory upgrade/runtime path;
10. critical missing requirement that would force architectural redesign later.

Every finding must be classified before action:

- **FIX NOW** — a genuine Phase 0 architecture gap that must be closed before Phase 1;
- **DEFER TO PHASE N** — a valid requirement owned by a later implementation phase; record it and do not reopen Phase 0 for it;
- **NOT AN ARCHITECTURE GAP** — implementation detail, local preference, optimization, or normal later-phase engineering; do not reopen governance.

Once the Phase 0 exit criteria are satisfied and the exit decision is recorded in project-state.md, Phase 0 is CLOSED. No new governance document, wording refinement, or completeness exercise may reopen Phase 0 by itself.

If a later phase discovers a concern, classify it first:
- architecture gap → stop the affected work and perform controlled architecture correction;
- implementation detail → continue the current phase;
- optimization/preference → do not reopen governance.

This rule prevents an Audit → documentation change → re-audit loop from becoming an infinite project cycle.

The target of Phase 0 is **sufficient architectural completeness to implement without fundamental redesign**, not exhaustive pre-definition of every future implementation detail.

## 6. Permanent execution order

The project proceeds through these phases in order.

### Phase 0 — Architecture baseline / governance finalization
Status: OPEN — final audit in progress.

Deliverables:
- architecture invariants;
- project state;
- ADR governance;
- architecture contract;
- Futures responsibility map;
- dependency rules;
- master roadmap/governance;
- README product boundary reference.

Exit condition:
- all governance baseline completeness criteria are verified on the current HEAD;
- all critical requirements have an explicit owner and enforcement path;
- no unresolved architecture contradiction remains;
- project-state records the evidence and authorizes Phase 1 explicitly.

### Phase 1 — Domain contracts
Define stable, implementation-independent Futures contracts.

Required coverage includes:
- instrument identity;
- contract type/family;
- Linear/Inverse;
- multiplier;
- settlement asset;
- margin asset;
- leverage;
- position side/mode;
- precision and units;
- funding;
- realized/unrealized PnL;
- exposure;
- liquidation;
- accounting;
- explicit validation/failure semantics.

Exit condition:
- every contract has owner, inputs, outputs, units, invariants, failure behavior, and applicability.

### Phase 2 — Application contracts and ports
Define use-case orchestration and stable ports without embedding exchange transport.

Exit condition:
- application cannot bypass domain contracts or risk/execution gates.

### Phase 3 — Risk architecture
Implement and validate:
- margin;
- leverage;
- liquidation distance;
- exposure;
- concentration;
- correlation;
- position sizing;
- account limits;
- fail-closed decisions.

Exit condition:
- invalid/unknown/stale/contradictory critical state cannot produce an executable decision.

### Phase 4 — Execution architecture
Define and implement:
- execution intent;
- execution risk gate;
- execution contract;
- order model;
- reconciliation;
- audit.

Exit condition:
- no unvalidated intent can become an order.

### Phase 5 — Exchange infrastructure
Build the 15 exchange adapters independently.

Each adapter must preserve meaningful exchange-specific behavior for:
- authentication;
- endpoints;
- request/response mapping;
- contract specification;
- multiplier/settlement;
- margin/leverage;
- funding;
- PnL/liquidation information;
- order semantics;
- precision/limits;
- position mode;
- reconciliation.

Exit condition:
- no adapter is a disguised copy of another;
- exchange-specific behavior stops at the infrastructure boundary;
- all mappings are independently testable.

### Phase 6 — Market/data pipeline
Implement the market and data path:

MARKET -> FUTURES INSTRUMENT -> MARKET ADAPTER -> MARKET DATA -> DATA VALIDATION -> REGIME PROBABILITY -> MTF STRUCTURE -> SETUP -> TREND/MOMENTUM -> CONFIRMATION -> COST/LIQUIDITY -> FUTURES RISK -> POSITION SIZING -> OPPORTUNITY RANKING -> DECISION -> SIGNAL CONTRACT

Exit condition:
- analysis remains separated from execution;
- invalid data fails closed;
- no analysis component can submit orders.

### Phase 7 — Cross-layer integration
Connect:

SIGNAL CONTRACT -> EXECUTION RISK GATE -> EXECUTION CONTRACT -> EXCHANGE ADAPTER -> ORDER -> POSITION/ORDER RECONCILIATION -> AUDIT

Exit condition:
- end-to-end behavior is deterministic, validated, auditable, and fail-closed.

### Phase 8 — Quality verification
Run gates in strict order:

G01 -> G02 -> G03 -> G04 -> G05 -> G06 -> G07 -> G08

No gate may be skipped because a later gate is green.

Required official standards:
- G01: zero unexplained format/lint violations;
- G02: zero unexplained type errors;
- G03: complete unit/contract coverage;
- G04: enforced architecture/dependency boundaries;
- G05: **>= 98%** coverage;
- G06: required security/supply-chain checks pass;
- G07: required integration/resilience and failure-path evidence;
- G08: **>= 90%** mutation score.

### Phase 9 — Release verification
Release is permitted only when the same final commit/HEAD has complete evidence for all required gates.

No historical green run may be used as proof for a different SHA.

## 7. Gate discipline

For every failure:

**Failure -> Evidence -> Root Cause -> Architecture Analysis -> Minimal Sufficient Fix -> Targeted Test -> Commit -> CI -> Same-SHA Verification**

Rules:
- fix the current failing gate first;
- do not jump ahead while the current gate is unresolved;
- never treat a symptom patch as a root-cause fix;
- never claim PASS from an older SHA;
- never use `--no-verify`;
- never lower a threshold;
- never delete or disable a test to make CI green.

## 8. Implementation unit protocol

Before creating or changing a production module, record:

- exact responsibility;
- layer;
- owning invariant;
- inputs;
- outputs;
- units/precision;
- allowed dependencies;
- forbidden dependencies;
- Linear/Inverse applicability;
- CRYPTO/FOREX/GOLD applicability;
- failure behavior;
- test boundary;
- downstream consumers.

If ownership is ambiguous, stop and resolve ownership before implementation.

## 9. Reuse policy

Reuse is allowed only when semantics are genuinely identical.

Do not share code merely because names or shapes look similar.

Especially prohibited:
- one formula pretending to cover Linear and Inverse when accounting differs;
- one generic exchange adapter erasing exchange semantics;
- one catch-all module combining unrelated financial responsibilities;
- compatibility abstractions that reintroduce Spot behavior.

Prefer explicit semantic boundaries over premature abstraction.

## 10. Testing strategy

Tests are part of the architecture, not a final cosmetic layer.

Required categories:
- unit tests for pure domain semantics;
- contract tests for stable boundaries;
- architecture/dependency tests;
- risk boundary and failure-path tests;
- exchange adapter contract/integration tests;
- reconciliation tests;
- resilience and failure-mode tests;
- security/supply-chain checks;
- mutation testing.

Coverage must represent meaningful behavior. Artificial tests, unreachable branches, exclusions, weakened assertions, and threshold manipulation are not acceptable substitutes.

## 11. Definition of done

A feature is not done because:
- the code imports;
- local tests pass;
- one CI job is green;
- coverage increased;
- a mock returns success.

A feature is done only when:
1. ownership is correct;
2. dependencies obey the architecture;
3. contracts and invariants are explicit;
4. failure behavior is fail-closed where required;
5. meaningful tests exist;
6. relevant quality gates pass;
7. the final same-SHA evidence is recorded.

## 12. AI handoff protocol

When a new AI/session starts work:

1. Start with `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`.
2. Follow its mandatory reading order; do not invent a competing document path.
3. Inspect the current repository HEAD and branch.
4. Identify the current phase and current failing/active gate.
5. Inspect current code before relying on historical assumptions.
6. Do not redesign the architecture unless an explicit architecture-change request exists.
7. Continue from the first incomplete phase/gate only.
8. Preserve all non-negotiable invariants.
9. Before any merge/release claim, verify the same SHA.

A new AI must **continue the map, not reinvent the map**.

## 13. Change-control rule

If implementation pressure appears to require an architectural change:

- stop implementation at the boundary;
- document the conflict;
- identify affected contracts, dependencies, tests, and downstream consumers;
- propose an ADR;
- obtain explicit approval;
- update the authoritative architecture documents;
- only then modify implementation.

No silent architecture drift is permitted.

## 14. Final target

The target is not merely a green repository.

The target is an evidence-backed, production-grade, Futures-only professional trading engine whose architecture remains understandable, enforceable, testable, auditable, and maintainable even when the implementing AI or engineering team changes.
