# Elite Architecture Contract

**Navigation:** Start with `docs/architecture/ARCHITECTURE-MASTER-INDEX.md` for the single project path. This contract remains authoritative for contract and quality requirements within the source-of-truth hierarchy.

## Product identity

FuturesOnlyEliteEngine is a production-grade, Futures-only professional trading engine for CRYPTO Futures, FOREX Futures, GOLD Futures, Linear Futures, Inverse Futures, and 15 independent exchange adapters.

## Runtime and deployment contract

### Python runtime

- **Required Python version: 3.13**.
- Python 3.13 is the declared production and CI runtime baseline unless changed through the architecture-change process.

### Deployment targets

The production engine must support:
- Windows Server
- Linux Server
- Windows Home/Desktop

Platform-specific behavior must remain behind explicit infrastructure boundaries. Cross-platform support must not weaken security, risk controls, execution validation, reconciliation, observability, or fail-closed behavior.

### Operational capabilities

The system is required to support both:

1. **Automated Futures trading** through the governed execution pipeline.
2. **Signal/operational notification delivery** through Telegram and email.

Notifications are observability/delivery outputs, not execution authority. Telegram or email failures must never be interpreted as successful order execution, and notification channels must not bypass risk/execution gates.


## Configuration, hardcoding, and sensitive information

- Secrets and sensitive values must never be embedded in production code, tests, fixtures, examples, documentation, logs, or committed configuration.
- Environment/deployment/account/exchange-specific operational values must be supplied through the explicit configuration/security boundary rather than hard-coded in business or infrastructure logic.
- Safety-critical configurable values must have typed validation, provenance, and fail-closed behavior; missing or malformed values cannot silently fall back to source-code defaults.
- Hard-coded constants are acceptable only for immutable domain vocabulary or true invariants whose semantics cannot vary by environment, account, deployment, or exchange configuration.
- Security scanning and architecture tests must enforce the boundary and detect accidental credential/token/key material and forbidden operational hardcoding.
## Architectural completeness requirements

Before production implementation of any capability, the architecture must explicitly define:

- canonical vocabulary and stable contract ownership;
- exact inputs, outputs, units, precision, timestamps, validation status, and failure semantics at critical boundaries;
- Linear/Inverse applicability and financial meaning;
- CRYPTO/FOREX/GOLD applicability;
- risk, execution, order lifecycle, reconciliation, and audit ownership;
- configuration/secrets and security ownership;
- data freshness/provenance and fail-closed behavior;
- idempotency and unknown-state handling where external state changes are involved;
- observability, operational error classification, and notification semantics;
- resilience rules for timeout, retry, partial failure, duplicate delivery, and contradictory external state;
- authoritative external-state semantics, idempotency identity, concurrency/versioning, restart/recovery reconciliation, and scoped/global execution-halt behavior;
- trusted clock/freshness/skew semantics and safety-critical configuration provenance/versioning;
- append-only/tamper-evident audit evidence and release artifact/source/dependency provenance;
- architecture-test and CI-enforcement expectations;
- phase/gate entry and exit evidence requirements;
- migration, rollback, and compatibility impact for approved architecture changes.

No critical behavior may remain governed only by convention, an implementation detail, or an undocumented assumption.

## Quality bar

Acceptance requires evidence. No marketing claim of world-class quality substitutes for deterministic tests, architecture enforcement, mutation evidence, security evidence, integration/resilience evidence, and release verification.

## Quality gates

| Gate | Required standard |
|---|---|
| G01 Format/Lint | Strict, zero unexplained violations |
| G02 Typecheck | Strict, zero unexplained type errors |
| G03 Unit/Contract | Full required contract suite |
| G04 Architecture/Dependency | Boundary rules enforced |
| G05 Coverage | >= 98% official minimum |
| G06 Security/Supply Chain | Required security checks pass |
| G07 Integration/Resilience | Required integration and failure-path evidence |
| G08 Release/Mutation | >= 90% mutation minimum |

Coverage may not be raised by deleting tests, excluding production code, lowering thresholds, weakening assertions, or using artificial tests.

## Core pipeline

MARKET -> FUTURES INSTRUMENT -> MARKET ADAPTER -> MARKET DATA -> DATA VALIDATION -> REGIME PROBABILITY -> MTF STRUCTURE -> SETUP -> TREND/MOMENTUM -> CONFIRMATION -> COST/LIQUIDITY -> FUTURES RISK -> POSITION SIZING -> OPPORTUNITY RANKING -> DECISION -> SIGNAL CONTRACT -> EXECUTION RISK GATE -> EXECUTION CONTRACT -> EXCHANGE ADAPTER -> ORDER -> POSITION/ORDER RECONCILIATION -> AUDIT

## Phase 1 domain contract baseline

The authorized Phase 1 Domain Contracts foundation must explicitly define, with production ownership and failure semantics:

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

Every Phase 1 contract follows the implementation unit protocol: Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers.

## Futures semantic requirements

Every applicable production Futures path must explicitly model contract family, Linear/Inverse, multiplier, settlement asset, margin asset, leverage, initial margin, maintenance margin, funding, realized PnL, unrealized PnL, exposure, liquidation, position side, position mode, precision, exchange limits, and reconciliation semantics.

Implicit defaults are prohibited when they can change financial meaning.

## Fail-closed requirements

Unknown, invalid, stale, contradictory, or incomplete critical Futures state must stop the relevant operation. Failure must never silently produce an order, accepted signal, valid-looking position, false reconciliation success, Spot fallback, or guessed contract specification.

## Phase/gate evidence rule

A phase or gate is complete only when its required evidence is tied to the current repository HEAD. Historical runs, stale branches, local-only results, or claims without reproducible evidence do not establish completion.

The required proof chain is:

ARCHITECTURE RULE → CONTRACT → PRODUCTION IMPLEMENTATION → TEST → CI ENFORCEMENT → SAME-SHA EVIDENCE

For architecture-only governance work, production implementation may legitimately remain pending; in that case the missing enforcement stage must be explicitly recorded as a future phase rather than implied to be complete.

## Build-order versus runtime-order rule

The phase/build order and the runtime pipeline are intentionally different concepts. The build order controls dependency-safe implementation; the runtime pipeline controls production execution flow. No document may infer that Phase order changes runtime ownership or that runtime ordering permits skipping a build phase.

## Implementation sequence

1. Architecture contract
2. Responsibility maps
3. Dependency rules
4. Domain contracts
5. Infrastructure ports
6. Production implementation
7. Unit/contract tests
8. Architecture tests
9. Integration/resilience tests
10. Security/supply-chain checks
11. Mutation verification
12. Release verification

No production implementation should precede a clearly owned contract.

## Multiplier / contract-specification contract

The canonical Phase 1 multiplier contract uses `CONTRACTS` as the quantity unit and exact finite positive Decimal arithmetic.

Linear Futures:
- multiplier = base-asset units per contract;
- base exposure = quantity × multiplier;
- quote notional = quantity × multiplier × price.

Inverse Futures:
- multiplier = quote-price-denomination units per contract;
- quote notional = quantity × multiplier;
- base exposure = (quantity × multiplier) ÷ price.

The price quote asset must equal the canonical Futures symbol quote asset. Margin and settlement semantics are separate contracts and must not be inferred from multiplier data. Invalid, zero, negative, non-finite, contradictory, ambiguous, or unsupported specifications fail closed. Exchange-specific lot/tick/precision metadata is mapped later and cannot redefine this domain meaning.

## Phase 1 cursor — settlement

The multiplier/contract-specification, settlement, margin, and leverage contracts are complete and evidenced on main. The next incomplete Phase 1 contract is initial margin semantics. It must explicitly define formula inputs, denomination, ownership, Linear/Inverse applicability, market applicability, precision requirements, and fail-closed behavior before production implementation.
\n## Phase 1 settlement asset / settlement semantics

Settlement is an explicit domain contract, not an exchange-side guess.

The canonical settlement asset comes from the Futures instrument identity and must match the settlement specification. Every settlement amount declares its source asset. If source and settlement assets match, conversion is forbidden. If they differ, a positive finite Decimal conversion rate is mandatory; the rate is defined as settlement-asset units per source-asset unit.

The settlement contract performs no network access, rate discovery, exchange selection, scheduling, persistence, account mutation, or margin inference. Those concerns belong to later application/infrastructure contracts. Missing or contradictory settlement terms fail closed.
\n## Phase 1 cursor — margin

The leverage vocabulary/contract-level constraints contract is complete and evidenced on main. The next incomplete Phase 1 contract is maintenance margin semantics. It must explicitly define formula inputs, denomination, ownership, Linear/Inverse applicability, market applicability, tier/rate/amount semantics where applicable, validation, precision, and fail-closed behavior before production implementation.


## Phase 1 margin asset / margin semantics contract

Margin is an explicit Futures domain contract. The canonical instrument identity is authoritative for the margin asset; margin asset and settlement asset are independent explicit denominations and must not be silently equated.

Every upstream margin amount declares its source asset. Same-asset amounts require no conversion and reject a supplied conversion rate. Cross-asset amounts require an explicit positive finite Decimal conversion rate defined as margin-asset units per source-asset unit.

This contract applies to CRYPTO/FOREX/GOLD and Linear/Inverse Futures. It performs no leverage, initial-margin, maintenance-margin, liquidation, risk-limit, or exchange-specific collateral inference. Network access, rate discovery, exchange selection, persistence, account mutation, runtime configuration, and hidden defaults are forbidden. Invalid or ambiguous terms fail closed.

The production boundary is contracts/futures/margin.py; meaningful contract tests are in tests/contracts/test_margin.py; CI enforcement is through .github/workflows/phase1-domain-contracts.yml.

## Phase 1 initial margin semantics contract

Initial margin is an explicit deterministic requirement derived from an already-canonicalized Futures notional and an explicit initial-margin ratio.

The contract is:
- unit: RATIO for the initial-margin requirement rate;
- numeric representation: exact finite Decimal;
- inputs: canonical Futures instrument identity, matching market, positive finite notional, and positive finite initial-margin ratio;
- formula: `initial_margin_amount = notional × initial_margin_ratio`;
- output denomination: the same declared denomination as the notional input;
- precision: exact Decimal multiplication with no implicit rounding or quantization;
- applicability: CRYPTO/FOREX/GOLD and Linear/Inverse Futures;
- ownership: Futures domain/contract boundary;
- canonical multiplier/contract-specification semantics are consumed and never redefined;
- initial-margin ratio is not derived from leverage, exchange defaults, account state, maintenance margin, liquidation, risk policy, or position sizing;
- no hidden ratio bounds or exchange-specific collateral policy;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account-state dependency;
- invalid or ambiguous inputs fail closed.

The production boundary is `contracts/futures/initial_margin.py`; meaningful contract tests are in `tests/contracts/test_initial_margin.py`; CI enforcement is through `.github/workflows/phase1-domain-contracts.yml`.

## Phase 1 cursor — maintenance margin

Initial-margin semantics are complete and evidenced on main merge SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`. The next incomplete Phase 1 contract is maintenance margin semantics.

Maintenance margin must not be treated as a leverage alias. Its canonical contract must explicitly define formula inputs, denomination, precision, Linear/Inverse and market applicability, and any tier/rate/offset semantics before implementation. Unknown or contradictory critical terms must fail closed.


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

Owner: Futures domain/contract boundary. Exposure and valuation are separate meanings. Linear gross base exposure = quantity × multiplier; Inverse gross base exposure = (quantity × multiplier) ÷ price. Linear quote value = quantity × multiplier × explicit valuation price; Inverse quote value = quantity × multiplier. Gross values are non-negative; LONG/SHORT supplies signed directional exposure only. Quantity is CONTRACTS and all financial inputs are exact finite positive Decimal values; bool/binary float inputs fail closed. Valuation denomination is explicit BASE or QUOTE with no implicit rounding. Reference price requires explicit provenance and aware UTC observation time; freshness requires explicit UTC as_of and positive max_age. Applies to CRYPTO/FOREX/GOLD and Linear/Inverse. It consumes prior contracts without redefining them and excludes PnL, fees, funding, margin, settlement, liquidation, and accounting. No network/SDK/persistence/runtime configuration/account mutation/exchange transport dependency. Invalid, missing, stale, contradictory, unsupported, or ambiguous critical state fails closed. Production/test/CI boundaries and same-SHA evidence are mandatory; no threshold or test weakening is permitted.


## Phase 1 exposure / position valuation closure evidence

The exposure/position-valuation contract is complete on implementation SHA `dc9461a562426e02af3fc3585beed917940da049` and merged to main as `953c69ee2335cda62d0729f5b7f0bb53f6b2a080`. Production, tests, exports, and CI are closed; Phase 1, G01, and Architecture Invariants were green on the implementation SHA.

## Phase 1 next-unit semantic gate — liquidation price and liquidation constraints

Owner must remain the Futures domain/contract boundary. The next contract must distinguish deterministic liquidation-price constraints from liquidation-event execution. It must define explicit inputs/outputs and denomination, Linear/Inverse formulas, CRYPTO/FOREX/GOLD scope, exact Decimal/no implicit rounding, provenance/freshness, fail-closed behavior, allowed dependencies, meaningful tests, CI, and same-SHA evidence. It must consume instrument, multiplier, margin, leverage, maintenance margin, position side/mode, price/quantity, funding, PnL, and exposure semantics without redefining them. Exchange-specific liquidation, mark-price, fee, funding, tier, settlement, and account-state defaults remain outside the canonical domain boundary.


## Phase 1 liquidation-price constraint closure evidence

Liquidation-price and liquidation-constraint semantics are COMPLETE on implementation SHA `b8b65b721fcae5720d5cf430c979700516d8c10a`, merged to main as `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`. The contract and tests are closed with explicit Linear/Inverse formulas, denomination, exact Decimal arithmetic, fail-closed denominator/direction constraints, and no exchange-specific trigger/execution semantics.

## Phase 1 next-unit semantic gate — liquidation event and trigger semantics

The next canonical contract must own deterministic trigger-condition semantics only. It must define explicit reference-price provenance/freshness, LONG/SHORT and ONE_WAY/HEDGE trigger direction, state inputs/outputs, Linear/Inverse and CRYPTO/FOREX/GOLD applicability, exact numeric/rounding behavior, stale/ambiguous failure semantics, idempotency/ordering/concurrency, meaningful tests, CI, and same-SHA evidence. It must consume the closed liquidation-price, exposure, PnL, margin, maintenance, position, and price/quantity contracts without redefining them. Forced execution, order placement, account mutation, network, SDK, persistence, and exchange-specific trigger/mark-price/tier/fee/funding defaults remain outside.

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


## Phase 1 accounting / settlement-accounting closure evidence

Futures accounting and settlement accounting semantics are implemented at the canonical Futures domain/contract boundary. The implementation is immutable and deterministic: it records balanced journal facts, consumes already-validated realized-PnL, funding, and settlement facts, preserves explicit asset denomination, Linear/Inverse identity, CRYPTO/FOREX/GOLD applicability, exact Decimal behavior, and fail-closed validation. No persistence, network, exchange SDK, order submission, account mutation, or exchange-specific accounting policy is introduced.

Evidence boundary:
- production: `contracts/futures/accounting.py`, `contracts/futures/settlement_accounting.py`;
- tests: `tests/contracts/accounting_contract_test.py`;
- CI: Phase 1 Domain Contracts, Architecture Invariants, and G01 Dependency Architecture on the same verification SHA;
- no threshold reduction, test weakening, skip/xfail, assertion removal, or dependency-boundary weakening.

Cross-journal idempotency and durable sequence enforcement remain downstream persistence/reconciliation responsibilities; the canonical domain journal enforces immutable entry identity, explicit causation/version data, and monotonic sequence within each declared journal batch. Contradictory external outcomes remain divergence rather than success.


## Current-state authority and historical-transition control

Historical phase-unit entries in this document preserve chronology. Their earlier “active unit”, “next authorized unit”, or “next step” wording is not live authorization and must not override `docs/architecture/project-state.md` → `Current authoritative state`. Phase 2+ production implementation remains blocked until the Phase 1 completeness/evidence audit is explicitly closed with current repository evidence. No gate skip, threshold reduction, test weakening, or Spot operational path is permitted.


## G02 Runtime Boundary Guard Rationale

G02 uses strict Pyright mode and keeps type-safety diagnostics as errors. The `reportUnnecessaryIsInstance` style diagnostic alone is disabled because static annotations do not guarantee that untrusted Python callers obey those annotations at runtime; the explicit fail-closed runtime guards are required and covered by contract tests. This setting is not permission to remove runtime validation or suppress any other type diagnostic.
