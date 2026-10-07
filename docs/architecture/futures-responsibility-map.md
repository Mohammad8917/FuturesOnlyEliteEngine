# Futures Responsibility Map

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
8. Execution is downstream of an explicit execution contract and risk gate.
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

### execution
Owns execution intent, risk-gated execution contracts, orders, reconciliation, and audit.

Execution must never accept an unvalidated intent as an order.

### infrastructure/exchanges
Owns external exchange integration. Each adapter independently owns authentication, endpoints, request/response mapping, order semantics, precision/limits, position mode, settlement details exposed by the exchange, and reconciliation behavior.

No generic adapter may erase meaningful exchange differences.

### Financial state authority and recovery rule

- execution owns the lifecycle state machine and execution authority, while infrastructure/exchanges/<exchange> supplies externally observed order, fill, position, and account evidence.
- Exchange-confirmed live account/order/position state is authoritative for external financial state. Local intent and cached state are not authoritative when evidence is missing, stale, contradictory, or unconfirmed.
- execution owns idempotency identity, duplicate suppression, concurrency/version checks, restart/failover recovery, and the rule that execution remains halted until required reconciliation succeeds.
- execution also owns the scoped/global trading halt boundary; risk may request a halt, but notification/delivery components can never grant or revoke trading authority.
- A dedicated time/clock boundary supplies UTC timestamps and monotonic elapsed-time measurement; safety-critical freshness, timeout, and clock-skew policy is configuration-owned and fail-closed.
- Audit evidence is owned by the execution/audit boundary and must be append-only/tamper-evident with stable event identity and causal correlation.

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
| Execution intent/gate | execution | Only validated intent may proceed |
| Order lifecycle | execution | Submission, acknowledgement, state transitions and errors are explicit |
| Exchange transport | infrastructure/exchanges/<exchange> | Transport/mapping only; no domain financial formulas |
| Position/order reconciliation | execution + exchange evidence ports | Unknown/divergent state is surfaced, never guessed successful |
| Audit | execution/audit boundary | Immutable evidence sufficient to reconstruct critical lifecycle |
| Configuration/secrets/security | configuration/security boundary | Fail closed; no credential leakage or authority drift |
| Observability/failure classification | observability boundary | Health/risk/execution/exchange/reconciliation failures remain distinguishable |
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

**Downstream consumers:** later settlement, margin, leverage, exposure, PnL, risk, and execution contracts consume the explicit specification; none may reinterpret its multiplier meaning.

## Phase 1 cursor — settlement ownership

The multiplier/contract-specification responsibility is closed with verified production and CI evidence. The next incomplete responsibility is margin asset and margin semantics, which must receive one explicit primary owner before implementation.
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

Settlement asset and settlement semantics are closed with verified implementation and CI evidence. The next incomplete responsibility is margin asset and margin semantics, which must receive one explicit primary owner and may consume closed settlement facts without redefining them.


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
