# Architecture Invariants — Constitution of FuturesOnlyEliteEngine

## Binding product boundary — ADR-0006 (OWNER-APPROVED)

This repository delivers a **permanent signal-only product** for exactly CRYPTO Futures, FOREX Futures, and GOLD Futures. This is a product prohibition, not a feature flag or default-off mode.

Allowed production capabilities are read-only market-data ingestion/validation, analytical indicators and SMC/confluence scoring, signal lifecycle and audit, advisory entry/stop/target/risk estimates with explicit assumptions, and Telegram/email signal/operational notifications. Backtesting, walk-forward/out-of-sample analysis, and Paper Trading are simulation-only and must be technically isolated from live side effects.

Forbidden product capabilities include live order submission/amendment/cancellation/retry, automated real-position opening/increasing/reducing/closing, account mutation, transfers, leverage changes, automated capital allocation, execution-authorizing Telegram controls/callbacks, and order-write credentials or APIs. No runtime component may translate a signal, callback, retry, restart, or configuration change into a live order. Do not add an execution layer, execution adapter, live-order client, or order-write dependency.

Keep Futures-only and explicit Linear/Inverse semantics, exact Decimal rules, fail-closed validation, secret hygiene, all G01–G08 thresholds, Phase 1 exit criteria, and same-SHA CI evidence. Signal risk figures are advisory, never guaranteed maximum losses or profitability. Repository code inventory does not establish the state of any external deployment.


## Status

**AUTHORITATIVE / IMMUTABLE BY DEFAULT**

This document defines the constitutional architectural invariants. It governs what no person, AI, agent, engineer, CI job, or implementation pressure may silently override.

A proposal to change an invariant is not an approved change.

## 1. Constitutional rule

The architecture is frozen by default.

No actor may directly modify an invariant because implementation is difficult, another design is shorter, a library prefers another design, a test is difficult, CI is failing, coverage is low, mutation score is low, an exchange has an unusual API, a deadline is approaching, or a new AI prefers another architecture.

The project owner may propose an architectural change, but the proposal must pass the same architecture-change governance process as every other architectural change.

**Mandatory principle:** No person, AI, agent, engineer, CI job, or implementation pressure may silently override an architectural invariant.

## 2. Runtime and deployment invariants

The supported runtime is **Python 3.13**. The project must not silently target another Python major/minor version as a substitute for the declared runtime.

The production system must support all three deployment environments:
- Windows Server
- Linux Server
- Windows Home/Desktop environments

The engine must be deployable and operational on all three environments without weakening Futures-only, risk, execution, security, or observability requirements.

The system has one operational product capability: **signal generation and signal/operational notification delivery** through Telegram and email. Live automated trading is permanently out of scope and forbidden.

Telegram/email delivery must never bypass risk or execution controls, and notification failure must not be treated as successful trade execution.

## 3. Product identity invariants

Product: FuturesOnlyEliteEngine — Elite Futures-Only Professional Trading Engine.

Operational scope:
- Futures only
- CRYPTO
- FOREX
- GOLD
- Linear Futures
- Inverse Futures
- Read-only market-data adapters only; provider count and identities are not assumed

Operational Spot is forbidden.

Historical Spot code, repositories, decisions, or compatibility requirements are reference material only and cannot restore an operational Spot path.

## 4. Futures semantic invariants

Linear and Inverse Futures are first-class contract families and must not be collapsed merely for code reuse.

Applicable Futures semantics must remain explicit for:
- contract family
- Linear/Inverse
- multiplier
- settlement asset
- margin asset
- price and quantity units
- leverage
- initial margin
- maintenance margin
- funding
- realized PnL
- unrealized PnL
- exposure
- liquidation
- position side
- position mode
- precision
- exchange limits

No implicit financial default may be introduced when it can alter financial meaning.

## 5. Layer ownership invariants

Responsibility flow and source-code dependency direction are distinct concepts and must not be conflated.

Responsibility flow:

MARKET/DATA (READ-ONLY) → VALIDATION → ANALYSIS/DECISION → ADVISORY RISK ESTIMATES → SIGNAL LIFECYCLE → AUDIT/OBSERVABILITY → NOTIFICATION

Source-code dependency direction is governed by dependency-rules.md:

DOMAIN → DOMAIN-SAFE CONTRACTS
APPLICATION → DOMAIN + CONTRACTS
RISK → DOMAIN + CONTRACTS
SIGNAL APPLICATION → DOMAIN + CONTRACTS + ANALYSIS
INFRASTRUCTURE → APPLICATION/CONTRACTS/DOMAIN PORTS

Mandatory boundaries:
- Domain remains infrastructure-independent.
- Strategy/analysis must not submit orders.
- Risk must not place orders.
- No execution capability exists; signal publication must validate analytical/risk-estimate inputs.
- Exchange-specific transport/SDK semantics remain outside the domain.
- Infrastructure must not redefine domain financial semantics.
- No layer may silently take ownership of another layer's responsibility.

## 6. Exchange isolation invariants

Read-only market-data adapters are independently owned infrastructure boundaries. No order-writing adapter or execution transport is part of the product.

Shared contracts/interfaces are allowed. A generic implementation that erases meaningful exchange differences is forbidden.

Exchange-specific behavior must remain independently representable and testable, including where applicable:
- authentication
- endpoints
- request/response mapping
- instrument specification
- multiplier/settlement
- margin/leverage
- funding
- PnL/liquidation information
- precision/limits
- position mode

## 7. Fail-closed invariants

Unknown, invalid, stale, contradictory, incomplete, or untrusted critical Futures state must not produce:
- a live order or account mutation
- a signal represented as executable
- a guessed contract specification
- false reconciliation success
- a Spot fallback
- a guessed risk value
- a guessed leverage/margin/liquidation value

Required behavior is fail-closed.

Convenient defaults are forbidden when they can change financial meaning.

## 8. Operational integrity invariants

The following are architectural safety requirements and must have an explicit owner, contract, implementation, test, and CI enforcement path before the affected capability is considered complete.

### Data, time, and numeric integrity
- Critical market data must have explicit validation status and provenance; the product does not require private account data.
- Stale, missing, malformed, contradictory, or out-of-order critical data must fail closed.
- Monetary and contract calculations must use an explicitly governed exact numeric representation; binary floating-point must not silently determine financial outcomes where exact precision is required.
- Boundary timestamps must be UTC-aware and their ordering semantics explicit.
- Time access must have an explicit clock boundary separating UTC wall-clock timestamps from monotonic elapsed-time measurement. Safety-critical freshness, timeout, signing-window, and clock-skew policies must be validated configuration; unknown or excessive skew must fail closed where it can affect financial correctness or authorization.
- Units, quote/base denomination, settlement denomination, quantity, price, multiplier, and precision must be explicit at financial boundaries.

### Configuration and secrets

- Credentials, API keys, signing material, passwords, tokens, private keys, connection strings containing secrets, and other sensitive information must never be hard-coded in source code, tests, fixtures, documentation, logs, examples, or committed configuration.
- Operational configuration must not be hard-coded when it is environment-, deployment-, account-, exchange-, credential-, or runtime-specific; it must enter through an explicitly owned configuration/security boundary and be validated before use.
- Market-data credentials, provider endpoints, freshness policy, and other safety-critical operational values must not be silently embedded as source-code constants when they are intended to be configurable.
- Hard-coded values are permitted only when they are genuine immutable domain vocabulary or compile-time invariants whose meaning cannot vary by environment/account/deployment; such values must remain owned by the appropriate domain/contract boundary.
- Tests and fixtures must use non-sensitive synthetic values and must never embed real credentials or production secrets.
- Credentials, API keys, signing material, and secrets must not be hard-coded, committed, logged, or exposed through normal diagnostics.
- Configuration must fail closed when a required safety-critical value is missing, malformed, or contradictory.
- Every safety-critical configuration value must have explicit provenance/source, schema/version semantics, validation status, and effective lifecycle; untracked or ambiguously sourced configuration must not silently authorize signal publication or external side effects.
- Configuration must not silently change Futures/Spot scope, risk policy, provider identity, or introduce live execution/order-write authority.

### Signal lifecycle, idempotency, and audit

- Every published signal must carry a stable unique identity and explicit replay/duplicate semantics.
- Signal lifecycle transitions must be idempotent; duplicate delivery, retries, restart, or callbacks must never cause live order side effects.
- Stale, invalid, contradictory, or incomplete critical data must prevent signal issuance or invalidate an existing signal according to its contract.
- Audit evidence must be append-only/tamper-evident and preserve analytical inputs, validation, assumptions, signal decision, publication, expiry/invalidation, and notification outcomes.
- This product has no live order, position-mutation, account-mutation, reconciliation-for-execution, or execution-halt capability.

### Observability and failure reporting
- Critical decisions and failures must be observable without leaking secrets or sensitive credentials.
- Notification delivery is non-authoritative: Telegram/email failure, delay, duplication, or outage must not alter trading authorization or execution truth.
- Operational health, risk rejection, execution rejection, exchange failure, and reconciliation divergence must remain distinguishable failure classes.

### Security and resilience
- External input and exchange responses are untrusted until validated at the appropriate boundary.
- Retries/timeouts/circuit-breaking may not convert an unknown financial state into success.
- Security controls, dependency integrity, and supply-chain verification are release requirements, not optional hardening.
- Release artifacts must be traceable to an immutable source revision and verified dependency/build provenance; release verification must account for dependency integrity, artifact identity, and the applicable configuration schema/version.

## 8.1 Phase 1 domain-contract enforcement invariant

The instrument identity and canonical Futures symbol unit, and the multiplier/contract-specification unit, are complete on the verified main lineage. Historical Phase 1 cursor snapshots in this constitution are retained as evidence history; the authoritative current cursor is maintained by the master index and project-state. The current Phase 1 work has progressed through accounting and settlement-accounting.

The multiplier/contract-specification contract must make the following explicit and validated: contract quantity/unit, multiplier meaning, contract-size semantics, quote/settlement denomination, Linear/Inverse applicability, market applicability (CRYPTO Futures, FOREX Futures, GOLD Futures), precision/representation requirements, valid ranges, and failure semantics for unknown, zero, negative, contradictory, stale, unsupported, or ambiguous specifications.

No exchange adapter may redefine the canonical multiplier or contract-size meaning. Exchange-specific instrument metadata must be mapped into the explicit domain contract, with contradictory or incomplete specifications failing closed.

The implementation must remain deterministic and domain-safe. The next unit is not complete until production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence are all present.

## 9. Quality invariants

The official quality floor is immutable by default:
- G01: zero unexplained format/lint violations
- G02: zero unexplained type errors
- G03: complete required unit/contract suite
- G04: enforced architecture/dependency boundaries
- G05: >= 98% coverage
- G06: required security/supply-chain checks pass
- G07: required integration/resilience and failure-path evidence
- G08: >= 90% mutation score

No actor may lower, bypass, weaken, exclude, skip, xfail, or otherwise manipulate these requirements to obtain green status.

## 10. Testing invariants

Tests are architectural enforcement, not cosmetic evidence.

Forbidden:
- deleting tests to improve results
- skipping tests
- weakening assertions
- excluding healthy production code
- artificial coverage
- mutation suppression intended to improve score
- fake success paths
- placeholder tests
- tests that merely reproduce implementation without verifying behavior

A green result obtained by weakening the test system is not valid green evidence.

## 11. Architecture-change firewall

Any proposed change touching one or more of the following is automatically an Architecture Change Candidate:
- Futures-only boundary
- Spot boundary
- market scope
- Linear/Inverse semantics
- financial formulas or accounting ownership
- layer ownership
- dependency direction
- risk/execution boundary
- exchange isolation
- pipeline ordering
- fail-closed behavior
- quality thresholds
- architecture enforcement
- release criteria

The actor must stop at the architectural boundary and perform impact analysis before implementation.

## 12. Owner-change protection

The project owner has authority to propose architectural changes.

The owner does not have permission to silently bypass governance.

If an owner request conflicts with an invariant, the AI/engineer MUST issue a serious warning before making any change:

> CRITICAL ARCHITECTURE WARNING: This request conflicts with an architectural invariant. Direct implementation would create architecture drift. Implementation is blocked pending impact analysis and architecture-change review.

The warning must identify:
- violated invariant
- affected contracts
- affected dependencies
- affected tests
- affected gates
- financial/operational risk
- safer alternatives where available

Owner intent alone is not evidence that an architectural change is safe.

## 13. Architecture-change procedure

A proposed architectural change must follow:

PROPOSAL
→ CRITICAL WARNING
→ IMPACT ANALYSIS
→ ALTERNATIVES
→ RISK ANALYSIS
→ ADR
→ EXPLICIT RECONFIRMATION
→ ARCHITECTURE DOCUMENT UPDATE
→ IMPLEMENTATION
→ ARCHITECTURE TESTS
→ CI ENFORCEMENT
→ SAME-SHA VERIFICATION

No step may be silently omitted.

## 14. ADR requirements

Every approved architecture change must have an ADR under docs/architecture/adr/.

Minimum ADR content:
- status
- date
- owner/proposer
- problem
- current architecture
- proposed change
- reason current architecture is insufficient
- alternatives considered
- affected invariants
- affected contracts
- affected dependencies
- affected tests
- risk analysis
- migration plan
- rollback plan
- explicit approval/reconfirmation

Valid states:
- PROPOSED
- APPROVED
- REJECTED
- SUPERSEDED

PROPOSED must never be treated as APPROVED.

## 15. AI immutability rule

A new AI/session must start at `docs/architecture/ARCHITECTURE-MASTER-INDEX.md` and follow its single mandatory navigation path:
1. read the master index;
2. read project-state.md;
3. read this document;
4. read architecture-contract.md;
5. read futures-responsibility-map.md;
6. read dependency-rules.md;
7. read master-roadmap-and-governance.md;
8. read docs/architecture/adr/README.md;
9. inspect current HEAD;
10. identify the current authorized phase/gate;
11. continue the first authorized incomplete action.

The index is a navigation control only; it cannot override the constitutional hierarchy.

A new AI must:

**Continue the map, not reinvent the map.**

## 16. Architecture completion proof

An architecture rule is not considered enforced until:

ARCHITECTURE RULE
→ CONTRACT
→ PRODUCTION IMPLEMENTATION
→ ARCHITECTURE TEST
→ CI ENFORCEMENT
→ EVIDENCE

Documentation alone is insufficient.

## 17. Emergency rule

There is no emergency bypass for architectural safety.

If production pressure, CI failure, exchange behavior, or implementation difficulty conflicts with an invariant:

STOP → WARN → ANALYZE → GOVERN → THEN CHANGE

Never:

PRESSURE → BYPASS

## 18. Final constitutional statement

The project is designed to survive AI replacement, engineer replacement, implementation refactoring, exchange API changes, CI changes, dependency changes, and operational pressure.

Architecture Integrity > Green CI
Root Cause > Symptom Patch
Real Implementation > Placeholder
Real Evidence > Claim
Fail Closed > Unsafe Continuation

## 8.1.1 Multiplier / contract-specification semantic lock

The Phase 1 multiplier contract is now frozen as the canonical domain boundary for this unit:

- quantity unit at this boundary is explicit `CONTRACTS`;
- multiplier/contract size is an exact positive finite `Decimal`;
- Linear multiplier means base-asset units per contract;
- Inverse multiplier means quote-price-denomination units per contract;
- Linear quote notional = quantity × multiplier × price;
- Inverse quote notional = quantity × multiplier;
- Linear base exposure = quantity × multiplier;
- Inverse base exposure = (quantity × multiplier) ÷ price;
- price is explicitly denominated in the canonical symbol quote asset;
- multiplier, quantity, and price must be positive and finite;
- zero, negative, non-finite, contradictory, or unsupported specifications fail closed;
- no binary floating-point representation may determine this contract's financial result;
- this contract does not infer margin or settlement semantics; those remain explicit downstream Phase 1 contracts;
- exchange lot size, tick size, and exchange-specific precision are not silently inferred here.

The canonical production contract is `contracts/futures/contract_specification.py`. Exchange adapters may map source metadata into this contract but may not redefine its financial meaning.

## 8.1.2 Phase 1 cursor after multiplier closure

The multiplier and contract-specification unit is **complete** on the verified main lineage: production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence all passed.

Historical maintenance-margin cursor state is superseded by the later closure records below. It must preserve the explicit multiplier, settlement, margin, and leverage boundaries and independently define initial-margin denomination, formula inputs, ownership, applicability, validation, and fail-closed behavior before implementation.
\n## 8.1.3 Settlement asset / settlement semantics lock

The settlement contract is now frozen for this implementation unit:
- settlement denomination is an explicit asset unit;
- the settlement asset must equal the canonical Futures instrument settlement asset;
- an upstream settlement amount must declare its source asset;
- same-asset settlement requires no conversion rate and rejects a supplied rate;
- cross-asset settlement requires an explicit positive finite Decimal conversion rate;
- the conversion rate means settlement-asset units per one source-asset unit;
- conversion is deterministic Decimal multiplication only;
- the contract never fetches rates, selects an exchange, schedules settlement, mutates account state, or infers margin;
- invalid, missing, zero, negative, non-finite, contradictory, or ambiguous settlement terms fail closed;
- exchange-specific settlement transport and timing remain infrastructure/application responsibilities and cannot redefine denomination semantics.
\n## 8.1.4 Phase 1 cursor after settlement closure

Settlement asset and settlement semantics are complete on verified main SHA `164dcb97c38271ab29f79f8e9b8068bcc8a55234`: production implementation, meaningful contract tests, Phase 1 CI, Architecture Invariants CI, and G01 CI are green on the same SHA.

The next incomplete Phase 1 production contract is **initial margin semantics**. It must define explicit formula inputs, denomination, Linear/Inverse applicability, market applicability, ownership, validation, and fail-closed behavior before implementation.


## 8.1.5 Phase 1 margin asset / margin semantics lock

The margin contract is now frozen for this implementation unit:
- the canonical instrument identity is authoritative for margin_asset;
- margin denomination is explicit ASSET;
- an upstream margin amount must declare its source_asset;
- same-asset margin requires no conversion rate and rejects a supplied rate;
- cross-asset margin requires an explicit positive finite Decimal conversion rate;
- the conversion rate means margin-asset units per one source-asset unit;
- the contract applies independently to CRYPTO Futures, FOREX Futures, GOLD Futures, Linear Futures, and Inverse Futures;
- margin asset is not implicitly required to equal settlement asset; both are independently explicit financial semantics;
- this contract does not infer leverage, initial margin, maintenance margin, liquidation, risk limits, or exchange-specific collateral policy;
- no network, exchange selection, scheduling, persistence, account mutation, or runtime configuration is permitted in the domain contract;
- invalid, missing, zero, negative, non-finite, contradictory, or ambiguous margin terms fail closed.

Production boundary: contracts/futures/margin.py.
Test boundary: tests/contracts/test_margin.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.


## 8.1.6 Phase 1 leverage vocabulary / contract-level constraints cursor

The first incomplete leverage unit is now authorized. It must explicitly define leverage representation, admissible bounds, ownership, Linear/Inverse applicability, CRYPTO/FOREX/GOLD applicability, configuration provenance, validation, and fail-closed behavior.

Leverage must never be silently inferred from exchange defaults, margin amount, notional, or account state. This unit does not calculate initial margin, maintenance margin, liquidation, or risk decisions; those remain separately owned contracts.

## 8.1.8 Phase 1 initial margin semantics lock

Initial margin is an explicit requirement on a validated Futures notional. It is owned by the Futures domain/contract boundary and is independent from leverage-bound validation.

- unit: RATIO for the initial-margin requirement rate;
- numeric representation: exact finite Decimal;
- initial_margin_ratio: explicit, strictly positive;
- formula input: explicit positive finite notional in a declared valuation/margin denomination;
- formula: initial margin amount = notional × initial_margin_ratio;
- output denomination: the same denomination as the supplied notional; no implicit asset conversion is performed here;
- no rounding or quantization is introduced unless a later explicit precision contract authorizes it;
- applicability: CRYPTO/FOREX/GOLD and Linear/Inverse Futures;
- the notional input must already use the canonical multiplier/contract-specification semantics; this contract does not redefine Linear/Inverse notional;
- the ratio is never inferred from leverage, exchange defaults, account state, maintenance margin, liquidation policy, or risk policy;
- no hidden minimum/maximum ratio is introduced by this contract;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation is permitted;
- invalid, missing, zero, negative, non-finite, contradictory, or ambiguous inputs fail closed.

Production boundary: `contracts/futures/initial_margin.py`.
Test boundary: `tests/contracts/test_initial_margin.py`.
CI boundary: `.github/workflows/phase1-domain-contracts.yml`.

The Phase 1 cursor remains here until production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence are all green.

## 8.1.9 Phase 1 cursor after initial margin closure

Initial margin semantics are COMPLETE on main merge SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`: production implementation, meaningful contract tests, Phase 1 CI, Architecture Invariants CI, and G01 CI are green on the same SHA.

The next incomplete Phase 1 production contract is **maintenance margin semantics**. It must explicitly define its ownership, formula inputs, denomination, precision, Linear/Inverse applicability, market applicability, tier/rate/amount semantics where applicable, and fail-closed behavior before implementation.

The initial-margin contract remains independently owned and must not be redefined by maintenance-margin logic.


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

The canonical Futures exposure/position-valuation boundary is now frozen for this Phase 1 unit:
- gross base exposure: Linear = quantity × multiplier; Inverse = (quantity × multiplier) ÷ price;
- gross quote notional/value at explicit price: Linear = quantity × multiplier × price; Inverse = quantity × multiplier;
- signed directional exposure is derived from explicit LONG/SHORT; gross exposure/value remains non-negative;
- quantity is CONTRACTS; all financial inputs are exact finite positive Decimal values; bool/binary float inputs fail closed;
- valuation denomination is explicit BASE or QUOTE; no implicit rounding/quantization or exchange-specific mark-price behavior;
- reference-price provenance is explicit, observation time is aware UTC, and freshness requires explicit UTC as_of plus positive max_age;
- CRYPTO/FOREX/GOLD and Linear/Inverse are mandatory;
- this boundary consumes prior canonical contracts without redefining multiplier, price/quantity, PnL, funding, margin, settlement, leverage, side/mode, or accounting;
- no network, SDK, persistence, runtime configuration, scheduler, account mutation, or exchange transport dependency;
- invalid, missing, stale, contradictory, unsupported, non-finite, zero, negative, or ambiguous state fails closed;
- production/test/CI boundaries are explicit and same-SHA evidence is required before cursor advance;
- no threshold reduction, test weakening, skip/xfail, guessed exchange semantics, or dependency-boundary weakening is permitted.


## Phase 1 exposure / position valuation closure evidence

Exposure and position valuation semantics are COMPLETE on implementation SHA `dc9461a562426e02af3fc3585beed917940da049`, merged to main as `953c69ee2335cda62d0729f5b7f0bb53f6b2a080`. Same-SHA evidence: Phase 1 Domain Contracts green; G01 Dependency Architecture green; Architecture Invariants green. Production `contracts/futures/exposure.py`, tests `tests/contracts/exposure_contract_test.py`, and CI `.github/workflows/phase1-domain-contracts.yml` are the enforced boundaries. No threshold reduction, test weakening, skip/xfail, guessed exchange behavior, or dependency weakening was used.

## Phase 1 next-unit semantic gate — liquidation price and liquidation constraints

The next authorized contract must freeze: owner and lifecycle boundary; explicit liquidation-price versus liquidation-event meaning; required position/entry/quantity/multiplier/margin/leverage/maintenance-margin and other explicitly owned inputs; Linear/Inverse formulas; CRYPTO/FOREX/GOLD; interaction without redefining closed contracts; exact Decimal/no implicit rounding; account/reference provenance and freshness; fail-closed invalid/stale/contradictory/unsupported/ambiguous state; domain-safe dependencies only; meaningful tests; CI; same-SHA evidence. Exchange-specific liquidation formulas, mark-price conventions, tiers, fees, funding, settlement, or defaults may not be guessed into the canonical contract.


## Phase 1 liquidation-price constraint closure evidence

Liquidation-price constraints are COMPLETE on implementation SHA `b8b65b721fcae5720d5cf430c979700516d8c10a`, merged as `c18a99d58b8b8dc904250fce38d738eee3bd9bd6`. Phase 1 Domain Contracts is green on the merge SHA; G01 is green on the implementation lineage. The boundary is exact Decimal, explicit denomination, Linear/Inverse, all three markets, fail-closed, and excludes exchange-specific trigger/transport/execution semantics.

## Phase 1 next-unit invariant gate — liquidation event and trigger semantics

The next contract must preserve the distinction between a deterministic trigger condition and liquidation execution. It must explicitly define reference-price provenance/freshness, LONG/SHORT and ONE_WAY/HEDGE trigger direction, required state, Linear/Inverse and three-market scope, exact Decimal/no implicit rounding, fail-closed stale/ambiguous behavior, domain-safe dependencies, idempotency/ordering/concurrency, meaningful tests, CI, and same-SHA evidence. Network, SDK, exchange transport, forced-order placement, account mutation, and exchange-specific mark-price/tier/fee/funding defaults remain outside the canonical domain boundary. No gate or threshold weakening is permitted.

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
- CI: Phase 1 Domain Contracts, Architecture Invariants, and G01 Dependency Architecture are required on the same verification SHA;
- no threshold reduction, test weakening, skip/xfail, assertion removal, or dependency-boundary weakening.

## Phase 1 final completeness/evidence audit

Accounting and settlement-accounting are the final minimum financial contract units in the Phase 1 contract set. The next authorized action is governance/evidence reconciliation across the eight authoritative architecture documents, canonical contracts, tests, dependency boundaries, and same-SHA CI evidence. Phase 2+ production implementation remains blocked until this audit closes.
