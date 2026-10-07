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
