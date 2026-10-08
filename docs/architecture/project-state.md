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
- Last verified SHA: `1d729f713c6094b9ae0cd59673632fd6dde43f5e`; verified immediately before this state snapshot with Architecture Invariants, G01 Dependency Architecture, and Phase 1 Domain Contracts all green on that exact SHA. The snapshot commit itself must be re-verified before being recorded as the next last-verified SHA.
- Completed phases: Phase 0 — Architecture Baseline / Governance Final Audit
- Active work: Phase 1 Domain Contracts — instrument, multiplier, settlement, margin, leverage, initial/maintenance margin, position side/mode, price/quantity, funding, PnL, exposure/valuation, and liquidation-price constraints are closed; liquidation event and trigger semantics are closed; the current incomplete unit is Futures accounting and settlement accounting semantics.
- Blocked work: Phase 2+ production implementation remains blocked until each preceding phase exit criteria is evidenced.
- Next authorized action: freeze and then implement Futures accounting and settlement accounting semantics across the authoritative architecture path; preserve denomination, exact numeric behavior, provenance, ordering/idempotency, reconciliation boundaries, and fail-closed semantics.
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

The active cursor is **maintenance margin semantics**.

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

Current cursor: **funding-rate value, interval, and funding calculation semantics**.

Next authorized action: define and implement the explicit maintenance-margin requirement contract from the frozen architecture baseline. No Phase 2+ work is authorized, and no threshold/test/gate weakening is permitted.

## Phase 1 initial margin implementation contract

The active implementation unit is initial-margin requirement semantics.

Frozen semantics:
- owner = Futures domain/contract boundary;
- unit = RATIO for the initial-margin requirement rate;
- inputs = canonical Futures instrument identity, matching market, explicit positive finite notional, and explicit positive finite initial-margin ratio;
- formula = initial margin amount = notional × initial_margin_ratio;
- output denomination = the same denomination as the supplied notional;
- exact Decimal arithmetic; no implicit rounding or quantization;
- CRYPTO/FOREX/GOLD and Linear/Inverse applicability;
- canonical multiplier/contract-specification semantics are consumed, not redefined;
- initial-margin ratio is not inferred from leverage, exchange defaults, account state, maintenance margin, liquidation, or risk policy;
- no hidden ratio bounds;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation;
- invalid, missing, zero, negative, non-finite, contradictory, or ambiguous inputs fail closed.

Production boundary: `contracts/futures/initial_margin.py`.
Test boundary: `tests/contracts/test_initial_margin.py`.
CI boundary: `.github/workflows/phase1-domain-contracts.yml`.

No cursor advance is authorized until production implementation, contract tests, CI enforcement, and same-SHA evidence are green.

## Phase 1 cursor transition — initial margin closed

- Initial margin semantics: COMPLETE — production implementation, contract tests, Phase 1 CI, Architecture Invariants CI, and G01 CI are green on same SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`.
- Active work: Phase 1 Domain Contracts — maintenance margin semantics.
- Next authorized action: define and implement the explicit maintenance-margin contract without inferring exchange-specific tiers, rates, or amounts.
- Forbidden action: do not redesign architecture, reintroduce operational Spot, bypass Linear/Inverse semantics, weaken tests/gates, lower G05/G08, or skip the first incomplete phase/gate.

## Phase 1 current cursor — maintenance margin

Current cursor: **maintenance margin semantics**.

The next unit must first freeze explicit ownership, inputs, outputs, denomination, precision, applicability, tier/rate/amount semantics where applicable, and fail-closed behavior before production implementation.


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

The active Phase 1 unit is exposure and position valuation semantics at the Futures domain/contract boundary. Exposure is distinct from valuation, PnL, margin, liquidation, accounting, execution, and exchange transport.

Frozen baseline:
- gross base exposure: Linear = quantity × multiplier; Inverse = (quantity × multiplier) ÷ price;
- gross quote notional/value at an explicit price: Linear = quantity × multiplier × price; Inverse = quantity × multiplier;
- LONG/SHORT affects signed directional exposure only; gross magnitude remains non-negative;
- quantity is CONTRACTS; quantity, multiplier, and prices are positive finite exact Decimal values; bool/binary float inputs fail closed;
- valuation denomination is explicit BASE or QUOTE; no implicit denomination or rounding/quantization;
- reference price requires explicit provenance and aware UTC observation time; freshness uses explicit UTC as_of and positive max_age only;
- applies to CRYPTO/FOREX/GOLD and Linear/Inverse; consumes prior contracts without redefining them;
- PnL/fees/funding/margin/settlement/liquidation/accounting are not silently included;
- no network, SDK, persistence, runtime configuration, scheduler, or account mutation dependency;
- invalid, missing, stale, contradictory, unsupported, or ambiguous critical state fails closed;
- production: contracts/futures/exposure.py; tests: tests/contracts/exposure_contract_test.py; CI: .github/workflows/phase1-domain-contracts.yml;
- same-SHA evidence is mandatory before cursor advance; no threshold/test/gate/dependency weakening.


## Phase 1 exposure / position valuation closure evidence

Exposure and position valuation semantics are COMPLETE. Production: `contracts/futures/exposure.py`; tests: `tests/contracts/exposure_contract_test.py`; exports and Phase 1 CI were updated. Implementation commit: `dc9461a562426e02af3fc3585beed917940da049`. The implementation commit passed Phase 1 Domain Contracts, G01 Dependency Architecture, and Architecture Invariants on the same SHA. It was merged to main as `953c69ee2335cda62d0729f5b7f0bb53f6b2a080`.

Frozen semantics: explicit gross exposure versus valuation; Linear base = quantity × multiplier; Inverse base = quantity × multiplier ÷ price; Linear quote value = quantity × multiplier × reference price; Inverse quote value = quantity × multiplier; LONG/SHORT supplies signed direction only; exact Decimal; explicit BASE/QUOTE denomination; explicit provenance and aware-UTC freshness; CRYPTO/FOREX/GOLD and Linear/Inverse; fail closed; no exchange-specific defaults or dependency weakening.

## Phase 1 next authorized unit — liquidation price and liquidation constraints

The next authorized Phase 1 unit is **liquidation price and liquidation constraints**. Before production implementation, all eight architecture documents must freeze owner, lifecycle meaning, required inputs/outputs, Linear/Inverse formulas, market applicability, interaction with closed contracts, exact numeric/rounding semantics, provenance/freshness, failure semantics, dependencies, meaningful tests, CI enforcement, and same-SHA evidence.

No Phase 2+ production work is authorized. No threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening is permitted.


## Phase 1 liquidation-price constraint closure evidence

Liquidation-price and liquidation-constraint semantics are COMPLETE. Implementation SHA: `b8b65b721fcae5720d5cf430c979700516d8c10a`; merge SHA: `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`. Production `contracts/futures/liquidation.py`, tests `tests/contracts/liquidation_contract_test.py`, exports, and Phase 1 CI were updated. Phase 1 Domain Contracts is green on both implementation and merge SHA; G01 is green on the implementation lineage. The contract uses explicit Linear/Inverse formulas, denomination, exact Decimal arithmetic, fail-closed constraints, and excludes exchange-specific liquidation execution/transport.

## Phase 1 current cursor — liquidation event and trigger semantics

The next authorized Phase 1 unit is **liquidation event and trigger semantics**. Before implementation, all eight architecture documents must freeze trigger ownership, reference-price provenance/freshness, LONG/SHORT and ONE_WAY/HEDGE behavior, state inputs/outputs, Linear/Inverse and three-market scope, exact numeric/rounding rules, invalid/stale/ambiguous handling, dependency boundaries, idempotency/ordering/concurrency, tests, CI, and same-SHA evidence.

No Phase 2+ production work is authorized. No threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening is permitted.

## Phase 1 liquidation event / trigger semantics closure

Liquidation event and trigger semantics are COMPLETE on evidence SHA `67b3592f7dbaa4f87c7065d439565e2a32b9eef4`.

Frozen semantics: the Futures domain/contract boundary owns deterministic trigger evaluation only; liquidation-price calculation is consumed, not redefined; the reference price requires explicit provenance, aware UTC observation time, explicit UTC `as_of`, and positive freshness `max_age`; LONG triggers at reference <= liquidation price and SHORT triggers at reference >= liquidation price; side is LONG/SHORT only and mode is ONE_WAY/HEDGE only; account/position identity, event/causation identity, state version, event sequence, quantity, entry, margin, maintenance ratio, liquidation price, and reference price are explicit; Linear/Inverse and CRYPTO/FOREX/GOLD are explicit; financial inputs are exact finite Decimal with no implicit rounding; stale, contradictory, ambiguous, invalid, or unsupported critical state fails closed; triggered events require monotonic sequence advancement and immutable event identity; execution, forced orders, account mutation, network, persistence, and exchange-specific mark-price/tier/fee/funding policy are forbidden.

Production: `contracts/futures/liquidation_event.py`. Tests: `tests/contracts/liquidation_event_contract_test.py`. CI: Phase 1 Domain Contracts + Architecture Invariants + G01. All three are green on the same evidence SHA.

## Phase 1 accounting / settlement-accounting semantic lock

The next authorized Phase 1 unit is **Futures accounting and settlement accounting semantics**.

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
