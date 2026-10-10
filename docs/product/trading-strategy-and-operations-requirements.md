# Product Requirements Register — Signal-Only Futures Analysis and Operations

**Status:** Owner-approved signal-only requirements register. Not a production implementation or release-readiness claim; all phase gates remain mandatory.  
**Created:** 2026-10-10  
**Purpose:** Preserve previously discussed owner requirements in one discoverable place and distinguish recorded decisions from unresolved design details.  
**Architecture authority:** `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`, the protected Source-of-Truth documents, and approved ADRs remain authoritative. This register does not override them.

## 1. Current finding and scope

The inspected `main` branch has a product/architecture description and a unified architecture path, but the strategy/indicator specification and operational details are not consolidated as a discoverable product requirements document on `main`. Related proposals exist separately:
- PR #43 — Hybrid Safe/Risky Entry signal policy: https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/43
- PR #44 — Telegram operations control plane, credentials, user isolation, capital allocation, and controls: https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/44
- PR #45 — Financial Audit Port proposal: https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/45

This document consolidates the known requirements and links the separate records; it does not silently approve or implement their proposals.


## 1.1 Owner decision: permanently signal-only product scope (ADR-0006 owner-approved; PR #51 pending required review/merge)

The owner explicitly approved complete removal of automated trading. The product is signal generation and advisory risk analysis for CRYPTO Futures, FOREX Futures, and GOLD Futures only. The owner-approved architecture migration is tracked in [ADR-0006 PR #51](https://github.com/Mohammad8917/FuturesOnlyEliteEngine/pull/51); protected Source-of-Truth changes and implementation remain governed by that PR and the repository's review/CI rules.

- **Target:** generate, validate, score, publish, expire, invalidate, and evaluate signals; provide risk estimates, suggested position sizing, backtesting, walk-forward/out-of-sample analysis, isolated Paper Trading, and Telegram/email notifications where implemented.
- **Forbidden product capability:** live order submit/amend/cancel/retry; automatic position or account mutation; automated leverage/capital changes; execution ON switches; Telegram/email commands that cause exchange side effects.
- Preserve useful market-data adapters, explicit Futures/Linear/Inverse financial contracts, pure risk calculations, and simulation-only components. Remove any live order-writing code if discovered by the full audit; the current audited main tree contains no application/execution/infrastructure runtime directories. Remove requirements that promise automated trading.
- Market-data adapters must be read-only; no order-write credentials or permissions are required or accepted by the signal-only runtime.
- Signal and risk calculations fail closed when required data, instrument semantics, or assumptions are missing, stale, contradictory, or unsupported. Suggested size/risk is advisory and not a guaranteed maximum loss.
- Backtesting and Paper Trading must be technically isolated from live order side effects.
- This requirements register records the owner's approval but is not proof of implementation completion or external deployment state. Do not claim complete removal until repository source/dependency/interface audits, static and regression tests, same-SHA CI, and any applicable deployment audit provide evidence.

## 2. Product invariants

- Futures only: CRYPTO Futures, FOREX Futures, and GOLD Futures.
- Linear and Inverse Futures remain semantically distinct.
- The CRYPTO Futures read-only market-data provider shortlist contains 15 venues as recorded in §6.1. The shortlist is not an execution-adapter target and is not proof that providers are reachable, legally available, or validated.
- Spot execution, Spot fallback, and using unrelated Spot balances as Futures trading capital are forbidden.
- Python 3.13; deployment targets include Windows Server, Linux Server, and Windows Home/Desktop.
- Strategy/analysis proposes signals; it never submits orders or bypasses Risk.
- Live execution, order-writing, real-position mutation, and account mutation are prohibited; risk calculations are advisory only.
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
- The scoring baseline discussed is **at least 5 out of 6**. The six scoring buckets, each bucket's exact definition, weights, conflict handling, missing-data handling, and indicator-to-bucket mapping must be explicitly specified before production signal issuance. Do not invent a scoring map.
- All mandatory hard gates must pass. A high score must never override stale/contradictory data, invalid structure, unsupported instrument, invalid price/quantity semantics, or missing/invalid assumptions required for an advisory risk estimate.

### 3.2 Timeframes, session, and signal limit

- H4: higher-timeframe structure/context.
- H1: confirmation.
- M15: primary setup/signal timeframe.
- M5 may be used only if it contributes an independently defined, tested signal-quality benefit; it must not be added as redundant confirmation by default.
- Discussed operating window: **04:00–24:00 Asia/Tehran time**. The timezone and daylight-saving behavior must be implemented explicitly and tested; store canonical timestamps in UTC and render the local timezone clearly.
- Maximum **7 signals per day** is a ceiling, not a quota or target. Fewer or zero signals are correct when criteria are not met. Define whether the daily counter is per user, strategy, market, or system before implementation; do not assume.
- The system must reject rather than force a signal if mandatory conditions are not met.

### 3.3 Stop, targets, and trade management baseline

- Initial stop-loss proposal: **1.5 × ATR(14)**, with the correct structural side and instrument price semantics.
- TP1 proposal: **1.5R**.
- TP2 proposal: **3R**.
- Any trailing reference level shown in a later analytical signal update may be calculated only after TP1 is reached; no position management occurs.
- These are strategy-level candidate parameters, not a substitute for valid SMC structure, exchange tick/quantity constraints, fees/funding/slippage treatment, or Risk approval.
- Exact ATR sampling, candle closure rules, swing/structure invalidation, trailing-reference formula/step, and gap handling are not fully defined here. Do not guess them in production; no partial exits, orders, or live-position management are implemented.
- No strategy metric or profitability claim is approved by this document. Backtests must avoid look-ahead, data leakage, survivorship bias, and unrealistic fees/slippage/funding assumptions.

## 4. Signal types, entry selection, and lifecycle

See PR #43 and `docs/architecture/adr/ADR-0005-dual-entry-policy.md` on its proposal branch for the detailed signal policy.

Recorded requirements:
- Show both Safe Entry and Risky Entry candidates when available.
- Safe Entry and Risky Entry are alternative analytical candidates only. The product does not automatically select an executable entry and never submits either candidate as an order.
- If any ranking or preference between Safe/Risky candidates is displayed, its criteria must be deterministic and tested. Until then, show them as alternatives without automated selection; ambiguous conditions fail closed.
- No Safe-only/Risky-only/Hybrid execution mode exists. Any future display preference is analytical presentation only and cannot authorize execution.
- Human-facing signal fields use Persian labels and include symbol, market, direction, UTC issuance time with timezone, Safe Entry, Risky Entry as alternatives, stop-loss, take-profit, optional explicitly assumed leverage reference (never applied), validity, unique signal ID, analytical-only type, status, and reason.
- Initial validity: 20 minutes. Maximum three renewals of 20 minutes each; maximum lifetime 80 minutes from original issuance.
- Renewal requires fresh reassessment, valid setup, and passing the defined advisory signal/risk-estimate validations; no execution Risk Gate exists. Resending is not renewal. No fourth renewal, entry-zone drift, chasing, or execution outside the selected zone.
- Invalid, expired, cancelled, stale, contradictory, or risk-rejected signals must be invalidated with a durable reason and an explicit Persian invalidation notification. Delivery retries must not restore validity.
- Stable signal identity, duplicate suppression, and idempotent signal lifecycle transitions are mandatory. The product creates no execution intent.
- Every signal is analytical-only and must never become executable by inference.

## 5. Signal-only safety and risk analysis

- The runtime has no live execution mode, order-write command, automatic position mutation, or account-mutating control.
- Signal eligibility depends on fresh/valid market data, supported Futures instrument semantics, deterministic strategy rules, and valid risk-estimate inputs. Unknown or contradictory critical data means no signal or an explicitly non-executable analytical result.
- Risk calculations may report reference entry, stop-loss, targets, costs, risk/reward, and suggested size only when assumptions and instrument metadata are explicit. These are advisory and must never authorize an order.
- Signal count is a ceiling, never a quota. No valid setup means no signal.
- Duplicate suppression and idempotent signal lifecycle transitions remain mandatory; these protect signal publication and status, not order execution.
- Backtest, walk-forward, out-of-sample, and Paper Trading workflows must not call live order-write APIs or mutate a real account.
- Health/status must report market-data freshness, analysis readiness, signal pipeline health, audit persistence, and notification state. It must not imply that live execution is available.
- Emergency controls may pause signal generation or notifications as explicitly defined, but must never close or mutate a real position.

## 6. Market-data access and credential boundary

- The signal-only runtime must not request, store, or accept exchange API credentials with order-write, transfer, or withdrawal permissions.
- Prefer public market-data endpoints. If a provider requires credentials for market data, use read-only least-privilege credentials, store secrets securely, redact them from logs, and support rotation/revocation.
- No user trading account, private balance, position, or order access is required for the signal-only product unless a separately approved read-only requirement explicitly adds it.
- No exchange-specific implementation may guess target providers, endpoints, permission models, symbols, contract filters, tick sizes, lot steps, or leverage limits.


### 6.1 CRYPTO Futures exchange shortlist — 15 venues

This shortlist records a proposed set of 15 CRYPTO Futures read-only market-data providers. It does **not** authorize live trading; all integrations must be strictly read-only. The list preserves recorded preferences but is not proof of support or availability.

1. **KuCoin Futures** — initial priority.
2. **Gate.io Futures** — initial priority.
3. **Bitget Futures** — initial priority.
4. **HTX Futures** — initial priority.
5. **MEXC Futures** — included with explicit elevated validation priority because the owner flagged instability; do not assume reliability.
6. **LBank Futures** — initial list.
7. **KCEX Futures** — initial list.
8. **CoinEx Futures** — initial list.
9. **OKX Derivatives** — added to reach the requested count.
10. **Bybit Derivatives** — added to reach the requested count.
11. **BingX Futures** — added to reach the requested count.
12. **Phemex Derivatives** — added to reach the requested count.
13. **Kraken Derivatives/Futures** — added to reach the requested count; product and regional eligibility must be checked.
14. **WhiteBIT Futures** — added to reach the requested count.
15. **Deribit Futures** — added to reach the requested count; product coverage is specialized and must not be assumed equivalent to broad altcoin venues.

**Excluded or separate items**
- **Binance:** explicitly blocked by the owner's stated operating constraint. Keep disabled in configuration and tests; do not connect or use it as a fallback. This is a user-supplied operational constraint, not an independently verified claim about global reachability.
- **CoinGecko:** price/market-data provider only, not one of the 15 exchanges. Any price use must be explicitly labeled and must not silently substitute Spot/reference prices for a Futures contract price.
- No unlisted venue may be added as an automatic fallback.

**Required per-venue acceptance gates before considering an adapter supported**
- Verify official API documentation and current availability of the exact Futures products; distinguish Linear, Inverse, dated futures, and perpetual swaps rather than treating them as interchangeable.
- Verify public/read-only access, rate limits, timestamps, symbol mapping, contract multiplier, settlement/quote currency, tick size, quantity step, funding/mark/index semantics, and error/retry behavior from authoritative sources.
- Normalize units and timestamps; reject stale, malformed, contradictory, unsupported, or ambiguous market data (fail closed).
- Add deterministic contract tests, malformed-payload tests, stale-data tests, rate-limit/outage tests, symbol/contract mapping tests, and parity tests against documented examples.
- Keep regional/legal eligibility as a deployment-time constraint; do not infer access merely because an API endpoint exists.
- Do not claim an adapter is implemented or production-ready until its code, tests, CI, and exact-head evidence pass. No private account, order-write, transfer, or withdrawal permission is allowed in this signal-only product.

## 7. Telegram operations menu

The Telegram interface is for signal delivery and signal-system operations only; it is not a trading control plane.

Allowed menu groups:
1. **Signals:** candidates, entry references, stop-loss/targets, risk/reward, validity, renewal count, status, invalidation reason, and unique signal ID.
2. **Markets:** independent CRYPTO/FOREX/GOLD Futures analysis and signal-notification preferences.
3. **Strategy & validation:** active strategy version, analysis timeframe, backtest/Paper Trading reports, and clearly labeled validation status.
4. **Health & operations:** market-data freshness, analysis readiness, signal pipeline, audit/notification health, incidents, and read-only maintenance status.
5. **Reports & help:** signal outcomes, estimated/realized evaluation metrics where evidenced, fees/funding assumptions, and user guidance.

Forbidden:
- Global or per-market **trading execution ON** controls.
- User trading-account management, API order-write key registration, capital allocation, leverage changes, order cancel/close, and position mutation.
- One-tap destructive actions or arbitrary shell/Python/SQL/URL/API commands.
- Any callback, retry, notification, restart, or signal status that can cause live order side effects.

Menu actions must be typed allow-listed signal/analysis operations. Bind sensitive callbacks to actor, target, state version, and expiry; rate-limit and reject replayed/duplicate/out-of-order callbacks. Persist and audit control changes. Persian remains the initial language requirement.

## 8. Signal risk estimates — no account allocation or trading controls

- Do not manage or allocate real exchange capital. Do not read private balances or automatically change leverage.
- Suggested position size, when requested, must be calculated only from an explicitly supplied reference capital/risk budget and explicit instrument semantics; label all assumptions and outputs as advisory.
- Do not carry forward proposed minimum account balance, allocation percentages, aggregate open-order risk, or daily trading-loss pause as live product controls. Those are execution/account-management policies and are out of scope for the signal-only target.
- Fees, funding, and slippage may be included as clearly labeled estimates when defensible inputs exist; unknown critical assumptions must be surfaced rather than fabricated.
- No risk metric or strategy performance result guarantees a maximum realized loss or profitability.

## 9. Other signal-only operational requirements

- Signal and operational notifications through Telegram and email; notifications are downstream outputs only.
- Explicit signal invalidation notices, delivery retry records, and stable signal identity.
- Health status reflects market-data freshness, strategy/analysis readiness, signal lifecycle integrity, audit persistence, and notification delivery—not process liveness alone and not live-execution readiness.
- Backtest → walk-forward validation → out-of-sample evaluation → Paper Trading are required validation stages before any performance claim. Metrics must be reproducible; no fabricated win-rate/profitability claims.
- Backtesting and Paper Trading must be isolated from live order submission and real-account mutation.
- Windows and Linux support must not weaken security, data integrity, or signal safety.
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
- each shortlisted exchange's supported Futures products, Linear/Inverse support, API permission model, account/margin modes, authoritative filters, regional availability, and test environments;
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
