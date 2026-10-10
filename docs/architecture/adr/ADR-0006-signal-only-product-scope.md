# ADR-0006 — Signal-Only Product Scope; Remove Automated Trading

## 1. Status
**PROPOSED — NOT APPROVED OR IMPLEMENTED**

This ADR is an architecture-change proposal. Creating this file or opening its PR does not change production behavior, authorize deletion, or supersede the protected Source of Truth.

## 2. Date
2026-10-10

## 3. Proposer / Owner
Repository owner, based on the explicit request to remove automated trading completely and retain only professional signal generation for CRYPTO Futures, FOREX Futures, and GOLD Futures.

## 4. Problem
The current authoritative architecture defines automated Futures trading as a first-class operational output and includes the responsibility path through Risk, Execution, exchange infrastructure, reconciliation, and audit. The owner has now directed that the product must not place trades automatically at all. Leaving contradictory requirements in place would allow future contributors to rebuild or accidentally expose live order execution.

## 5. Current Architecture
The protected architecture currently names automated Futures trading as a first-class output and documents:
- MARKET/DATA → ANALYSIS/DECISION → RISK → EXECUTION → EXCHANGE INFRASTRUCTURE → RECONCILIATION → AUDIT/OBSERVABILITY.
- 15 independent exchange adapters as a product target.
- Execution contracts, order lifecycle/idempotency, reconciliation, execution halt, and automated trading gates.
- Telegram/email operational controls that include trading automation ON/OFF.

The repository is currently documented as Phase 1 — Domain Contracts. This proposal does not assert that a live order-submission runtime exists or is deployed; a bounded audit of `main` did not identify one.

## 6. Proposed Change
Change the product to **signal-only** for exactly these supported market categories:
- CRYPTO Futures
- FOREX Futures
- GOLD Futures

Retain the Futures-only boundary and explicit Linear/Inverse semantics wherever they are needed to analyze instruments and calculate valid signals.

The product may:
- ingest and validate market data;
- calculate indicators and SMC/confluence features;
- generate, score, publish, expire, invalidate, and audit signals;
- calculate and display reference entry, stop-loss, targets, estimated costs, risk/reward, and suggested position sizing when the required instrument metadata and assumptions are explicit;
- provide backtesting, walk-forward/out-of-sample analysis, and Paper Trading as simulation-only validation;
- send Telegram/email signal and operational notifications;
- provide read-only market/signal/analytics status.

The product must **never**:
- submit, amend, cancel, or retry a live exchange order;
- automatically open, increase, reduce, or close a real position;
- automatically transfer funds, change leverage, allocate capital, or mutate an exchange account;
- turn a signal, Telegram command, retry, restart, or configuration change into a live execution intent;
- expose an automation ON switch or suggest that live order execution is available.

Remove automated-trading capability from the product scope and roadmap—not merely hide it behind a feature flag. Remove production order-execution implementations, live order submission paths, execution-specific Telegram controls, and product requirements that promise automated trading, after the ADR is approved and migration is authorized.

Do **not** delete useful market-data adapters, Futures instrument/financial contracts, risk calculations used to describe signal risk, or simulation-only components merely because their names overlap with execution concepts. Audit each component and remove it only if it exclusively supports live execution or contradicts signal-only behavior. No exchange-specific market-data work may guess which exchanges the owner has selected.

Signal generation must remain fail-closed for stale/invalid data, unsupported instruments, unknown contract semantics, invalid price/quantity units, and missing inputs required for a meaningful risk estimate. Risk figures are advisory and must not be represented as guaranteed maximum losses or profitable outcomes.

## 7. Why Current Architecture Is Insufficient
A global OFF switch is not a permanent product boundary: future code can re-enable execution, bypass the switch, or interpret the roadmap as authorization to restore live trading. The requested target is structurally signal-only, so the product specification and architecture must no longer promise automated order execution.

## 8. Alternatives Considered
1. Keep full automated trading but disabled by default — rejected because it preserves a capability the owner has asked to remove completely.
2. Retain live execution behind a kill switch — rejected for the same reason.
3. Signal-only product, preserving analysis/risk/simulation and useful shared Futures contracts — proposed.
4. Delete all exchange and Futures financial abstractions — rejected because market-data analysis and valid Futures signal/risk calculations still require explicit instrument semantics.

## 9. Affected Invariants
This proposal conflicts with the current immutable-by-default architecture and requires explicit approval before changing:
- `docs/architecture/architecture-invariants.md`: automated Futures trading as a first-class output.
- `docs/architecture/architecture-invariants.md`: responsibility flow including EXECUTION and the 15 exchange-adapter target insofar as order execution is concerned.
- `docs/architecture/architecture-contract.md`, `futures-responsibility-map.md`, `dependency-rules.md`, `master-roadmap-and-governance.md`, `ARCHITECTURE-MASTER-INDEX.md`, and `project-state.md` where they promise or authorize automated trading/execution.
- Telegram operations requirements that describe live trading ON/OFF or account-mutating commands.

The Futures-only market boundary (CRYPTO/FOREX/GOLD Futures), Linear/Inverse distinction, exact Decimal, fail-closed rules, secrets protection, quality thresholds, ADR governance, and same-SHA CI remain unchanged.

## 10. Affected Contracts
After approval, audit and revise:
- Product/operational capability contract to signal-only.
- Signal lifecycle and notification contracts.
- Risk-estimate and suggested-sizing semantics (advisory, not authorization to place orders).
- Application command allow-list and Telegram controls, removing order/account mutation commands.
- Exchange adapter scope: market-data/read-only capability only; no order-write credentials or order-write methods.
- Audit and health status to report signal pipeline/data readiness rather than live-execution readiness.
- Simulation/Paper Trading contracts to guarantee no live side effects.

No unknown exchange, instrument filters, tick/lot rules, fees, funding assumptions, or account mode may be invented.

## 11. Affected Dependencies
- Analysis may depend on market-data and pure Futures domain contracts.
- Signal risk calculations may consume explicit instrument metadata and assumptions.
- Signal delivery depends on signal state and notification contracts only.
- No product runtime path may depend on an order-submission client or execution command.
- Any retained legacy execution code must be unreachable from production application entry points during migration and removed once migration tests and references are complete; the final target contains no live order-writing path.
- No shell/SQL/arbitrary API command is introduced as a substitute for execution.

## 12. Affected Tests / Gates
Keep all existing CI thresholds and gates unchanged. Do not skip, delete, xfail, exclude, or weaken tests to achieve green status.

Add/retain tests for:
- static/source-level absence of live order submission and account-mutation calls from production runtime;
- no live order-write methods or execution ON controls in supported app interfaces;
- Telegram/email can publish signals but cannot create order intents;
- restart, retries, duplicated callbacks, stale signals, and malformed configuration never produce live side effects;
- signal-only mode and Paper Trading are explicitly distinct from live execution;
- CRYPTO/FOREX/GOLD Futures and Linear/Inverse semantics remain explicit;
- stale/missing/contradictory data fails closed for signal issuance or risk estimates;
- all mandatory G01–G08, Phase 1, Architecture Invariants, coverage, mutation, and same-SHA verification rules remain enforced.

Deletion must be evidence-driven: identify every order-write path and its callers first, then remove it with tests proving absence. Do not claim deletion is complete based on documentation alone.

## 13. Risk Analysis
Benefits:
- removes the class of losses caused by accidental or buggy automated order submission;
- reduces secret permissions and attack surface by eliminating order-write credentials and commands;
- narrows product behavior and operational responsibility.

Risks/costs:
- no automated execution remains available as a future product feature unless a new architecture decision explicitly reverses this decision;
- removing execution code may affect imports, tests, dependency checks, and legacy documentation;
- signal quality, market-data correctness, cost assumptions, and user decisions can still cause financial loss;
- simulation and Paper Trading must be technically isolated from live exchange side effects;
- the repository may have no live execution implementation to delete today, so actual deletion scope must be established from a complete source/reference audit.

## 14. Migration Plan
1. Review and approve this ADR through the required owner/governance process.
2. Inventory all protected documents, product docs, code, dependencies, credentials, workflows, commands, tests, and branches that describe or implement live execution.
3. Update protected Source-of-Truth documents only through the approved ADR migration.
4. In the currently authorized project phase, complete the allowed contract/governance changes and do not bypass the Phase 1 exit gates. Production implementation remains blocked until the roadmap authorizes it.
5. Remove order-write runtime code and account-mutating controls in scoped PRs; preserve signal generation, read-only market data, pure financial contracts, and simulation-only validation.
6. Add negative tests/static guards that prove no live order-write path remains.
7. Run required tests and gates and verify all results on the exact final SHA.
8. Audit branches and deployment/configuration separately. A repository change alone does not prove an already-running external deployment has been stopped.

## 15. Rollback Plan
Do not restore live execution by reverting code or toggling a setting. If the signal-only scope proves insufficient, a future owner proposal must use a new ADR, critical warning, impact analysis, explicit reconfirmation, and required CI evidence before any execution architecture is reintroduced. The safe operational state remains no live order side effects.

## 16. Explicit Approval / Reconfirmation
**Owner intent recorded:** The owner explicitly requested: “معامله خودکار کامل تضمینی حذف کن فقط سیگنال تولید کنه برای سه بازار” — completely remove automated trading and generate signals only for the three markets.

**Specific ADR approval:** Pending review of this exact impact analysis and formal approval under the repository's ADR workflow. Until then, this ADR remains PROPOSED, protected Source-of-Truth documents remain unchanged, and no code deletion is claimed or authorized by this proposal alone.
