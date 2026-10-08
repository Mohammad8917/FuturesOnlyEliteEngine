# Architecture Invariants — Constitution of FuturesOnlyEliteEngine

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

The system has two first-class operational outputs:
- **Automated Futures trading**, subject to the full risk and execution gates.
- **Signal and operational notification delivery** through Telegram and email.

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
- 15 independent exchange adapters

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
- reconciliation

No implicit financial default may be introduced when it can alter financial meaning.

## 5. Layer ownership invariants

Responsibility flow and source-code dependency direction are distinct concepts and must not be conflated.

Responsibility flow:

MARKET/DATA → ANALYSIS/DECISION → RISK → EXECUTION → EXCHANGE INFRASTRUCTURE → RECONCILIATION → AUDIT/OBSERVABILITY

Source-code dependency direction is governed by dependency-rules.md:

DOMAIN → DOMAIN-SAFE CONTRACTS
APPLICATION → DOMAIN + CONTRACTS
RISK → DOMAIN + CONTRACTS
EXECUTION → CONTRACTS + DOMAIN FACTS + RISK DECISIONS
INFRASTRUCTURE → APPLICATION/CONTRACTS/DOMAIN PORTS

Mandatory boundaries:
- Domain remains infrastructure-independent.
- Strategy/analysis must not submit orders.
- Risk must not place orders.
- Execution must not bypass risk validation.
- Exchange-specific transport/SDK semantics remain outside the domain.
- Infrastructure must not redefine domain financial semantics.
- No layer may silently take ownership of another layer's responsibility.

## 6. Exchange isolation invariants

The 15 exchange adapters remain independently owned infrastructure boundaries.

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
- order semantics
- precision/limits
- position mode
- reconciliation

## 7. Fail-closed invariants

Unknown, invalid, stale, contradictory, incomplete, or untrusted critical Futures state must not produce:
- an executable order
- an accepted executable signal
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
- Critical market and account data must have explicit validation status and provenance.
- Stale, missing, malformed, contradictory, or out-of-order critical data must fail closed.
- Monetary and contract calculations must use an explicitly governed exact numeric representation; binary floating-point must not silently determine financial outcomes where exact precision is required.
- Boundary timestamps must be UTC-aware and their ordering semantics explicit.
- Time access must have an explicit clock boundary separating UTC wall-clock timestamps from monotonic elapsed-time measurement. Safety-critical freshness, timeout, signing-window, and clock-skew policies must be validated configuration; unknown or excessive skew must fail closed where it can affect financial correctness or authorization.
- Units, quote/base denomination, settlement denomination, quantity, price, multiplier, and precision must be explicit at financial boundaries.

### Configuration and secrets

- Credentials, API keys, signing material, passwords, tokens, private keys, connection strings containing secrets, and other sensitive information must never be hard-coded in source code, tests, fixtures, documentation, logs, examples, or committed configuration.
- Operational configuration must not be hard-coded when it is environment-, deployment-, account-, exchange-, credential-, or runtime-specific; it must enter through an explicitly owned configuration/security boundary and be validated before use.
- Risk limits, leverage limits, execution authority, exchange credentials, endpoints, account identifiers, and other safety-critical operational values must not be silently embedded as source-code constants when they are intended to be configurable.
- Hard-coded values are permitted only when they are genuine immutable domain vocabulary or compile-time invariants whose meaning cannot vary by environment/account/deployment; such values must remain owned by the appropriate domain/contract boundary.
- Tests and fixtures must use non-sensitive synthetic values and must never embed real credentials or production secrets.
- Credentials, API keys, signing material, and secrets must not be hard-coded, committed, logged, or exposed through normal diagnostics.
- Configuration must fail closed when a required safety-critical value is missing, malformed, or contradictory.
- Every safety-critical configuration value must have explicit provenance/source, schema/version semantics, validation status, and effective lifecycle; untracked or ambiguously sourced configuration must not silently authorize execution.
- Configuration must not silently change Futures/Spot scope, risk policy, exchange identity, or execution authority.

### Order lifecycle, concurrency, recovery, and reconciliation
- Every executable intent must carry an immutable, unique idempotency identity with an explicitly defined uniqueness scope and replay/duplicate semantics. Exchange-native client-order identifiers must be used where supported, while internal deduplication remains mandatory regardless of exchange capability.
- Live exchange-confirmed order and position state is the authoritative source for actual external account state. Local intent/state is evidence and working state until externally confirmed; local state must never be promoted to financial truth merely because an exchange response is missing or ambiguous.
- Unknown order, fill, position, balance, or account state must block new execution for the affected scope until authoritative reconciliation resolves the uncertainty.
- Concurrent order/position transitions must be serialized or protected by an explicit version/concurrency invariant so stale local state cannot create duplicate, conflicting, or out-of-order financial mutations.
- After process restart, failover, reconnect, or loss of local state, execution authority must remain disabled until required account/order/position reconciliation completes successfully.
- A scoped/global trading halt (kill switch/circuit breaker) must exist at the execution-authority boundary. When active, no new executable order may be submitted; activation and release must be auditable and fail closed when the halt state is unknown.

### Order lifecycle and reconciliation
- Every executable order must have a traceable validated execution intent and risk decision.
- Order submission must be idempotency-aware where the external exchange supports or requires it.
- Unknown order/position state must never be converted into a guessed success state.
- Reconciliation must detect and surface divergence between local and exchange state; it must not silently overwrite contradictory financial facts.
- Audit records must preserve enough immutable evidence to reconstruct the decision, risk validation, execution intent, order result, and reconciliation outcome.
- Audit evidence must be append-only/tamper-evident at the architecture boundary, with stable event identity and causal correlation sufficient to reconstruct the lifecycle without relying on mutable operational logs.

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

The instrument identity and canonical Futures symbol unit, and the multiplier/contract-specification unit, are complete on the verified main lineage. The first incomplete Phase 1 production contract is now **maintenance margin semantics**.

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

The current incomplete Phase 1 production contract is **maintenance margin semantics**. It must preserve the explicit multiplier, settlement, margin, and leverage boundaries and independently define initial-margin denomination, formula inputs, ownership, applicability, validation, and fail-closed behavior before implementation.
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