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

**Phase 0 status:** CLOSED — Phase 1 Domain Contracts authorized.

Phase 1 Domain Contracts is authorized. Phase 2+ remains blocked until each preceding phase exit criteria is evidenced.



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
Status: CLOSED — Phase 1 Domain Contracts authorized.

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

### Phase 1.1 — Canonical domain contract baseline

The Phase 1 contract baseline is explicit and must not be inferred from implementation:

- instrument identity;
- canonical Futures symbol semantics;
- contract family/type, including explicit Linear/Inverse applicability;
- multiplier and contract specification;
- settlement asset and settlement semantics;
- margin asset and margin semantics;
- leverage vocabulary and contract-level constraints;
- position side and position mode;
- price, quantity, monetary units, denomination, precision, and rounding;
- funding-rate value, interval, and funding calculation;
- realized PnL and unrealized PnL;
- exposure and position valuation;
- liquidation price and liquidation constraints;
- Futures accounting and settlement accounting;
- validation status, provenance/freshness where applicable, and explicit failure semantics.

Each contract must satisfy the mandatory implementation unit protocol and remain free of network, transport, persistence, or exchange-specific behavior.

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
- execution-halt requests/circuit-breaker conditions and explicit handoff to the execution authority boundary;
- validated time/freshness/skew inputs and safety-critical configuration provenance.

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
- idempotency identity and duplicate-submission protection;
- concurrency/versioning for order and position transitions;
- restart/failover recovery with mandatory reconciliation before execution resumes;
- scoped/global execution halt semantics;
- append-only/tamper-evident audit evidence and release provenance requirements.

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

### Security/hardcoding enforcement

The security baseline explicitly forbids hard-coded sensitive information and environment/deployment/account/exchange-specific operational configuration. Safety-critical configuration must be validated and fail closed. G06 and the architecture/security test suite must enforce this boundary without relying on manual review alone.

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

## Phase 1 multiplier / contract-specification gate

The multiplier unit is governed by the following fixed contract before downstream Phase 1 work:

1. quantity is explicitly CONTRACTS;
2. multiplier/contract size is an exact finite positive Decimal;
3. Linear multiplier is base units per contract and notional uses quantity × multiplier × price;
4. Inverse multiplier is quote-price-denomination units per contract and notional uses quantity × multiplier;
5. base exposure is explicitly family-specific;
6. price denomination is bound to the canonical quote asset;
7. invalid/zero/negative/non-finite/contradictory/ambiguous/unsupported specifications fail closed;
8. margin and settlement are separate contracts;
9. exchange-specific lot/tick/precision metadata cannot redefine domain semantics.

Gate exit requires production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence. No Phase 1 cursor advance occurs before all four are present.

## Phase 1 cursor transition

Multiplier and contract specification has exited its gate with production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence on main SHA `8c0e2da70cb49fa6c8863d5d1ba1e4a348bcaacf`.

The next authorized Phase 1 unit is **initial margin semantics**. The implementation-unit protocol and no-weakening gate discipline remain unchanged.
\n## Phase 1 settlement gate

The settlement unit must close with:
1. explicit settlement asset bound to canonical instrument identity;
2. explicit source denomination;
3. deterministic same-asset/no-conversion semantics;
4. deterministic cross-asset conversion semantics with explicit positive finite Decimal rate;
5. no domain dependency on exchange/network/scheduling/persistence/account mutation;
6. fail-closed validation for all invalid or ambiguous terms;
7. meaningful contract tests;
8. CI enforcement;
9. same-SHA evidence.

No later Phase 1 contract may advance ahead of this gate.
\n## Phase 1 cursor transition — margin

Settlement semantics have exited their gate with production implementation, meaningful tests, CI enforcement, and same-SHA evidence on main SHA `164dcb97c38271ab29f79f8e9b8068bcc8a55234`.

Historical Phase 1 margin unit: closed with same-SHA evidence. The current next authorized Phase 1 unit is **leverage vocabulary and contract-level constraints**. The implementation-unit protocol and no-weakening gate discipline remain unchanged.


## Phase 1 margin gate

The margin unit must close with:
1. margin asset explicitly owned by canonical instrument identity;
2. explicit ASSET denomination;
3. explicit source denomination for upstream margin amounts;
4. deterministic same-asset/no-conversion semantics;
5. deterministic cross-asset conversion with an explicit positive finite Decimal rate;
6. explicit separation of margin asset from settlement asset;
7. no leverage, initial-margin, maintenance-margin, liquidation, or exchange-specific collateral inference;
8. no domain dependency on network, exchange SDK, persistence, runtime configuration, or hidden defaults;
9. fail-closed validation for invalid or ambiguous terms;
10. meaningful contract tests;
11. CI enforcement;
12. same-SHA evidence.

No later Phase 1 contract may advance ahead of this gate.

## Phase 1 initial margin gate

The initial-margin unit must close with:
1. explicit ownership at the Futures domain/contract boundary;
2. explicit RATIO denomination for the requirement rate;
3. exact finite Decimal semantics;
4. explicit positive finite notional input with declared denomination;
5. explicit positive finite initial-margin ratio;
6. deterministic formula: initial margin amount = notional × initial_margin_ratio;
7. output denomination identical to the supplied notional denomination;
8. no implicit rounding or quantization;
9. CRYPTO/FOREX/GOLD coverage;
10. Linear/Inverse coverage while consuming canonical family-specific notional semantics;
11. no leverage, exchange-default, account-state, maintenance-margin, liquidation, risk, or position-sizing inference;
12. no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation;
13. fail-closed validation for invalid or ambiguous inputs;
14. meaningful contract tests;
15. CI enforcement;
16. same-SHA evidence.

No Phase 1 cursor advance is permitted until all sixteen conditions are evidenced.

## Phase 1 cursor transition — initial margin closed

Initial margin semantics have exited their gate with production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence on main SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`.

The next authorized Phase 1 unit is **maintenance margin semantics**. The implementation-unit protocol and no-weakening gate discipline remain unchanged.

## Phase 1 maintenance margin gate

Before implementation, maintenance margin must explicitly define:
1. owner and responsibility boundary;
2. formula inputs and outputs;
3. denomination and exact numeric representation;
4. Linear/Inverse applicability;
5. CRYPTO/FOREX/GOLD applicability;
6. tier/rate/amount semantics where applicable;
7. precision and rounding behavior;
8. fail-closed handling of missing, invalid, contradictory, stale, unsupported, or ambiguous terms;
9. allowed and forbidden dependencies;
10. meaningful contract tests;
11. CI enforcement;
12. same-SHA evidence.

No maintenance-margin implementation may infer exchange-specific values or weaken any quality threshold.


## Phase 1 maintenance margin semantic lock

Maintenance margin is an explicit Futures domain/contract requirement. It is distinct from leverage, initial margin, liquidation, risk policy, and exchange-specific collateral policy.

Frozen semantics:
- owner: Futures domain/contract boundary;
- unit: RATIO for the maintenance-margin requirement rate;
- numeric representation: exact finite Decimal;
- inputs: canonical Futures instrument identity, matching market, explicit positive finite notional, and explicit positive finite maintenance-margin ratio;
- formula: `maintenance_margin_amount = notional × maintenance_margin_ratio`;
- output denomination: identical to the explicit notional denomination;
- precision: exact Decimal multiplication with no implicit rounding or quantization;
- applicability: CRYPTO Futures, FOREX Futures, GOLD Futures; Linear and Inverse;
- the notional is consumed from canonical multiplier/contract-specification semantics and is not redefined here;
- exchange-specific tiers, rates, offsets, brackets, notional bands, or collateral rules are not guessed or silently defaulted by this canonical contract;
- no inference from leverage, initial margin, account state, liquidation, risk policy, exchange defaults, or position sizing;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation dependency;
- missing, invalid, zero, negative, non-finite, contradictory, unsupported, stale, or ambiguous critical terms fail closed;
- meaningful contract tests, CI enforcement, and same-SHA evidence are required before the cursor can advance.

Production boundary: `contracts/futures/maintenance_margin.py`.
Test boundary: `tests/contracts/test_maintenance_margin.py`.
CI boundary: `.github/workflows/phase1-domain-contracts.yml`.

The canonical implementation does not claim exchange-specific tier schedules. Such schedules may be mapped later through explicit exchange/infrastructure contracts only when their provenance, tier selection semantics, denomination, precision, freshness, and failure behavior are explicit.


## Phase 1 maintenance margin closure evidence

Maintenance-margin semantics are COMPLETE on main merge SHA `7f647c4105738d7dfe298b283841e3eaec6524a7`.

Evidence on the exact merge SHA:
- production boundary: `contracts/futures/maintenance_margin.py`;
- test boundary: `tests/contracts/test_maintenance_margin.py`;
- Phase 1 Domain Contracts CI: green;
- Architecture Invariants CI: green;
- G01 Dependency Architecture CI: green.

The frozen contract remains:
- explicit RATIO requirement rate;
- exact finite Decimal arithmetic;
- explicit positive finite notional and maintenance-margin ratio;
- deterministic `notional × maintenance_margin_ratio`;
- unchanged notional denomination;
- CRYPTO/FOREX/GOLD and Linear/Inverse coverage;
- no guessed exchange-specific tiers/rates/offsets;
- fail-closed invalid, ambiguous, stale, contradictory, unsupported, or missing critical terms;
- no threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening.

The next authorized Phase 1 unit is **position side and position mode semantics**. No Phase 2+ production implementation is authorized before the preceding Phase 1 exit criteria are evidenced.


## Phase 1 position side / position mode semantic lock

Maintenance-margin semantics are closed. The next Phase 1 unit is position side and position mode semantics.

Frozen baseline:
- owner: Futures domain/contract boundary;
- position side vocabulary: explicit LONG or SHORT only;
- position mode vocabulary: explicit ONE_WAY or HEDGE only;
- both are immutable, exchange-independent boundary vocabulary;
- ONE_WAY means one net position side at a time; HEDGE permits independently addressed LONG and SHORT positions;
- BOTH, NET, Spot, or implicit third states are rejected by the canonical contract;
- mode and side must be explicitly supplied; neither may be inferred from exchange/account state, order payloads, leverage, margin, or strategy behavior;
- exact financial calculation is not performed by this vocabulary contract;
- applicable to CRYPTO Futures, FOREX Futures, and GOLD Futures, and to Linear and Inverse Futures;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation dependency;
- invalid, missing, contradictory, unsupported, or ambiguous values fail closed;
- exchange-specific mapping may translate external mode/side representations only at infrastructure boundaries and may not redefine canonical meaning;
- meaningful contract tests, CI enforcement, and same-SHA evidence are required before the cursor advances.

Production boundaries: contracts/futures/position_side.py, contracts/futures/position_mode.py.
Test boundary: tests/contracts/test_position_side_mode.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.


## Phase 1 position side / position mode closure evidence

Position side and position mode semantics are COMPLETE on main merge SHA `6731c6c80d4d31c4bb180dbb2d343de76537971a`.

Evidence on the exact merge SHA:
- production boundaries: `contracts/futures/position_side.py`, `contracts/futures/position_mode.py`;
- test boundary: `tests/contracts/test_position_side_mode.py`;
- Phase 1 Domain Contracts CI: green;
- Architecture Invariants CI: green;
- G01 Dependency Architecture CI: green.

The frozen contract remains explicit LONG/SHORT side vocabulary and ONE_WAY/HEDGE mode semantics, with no exchange/account inference, no Spot semantics, no hidden defaults, and fail-closed invalid or ambiguous values.

The next authorized Phase 1 unit is **price, quantity, monetary units, denomination, precision, and rounding semantics**. No threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening is permitted.


## Phase 1 next-unit semantic gate — price / quantity / monetary units

The next unit must first freeze one explicit primary owner and define:
1. price and quantity units;
2. monetary denomination and quote/base/settlement relationships;
3. exact numeric representation;
4. precision and rounding/quantization semantics;
5. Linear/Inverse applicability;
6. CRYPTO/FOREX/GOLD applicability;
7. interaction with the already-closed multiplier, settlement, margin, leverage, initial-margin, maintenance-margin, and position side/mode contracts without redefining them;
8. missing, invalid, contradictory, stale, unsupported, or ambiguous input behavior;
9. allowed and forbidden dependencies;
10. meaningful tests;
11. CI enforcement;
12. same-SHA evidence.

No exchange-specific precision, tick size, lot size, rounding mode, or default may be guessed into the canonical contract.


## Phase 1 price / quantity / monetary-unit semantic lock

Position side and position mode are complete on main merge SHA 6731c6c80d4d31c4bb180dbb2d343de76537971a. The active Phase 1 contract is price, quantity, monetary units, denomination, precision, and rounding semantics.

Frozen baseline:
- owner: Futures domain/contract boundary;
- price unit: QUOTE_PER_BASE — quote-asset units per one base-asset unit;
- quantity unit: CONTRACTS, consistent with the canonical multiplier contract;
- price denomination must equal the canonical Futures symbol quote asset;
- price and quantity are exact finite positive Decimal values; bool and binary float inputs are rejected;
- canonical precision policy is EXACT and canonical rounding policy is NONE: no implicit quantization or rounding occurs;
- exchange tick sizes, lot sizes, decimal-place limits, exchange-specific precision, and exchange rounding modes are not guessed or embedded here;
- applicable to CRYPTO/FOREX/GOLD and Linear/Inverse Futures;
- this contract does not redefine multiplier, settlement, margin, leverage, initial/maintenance margin, position side/mode, funding, PnL, liquidation, or execution rules;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation dependency;
- invalid, missing, contradictory, unsupported, non-finite, zero, negative, or ambiguous values fail closed;
- infrastructure may map exchange-specific precision/rounding metadata only after this canonical semantic boundary and may not redefine its meaning;
- meaningful tests, CI enforcement, and same-SHA evidence are required before the cursor advances.

Production boundary: contracts/futures/price_quantity.py.
Test boundary: tests/contracts/test_price_quantity.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.


## Phase 1 price / quantity / monetary-unit closure evidence

Price, quantity, monetary units, denomination, precision, and rounding semantics are COMPLETE on main merge SHA `13c8edef7a0553b1262f2487935e001ef5348aa7`.

Evidence on the exact merge SHA:
- production boundary: `contracts/futures/price_quantity.py`;
- test boundary: `tests/contracts/test_price_quantity.py`;
- Phase 1 Domain Contracts CI: green;
- Architecture Invariants CI: green;
- G01 Dependency Architecture CI: green.

The frozen contract is exact QUOTE_PER_BASE pricing, CONTRACTS quantity, explicit quote denomination, exact Decimal precision, and no implicit rounding/quantization. Exchange-specific tick/lot/precision/rounding rules remain outside the canonical contract.

The next authorized Phase 1 unit is **funding-rate value, interval, and funding calculation semantics**. No threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening is permitted.


## Phase 1 next-unit semantic gate — funding rate

The next unit must first freeze one explicit owner and define:
1. funding-rate unit and sign convention;
2. funding interval and time semantics, including UTC boundary requirements;
3. calculation inputs and outputs and their denominations;
4. exact numeric representation and precision/rounding behavior;
5. Linear/Inverse applicability;
6. CRYPTO/FOREX/GOLD applicability;
7. interaction with multiplier, settlement, margin, leverage, initial/maintenance margin, price/quantity, and position side/mode without redefining them;
8. provenance/freshness and stale/unknown behavior where applicable;
9. allowed and forbidden dependencies;
10. meaningful tests;
11. CI enforcement;
12. same-SHA evidence.

No exchange-specific funding interval, rate source, sign convention, or rounding rule may be guessed into the canonical contract.


## Phase 1 funding semantic lock

The active Phase 1 unit is funding-rate value, interval, provenance/freshness, and funding calculation semantics. This is a canonical Futures domain/contract boundary, not an exchange implementation.

Frozen baseline:
- owner: Futures domain/contract boundary;
- funding-rate unit: explicit `INTERVAL_RATE`, a dimensionless rate applied to one explicit funding interval;
- sign convention: explicit project vocabulary `POSITIVE_LONG_PAYS`: positive funding makes the explicit LONG side the payer and SHORT the receiver; negative funding reverses payer/receiver;
- interval: explicit aware-UTC start and end with strictly positive duration; no default interval is inferred;
- calculation input: an explicit positive finite notional already supplied by the canonical financial boundary; this contract does not recompute multiplier, price, quantity, settlement, margin, or exposure;
- calculation output: a deterministic funding transfer in the explicit notional denomination; payment amount is `abs(notional × funding_rate)`;
- zero funding rate is valid semantic data and produces no transfer;
- exact finite Decimal representation is mandatory; bool, binary floating-point, non-finite, invalid, or ambiguous financial values fail closed; no implicit rounding or quantization is introduced;
- applicability: CRYPTO, FOREX, and GOLD Futures; Linear and Inverse contract families;
- provenance: a non-empty explicit rate source and UTC observation timestamp are mandatory;
- freshness: stale observations and invalid time ordering fail closed; freshness requires an explicit UTC `as_of` and positive `max_age`; no hidden clock or age threshold exists;
- position side is consumed from the already-closed canonical LONG/SHORT vocabulary; position mode is not redefined here;
- prior multiplier, settlement, margin, leverage, initial-margin, maintenance-margin, and price/quantity contracts are consumed without redefinition;
- exchange-specific funding interval, external sign conventions, rate sources, rounding rules, transport, SDK behavior, scheduler behavior, persistence, runtime configuration, account mutation, and payment execution are outside this canonical boundary;
- exchange adapters may normalize their external funding semantics into this canonical vocabulary only at the infrastructure boundary and may not silently redefine canonical meaning;
- production boundary: `contracts/futures/funding.py`;
- test boundary: `tests/contracts/funding_contract_test.py`;
- CI boundary: `.github/workflows/phase1-domain-contracts.yml`;
- meaningful tests, CI enforcement, and same-SHA evidence are mandatory before the Phase 1 cursor may advance;
- no threshold reduction, test weakening, skip/xfail, guessed exchange behavior, or dependency-boundary weakening is permitted.


## Phase 1 funding closure evidence

Funding-rate value, interval, provenance/freshness, and funding calculation semantics are COMPLETE on main merge SHA `1744bc33db9678cfbf9ef57a5a1bb7e15b3acbaa`.

Evidence on the exact merge SHA:
- production boundary: `contracts/futures/funding.py`;
- test boundary: `tests/contracts/funding_contract_test.py`;
- export boundary: `contracts/futures/__init__.py`;
- Phase 1 Domain Contracts CI: green;
- Architecture Invariants CI: green;
- G01 Dependency Architecture CI: green.

The frozen contract is explicit `INTERVAL_RATE` funding, canonical `POSITIVE_LONG_PAYS` sign semantics, explicit UTC interval, exact Decimal arithmetic, explicit provenance/freshness, deterministic denomination-preserving transfer semantics, valid zero-rate/no-transfer behavior, CRYPTO/FOREX/GOLD and Linear/Inverse applicability, and fail-closed invalid/stale/ambiguous critical state. Exchange-specific funding behavior remains outside the canonical domain boundary.

No threshold reduction, test weakening, skip/xfail, guessed exchange behavior, or dependency-boundary weakening was used.

The next authorized Phase 1 unit is **realized PnL and unrealized PnL semantics**.

## Phase 1 next-unit semantic gate — realized and unrealized PnL

Before implementation, the next unit must freeze one explicit owner and define:
1. realized versus unrealized PnL meaning and lifecycle boundary;
2. required inputs, outputs, units, and denominations;
3. Linear/Inverse formulas without collapsing their financial meaning;
4. CRYPTO/FOREX/GOLD applicability;
5. interaction with canonical instrument, multiplier, settlement, margin, leverage, price/quantity, funding, position side/mode, and accounting boundaries without redefining them;
6. exact numeric representation and precision/rounding behavior;
7. realized/unrealized state transition semantics and what events make PnL realized;
8. valuation/reference-price provenance and freshness where applicable;
9. invalid, missing, stale, contradictory, unsupported, or ambiguous state behavior;
10. allowed and forbidden dependencies;
11. meaningful tests and CI enforcement;
12. same-SHA evidence before the cursor advances.

No exchange-specific PnL formula, fee treatment, mark-price convention, settlement behavior, rounding rule, or accounting default may be guessed into the canonical contract.


## Phase 1 realized/unrealized PnL semantic lock

The active Phase 1 unit is realized PnL and unrealized PnL. This is a canonical Futures financial contract boundary and does not own execution, fees, funding transfers, settlement, liquidation, or account mutation.

Frozen baseline:
- owner: Futures domain/contract boundary;
- realized PnL is deterministic PnL for an explicit quantity of an existing position that is closed/offset by an explicit exit price;
- unrealized PnL is deterministic mark/reference-price PnL for an explicit still-open position quantity;
- Linear PnL denomination is QUOTE; formula before side sign is quantity × multiplier × (reference_price − entry_price);
- Inverse PnL denomination is BASE; formula before side sign is quantity × multiplier × (1 / entry_price − 1 / reference_price);
- LONG uses the formula sign directly; SHORT negates it;
- realized calculation uses the explicit closing/offsetting execution price; unrealized calculation uses an explicit valuation/reference price;
- quantity, multiplier, and prices are explicit positive finite exact Decimal values; bool and binary floating-point inputs are rejected;
- zero PnL is valid and is not treated as an error;
- no implicit rounding or quantization is introduced;
- unrealized valuation requires explicit non-empty provenance and an aware UTC observation timestamp; stale or time-inconsistent valuation fails closed when freshness is checked;
- freshness uses explicit UTC as_of and positive max_age; no hidden clock or age threshold is used;
- fees, commissions, funding transfers, settlement transfers, margin, leverage, liquidation, and accounting entries are not silently included in PnL;
- partial close/offset semantics are represented by the explicit quantity supplied to the contract; this contract does not invent position-state transitions;
- applicable to CRYPTO, FOREX, and GOLD Futures and Linear and Inverse contract families;
- prior instrument, multiplier, settlement, margin, leverage, position side/mode, price/quantity, and funding contracts are consumed without redefinition;
- execution infrastructure owns provenance of a realized closing execution; market/data infrastructure owns valuation-price sourcing; this contract consumes validated facts;
- no network, exchange SDK, persistence, runtime configuration, scheduler, account mutation, or exchange-specific mark-price/fee/accounting rule belongs here;
- exchange-specific PnL conventions must be normalized at the infrastructure boundary and may not silently redefine canonical formulas;
- production boundary: contracts/futures/pnl.py;
- test boundary: tests/contracts/pnl_contract_test.py;
- CI boundary: .github/workflows/phase1-domain-contracts.yml;
- meaningful tests, CI enforcement, and same-SHA evidence are mandatory before the cursor advances;
- no threshold reduction, test weakening, skip/xfail, guessed exchange behavior, or dependency-boundary weakening is permitted.

## Phase 1 PnL closure evidence

Realized PnL and unrealized PnL semantics are COMPLETE on main merge SHA `70f319231a758768e18eb951383aa17ed1fe080f`.

Evidence on the exact merge SHA:
- production boundary: `contracts/futures/pnl.py`;
- test boundary: `tests/contracts/pnl_contract_test.py`;
- export boundary: `contracts/futures/__init__.py`;
- Phase 1 Domain Contracts CI: green;
- Architecture Invariants CI: green;
- G01 Dependency Architecture CI: green.

The frozen contract explicitly separates realized closing/offset PnL from unrealized valuation PnL, preserves Linear QUOTE and Inverse BASE denomination, uses explicit LONG/SHORT sign semantics, exact Decimal arithmetic, zero-PnL validity, valuation provenance/freshness, and excludes fees/funding/settlement/accounting from PnL unless explicitly represented by their own contracts. No exchange-specific PnL convention was guessed.

No threshold reduction, test weakening, skip/xfail, guessed exchange behavior, or dependency-boundary weakening was used.

The next authorized Phase 1 unit is **exposure and position valuation semantics**.

## Phase 1 next-unit semantic gate — exposure and position valuation

Before implementation, the next unit must freeze one explicit owner and define:
1. exposure versus valuation meaning and lifecycle boundary;
2. required position inputs, quantities, prices, multipliers, outputs, units, and denominations;
3. Linear/Inverse formulas without collapsing their financial meaning;
4. CRYPTO/FOREX/GOLD applicability;
5. interaction with instrument, multiplier, settlement, margin, leverage, price/quantity, funding, PnL, position side/mode, and accounting without redefining them;
6. exact numeric representation and precision/rounding behavior;
7. reference-price provenance and freshness where valuation is used;
8. invalid, missing, stale, contradictory, unsupported, or ambiguous state behavior;
9. allowed and forbidden dependencies;
10. meaningful tests and CI enforcement;
11. same-SHA evidence before the cursor advances.

No exchange-specific exposure, mark-price, valuation, rounding, fee, or accounting default may be guessed into the canonical contract.

## Phase 1 exposure / position valuation semantic lock

The authorized Phase 1 unit is exposure and position valuation. Exit criteria are frozen: explicit Futures-domain owner; separate exposure versus valuation meaning; explicit Linear/Inverse formulas and BASE/QUOTE denomination; CRYPTO/FOREX/GOLD coverage; exact Decimal/no implicit rounding; explicit reference-price provenance and UTC freshness; consumption rather than redefinition of prior contracts; no exchange-specific defaults; fail-closed invalid/stale/contradictory/unsupported/ambiguous state; domain-safe dependency boundary; meaningful tests; CI enforcement; and same-SHA evidence. Gross exposure/value is non-negative, while LONG/SHORT supplies signed direction. No threshold reduction, skip/xfail, assertion weakening, or dependency-boundary weakening is allowed.


## Phase 1 exposure / position valuation closure evidence

Exposure and position valuation is COMPLETE on implementation SHA `dc9461a562426e02af3fc3585beed917940da049`, merged to main as `953c69ee2335cda62d0729f5b7f0bb53f6b2a080`. The implementation passed Phase 1 Domain Contracts, G01 Dependency Architecture, and Architecture Invariants on the same implementation SHA.

## Phase 1 next-unit governance gate — liquidation price and liquidation constraints

The next authorized Phase 1 unit is liquidation price and liquidation constraints. Entry requires an explicit semantic lock across ownership, lifecycle, inputs/outputs, denomination, Linear/Inverse formulas, market applicability, interactions with all closed contracts, exact Decimal/no rounding, provenance/freshness, fail-closed behavior, dependency boundaries, meaningful tests, CI, and same-SHA evidence. No exchange-specific liquidation/mark-price/tier/fee/funding/settlement default may be introduced. No threshold, test, skip/xfail, or dependency weakening is allowed.


## Phase 1 liquidation-price constraint closure evidence

Liquidation-price constraints are COMPLETE on implementation SHA `b8b65b721fcae5720d5cf430c979700516d8c10a`, merged as `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`. The implementation passed Phase 1 Domain Contracts and G01 on the implementation lineage; merge SHA Phase 1 evidence is green. No quality gate was weakened.

## Phase 1 next-unit governance gate — liquidation event and trigger semantics

The next authorized unit is liquidation event and trigger semantics. Entry requires explicit ownership, trigger/reference provenance and freshness, side/mode semantics, required state, Linear/Inverse and three-market scope, exact Decimal/no implicit rounding, fail-closed stale/ambiguous behavior, idempotency/ordering/concurrency, dependency boundaries, meaningful tests, CI, and same-SHA evidence. The canonical contract must not implement forced execution, order placement, account mutation, exchange transport, or exchange-specific mark-price/tier/fee/funding defaults. No threshold reduction, skip/xfail, assertion weakening, or dependency weakening is permitted.
