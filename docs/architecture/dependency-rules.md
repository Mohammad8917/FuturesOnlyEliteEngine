# Dependency Rules

## Authoritative direction

The dependency graph is intentionally one-directional and must be read together with ARCHITECTURE-MASTER-INDEX.md:

DOMAIN → CONTRACTS (only where contracts are domain-safe)
APPLICATION → DOMAIN + CONTRACTS
RISK → DOMAIN + CONTRACTS
EXECUTION → CONTRACTS + DOMAIN FACTS + RISK DECISIONS
INFRASTRUCTURE → APPLICATION / CONTRACTS / DOMAIN PORTS
OBSERVABILITY / NOTIFICATION → EXPLICIT OUTPUT PORTS; NEVER UPSTREAM AUTHORITY

Infrastructure must never become a dependency of domain.

## Boundary ownership

- Domain owns pure Futures financial semantics.
- Contracts own stable boundary vocabulary and validation semantics.
- Application owns use-case orchestration.
- Risk owns policy decisions and risk acceptance/rejection.
- Execution owns execution intent, gated order lifecycle, reconciliation, and audit.
- Infrastructure owns external transport and exchange mapping.
- Market/data acquisition owns external data retrieval and normalization through explicit ports; it does not own risk or execution decisions.
- Strategy/analysis owns analytical decisions only and cannot submit orders.
- Configuration/security owns configuration validation, credential handling, secret boundaries, and execution-authority configuration.
- Observability/notification owns reporting/delivery only; it cannot authorize trading.
- Architecture tests and CI enforce boundaries; they do not become financial-domain owners.

If a responsibility cannot be assigned to exactly one primary owner, implementation is blocked until ownership is resolved.

## Allowed dependency details

Domain may depend only on domain-safe contracts and standard deterministic language facilities. Domain must not depend on runtime configuration, I/O, clocks with uncontrolled behavior, transport, persistence, exchange SDKs, or notification systems.

Application may depend on domain and contracts and may depend on explicit ports for external capabilities. It must not encode exchange-specific transport.

Risk may consume validated domain/account/data facts and policy/configuration inputs through explicit contracts. Risk may return decisions, but it may not create or submit orders, call exchange transport, or mutate exchange state.

Execution may consume validated signal/intent contracts, domain facts, and risk decisions. Execution may invoke explicit exchange ports only after the execution risk gate. Unknown external state must remain unknown.

Infrastructure may implement ports and adapt external systems. Infrastructure may not redefine domain financial semantics or bypass risk/execution boundaries.

Observability/notification is downstream. It must never be a dependency that determines whether an order is authorized, accepted, or considered successful.

## Forbidden dependencies

Domain modules must not import exchange SDKs, HTTP clients, database clients, message brokers, environment/config loaders, filesystem APIs, nondeterministic random values, retry/backoff transport logic, or external side effects.

Risk logic must not place orders or mutate exchange state.

Analysis/strategy logic must not submit orders, call execution adapters, or silently mutate positions.

Notification code must not authorize, retry into, or represent execution success.

Configuration code must not silently change Futures/Spot scope, risk policy, exchange identity, or execution authority.

## Configuration, hardcoding, and secret boundary

Configuration/security is the sole owner of loading, validating, and providing operational configuration and secret material.

Forbidden:
- hard-coded credentials, API keys, tokens, passwords, private/signing keys, secret connection strings, or real account identifiers;
- hard-coded environment/deployment/account-specific operational settings inside domain, application, risk, execution, exchange adapters, tests, or documentation;
- source-code defaults that silently substitute for missing safety-critical configuration;
- tests or fixtures containing production secrets or realistic credential material.

Allowed only when genuinely immutable:
- canonical domain vocabulary;
- true protocol/contract invariants whose value cannot vary by environment, account, deployment, or exchange configuration.

Architecture/security tests and CI must enforce this boundary. Configuration may provide values to authorized consumers, but it must not grant execution authority merely by being present.

## Exchange isolation

Exchange-specific identifiers and semantics stop at the infrastructure boundary.

Domain code must not use exchange-name conditionals to implement transport behavior. Exchange-specific mapping belongs under infrastructure/exchanges/<exchange>/ and must remain independently testable.

## Futures-only boundary

No dependency may introduce Spot instrument types, Spot provider routes, Spot order endpoints, Spot market scopes, permissive futures-false switches, or Futures-to-Spot fallback.

A provider failure must fail closed, never downgrade market type.

## Data and state safety

Critical external data must carry validation/provenance/freshness semantics before use at financial boundaries.

Stale, malformed, contradictory, incomplete, or out-of-order critical data must not flow into executable decisions.

Order and position reconciliation must detect divergence and unknown state; no dependency may convert uncertainty into success.

## Phase 1 domain-contract dependency boundary

The instrument identity and canonical Futures symbol unit and multiplier/contract-specification unit are complete on the current main lineage. The next Phase 1 implementation unit is **initial margin semantics**.

Ownership:
- domain/futures owns the pure financial meaning of multiplier and contract-size semantics.
- contracts/futures owns stable boundary vocabulary and validation semantics.
- infrastructure/exchanges/<exchange> may map exchange-specific contract metadata into the canonical contract, but may not redefine multiplier meaning or introduce Spot semantics.
- application, strategy, risk, and execution may consume the validated contract but may not create competing multiplier or contract-size rules.

Allowed dependencies remain deterministic standard-library/domain-safe facilities and domain-safe contracts only. The unit must not depend on exchange SDKs, HTTP clients, persistence, runtime configuration loaders, clocks, environment-specific values, or notification systems.

Linear/Inverse applicability and market applicability must be explicit. Unknown, zero, negative, contradictory, stale, unsupported, or ambiguous specifications must fail closed. The downstream contract cursor advances only after production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence.

## Architecture tests must prove

- domain does not import infrastructure;
- domain does not import exchange SDKs;
- strategy does not import execution adapters;
- risk does not submit orders;
- execution cannot bypass risk validation;
- Spot is not an operational dependency;
- exchange-specific code remains outside domain;
- Linear and Inverse are explicit contract semantics;
- market/data boundaries cannot place orders;
- notification/observability cannot authorize execution;
- configuration cannot silently alter execution authority;
- critical dependencies respect the single-owner responsibility map.

## Multiplier / contract-specification dependency boundary

The multiplier and contract-specification contract is owned by the Futures domain/contract boundary. It may depend only on domain-safe vocabulary and deterministic standard-library numeric facilities.

Allowed:
- canonical Futures instrument identity;
- explicit market and Linear/Inverse vocabulary;
- exact Decimal arithmetic;
- immutable value objects.

Forbidden:
- exchange SDKs or transports;
- network, persistence, runtime configuration, clocks, or notifications;
- exchange-specific defaults;
- binary-float financial calculations;
- implicit margin, leverage, settlement, or precision policy.

Infrastructure maps exchange metadata into the canonical specification. It must reject incomplete or contradictory metadata rather than redefine the multiplier semantics.

## Phase 1 cursor after multiplier closure

Multiplier/contract specification is a closed domain contract with verified implementation and CI evidence. The next dependency-boundary unit is settlement asset and settlement semantics. Settlement logic must consume the explicit multiplier contract and may not redefine it.
\n## Settlement asset / settlement semantics dependency boundary

Settlement semantics are owned by the Futures domain/contract boundary. The contract may consume only canonical instrument identity, explicit market vocabulary, immutable value objects, and exact Decimal arithmetic.

Allowed:
- canonical Futures symbol settlement asset;
- explicit source asset;
- exact positive finite Decimal conversion rate;
- deterministic conversion.

Forbidden:
- exchange SDKs, HTTP/network, persistence, clocks, scheduling, runtime configuration, account mutation, or notifications;
- exchange-specific defaults;
- implicit conversion rates;
- guessed settlement denomination.

Infrastructure may supply a validated source asset and externally obtained conversion rate through a later port, but the domain contract must reject missing or contradictory values.
\n## Phase 1 cursor after settlement closure

Settlement semantics are closed with same-SHA evidence on main. The next dependency-boundary unit is margin asset and margin semantics. Margin must consume explicit instrument and settlement contracts without redefining their meaning.


## Phase 1 margin asset / margin semantics dependency boundary

Margin semantics are owned by the Futures domain/contract boundary. The margin contract may consume only the canonical Futures instrument identity, explicit market vocabulary, immutable value objects, and exact Decimal arithmetic. It may use already-closed settlement facts only as domain facts; it must not redefine settlement semantics.

Required margin inputs are explicit:
- canonical instrument identity, including its authoritative margin asset;
- source asset for any upstream margin amount;
- exact positive finite Decimal conversion rate only when source and margin assets differ.

Forbidden dependencies remain exchange SDKs, network I/O, persistence, clocks, runtime configuration, notifications, hidden defaults, leverage inference, and exchange-specific collateral policy. A margin contract must never silently substitute settlement asset for margin asset.


## Phase 1 leverage dependency boundary

Leverage vocabulary and contract-level constraints are owned by the Futures domain/contract boundary. The contract may consume canonical instrument identity and explicit margin facts as domain inputs but may not redefine their semantics.

Leverage configuration must be explicit, validated, provenance-aware, and fail closed. Exchange SDKs, network I/O, persistence, runtime configuration access, hidden defaults, risk policy, and execution mutation are forbidden dependencies of the canonical leverage contract.

## Phase 1 initial margin dependency boundary

Initial-margin semantics are owned by the Futures domain/contract boundary. The contract owns only the deterministic initial-margin requirement calculation and validation of its explicit inputs.

Required inputs are explicit:
- canonical Futures instrument identity;
- matching market;
- positive finite exact Decimal notional;
- positive finite exact Decimal initial-margin ratio.

The notional input is consumed as an already-canonicalized valuation from the multiplier/contract-specification boundary. The initial-margin contract must not redefine Linear/Inverse notional or infer it from raw exchange metadata.

Allowed dependencies:
- canonical Futures instrument/domain vocabulary;
- immutable value objects;
- deterministic standard-library Decimal arithmetic.

Forbidden dependencies:
- exchange SDKs or transports;
- network I/O;
- persistence;
- runtime configuration;
- clocks or scheduling;
- notifications;
- account state;
- leverage inference;
- maintenance margin, liquidation, risk, or position-sizing policy;
- exchange-specific collateral defaults.

The contract computes only `initial_margin_amount = notional × initial_margin_ratio`, preserves the notional denomination, performs no implicit conversion or rounding, and fails closed on invalid or ambiguous inputs.

## Phase 1 cursor after initial margin closure

Initial-margin semantics are closed with same-SHA evidence on main merge SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`. The next dependency-boundary unit is maintenance margin semantics.

Maintenance-margin implementation must first establish explicit ownership and formula inputs. Exchange-specific tier tables may be mapped into a canonical domain contract but may not be guessed or silently defaulted. The contract must remain free of exchange SDKs, network I/O, persistence, runtime configuration, and account mutation.


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

## Phase 1 exposure / position valuation dependency lock

Exposure/position valuation is a domain-safe canonical contract. It may depend only on existing domain/contract facts such as instrument identity, multiplier/contract specification, price/quantity, and explicit position side. It must not depend on exchange SDKs, network I/O, persistence, runtime configuration, scheduling, account mutation, or exchange transport. Linear/Inverse formulas remain explicit: base exposure is quantity × multiplier for Linear and quantity × multiplier ÷ price for Inverse; quote value is quantity × multiplier × price for Linear and quantity × multiplier for Inverse. Valuation requires explicit denomination, reference provenance, and aware UTC observation/freshness. PnL/funding/margin/settlement/accounting are not redefined or silently included. Invalid, stale, contradictory, unsupported, or ambiguous critical state fails closed. Same-SHA CI evidence is mandatory and no dependency or quality gate may be weakened.
