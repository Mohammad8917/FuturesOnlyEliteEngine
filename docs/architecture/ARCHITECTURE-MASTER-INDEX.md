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
8. docs/architecture/adr/README.md — architecture-change process.
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

**Current cursor:** leverage vocabulary and contract-level constraints.

The instrument identity and canonical Futures symbol unit is evidenced complete on the current main lineage. The next incomplete authorized Phase 1 unit must be completed through the full implementation-unit path:

Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers → Implementation → Test → CI → Same-SHA Evidence.

The cursor is not satisfied by documentation alone. Phase 1 remains incomplete until every canonical contract unit closes this evidence path.

## 11. Current project control
The current project state is Phase 1 — Domain Contracts. Phase 0 — Architecture Baseline / Governance Final Audit is CLOSED, and Phase 1 is authorized. Phase 2+ remains blocked until each preceding phase exit criteria is evidenced.
The next action is always the first incomplete authorized item — never a redesign and never a downstream implementation.

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

Historical closure: the multiplier, settlement, and margin units are evidenced complete on main. The current first incomplete authorized Phase 1 unit is **leverage vocabulary and contract-level constraints**.

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

**Current cursor:** margin asset and margin semantics.

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
