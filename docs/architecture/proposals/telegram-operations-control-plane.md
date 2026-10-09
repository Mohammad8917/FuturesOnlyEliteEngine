# Proposal — Telegram Operations Control Plane

**Status:** PROPOSED — not approved, not implemented  
**Date:** 2026-10-10  
**Proposer:** Project owner requirements captured from the current discussion  
**Scope:** FuturesOnlyEliteEngine Telegram operations menu for automated-trading controls, market selection, authorized-user management, and bot health visibility.

## 1. Problem

The owner requires all routine operational controls to be available from the Telegram menu, without requiring shell or source-code edits for these actions:
- enable or disable automated trading globally;
- independently enable or disable CRYPTO Futures, FOREX Futures, and GOLD Futures, allowing any non-empty combination (one, two, or all three markets);
- add and remove users from the Telegram menu, with an owner-configurable active-user capacity and a hard system maximum of 1,000 active users (for example, capacity can be set to 2, 50, or 1,000);
- connect each user's own exchange API credentials and isolate each user's account, balance, allocation, and execution;
- configure a per-user allocation percentage so only a bounded portion of that user's funds is available to the bot, never silently allocating 100% of funds;
- check whether the bot is running and whether its critical components are healthy.

This document records requirements only. It does not claim that Telegram, automated execution, user management, or health monitoring already exists.

## 2. Current architecture and baseline

The repository's documented architecture separates domain semantics, application orchestration, risk policy, execution lifecycle, infrastructure/transport, and informational notifications. Telegram must remain an adapter/control interface; it must not own financial calculations or bypass risk/execution gates.

The inspected `main` baseline is commit `87af92e1bcf2adad555e4c9187d3b2b5c613e7f2`. The existing tree inspected for the earlier architecture impact analysis did not contain dedicated production implementations for application orchestration, risk, execution, exchange adapters, or notification/Telegram. Their existence or operational readiness must not be assumed.

Phase 2+ production implementation remains blocked until the required Phase 1 and governance exit evidence is satisfied. This proposal does not authorize bypassing that gate.

## 3. Proposed behavior

### 3.1 Telegram menu

Provide a clear, localized menu with at least these entries:
1. **Automated trading: ON / OFF**
2. **Markets**
   - CRYPTO Futures: ON / OFF
   - FOREX Futures: ON / OFF
   - GOLD Futures: ON / OFF
3. **Authorized users**
   - list current authorized users (privacy-safe identifiers only);
   - add a user;
   - remove/revoke a user;
   - show current count and configured capacity, e.g. `N / capacity` (capacity adjustable in the menu, hard maximum 1,000);
   - set the active-user capacity from 1 through 1,000, never above 1,000;
4. **Bot status / Health**
5. **Audit / recent control changes** (read-only view, bounded and privacy-safe).

The market toggles are independent: any non-empty combination of the three markets may be selected. Spot is never an available market. Linear/Inverse contract handling remains governed by the existing Futures architecture and explicit instrument metadata.

### 3.2 Safe global and market switches

- Global automated trading defaults to OFF after first setup, restart with missing/invalid state, or uncertain recovery.
- A market being ON does not by itself enable execution: the global automated-trading switch must also be ON.
- Effective eligibility requires global ON, that market ON, a currently authorized actor/user, fresh valid data, a valid signal/intent, and all existing Risk and Execution gates to pass.
- Turning global automated trading OFF must block new automated execution intents immediately. The exact treatment of already-open positions and already-submitted orders must be specified separately; OFF must not silently imply liquidation or cancellation.
- Turning a market OFF blocks new automated intents for that market. It must not silently close positions or cancel existing orders.
- Any stale, contradictory, missing, or unreadable control state fails closed to no new automated execution.
- Enabling a switch must not override risk limits, exchange/account restrictions, instrument validation, reconciliation, or other mandatory gates.

### 3.3 Authorized-user management (configurable capacity, hard maximum 1,000)

- Hard limit: at most 100 active authorized users; the 101st addition is rejected without partial state changes.
- Add/remove operations must be authenticated, authorized, confirmed for destructive changes, audited, and idempotent.
- Use stable Telegram numeric user IDs as identity; usernames/display names are mutable and must not be identity keys.
- Unknown users cannot change switches or invoke trading controls.
- Removing/revoking a user takes effect for future control requests and new automated intents associated with that user's authorization. It must not silently cancel or liquidate positions already open.
- A failed persistence write must not report success or leave an ambiguous authorization state.
- Do not expose API keys in ordinary chat messages, status screens, logs, or audit output. The menu must use a dedicated secure credential-entry/onboarding flow with explicit account ownership confirmation; secrets must be encrypted at rest, access-restricted, redacted from logs, and never retrievable in plaintext through the bot. Each user's credentials and exchange account context must be isolated from every other user. Require least-privilege API keys; withdrawals/transfers must not be permitted by the trading bot. Exact exchange permission checks depend on the exchanges the owner later selects.
- Authorization policy must distinguish the owner/admin who can change global controls and the allowed users who may use approved trading functions. The precise role model is an unresolved decision and must be explicitly approved before implementation.

### 3.4 Per-user exchange account and capital allocation

- Every user trades only through that user's own explicitly linked exchange account and API credentials; no shared owner account and no cross-user credential reuse.
- Each user has a separate account context, credential reference, available-balance/equity snapshot, allocation policy, positions/orders view, risk limits, and audit trail. One user's failure or revocation must not leak into or mutate another user's account.
- The bot must never assume the entire account balance is available for trading. Each user must have an explicit allocation percentage and the resulting permitted allocation must remain strictly below 100% of the chosen funds basis. If no allocation is configured, the balance basis is unknown/stale, or the calculated allocation is invalid, that user's automated trading remains disabled.
- Allocation percentage is a capital-allocation ceiling, not a promise to invest that percentage on every trade and not a substitute for per-trade risk limits, margin checks, position limits, or the Risk gate.
- The exact funds basis (for example, available balance versus equity), allocation refresh/freshness rules, hard maximum allocation percentage, and whether the percentage caps total concurrent exposure or a capital pool must be explicitly decided before implementation. Do not guess these values.
- Each user's API credential must use least privilege and must not allow withdrawals/transfers. Where supported, users should restrict keys by IP and other exchange-provided controls. Exchange-specific key permissions and account-mode verification remain blocked until the owner names the exchanges.
- Credential onboarding must not echo or persist secrets in Telegram chat history, callback payloads, application logs, exception traces, or audit events. Use a secure entry mechanism, encrypt secrets at rest, restrict access, support revocation/rotation, and report only masked credential status.
- A credential or account that is invalid, revoked, permission-inadequate, stale, or ambiguous fails closed for that user's new automated execution only; other users may continue only if their independent health and gates pass.

### 3.5 Bot status and health

The status screen must distinguish at least:
- process/service liveness;
- Telegram adapter/polling or webhook health;
- configuration/control-state readability;
- market-data freshness per enabled market;
- exchange-adapter connectivity/readiness, once exchange(s) are explicitly selected;
- Risk and Execution gate readiness;
- reconciliation/audit persistence readiness;
- last successful health update and component-specific failure reason.

Display an overall status such as HEALTHY / DEGRADED / NOT READY, with component-level details. A running process or responsive Telegram bot alone must never be represented as proof that automated trading is safe or active. Unknown/stale health is NOT READY for new automated execution. Health checks must be read-only and must not submit test orders.

## 4. CRITICAL ARCHITECTURE WARNING

Telegram controls create a privileged operational control plane over automated Futures execution and multi-user exchange credentials. A compromised Telegram account, credential leakage, cross-user account mix-up, authorization race, stale toggle state, replayed callback, duplicate update, or failed persistence operation could enable unauthorized trading, expose account information, exceed a user's intended capital allocation, or misreport that trading is disabled.

Mitigations required before implementation:
- verify actor identity and role on every callback at the server side; hiding menu buttons is not authorization;
- persist control changes atomically and audit actor, action, old/new state, UTC timestamp, outcome, and correlation/idempotency key;
- make repeated/replayed callbacks idempotent and reject stale or malformed callback data;
- use explicit confirmation for enabling global automation and for removing users;
- fail closed on unreadable/ambiguous state and never infer ON from defaults;
- preserve Risk, Execution, reconciliation, and audit gates; Telegram cannot call exchange APIs directly;
- do not claim health or readiness when required checks are unknown or stale;
- rate-limit and bound user-management/control operations; never log secrets or unnecessary personal data;
- isolate credential vault references, account identifiers, balance snapshots, orders, positions, allocation, and audit records per user;
- enforce a configured allocation strictly below 100% of the selected funds basis and reject missing/unknown allocation state;
- require no-withdrawal API permissions and secure credential rotation/revocation;
- prevent one user's API credentials or account context from being used by any other user.

## 5. Alternatives considered

1. **Telegram-only operational control surface (proposed):** matches the owner's requirement; requires strict authorization, persistence, audit, and readiness safeguards.
2. **Environment/config-file-only controls:** rejected as the primary user workflow because the owner explicitly requires menu-based controls.
3. **Allow all Telegram users to control automation:** rejected as unsafe.
4. **Treat process liveness as trading readiness:** rejected because it can misrepresent stale data, disconnected exchanges, or blocked Risk/Execution components.

## 6. Affected invariants and contracts

Potentially affected:
- Futures-only product boundary; CRYPTO/FOREX/GOLD Futures only; no Spot path or fallback.
- Domain/application/risk/execution/infrastructure ownership and dependency direction.
- Fail-closed behavior and the mandatory Risk → Execution authorization path.
- Idempotency, duplicate suppression, auditability, and operational state recovery.
- Telegram notifications are not authority to bypass execution gates.
- Windows/Linux portability, Python 3.13, and no hardcoded secrets/configuration.

No existing invariant is changed by this proposal. If implementation requires changing an invariant or dependency boundary, a formal ADR and explicit owner reconfirmation are required first.

## 7. Affected contracts, dependencies, tests, and gates

Before implementation, define and test:
- control-state contract and safe startup/recovery behavior;
- independent market switches and the global switch's precedence;
- server-side actor authorization and role policy;
- configurable user-capacity boundaries (1, 2, 1,000, 1,001), count changes, reducing capacity below current active users, duplicate add, revoke, and persistence failure;
- per-user credential isolation, credential rotation/revocation, missing/invalid permissions, secret redaction, and no cross-account reads/writes;
- allocation boundaries (unset, zero, valid configured percentage, just below 100%, 100%, above 100%), stale balance, and allocation recalculation;
- prove that no order can consume the full account funds or exceed the explicit per-user allocation ceiling, while all separate Risk gates remain mandatory;
- callback replay, duplicate delivery, concurrency, stale callback, and unauthorized actor cases;
- immediate prevention of new intents after disable/revoke, without implicit position liquidation or order cancellation;
- health-state aggregation, stale/unknown components, per-market data freshness, and no test-order side effects;
- audit event schema, UTC timestamps, idempotency, and secret/privacy redaction;
- Windows/Linux behavior and full CI/same-SHA evidence under the existing quality floors.

Tests must not be skipped/xfail'd, thresholds lowered, or gates bypassed.

## 8. Unresolved decisions — do not guess

1. Which Futures exchanges will be supported? Exchange-specific connectivity, API permission validation, and account-mode verification remain blocked until the owner names them.
2. What is the exact authorization role model: owner-only administrator, additional administrators, and what ordinary authorized users may do?
3. Does configured capacity count only active authorized users, or also pending invitations? Proposed default: active users only; pending invitations cannot trade.
4. What is the capital-allocation basis (available balance or equity), the maximum percentage strictly below 100%, and does it cap a capital pool or total concurrent exposure? These values must be explicitly selected and must never default to the full balance.
5. What is the required confirmation flow for enabling global automation and for disabling it? Proposed safe default: confirm enable; allow disable immediately after server-side authorization.
6. Which language(s) should the menu and health messages support? Proposed initial default: Persian.

No exchange, account model, credentials workflow, trading permissions, or market-specific metadata may be inferred.

## 9. Migration and rollback

Implement only after Phase 1 exit criteria and governance approvals are evidenced. Introduce the control-state contract and tests first, then application orchestration, then the Telegram adapter and health reporting, and only later connect approved exchange adapters. Rollback must default global automation to OFF, preserve authorization/audit records, and never auto-liquidate positions or cancel orders as a side effect.

## 10. Explicit approval / reconfirmation

**Pending.** This is a proposed requirements and impact document, not approval to change architecture or implement production trading controls. Owner reconfirmation and resolution of the required open decisions are needed before implementation.