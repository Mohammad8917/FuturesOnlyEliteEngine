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

## 10. Missing-requirement firewall
Before implementation of any new capability, explicitly check for ownership and contracts for:
- data provenance, freshness, ordering, contradiction handling;
- units, denominations, precision, UTC and numeric representation;
- Linear/Inverse formulas and applicability;
- market applicability;
- risk/account/exposure/margin/liquidation/funding/PnL;
- execution intent, idempotency, unknown order state;
- position/order reconciliation;
- audit immutability;
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

## 11. Current project control
The current project state is Phase 0 — Architecture Baseline / Governance Final Audit. Production implementation remains blocked until the Phase 0 exit criteria are evidenced on the current HEAD.
The next action is always the first incomplete authorized item — never a redesign and never a downstream implementation.

Continue the map, not reinvent the map.

## 12. Phase 0 closure / anti-cycle control
Phase 0 has a finite closure point. Its final audit exists to remove architecture blockers, not to continuously expand governance documentation.

Audit findings are classified as **FIX NOW**, **DEFER TO PHASE N**, or **NOT AN ARCHITECTURE GAP**. Only genuine Phase 0 architecture gaps are fixed before exit. Later implementation details, optimizations, and preferences must remain in their owning phase.

After all Phase 0 exit criteria are evidenced on the current HEAD and the exit decision is recorded in `project-state.md`, Phase 0 is **CLOSED**. Do not reopen it merely for additional documentation completeness. A later-phase concern reopens architecture only when it is a genuine architecture gap that would invalidate the current contract; otherwise the current phase continues.

This is the control against an infinite audit → document → re-audit cycle.
