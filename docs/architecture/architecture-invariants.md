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

The instrument identity and canonical Futures symbol unit, and the multiplier/contract-specification unit, are complete on the verified main lineage. The first incomplete Phase 1 production contract is now **leverage vocabulary and contract-level constraints**.

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

The current incomplete Phase 1 production contract is **leverage vocabulary and contract-level constraints**. It must preserve the explicit multiplier, settlement, and margin boundaries and independently define leverage units, limits, applicability, validation, and fail-closed behavior before implementation.
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

The next incomplete Phase 1 production contract is **leverage vocabulary and contract-level constraints**. It must define leverage representation, bounds, Linear/Inverse applicability, market applicability, configuration ownership, validation, and fail-closed behavior before implementation.


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
