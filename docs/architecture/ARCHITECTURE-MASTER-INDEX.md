# Architecture Master Index — FuturesOnlyEliteEngine

## Purpose
This is the single navigation and execution path for the architecture. It prevents documents from presenting competing routes, responsibilities, or phase orders.
This index does not override the constitutional source-of-truth hierarchy. It tells every AI, engineer, reviewer, and session where to start, what controls what, who owns what, and what must happen next.

## 1. Mandatory reading path
1. This file — navigation and unified path.
2. docs/architecture/project-state.md — current authorized phase/gate and evidence state.
3. docs/architecture/architecture-invariants.md — immutable constitutional constraints.
4. docs/architecture/architecture-contract.md — required system contracts and quality gates.
5. docs/architecture/futures-responsibility-map.md — ownership of responsibilities.
6. docs/architecture/dependency-rules.md — allowed/forbidden dependency direction.
7. docs/architecture/master-roadmap-and-governance.md — phase order, entry/exit criteria, and change control.
8. docs/architecture/CHANGE-GUARD.md — repository-level protected-surface and enforcement guard.
9. docs/architecture/adr/README.md — architecture-change process.
README.md is the public product boundary and points back to this index.

### Conflict resolution
If content conflicts, use: Invariants → approved ADR → Contract → Responsibility Map → Dependency Rules → Roadmap → Project State → Code/Tests/CI evidence → historical material.
project-state.md controls what is authorized now; it does not override architecture rules.

## 2. Product boundary
- Futures-only.
- Markets: CRYPTO Futures, FOREX Futures, GOLD Futures.
- Contract families: Linear Futures and Inverse Futures.
- Exactly 15 independent exchange adapters.
- Automated Futures trading is the operational execution capability.
- Telegram/email are delivery and observability channels only.
- Operational Spot is forbidden.
- Runtime baseline: Python 3.13.
- Deployment targets: Windows Server, Linux Server, Windows Home/Desktop.

## 3. Unified architecture path
MARKET → FUTURES INSTRUMENT → MARKET ADAPTER → MARKET DATA → DATA VALIDATION → REGIME PROBABILITY → MTF STRUCTURE → SETUP → TREND/MOMENTUM → CONFIRMATION → COST/LIQUIDITY → FUTURES RISK → POSITION SIZING → OPPORTUNITY RANKING → DECISION → SIGNAL CONTRACT → EXECUTION RISK GATE → EXECUTION CONTRACT → EXCHANGE ADAPTER → ORDER → POSITION/ORDER RECONCILIATION → AUDIT → NOTIFICATION/OBSERVABILITY
Notification/observability is downstream reporting. It never authorizes, validates, or represents successful execution.

## 4. Unified ownership model
| Responsibility | Owner | Must not own |
|---|---|---|
| Futures financial semantics | domain/futures | transport, I/O, exchange SDKs |
| Stable boundary contracts | contracts/futures | network behavior, hidden defaults |
| Use-case orchestration | application/futures | exchange-specific transport |
| Market/data acquisition and normalization | explicit market/data boundary + infrastructure ports | risk decisions, order placement |
| Strategy/analysis | explicitly assigned analysis/application boundary | execution or order submission |
| Risk policy and risk decisions | risk | order submission, exchange mutation |
| Execution intent and execution gate | execution | bypassing risk |
| Order lifecycle | execution | exchange transport details |
| Reconciliation and audit | execution + infrastructure evidence ports | guessed success |
| Exchange transport/mapping | infrastructure/exchanges/<exchange> | domain financial semantics |
| Configuration/secrets | explicit configuration/security boundary | silently changing execution authority |
| Notifications/observability | explicit observability/delivery boundary | trading authorization |
| Architecture enforcement | architecture tests + CI | production financial behavior |
| Release verification | release/CI governance | bypassing gates |

If ownership is not explicit, implementation is blocked.

## 5. Dependency path
Domain → Contracts (only where domain-safe)
Application → Domain + Contracts
Risk → Domain + Contracts
Execution → Contracts + Domain facts + Risk decisions
Infrastructure → Application/Contracts/Domain ports
Observability/Notifications → explicit output ports; never upstream authority
Infrastructure never becomes a dependency of domain. Strategy never calls execution. Risk never places orders. Exchange-specific transport never enters domain.

## 6. Upgrade path
Phase 0 Governance → Phase 1 Domain Contracts → Phase 2 Application Contracts/Ports → Phase 3 Risk → Phase 4 Execution → Phase 5 15 Exchanges → Phase 6 Market/Data → Phase 7 Cross-Layer Integration → Phase 8 G01–G08 → Phase 9 Release Verification
No phase may be skipped, reordered, or partially declared complete without evidence.

## 7. Implementation unit path
Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers → Implementation → Test → CI → Same-SHA Evidence
Ambiguous ownership blocks implementation.

## 8. Architecture-change path
PROPOSAL → WARNING → IMPACT ANALYSIS → ALTERNATIVES → RISK ANALYSIS → ADR → EXPLICIT RECONFIRMATION → DOCUMENT UPDATE → IMPLEMENTATION → ARCHITECTURE TEST → CI → SAME-SHA VERIFICATION
No emergency bypass exists.

## 9. Definition of complete
A critical requirement is complete only when its path is closed:
RULE → CONTRACT → OWNER → PRODUCTION IMPLEMENTATION → TEST → CI ENFORCEMENT → CURRENT-HEAD EVIDENCE
For Phase 0 governance-only work, implementation/test/CI stages may be future-phase work, but that must be explicitly recorded rather than implied complete.

### Security/hardcoding firewall
- no hard-coded secrets, credentials, tokens, signing keys, passwords, secret-bearing connection strings, or real account identifiers;
- no hard-coded environment/deployment/account/exchange-specific operational configuration;
- no silent source-code defaults for safety-critical configuration;
- only genuinely immutable domain vocabulary/invariants may remain as source constants;
- architecture/security tests and CI must enforce these rules.

## 10. Missing-requirement firewall
Before implementation of any new capability, explicitly check for ownership and contracts for:
- data provenance, freshness, ordering, contradiction handling;
- authoritative exchange-state semantics versus local intent/cache state;
- idempotency identity, duplicate suppression, concurrency/versioning, restart/failover recovery, and scoped/global execution halt;
- trusted clock source, monotonic timing, freshness, timeout, and clock-skew policy;
- units, denominations, precision, UTC and numeric representation;
- Linear/Inverse formulas and applicability;
- market applicability;
- risk/account/exposure/margin/liquidation/funding/PnL;
- execution intent, idempotency, unknown order state;
- position/order reconciliation;
- append-only/tamper-evident audit evidence, stable event identity, causal correlation, and release artifact/source/dependency provenance;
- configuration, credentials, secrets, signing, permissions;
- security and supply-chain;
- retries, timeouts, partial failure, circuit breaking;
- observability and failure classification;
- Telegram/email delivery semantics;
- deployment/platform differences;
- architecture tests and CI enforcement;
- migration, compatibility, rollback;
- phase/gate evidence and same-SHA verification.
Anything critical that lacks an owner, contract, enforcement path, or failure semantics is an architecture gap and blocks the affected phase.

## 10.1 Phase 1 — Domain Contract Baseline

Phase 1 is the first authorized implementation phase. Its contract set is the canonical foundation for every later layer and must be completed before Phase 2 begins.

The minimum Futures domain contract set is:

- instrument identity and canonical Futures symbol semantics;
- contract family and explicit Linear/Inverse applicability;
- multiplier and contract specification;
- settlement asset and settlement semantics;
- margin asset and margin semantics;
- leverage vocabulary and contract-level constraints;
- position side and position mode;
- price, quantity, monetary units, denomination, precision, and rounding semantics;
- funding-rate value, interval, and funding calculation semantics;
- realized PnL and unrealized PnL;
- exposure and position valuation semantics;
- liquidation price and liquidation constraints;
- Futures accounting and settlement accounting;
- validation status, provenance/freshness where applicable, and explicit failure semantics.

For every contract, the implementation unit protocol is mandatory: Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers.

Phase 1 is complete only when every required contract has a production implementation boundary, meaningful contract tests, and current same-SHA evidence. No Phase 2+ implementation may be used to conceal an incomplete Phase 1 contract.

## 10.2 Phase 1 execution cursor

**Current cursor:** Phase 1 candidate completeness/evidence audit is closed on the latest verified candidate snapshot recorded in `docs/architecture/project-state.md` → `Current authoritative state`; PR #35 owner review/merge is pending, followed by same-SHA verification on `main`. Phase 2+ remains blocked until that governance step is complete. Do not treat a historical SHA in this index as current evidence.

The minimum Phase 1 canonical contract units have been implemented and the candidate-branch completeness/evidence audit is recorded as closed in the current authoritative project state. This is a candidate-branch result only: it does not establish that the same result is merged or verified on `main`. The active next step is the PR #35 owner-review/authorized-merge gate, followed by verification of applicable checks on the exact resulting `main` SHA and correction of the historical G05 false-green on `main`.

The full implementation-unit evidence path remains mandatory for any newly authorized contract work:

Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers → Implementation → Test → CI → Same-SHA Evidence.

No new Phase 1 unit or Phase 2+ production implementation may be inferred from this index while the current project-state gate remains pending. Documentation alone is never evidence of implementation or CI success.

## 11. Current project control
The current project state is Phase 1 — Domain Contracts. Phase 0 — Architecture Baseline / Governance Final Audit is CLOSED, and Phase 1 is authorized. Phase 2+ remains blocked until each preceding phase exit criteria is evidenced.
The next action must follow `docs/architecture/project-state.md` → `Current authoritative state`. At this snapshot it is owner review/authorized merge of PR #35 and exact-SHA verification on `main`, not another contract unit or Phase 2 implementation.

Continue the map, not reinvent the map.

## 12. Phase 0 closure / anti-cycle control
Phase 0 has a finite closure point. Its final audit exists to remove architecture blockers, not to continuously expand governance documentation.

Audit findings are classified as **FIX NOW**, **DEFER TO PHASE N**, or **NOT AN ARCHITECTURE GAP**. Only genuine Phase 0 architecture gaps are fixed before exit. Later implementation details, optimizations, and preferences must remain in their owning phase.

After all Phase 0 exit criteria are evidenced on the current HEAD and the exit decision is recorded in `project-state.md`, Phase 0 is **CLOSED**. Do not reopen it merely for additional documentation completeness. A later-phase concern reopens architecture only when it is a genuine architecture gap that would invalidate the current contract; otherwise the current phase continues.

This is the control against an infinite audit → document → re-audit cycle.

## 10.3 Phase 1 multiplier / contract-specification lock

The first Phase 1 implementation unit after instrument identity is now contractually fixed:

- quantity unit: `CONTRACTS`;
- multiplier/contract size: exact positive finite Decimal;
- Linear: multiplier = base units per contract; notional = quantity × multiplier × price;
- Inverse: multiplier = quote-price-denomination units per contract; notional = quantity × multiplier;
- base exposure is explicit and family-specific;
- price denomination must equal the canonical symbol quote asset;
- zero, negative, non-finite, contradictory, ambiguous, or unsupported values fail closed;
- margin and settlement are not inferred by this contract;
- exchange-specific lot/tick/precision rules remain outside this domain contract.

Implementation boundary: `contracts/futures/contract_specification.py`. The contract closes only after production implementation, meaningful tests, CI enforcement, and same-SHA evidence.

## 10.4 Phase 1 execution cursor — settlement

Historical closure: the multiplier, settlement, and margin units are evidenced complete on main. The current first incomplete authorized Phase 1 unit is **initial margin semantics**.

Required path remains:
Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers → Implementation → Test → CI → Same-SHA Evidence.

No downstream Phase 1 unit may be declared complete ahead of this cursor.
\n## 10.5 Phase 1 settlement implementation contract

The settlement unit is now explicitly defined:
- owner: Futures domain/contract boundary;
- settlement unit: ASSET;
- settlement asset: must equal canonical instrument settlement asset;
- source asset: explicit upstream denomination;
- same-asset settlement: conversion prohibited and unnecessary;
- cross-asset settlement: explicit positive finite Decimal rate required;
- rate direction: settlement-asset units per source-asset unit;
- no network, exchange selection, scheduling, persistence, account mutation, or margin inference;
- fail closed on missing, invalid, zero, negative, non-finite, contradictory, or ambiguous settlement terms.

The production boundary is `contracts/futures/settlement.py`. Closure requires meaningful tests, Phase 1 CI, and same-SHA evidence.
\n## 10.6 Phase 1 execution cursor — margin

Settlement asset and settlement semantics are now evidenced complete on main SHA `164dcb97c38271ab29f79f8e9b8068bcc8a55234`.

Historical cursor: margin asset and margin semantics (closed).

Required path remains:
Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers → Implementation → Test → CI → Same-SHA Evidence.


## 10.7 Phase 1 margin implementation contract

The margin unit is explicitly defined:
- owner: Futures domain/contract boundary;
- authoritative margin asset: FuturesInstrumentIdentity.margin_asset;
- margin unit: ASSET;
- source asset: explicit upstream denomination;
- same-asset margin: conversion prohibited and unnecessary;
- cross-asset margin: explicit positive finite Decimal conversion rate required;
- rate direction: margin-asset units per source-asset unit;
- margin asset and settlement asset remain separate explicit semantics and may differ;
- no leverage, initial-margin, maintenance-margin, liquidation, or exchange-specific collateral formula is inferred by this unit;
- no network, exchange selection, scheduling, persistence, account mutation, or runtime configuration;
- invalid, missing, zero, negative, non-finite, contradictory, or ambiguous terms fail closed.

Production boundary: contracts/futures/margin.py.
Test boundary: tests/contracts/test_margin.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.


## 10.8 Phase 1 leverage implementation contract

The margin asset/margin semantics unit is evidenced complete on main merge SHA f2c30bf3da77f56b2dd2d9350af7bb1376f47797.

Historical cursor at that recorded stage (not live authorization): leverage vocabulary and contract-level constraints. Current authorization is controlled by `docs/architecture/project-state.md` → `Current authoritative state`.

The leverage unit must explicitly define:
- leverage representation and exact numeric semantics;
- admissible bounds and invalid-value behavior;
- ownership and configuration provenance;
- Linear/Inverse applicability;
- CRYPTO/FOREX/GOLD applicability;
- interaction boundaries with margin, risk, and execution;
- fail-closed behavior for missing, invalid, contradictory, stale, or unsupported leverage;
- no exchange-default inference or hidden leverage;
- production implementation, meaningful tests, CI enforcement, and same-SHA evidence before cursor advance.

## 10.10 Phase 1 initial margin implementation contract

Historical transition record (not live authorization): initial margin was the next Phase 1 unit at that recorded stage. Its recorded requirements were formula inputs, denomination, exact numeric semantics, applicability, ownership, validation, and fail-closed behavior. Current authorization is controlled by `docs/architecture/project-state.md` → `Current authoritative state`.

- owner: Futures domain/contract boundary;
- unit: RATIO for the initial-margin requirement rate;
- numeric type: exact finite Decimal;
- formula input: explicit positive finite notional in a declared valuation/margin denomination;
- initial_margin_ratio: explicit positive finite Decimal;
- formula: initial margin amount = notional × initial_margin_ratio;
- output denomination: identical to the supplied notional denomination;
- precision: exact Decimal multiplication; no implicit rounding or quantization;
- applicability: CRYPTO/FOREX/GOLD and Linear/Inverse;
- notional semantics are consumed from the canonical multiplier/contract-specification boundary and are not redefined here;
- initial-margin ratio is never inferred from leverage, exchange defaults, account state, maintenance margin, liquidation, or risk policy;
- no hidden ratio bounds are introduced;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation;
- fail closed on missing, invalid, zero, negative, non-finite, contradictory, or ambiguous inputs.

Production boundary: `contracts/futures/initial_margin.py`.
Test boundary: `tests/contracts/test_initial_margin.py`.
CI boundary: `.github/workflows/phase1-domain-contracts.yml`.

## 10.11 Phase 1 execution cursor — maintenance margin

Initial margin semantics are COMPLETE with same-SHA evidence on main merge SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`.

Historical cursor at that recorded stage (not live authorization): maintenance margin semantics. Current authorization is controlled by `docs/architecture/project-state.md` → `Current authoritative state`.

Historical next-unit requirements (not live authorization): the maintenance-margin unit must follow the full implementation-unit protocol and explicitly define ownership, inputs, outputs, denomination, precision, Linear/Inverse applicability, CRYPTO/FOREX/GOLD applicability, tier/rate/amount semantics where applicable, failure behavior, test boundary, CI enforcement, and same-SHA evidence. Current authorization is controlled by `docs/architecture/project-state.md` → `Current authoritative state`.

No maintenance-margin formula may be inferred from leverage or copied from an exchange without an explicit canonical contract.


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

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **position side and position mode semantics**. No Phase 2+ production implementation is authorized before the preceding Phase 1 exit criteria are evidenced.


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

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **price, quantity, monetary units, denomination, precision, and rounding semantics**. No threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening is permitted.


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

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **funding-rate value, interval, and funding calculation semantics**. No threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening is permitted.


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

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **realized PnL and unrealized PnL semantics**.

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

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **exposure and position valuation semantics**.

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

The active Phase 1 unit is exposure and position valuation semantics. This is a canonical Futures domain/contract boundary and remains distinct from PnL, margin, liquidation, accounting, execution, and exchange transport.

Frozen baseline:
- owner: Futures domain/contract boundary;
- exposure means explicit economic magnitude and optional signed directional quantity represented by an existing position; valuation means expressing that position at an explicit reference price in an explicitly named denomination;
- gross base exposure is positive magnitude: Linear = quantity × multiplier; Inverse = (quantity × multiplier) ÷ price;
- gross quote notional/value at an explicit price is: Linear = quantity × multiplier × price; Inverse = quantity × multiplier;
- LONG/SHORT affects signed directional exposure only; gross exposure/value remains non-negative and does not encode side;
- quantity is explicit CONTRACTS and must be positive finite exact Decimal; multiplier and prices are positive finite exact Decimal values; bool and binary floating-point inputs are rejected;
- valuation outputs explicitly identify BASE or QUOTE denomination; no denomination is inferred;
- reference price requires non-empty provenance and aware UTC observation timestamp; freshness requires explicit UTC as_of and positive max_age, with no hidden clock or threshold;
- no implicit rounding, quantization, tick-size, lot-size, precision, or exchange-specific mark-price convention;
- applies to CRYPTO, FOREX, GOLD Futures and Linear/Inverse;
- consumes prior instrument, multiplier, price/quantity, position side/mode, funding and PnL contracts without redefining them;
- PnL remains owner of profit/loss formulas; exposure/valuation excludes PnL, fees, funding transfers, margin, settlement, liquidation, and accounting unless explicitly represented by those contracts;
- no network, exchange SDK, persistence, runtime configuration, scheduler, account mutation, or exchange-specific transport dependency;
- invalid, missing, stale, contradictory, unsupported, non-finite, zero, negative, or ambiguous critical state fails closed;
- production: contracts/futures/exposure.py; tests: tests/contracts/exposure_contract_test.py; CI: .github/workflows/phase1-domain-contracts.yml;
- meaningful tests, CI enforcement, and same-SHA evidence are mandatory before cursor advance;
- no threshold reduction, test weakening, skip/xfail, guessed exchange behavior, or dependency-boundary weakening is permitted.


## Phase 1 exposure / position valuation closure evidence

Exposure and position valuation semantics are COMPLETE on implementation merge SHA `953c69ee2335cda62d0729f5b7f0bb53f6b2a080`.

Evidence on the exact implementation lineage:
- production boundary: `contracts/futures/exposure.py`;
- test boundary: `tests/contracts/exposure_contract_test.py`;
- export boundary: `contracts/futures/__init__.py`;
- CI boundary: `.github/workflows/phase1-domain-contracts.yml`;
- Phase 1 Domain Contracts: green on implementation commit `dc9461a562426e02af3fc3585beed917940da049`;
- G01 Dependency Architecture: green on implementation commit `dc9461a562426e02af3fc3585beed917940da049`;
- Architecture Invariants: green on implementation commit `dc9461a562426e02af3fc3585beed917940da049`.

The frozen semantics remain explicit gross exposure versus valuation, Linear/Inverse formulas, explicit BASE/QUOTE denomination, LONG/SHORT directional sign, exact Decimal arithmetic, reference provenance/freshness, all three Futures markets, fail-closed critical state, and no exchange-specific defaults or dependency weakening.

## Phase 1 next-unit semantic gate — liquidation price and liquidation constraints

Before implementation, the next unit must freeze one explicit owner and define:
1. liquidation price meaning versus liquidation event/engine responsibility;
2. required position, entry, quantity, multiplier, margin, leverage, maintenance-margin, fee/funding/settlement inputs and explicit outputs;
3. Linear/Inverse formulas without collapsing their financial meaning;
4. CRYPTO/FOREX/GOLD applicability;
5. interaction with all closed contracts without redefining them;
6. exact numeric representation and precision/rounding behavior;
7. reference-price/account-state provenance and freshness where applicable;
8. invalid, missing, stale, contradictory, unsupported, or ambiguous state behavior;
9. allowed and forbidden dependencies, including no exchange SDK/network in the canonical contract;
10. meaningful tests and CI enforcement;
11. same-SHA evidence before cursor advance.

No exchange-specific liquidation formula, fee/funding treatment, tier/default, mark-price, rounding, or account-state assumption may be guessed into the canonical contract.


## Phase 1 liquidation-price constraint closure evidence

Liquidation-price and liquidation-constraint semantics are COMPLETE on implementation merge SHA `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`.

Evidence on the implementation lineage:
- production: `contracts/futures/liquidation.py`;
- tests: `tests/contracts/liquidation_contract_test.py`;
- exports: `contracts/futures/__init__.py`;
- CI: `.github/workflows/phase1-domain-contracts.yml`;
- Phase 1 Domain Contracts: green on implementation SHA `b8b65b721fcae5720d5cf430c979700516d8c10a` and again on merge SHA `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`;
- G01 Dependency Architecture: green on implementation SHA `b8b65b721fcae5720d5cf430c979700516d8c10a` and merge lineage;
- the contract preserves explicit Linear/Inverse formulas, denomination, exact Decimal arithmetic, fail-closed direction/denominator constraints, and no exchange-specific trigger/mark-price/fee/funding/tier behavior.

## Phase 1 next-unit semantic gate — liquidation event and trigger semantics

Before implementation, the next unit must freeze one explicit owner and define:
1. liquidation event versus liquidation-price constraint meaning and lifecycle boundary;
2. trigger/reference price source and explicit provenance/freshness;
3. trigger direction for LONG/SHORT and ONE_WAY/HEDGE without inventing a third side/mode;
4. required position, account/margin, maintenance, liquidation-price, and state inputs/outputs;
5. Linear/Inverse and CRYPTO/FOREX/GOLD applicability;
6. interaction with all closed contracts without redefining them;
7. exact numeric and precision/rounding behavior;
8. invalid, missing, stale, contradictory, unsupported, or ambiguous trigger state behavior;
9. allowed/forbidden dependencies and ownership of account mutation/execution;
10. idempotency, ordering, concurrency, and fail-closed behavior for an event boundary;
11. meaningful tests, CI enforcement, and same-SHA evidence.

The canonical contract may define deterministic trigger semantics but must not implement exchange transport, liquidation execution, forced-order placement, account mutation, or exchange-specific mark-price/tier/fee/funding defaults.

## Phase 1 liquidation event / trigger semantics closure

Liquidation event and trigger semantics are COMPLETE on evidence SHA `67b3592f7dbaa4f87c7065d439565e2a32b9eef4`.

Frozen semantics: the Futures domain/contract boundary owns deterministic trigger evaluation only; liquidation-price calculation is consumed, not redefined; the reference price requires explicit provenance, aware UTC observation time, explicit UTC `as_of`, and positive freshness `max_age`; LONG triggers at reference <= liquidation price and SHORT triggers at reference >= liquidation price; side is LONG/SHORT only and mode is ONE_WAY/HEDGE only; account/position identity, event/causation identity, state version, event sequence, quantity, entry, margin, maintenance ratio, liquidation price, and reference price are explicit; Linear/Inverse and CRYPTO/FOREX/GOLD are explicit; financial inputs are exact finite Decimal with no implicit rounding; stale, contradictory, ambiguous, invalid, or unsupported critical state fails closed; triggered events require monotonic sequence advancement and immutable event identity; execution, forced orders, account mutation, network, persistence, and exchange-specific mark-price/tier/fee/funding policy are forbidden.

Production: `contracts/futures/liquidation_event.py`. Tests: `tests/contracts/liquidation_event_contract_test.py`. CI: Phase 1 Domain Contracts + Architecture Invariants + G01. All three are green on the same evidence SHA.

## Phase 1 accounting / settlement-accounting semantic lock

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **Futures accounting and settlement accounting semantics**. Current authorization is controlled exclusively by `docs/architecture/project-state.md` → `Current authoritative state`.

Frozen baseline:
- owner: Futures domain/contract boundary for deterministic accounting facts and settlement-accounting facts; application/infrastructure own persistence, external settlement transport, exchange mapping, and account mutation;
- accounting is represented as immutable, append-only journal facts; the canonical contract does not write a database, mutate an account, call a network, or submit an order;
- every journal entry has explicit entry identity, causation identity, state version, sequence, account scope, instrument identity, asset denomination, debit/credit direction, and exact finite Decimal amount;
- an entry has exactly one positive amount and one explicit debit/credit direction; a journal batch must be balanced per explicit asset denomination;
- realized PnL is consumed as an already-validated signed fact; the accounting boundary does not recompute PnL, multiplier, price, margin, liquidation, or funding;
- funding transfers are consumed as explicit payer/receiver facts with explicit denomination; settlement transfers are explicit source/settlement denomination facts and require explicit conversion semantics from the already-closed settlement contract;
- Linear/Inverse, CRYPTO/FOREX/GOLD, and BASE/QUOTE/settlement denomination remain explicit; no family or denomination is inferred from a generic number;
- zero transfer is meaningful only where the upstream contract explicitly declares a zero-valued semantic fact; journal entries themselves require strictly positive amounts;
- exact Decimal arithmetic is mandatory; bool, binary float, non-finite, zero/negative, missing, contradictory, unsupported, or ambiguous critical financial state fails closed; no rounding or quantization;
- ordering is monotonic within the declared account/instrument scope; duplicate entry identity or reused causation/version combination cannot silently create a second accounting fact;
- contradictory balances or external settlement outcomes are divergence, not success; reconciliation remains a later boundary and may not silently overwrite canonical facts;
- settlement accounting records denomination-preserving transfers and explicit cross-asset conversions only when an explicit positive conversion rate is supplied by the settlement contract;
- no exchange-specific fee, tier, balance, settlement timing, wallet, collateral, or ledger policy is guessed into the canonical contract;
- meaningful contract tests, Phase 1 CI, Architecture Invariants CI, G01 CI, and same-SHA evidence are mandatory before the cursor advances.

## Phase 1 final completeness/evidence audit

Futures accounting and settlement accounting are the final minimum financial contract units in the canonical Phase 1 contract set. Before Phase 2, the repository must prove on one exact SHA that every required Phase 1 contract has a production boundary, meaningful tests, dependency enforcement, aligned eight-document governance state, and green Phase 1/G01/Architecture evidence. This is an evidence/governance gate, not authorization for Phase 2 production coding.


## Phase 1 accounting / settlement-accounting closure evidence

Futures accounting and settlement accounting semantics are implemented at the canonical Futures domain/contract boundary. The implementation is immutable and deterministic: it records balanced journal facts, consumes already-validated realized-PnL, funding, and settlement facts, preserves explicit asset denomination, Linear/Inverse identity, CRYPTO/FOREX/GOLD applicability, exact Decimal behavior, and fail-closed validation. No persistence, network, exchange SDK, order submission, account mutation, or exchange-specific accounting policy is introduced.

Evidence boundary:
- production: `contracts/futures/accounting.py`, `contracts/futures/settlement_accounting.py`;
- tests: `tests/contracts/accounting_contract_test.py`;
- CI: Phase 1 Domain Contracts, Architecture Invariants, and G01 Dependency Architecture on the same verification SHA;
- no threshold reduction, test weakening, skip/xfail, assertion removal, or dependency-boundary weakening.

Cross-journal idempotency and durable sequence enforcement remain downstream persistence/reconciliation responsibilities; the canonical domain journal enforces immutable entry identity, explicit causation/version data, and monotonic sequence within each declared journal batch. Contradictory external outcomes remain divergence rather than success.


## Current-state authority and historical-transition control

Historical phase-unit entries in this document preserve chronology. Their earlier “active unit”, “next authorized unit”, or “next step” wording is not live authorization and must not override `docs/architecture/project-state.md` → `Current authoritative state`. The Phase 1 candidate completeness/evidence audit is recorded as closed on the candidate branch only; PR #35 owner review/authorized merge and exact-resulting-SHA verification on `main` remain pending. Phase 2+ production implementation stays blocked until those governance and `main` verification steps are complete and the historical G05 false-green is corrected. No gate skip, threshold reduction, test weakening, or Spot operational path is permitted.
