# Futures Responsibility Map

## Binding product boundary — ADR-0006 (OWNER-APPROVED)

This repository delivers a **permanent signal-only product** for exactly CRYPTO Futures, FOREX Futures, and GOLD Futures. This is a product prohibition, not a feature flag or default-off mode.

Allowed production capabilities are read-only market-data ingestion/validation, analytical indicators and SMC/confluence scoring, signal lifecycle and audit, advisory entry/stop/target/risk estimates with explicit assumptions, and Telegram/email signal/operational notifications. Backtesting, walk-forward/out-of-sample analysis, and Paper Trading are simulation-only and must be technically isolated from live side effects.

Forbidden product capabilities include live order submission/amendment/cancellation/retry, automated real-position opening/increasing/reducing/closing, account mutation, transfers, leverage changes, automated capital allocation, execution-authorizing Telegram controls/callbacks, and order-write credentials or APIs. No runtime component may translate a signal, callback, retry, restart, or configuration change into a live order. Do not add an execution layer, execution adapter, live-order client, or order-write dependency.

Keep Futures-only and explicit Linear/Inverse semantics, exact Decimal rules, fail-closed validation, secret hygiene, all G01–G08 thresholds, Phase 1 exit criteria, and same-SHA CI evidence. Signal risk figures are advisory, never guaranteed maximum losses or profitability. Repository code inventory does not establish the state of any external deployment.


## Status

This is the authoritative responsibility map for the Futures domain. It defines ownership boundaries before implementation begins.

## Non-negotiable invariants

1. The product is Futures-only. No operational Spot model, provider, endpoint, flag, or execution path may be introduced.
2. Supported market families are CRYPTO, FOREX, and GOLD.
3. Linear Futures and Inverse Futures are first-class contract families.
4. Domain code contains business semantics and must not depend on exchange SDKs, HTTP clients, databases, queues, or framework code.
5. Application code orchestrates use cases; it does not own exchange-specific semantics.
6. Infrastructure owns transport and external-system integration only.
7. Risk decisions are fail-closed.
8. Live execution is prohibited; no execution contract, order lifecycle, or order-write adapter is part of the product.
9. One production module has one primary responsibility.
10. No module may silently combine instrument identity, pricing, margin, liquidation, execution, persistence, and transport responsibilities.
11. Exact financial precision is mandatory where monetary precision matters.
12. UTC-aware timestamps are mandatory at boundaries.
13. Linear and Inverse semantics must not be unified by pretending their accounting formulas are interchangeable.
14. Exchange-specific behavior belongs in exchange-specific infrastructure/mappings, not domain conditionals.
15. Critical invariants must be executable as contract or architectural tests where practical.

## Layer ownership

### domain/futures
Owns pure Futures business semantics: instrument identity, contract family, Linear/Inverse semantics, multiplier, settlement, margin, leverage, funding, PnL, liquidation, position, exposure, and Futures accounting.

Must not call exchange APIs, read environment variables, perform I/O, persist state, send orders, or contain retry/network logic.

### application/futures
Owns orchestration of Futures use cases. It may coordinate instrument resolution, margin, leverage, PnL, liquidation, position state, and risk/execution workflows.

It must not implement exchange transport or bypass domain contracts.

### contracts/futures
Owns stable boundary contracts with explicit fields, units, precision, timestamps, contract family, settlement semantics, position mode, and validation requirements.

Contracts must not contain network behavior or hidden defaults.

### risk
Owns portfolio/trading risk policy: margin limits, leverage limits, liquidation distance, exposure, concentration, correlation, position sizing, and account limits.

Risk consumes domain facts and policy inputs. It does not place orders.

### Signal lifecycle and audit

Owns analytical signal identity, validation status, issuance, expiry, invalidation, renewal limits, idempotency, and immutable audit evidence. It has no order, account-mutation, or live execution authority.

### infrastructure/exchanges
Owns external exchange integration. Each adapter independently owns authentication, endpoints, request/response mapping, order semantics, precision/limits, position mode, settlement details exposed by the exchange, and reconciliation behavior.

No generic adapter may erase meaningful exchange differences.

### Signal-state authority and recovery rule

- Signal lifecycle owns signal state only; read-only market-data infrastructure supplies market observations and cannot mutate or reconcile live account/order/position state.
- Stale, missing, contradictory, or unconfirmed market data remains unknown and blocks signal issuance or triggers invalidation.
- Signal lifecycle owns duplicate suppression, version checks, restart recovery, and stale-signal invalidation.
- A dedicated time/clock boundary supplies UTC timestamps and monotonic elapsed-time measurement; signal freshness policy is explicit and fail-closed.
- Notification/delivery components can publish signal payloads only and can never grant trading authority.
- Audit evidence is append-only/tamper-evident and records signal analysis, validation, publication, and lifecycle transitions.

### Configuration/secrets/security hardcoding rule

The configuration/security boundary owns all operational configuration and secret material. It must prevent hard-coded credentials, tokens, keys, passwords, secret-bearing connection strings, real account identifiers, and environment-specific operational settings from entering source, tests, fixtures, documentation, or logs. Safety-critical configuration is validated and fail-closed. Only genuinely immutable domain vocabulary/invariants may remain as source constants.

## Phase 1 domain contract ownership baseline

The domain/futures and contracts/futures boundaries jointly define the Phase 1 contract foundation. The owned contract vocabulary explicitly includes:

- instrument identity and canonical Futures symbol semantics;
- contract family and Linear/Inverse applicability;
- multiplier and contract specification;
- settlement asset and settlement semantics;
- margin asset and margin semantics;
- leverage and contract-level leverage constraints;
- position side and position mode;
- price, quantity, monetary units, denomination, precision, and rounding;
- funding-rate value, funding interval, and funding calculation;
- realized PnL and unrealized PnL;
- exposure and position valuation;
- liquidation price and liquidation constraints;
- Futures accounting and settlement accounting;
- validation status, provenance/freshness where applicable, and explicit failure semantics.

The primary owner must be explicit for every contract. These contracts remain pure/domain-safe and do not contain transport, persistence, network, or exchange-specific behavior.

## Cross-layer responsibility map

The Futures responsibility map is not limited to domain/futures files. The following responsibilities are mandatory before implementation:

| Responsibility | Primary owner | Boundary rule |
|---|---|---|
| Canonical Futures vocabulary/contracts | contracts/futures + domain/futures | No hidden defaults; units, precision, UTC and validation explicit |
| Market/data acquisition | market/data boundary + infrastructure ports | External data is untrusted until validated; no order authority |
| Strategy/analysis | analysis/application boundary | Produces analytical facts/decisions; cannot submit orders |
| Futures risk policy | risk | Owns acceptance/rejection and sizing policy; cannot place orders |
| Signal lifecycle | signal application | Signal state only; never creates live orders |
| Signal lifecycle | signal application | Issuance, expiry, invalidation, renewal and idempotency are explicit |
| Market-data transport | read-only infrastructure/provider boundary | Read-only transport/mapping only; no order writes or domain financial formulas |
| Market-data validation | read-only data boundary | Stale/unknown/contradictory data fails closed |
| Audit | signal application/audit boundary | Immutable evidence reconstructs analysis and signal lifecycle |
| Configuration/secrets/security | configuration/security boundary | Fail closed; no credential leakage or authority drift |
| Observability/failure classification | observability boundary | Data/analysis/signal/audit/notification failures remain distinguishable |
| Telegram/email delivery | notification boundary | Delivery only; never trading authority or execution truth |
| Architecture enforcement | architecture tests + CI | Enforces ownership/dependency rules |
| Release verification | release/CI governance | Same-SHA evidence for all required gates |

Every primary owner must define inputs, outputs, units, precision, timestamps, validation state, failure behavior, allowed/forbidden dependencies, Linear/Inverse applicability, market applicability, tests, and downstream consumers.

If a requirement has no primary owner, it is an unresolved architecture gap.

## Futures file responsibility matrix

| Module | Sole responsibility | Explicitly forbidden |
|---|---|---|
| futures_instrument.py | Canonical Futures instrument identity | PnL, margin, HTTP |
| instrument_spec.py | Immutable instrument specification | Runtime exchange calls |
| instrument_identity.py | Stable identity and symbol semantics | Risk decisions |
| contract_type.py | Contract-family/type vocabulary | Pricing calculations |
| contract_specification.py | Contract terms for valuation/accounting | Transport |
| contract_constraints.py | Contract-level validity constraints | Portfolio policy |
| linear_contract.py | Linear contract semantic rules | Exchange API |
| linear_multiplier.py | Linear multiplier semantics | Position lifecycle |
| linear_settlement.py | Linear settlement semantics | Order submission |
| inverse_contract.py | Inverse contract semantic rules | Exchange API |
| inverse_multiplier.py | Inverse multiplier semantics | Portfolio risk |
| inverse_settlement.py | Inverse settlement semantics | Order submission |
| margin_model.py | Domain-level margin calculation semantics | Account policy orchestration |
| initial_margin.py | Initial-margin requirement calculation | Liquidation workflow |
| maintenance_margin.py | Maintenance-margin requirement semantics | Exchange transport |
| leverage_policy.py | Allowed leverage policy | Network calls |
| leverage_constraints.py | Contract-level leverage validation | Position sizing policy |
| funding_rate.py | Validated funding-rate value semantics | Fetching rates |
| funding_model.py | Funding calculation semantics | Scheduling/network |
| funding_interval.py | Funding interval semantics | Funding payment execution |
| unrealized_pnl.py | Unrealized PnL semantics | Persistence |
| realized_pnl.py | Realized PnL semantics | Order submission |
| pnl_model.py | Composition of PnL rules | Exchange transport |
| liquidation_model.py | Liquidation rule semantics | Closing orders |
| liquidation_price.py | Liquidation-price calculation | API calls |
| liquidation_constraints.py | Liquidation safety constraints | Trade execution |
| futures_position.py | Futures position state | Portfolio policy |
| position_side.py | Position-side vocabulary and validation | Exchange mapping |
| position_mode.py | Position-mode semantics | HTTP |
| exposure.py | Position/exposure value semantics | Account-wide policy |
| exposure_model.py | Exposure composition | Exchange transport |
| futures_accounting.py | Futures accounting composition | Database writes |
| settlement_accounting.py | Settlement accounting semantics | Network/transport |

## Ownership rules

A change must be made in the narrowest owner that actually owns the invariant.

- Liquidation formula bugs belong to domain/futures/liquidation, not an exchange adapter.
- Exchange-specific liquidation endpoint mapping belongs to that exchange's infrastructure adapter/mapping.
- Portfolio maximum-leverage rules belong to risk, not domain/futures/leverage.
- Order serialization belongs to the exchange adapter, not Futures domain semantics.
- Contract-field invariants belong to the contract/domain boundary, not a test-only helper.

## Linear vs Inverse

Linear and Inverse are separate semantic implementations behind explicit contracts. Shared abstractions may define vocabulary and invariants, but must not force identical formulas.

Any formula involving multiplier, settlement asset, quote/base denomination, margin currency, PnL denomination, position value, or liquidation price must explicitly declare its contract semantics.

## Review gate

No Futures implementation is accepted until its owner, inputs, outputs, forbidden dependencies, Linear/Inverse applicability, market applicability, failure behavior, and test boundary are explicit.

## Multiplier / contract-specification ownership

**Primary owner:** Futures domain/contract boundary.

**Inputs:** canonical Futures instrument identity, market, contract family, explicit quantity unit, exact multiplier, and explicit price quote denomination.

**Outputs:** immutable contract specification plus deterministic quote-notional and base-exposure calculations.

**Units:** quantity in CONTRACTS; Linear multiplier in base units/contract; Inverse multiplier in quote-price-denomination units/contract; price in canonical quote denomination; exact Decimal arithmetic with no rounding at this boundary.

**Allowed dependencies:** domain-safe Futures vocabulary and deterministic standard-library numeric facilities.

**Forbidden dependencies:** exchange SDKs, network, persistence, runtime configuration, clocks, notifications, hidden defaults, and implicit margin/settlement policy.

**Failure semantics:** zero, negative, non-finite, contradictory, ambiguous, unsupported, or invalid inputs fail closed.

**Downstream consumers:** later settlement, margin, leverage, exposure, PnL, and advisory signal-risk calculations consume the explicit specification; none may reinterpret its multiplier meaning.

## Phase 1 cursor — settlement ownership

The multiplier, settlement, margin, and leverage responsibilities are closed with verified production and CI evidence. The next incomplete responsibility is maintenance margin semantics, which must receive one explicit primary owner before implementation.
\n## Settlement asset / settlement semantics ownership

**Primary owner:** Futures domain/contract boundary.

**Inputs:** canonical Futures instrument identity, market, explicit settlement asset, explicit source asset, and—only when assets differ—an exact positive finite Decimal conversion rate.

**Outputs:** immutable settlement specification and deterministic settlement-asset amount.

**Units:** settlement quantity in ASSET units; conversion rate in settlement-asset units per source-asset unit; exact Decimal arithmetic.

**Allowed dependencies:** canonical Futures contracts and deterministic standard-library numeric facilities.

**Forbidden dependencies:** exchange SDKs, network, persistence, clocks, schedulers, account mutation, notifications, hidden defaults, and implicit rates.

**Linear/Inverse:** applicable to both; settlement denomination remains explicit and is not inferred from contract family.

**Markets:** CRYPTO Futures, FOREX Futures, and GOLD Futures.

**Failure semantics:** fail closed on mismatch, missing conversion, non-positive/non-finite rate, invalid asset, or contradictory terms.

**Downstream consumers:** settlement accounting, PnL, margin, reconciliation, and execution may consume the validated settlement specification; none may redefine its denomination semantics.
\n## Phase 1 cursor — margin ownership

Settlement asset, margin asset/margin semantics, and leverage are closed with verified implementation and CI evidence. The next incomplete responsibility is maintenance margin semantics, which must receive one explicit primary owner without redefining multiplier, settlement, margin, leverage, or initial-margin semantics.


## Phase 1 margin asset / margin semantics ownership

Primary owner: Futures domain/contract boundary.

Inputs: canonical Futures instrument identity, market, explicit source asset, and—only when source and margin assets differ—an exact positive finite Decimal conversion rate.

Outputs: immutable margin specification and deterministic margin-asset amount.

Units: margin quantity in ASSET units; conversion rate in margin-asset units per source-asset unit; exact Decimal arithmetic.

Linear/Inverse: applicable to both; margin denomination is explicit and never inferred from contract family.

Markets: applicable to CRYPTO Futures, FOREX Futures, and GOLD Futures.

Dependencies allowed: canonical instrument identity, explicit market vocabulary, immutable value objects, exact Decimal arithmetic.

Dependencies forbidden: exchange SDKs, network I/O, persistence, runtime configuration, clocks, notifications, hidden defaults, leverage inference, liquidation policy, and exchange-specific collateral policy.

Downstream consumers: leverage, risk, position sizing, liquidation, PnL, reconciliation, and execution may consume the validated margin specification; none may redefine the margin asset or conversion semantics.

## Phase 1 initial margin semantics ownership

**Primary owner:** Futures domain/contract boundary.

**Inputs:** canonical Futures instrument identity, matching market, explicit positive finite notional, and explicit positive finite initial-margin ratio.

**Output:** immutable initial-margin specification plus deterministic initial-margin amount.

**Unit:** initial-margin requirement rate in dimensionless RATIO; calculated initial-margin amount in the same explicit denomination as the supplied notional.

**Formula:** initial margin amount = notional × initial_margin_ratio.

**Precision:** exact finite Decimal arithmetic; no implicit rounding or quantization.

**Linear/Inverse:** applicable to both; the contract consumes canonical family-specific notional semantics and does not redefine them.

**Markets:** applicable to CRYPTO Futures, FOREX Futures, and GOLD Futures.

**Allowed dependencies:** canonical Futures vocabulary, immutable value objects, and deterministic standard-library Decimal arithmetic.

**Dependencies forbidden:** exchange SDKs, network I/O, persistence, runtime configuration, clocks, notifications, account state, leverage inference, maintenance margin, liquidation policy, risk policy, position sizing, and exchange-specific collateral defaults.

**Failure semantics:** missing, invalid, zero, negative, non-finite, contradictory, or ambiguous inputs fail closed.

**Downstream consumers:** risk and position-sizing policy may consume the validated initial-margin result; none may redefine its formula, denomination, or ownership.

## Phase 1 maintenance margin semantics ownership cursor

Initial-margin semantics are closed with verified implementation and CI evidence on merge SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`.

The next incomplete responsibility is **maintenance margin semantics** and must receive one explicit primary owner before implementation. Ownership must define inputs, outputs, units/precision, Linear/Inverse applicability, market applicability, tier/rate/amount semantics where applicable, dependencies, failure semantics, and downstream consumers.

No exchange-specific maintenance-margin policy may be silently promoted to canonical domain meaning.


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

Ownership is the Futures domain/contract boundary. Exposure is explicit position economic magnitude; valuation is explicit expression at a reference price. Linear base exposure = quantity × multiplier; Inverse base exposure = (quantity × multiplier) ÷ price. Linear quote value = quantity × multiplier × reference price; Inverse quote value = quantity × multiplier. LONG/SHORT only supplies signed direction; gross magnitude stays non-negative. Quantity is CONTRACTS and financial inputs are exact finite Decimal; bool/binary float fail closed. Valuation denomination is explicit BASE or QUOTE. Reference-price provenance and aware UTC observation are mandatory; freshness uses explicit UTC as_of and positive max_age. Applies to all three Futures markets and both families. Prior contracts are consumed, not redefined; PnL, funding, fees, margin, settlement, liquidation, accounting, execution, network, SDK, persistence, runtime config and account mutation remain outside. Invalid/stale/contradictory/unsupported/ambiguous critical state fails closed. Same-SHA CI evidence is required.


## Phase 1 exposure / position valuation closure evidence

Exposure and position valuation is COMPLETE on implementation SHA `dc9461a562426e02af3fc3585beed917940da049`; merged to main as `953c69ee2335cda62d0729f5b7f0bb53f6b2a080`. The domain contract, meaningful tests, CI enforcement, and same-SHA Phase 1/G01/Architecture evidence are closed.

## Phase 1 next-unit ownership gate — liquidation price and liquidation constraints

Owner: Futures domain/contract boundary for deterministic liquidation-price semantics and constraints. Execution/account mutation/liquidation events remain outside. The contract must explicitly consume prior position, multiplier, margin, leverage, maintenance-margin, price/quantity, side/mode, funding, PnL, and exposure facts without redefining them; define Linear/Inverse formulas, all three markets, exact Decimal/no rounding, provenance/freshness, fail-closed state, and domain-safe dependencies. Exchange transport, SDK, network, account mutation, exchange-specific mark-price/tier/fee/funding/settlement defaults are forbidden. Meaningful tests, CI, and same-SHA evidence are mandatory.


## Phase 1 liquidation-price constraint closure evidence

Liquidation-price constraints are COMPLETE on implementation SHA `b8b65b721fcae5720d5cf430c979700516d8c10a`, merged as `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`. Ownership remains the Futures domain/contract boundary; execution, forced close, account mutation, and exchange transport are outside.

## Phase 1 next-unit ownership gate — liquidation event and trigger semantics

Owner: Futures domain/contract boundary for deterministic trigger-condition vocabulary and state evaluation. It must consume explicit liquidation price, reference price, side/mode, and validated position/account facts without redefining them. Trigger provenance/freshness, LONG/SHORT and ONE_WAY/HEDGE behavior, Linear/Inverse, all three markets, exact Decimal/no rounding, fail-closed state, idempotency/ordering/concurrency, tests, CI, and same-SHA evidence are mandatory. Execution infrastructure owns forced-order placement and account mutation; exchange adapters own external trigger/mark-price normalization. Network, SDK, persistence, scheduler, and exchange-specific defaults are forbidden in the canonical contract.

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
