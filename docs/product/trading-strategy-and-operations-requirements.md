# Product Requirements Register — Trading Strategy, Automation, Credentials, and Telegram Operations

**Status:** Consolidated requirements register / proposal. Not a production implementation, not a release-readiness claim, and not permission to bypass phase gates.  
**Created:** 2026-10-10  
**Purpose:** Preserve previously discussed owner requirements in one discoverable place and distinguish recorded decisions from unresolved design details.  
**Architecture authority:** `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`, the protected Source-of-Truth documents, and approved ADRs remain authoritative. This register does not override them.

## 1. Current finding and scope

The inspected `main` branch has a product/architecture description and a unified architecture path, but the strategy/indicator specification and operational details are not consolidated as a discoverable product requirements document on `main`. Related proposals exist separately:
- PR #43 — Hybrid Safe/Risky Entry signal policy: https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/43
- PR #44 — Telegram operations control plane, credentials, user isolation, capital allocation, and controls: https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/44
- PR #45 — Financial Audit Port proposal: https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/45

This document consolidates the known requirements and links the separate records; it does not silently approve or implement their proposals.


## 1.1 Owner decision: signal-only mode; live execution disabled

**Current approved operating policy:** `SIGNAL_ONLY`. **Live automated execution: `DISABLED`.** The long-term execution architecture is retained; this is a temporary safety/validation gate, not a decision to delete automated trading from the roadmap.

- **Stable reason code:** `LIVE_EXECUTION_DISABLED_UNVALIDATED_READINESS`.
- **Status explanation (user-facing):** Live execution is disabled because financial arithmetic and durable audit integration, risk/position sizing, execution idempotency, exchange reconciliation, security validation, and reproducible backtest/out-of-sample/Paper Trading evidence have not yet all been verified.
- Missing, stale, unknown, or indeterminate readiness means disabled. Startup, restart, lost state, and uncertain recovery default to OFF; no automatic resume.
- Signal analysis, signal delivery, backtesting, and Paper Trading may proceed where implemented and separately validated. They must not submit live orders.
- While disabled, live order submission, replacement, cancellation-as-automation, and automatic position mutations must be rejected at the execution boundary. Emergency pause must not silently liquidate positions.
- Health/status/UI output must distinguish this intentional disabled policy from an unexpected system fault and show both the stable reason code and readable explanation.
- Re-enabling is a separate gated decision: all required financial/audit, risk, idempotency, reconciliation, security, backtest/out-of-sample, Paper Trading, and same-SHA CI evidence must pass, followed by explicit owner authorization. No profitability guarantee is implied.

**Implementation status caveat:** This is the recorded owner decision and required behavior, not proof that a runtime kill switch has already been implemented. The bounded audit of `main` found the repository still at Phase 1 Domain Contracts and did not identify an operational live-order runtime to turn off. Track enforcement and verification under [Issue #50](https://github.com/Mohammad8917/FuturesOnlyEliteEngine/issues/50). Do not claim deployed trading is disabled until the actual deployed/runtime path is inspected and verified.

## 2. Product invariants

- Futures only: CRYPTO Futures, FOREX Futures, and GOLD Futures.
- Linear and Inverse Futures remain semantically distinct.
- The product target includes 15 independent exchange adapters, but no exchange-specific work may guess which exchanges are selected.
- Spot execution, Spot fallback, and using unrelated Spot balances as Futures trading capital are forbidden.
- Python 3.13; deployment targets include Windows Server, Linux Server, and Windows Home/Desktop.
- Strategy/analysis proposes signals; it never submits orders or bypasses Risk.
- Execution must follow explicit Risk approval, execution contracts, idempotency, reconciliation, and audit controls.
- Telegram/email are notification and operations interfaces, not evidence of order success and not a bypass around Risk/Execution.
- Exact financial semantics, fail-closed behavior, secret protection, tests, CI thresholds, and same-SHA evidence remain mandatory.

## 3. Strategy baseline recorded from owner discussion

The following is the recorded baseline for the proposed strategy. It must be implemented only after its deterministic rules and acceptance tests are defined; this section alone is not evidence of live trading capability.

### 3.1 Strategy family and concepts

- Core: **SMC + Confluence Scoring**.
- SMC structure concepts: Break of Structure (BOS), Order Blocks (OB), Fair Value Gaps (FVG), and Liquidity Sweeps.
- Trend context: EMA(50) and EMA(200).
- Momentum/context: RSI(14), MACD, ADX(14), ATR(14), Volume, and VWAP.
- MACD and VWAP are contextual/conditional confirmations, not automatic mandatory conditions in every market.
- The scoring baseline discussed is **at least 5 out of 6**. The six scoring buckets, each bucket's exact definition, weights, conflict handling, missing-data handling, and whether a given indicator contributes to one or more buckets must be explicitly specified before executable signals are allowed. Do not invent a scoring map.
- All mandatory hard gates must pass. A high score must never override stale/contradictory data, invalid structure, unsupported instrument, invalid price/quantity semantics, failed Risk Gate, or execution restrictions.

### 3.2 Timeframes, session, and signal limit

- H4: higher-timeframe structure/context.
- H1: confirmation.
- M15: primary execution/setup timeframe.
- M5 may be used only if it contributes an independently defined, tested signal-quality benefit; it must not be added as redundant confirmation by default.
- Discussed operating window: **04:00–24:00 Asia/Tehran time**. The timezone and daylight-saving behavior must be implemented explicitly and tested; store canonical timestamps in UTC and render the local timezone clearly.
- Maximum **7 signals per day** is a ceiling, not a quota or target. Fewer or zero signals are correct when criteria are not met. Define whether the daily counter is per user, strategy, market, or system before implementation; do not assume.
- The system must reject rather than force a signal if mandatory conditions are not met.

### 3.3 Stop, targets, and trade management baseline

- Initial stop-loss proposal: **1.5 × ATR(14)**, with the correct structural side and instrument price semantics.
- TP1 proposal: **1.5R**.
- TP2 proposal: **3R**.
- Begin trailing-stop management only after TP1 is reached.
- These are strategy-level candidate parameters, not a substitute for valid SMC structure, exchange tick/quantity constraints, fees/funding/slippage treatment, or Risk approval.
- Exact ATR sampling, candle closure rules, swing/structure invalidation, partial-exit fraction at TP1, trailing formula/step, order type, and behavior under gaps/partial fills are not yet fully defined here. Do not guess them in production.
- No strategy metric or profitability claim is approved by this document. Backtests must avoid look-ahead, data leakage, survivorship bias, and unrealistic fees/slippage/funding assumptions.

## 4. Signal types, entry selection, and lifecycle

See PR #43 and `docs/architecture/adr/ADR-0005-dual-entry-policy.md` on its proposal branch for the detailed signal policy.

Recorded requirements:
- Show both Safe Entry and Risky Entry candidates when available.
- Automated execution selects exactly **one** candidate per decision; never submit both from the same signal.
- Hybrid selection criteria must be deterministic and tested. Until they are, ambiguous conditions fail closed and no executable entry is selected.
- Safe-only mode selects Safe Entry; Risky-only mode selects Risky Entry; Hybrid selects one only when validated conditions unambiguously permit it.
- Human-facing signal fields use Persian labels and include symbol, market, direction, UTC issuance time with timezone, Safe Entry, Risky Entry, selected entry type, stop-loss, take-profit, leverage, validity, unique signal ID, analytical/executable type, status, and reason.
- Initial validity: 20 minutes. Maximum three renewals of 20 minutes each; maximum lifetime 80 minutes from original issuance.
- Renewal requires fresh reassessment, valid setup, and passing Risk Gate. Resending is not renewal. No fourth renewal, entry-zone drift, chasing, or execution outside the selected zone.
- Invalid, expired, cancelled, stale, contradictory, or risk-rejected signals must be invalidated with a durable reason and an explicit Persian invalidation notification. Delivery retries must not restore validity.
- Stable signal identity, duplicate suppression, idempotent lifecycle transitions, and no duplicate execution intent are mandatory.
- An analytical signal, or one with no concrete selected entry, must never become executable by inference.

## 5. Automated trading and risk gates

- Automation is gated by a global ON/OFF switch, independent market switches for CRYPTO/FOREX/GOLD Futures, user authorization, current valid signal, fresh market data, exchange/account readiness, healthy audit/reconciliation, and the existing Risk and Execution gates.
- ON requires explicit confirmation and a readiness checklist; OFF/pause must take effect immediately after authorization.
- Process liveness alone is not trading readiness. Any required UNKNOWN/NOT READY component blocks enabling.
- Risk rejection, stale balance/data, unsupported instrument, invalid exchange metadata, unresolved critical reconciliation mismatch, uncertain order state, or audit failure must fail closed for new entries.
- Maximum signal count is never a reason to enter a trade. No valid setup means no trade.
- Order sizing must respect explicit allocation, verified available Futures margin, instrument contract semantics, tick/lot/minimum rules, fees and buffers. Never automatically increase leverage, allocation, or order size to force acceptance.
- Duplicate-order prevention, client/execution idempotency, handling rejected/partial/unknown orders, state reconciliation, and durable audit events are required.
- A daily-loss pause and other risk ceilings must not be bypassed by Telegram, strategy scores, retries, or notification status.

## 6. Exchange API credentials and account isolation

See PR #44 for the detailed Telegram operations proposal.

Requirements recorded there:
- Each user's credentials, account context, balances, positions, orders, allocation, and audit records are isolated. Never use one user's credentials for another user or silently trade through a shared owner account.
- API secrets must never be collected in ordinary Telegram messages/callback data, committed to source, printed in logs, or displayed in plaintext. Telegram may initiate a secure registration workflow, but secret entry belongs in a separately approved, access-controlled secret-entry interface/vault.
- Encrypt secrets at rest, restrict access, redact logs/traces, support rotation and revocation, and verify the credential/account binding.
- Use least-privilege API keys. Withdrawal/transfer permissions must be absent; use IP restrictions where supported.
- Telegram displays masked credential status only, never the secret itself.
- Exchange-specific permission checks, account modes, supported Futures contract families, IP controls, and metadata validation cannot be completed until the owner provides the target exchange list. Do not guess exchanges, endpoints, permissions, symbols, tick sizes, lot steps, leverage limits, or minimum order rules.

## 7. Telegram operations menu

The menu is an operational control plane, not a trading engine. PR #44 records the detailed proposal. The consolidated menu groups are:

1. **Trading:** global automation ON/OFF; independent CRYPTO/FOREX/GOLD Futures switches; per-user enable/pause; readiness checklist.
2. **Signals:** candidate list, signal type, chosen entry, validity/expiry, renewal count, status, invalidation reason. Viewing a signal never authorizes an order.
3. **Users & access:** authorized-user list, add/remove/revoke, role/approval workflow, current active count/capacity. The proposal records a configurable active-user capacity with a hard maximum of 1,000; capacity reduction below active count must be rejected until users are explicitly removed.
4. **Accounts & credentials:** secure registration/verification/rotation/revocation workflow; masked status only; per-user account isolation.
5. **Capital & allocation:** verified Futures-margin balance, balance freshness, allocation percentage, used/reserved allocation, available margin and exposure. Never silently allocate 100% of account funds.
6. **Risk & limits:** current per-trade and aggregate risk use, daily-loss pause, margin headroom, and stable blocked reason codes.
7. **Positions & orders:** read-only view and reconciliation status by default. Any future cancel/close action requires explicit scope, authorization, confirmation, idempotency, and audit.
8. **Health & operations:** component readiness, incidents, maintenance/read-only mode, persisted control-state timestamp, recovery state, and reconciliation mismatch.
9. **Audit & reports:** privacy-safe control history; daily/weekly PnL, fees/funding, drawdown, allocation utilization, rejected-order reasons.
10. **Notifications & help:** user preferences and clear instructions; delivery failure never changes signal, risk, or execution state.

Menu security/usability requirements:
- Compact localized main menu with grouped submenus; Persian is the recorded initial language.
- Read-only by default for balances, positions, orders, PnL, health, signals, audit, and reconciliation.
- Two-step confirmation for global ON, market/user ON, credential binding/replacement, allocation/capacity changes, and any approved cancel/close action. Reject stale confirmations.
- No one-tap destructive close-all/cancel-all action.
- Bind sensitive callbacks to actor, target, state version, and expiry; rate-limit and reject replayed/duplicate/out-of-order callbacks.
- No shell, Python, SQL, arbitrary URL fetch, or arbitrary API command from Telegram; actions map to typed allow-listed application commands.
- Persist control changes atomically and audit actor, action, old/new state, UTC time, outcome, and correlation/idempotency key.
- On restart or uncertain control-state recovery, default global automation to OFF; never auto-resume trading without explicit owner confirmation.
- Ordinary users see only their own account data; owner cross-user views remain privacy-safe and mask secrets.

## 8. Recorded capital/risk proposal values — not universal exchange rules

PR #44 records the following proposed owner requirements. They must be confirmed against the current policy/ADR record before production enforcement; this register does not make them live:
- Eligibility floor: at least **USD 20 equivalent** of verified available Futures-margin balance. Below threshold, stale/unknown/unconvertible balance means ineligible.
- Allocation default: **10%** of the selected verified Futures-margin balance; per-user configurable; hard application ceiling **50%**. Allocation budget is not notional exposure or per-trade risk.
- Proposed planned loss per trade: at most **0.5%** of allocated capital.
- Proposed aggregate planned open risk, including pending orders: at most **2%** of allocated capital.
- Proposed daily loss pause: **3%** from the configured daily baseline pauses new entries for that user until authorized reset at the next risk period.
- USD 20 is a user eligibility floor, not a guarantee that any exchange/instrument permits an order at that value. Authoritative exchange filters must be fetched and validated; examples such as USD 5 or USD 10 are not universal constants.
- Risk calculations must account for fees/funding/slippage where estimable and fail closed if a meaningful loss bound cannot be computed. These limits cannot guarantee a maximum realized loss under gaps, outages, or liquidation.

## 9. Other operational requirements discussed

- Signal and operational notifications through Telegram and email; notifications are downstream outputs only.
- Explicit invalidation notices and delivery retry records.
- Auditable control changes, signal lifecycle, execution intent, and reconciliation outcomes.
- Health status must reflect critical component readiness, data freshness, exchange/account connection, Risk/Execution state, reconciliation, and audit persistence—not merely whether the process is running.
- Emergency pause must block new automated intents; it must not silently liquidate positions.
- Daily/weekly reports should distinguish realized/unrealized PnL, fees, funding, drawdown, allocation use, and rejected-order reasons.
- Cross-platform support (Windows and Linux) must not weaken security or trading safety.
- Backtest → walk-forward validation → out-of-sample evaluation → paper trading are required validation stages before any live-trading claim. Metrics must be based on reproducible evidence; no fabricated win-rate/profitability claim.
- API keys, tokens, passwords, account identifiers, and secret-bearing configuration must never be hard-coded or exposed.

## 10. Explicitly unresolved — do not invent answers

Before executable production behavior is approved, specify and test:
- the six exact scoring buckets, their inputs/weights, missing-data behavior, tie/conflict rules, and hard gates;
- precise BOS/OB/FVG/liquidity-sweep definitions, swing lookback, candle-close versus intrabar rules, and market-regime handling;
- exact MACD/VWAP conditional applicability;
- exact timezone implementation for the 04:00–24:00 Tehran window and daily reset semantics;
- scope of the seven-signals/day ceiling (per user, strategy, market, or system);
- exact partial-exit quantity at TP1 and trailing-stop formula/step;
- safe/risky/hybrid selection thresholds and the contract for selecting one candidate;
- exchange list and each exchange's supported Futures products, Linear/Inverse support, API permission model, account/margin modes, authoritative filters, and test environments;
- final admin/role model, user invitation/activation semantics, and secure secret-entry interface;
- exact definition of eligible balance/valuation conversion and policy versioning;
- approved durable audit-port implementation and behavior when audit persistence is unavailable;
- final acceptance criteria for backtest/walk-forward/out-of-sample/paper-trading results.
Until resolved, ambiguous or unavailable critical inputs must fail closed; no exchange-specific implementation may be guessed.

## 11. Governance and implementation boundary

- This document is a requirements register, not an approved ADR and not a production implementation.
- It does not modify protected Source-of-Truth documents and does not authorize Phase 2+ work while Phase 1/governance blockers remain open.
- Any change to frozen invariants, ownership, dependency direction, fail-closed behavior, pipeline order, or risk semantics must follow the formal ADR process and explicit owner reconfirmation.
- Do not skip/xfail/delete tests, reduce thresholds, fabricate PASS, or call operational G07 passed when it is not.
- A requirement is complete only with: rule → contract → owner → production implementation → meaningful tests → CI enforcement → current-head same-SHA evidence.
- Existing PRs #43–#45 remain separate review/approval records; this register does not silently merge or approve them.

## 12. Related authoritative navigation

- Architecture entry point: `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`
- Current authorized phase/gate: `docs/architecture/project-state.md`
- Invariants: `docs/architecture/architecture-invariants.md`
- Contracts: `docs/architecture/architecture-contract.md`
- Responsibility ownership: `docs/architecture/futures-responsibility-map.md`
- Dependency direction: `docs/architecture/dependency-rules.md`
- Governance/roadmap: `docs/architecture/master-roadmap-and-governance.md`
- ADR process: `docs/architecture/adr/README.md`
- Hybrid signal policy proposal: PR #43
- Telegram operations proposal: PR #44
- Financial audit port proposal: PR #45
