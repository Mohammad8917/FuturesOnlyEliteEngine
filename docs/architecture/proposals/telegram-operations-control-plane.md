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
5. **Audit / recent control changes** (read-only view, bounded and privacy-safe);
6. **Per-user trading controls** (admin can enable/disable an individual user's automation independently of global and market switches);
7. **Account & capital** (verified Futures balance in USD-equivalent, available margin, configured allocation, used/reserved allocation, current exposure, and last successful refresh time);
8. **Risk & limits** (read-only current per-trade/aggregate risk usage, daily-loss status, margin headroom, and reasons trading is blocked);
9. **Credentials & account connection** (masked status only; admin-only register/verify/rotate/revoke workflow; never display a secret);
10. **Positions & orders** (read-only view and reconciliation status; any cancel/close action must be a separate explicitly authorized and confirmed operation);
11. **Emergency pause** (global, per-market, and per-user pause; pausing blocks new automated intents and does not silently liquidate positions);
12. **Allocation settings** (admin-authorized per-user allocation percentage and a clear preview of the resulting cap before saving).

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

- The owner can adjust active-user capacity from the Telegram menu; the hard system maximum is 1,000 active users. If capacity is 2, a third active user is rejected; if capacity is 1,000, user 1,001 is rejected. Capacity changes never remove existing users automatically; reducing capacity below the current active count is rejected until the owner explicitly removes users.
- Add/remove operations must be authenticated, authorized, confirmed for destructive changes, audited, and idempotent.
- Use stable Telegram numeric user IDs as identity; usernames/display names are mutable and must not be identity keys.
- Unknown users cannot change switches or invoke trading controls.
- Removing/revoking a user takes effect for future control requests and new automated intents associated with that user's authorization. It must not silently cancel or liquidate positions already open.
- A failed persistence write must not report success or leave an ambiguous authorization state.
- Users provide their own exchange API credentials to the owner/admin, who manually registers them. **Do not collect API key/secret/passphrase in ordinary Telegram chat or callback data.** The Telegram menu should initiate an admin-only registration workflow, but the actual secret entry must occur in a dedicated access-controlled secret-entry interface/vault (or another separately approved secure channel) where chat history cannot retain the secret. The admin must verify account ownership and account label before binding the credential reference to the correct user. Encrypt secrets at rest, restrict access, redact logs/traces, and never display/retrieve secrets in plaintext through Telegram. Each user's credentials and exchange account context must be isolated. Require least-privilege API keys; withdrawal and transfer permissions must be absent. Where supported, restrict API keys to the production server's fixed IP. Exact permission checks depend on the exchanges the owner later selects.
- Initial authorization policy is owner-only administration. Ordinary users may view only their own account status and cannot change global/market switches, user capacity, credentials, or risk ceilings. Additional administrators require an explicit owner-granted role and audited approval.

### 3.4 Per-user exchange account and capital allocation

- Every user trades only through that user's own explicitly linked exchange account and API credentials; no shared owner account and no cross-user credential reuse.
- Each user has a separate account context, credential reference, available-balance/equity snapshot, allocation policy, positions/orders view, risk limits, and audit trail. One user's failure or revocation must not leak into or mutate another user's account.
- The bot must never assume the entire account balance is available for trading. Each user must have an explicit allocation percentage and the resulting permitted allocation must remain strictly below 100% of the chosen funds basis. If no allocation is configured, the balance basis is unknown/stale, or the calculated allocation is invalid, that user's automated trading remains disabled.
- Allocation percentage is a capital-allocation ceiling, not a promise to invest that percentage on every trade and not a substitute for per-trade risk limits, margin checks, position limits, or the Risk gate.
- Selected capital policy: verified available balance of the user's chosen Futures margin account is the allocation basis; default allocation is 10%, with a hard application ceiling of 50%. This caps the bot's allocated capital budget, not notional exposure. Balance freshness, equity, unrealized PnL, used/maintenance margin, pending-order reservations, and risk are checked separately; stale or uncertain data blocks new entries.
- Each user's API credential must use least privilege and must not allow withdrawals/transfers. Where supported, users should restrict keys by IP and other exchange-provided controls. Exchange-specific key permissions and account-mode verification remain blocked until the owner names the exchanges.
- Credential onboarding must not echo or persist secrets in Telegram chat history, callback payloads, application logs, exception traces, or audit events. Use a secure entry mechanism, encrypt secrets at rest, restrict access, support revocation/rotation, and report only masked credential status.
- A credential or account that is invalid, revoked, permission-inadequate, stale, or ambiguous fails closed for that user's new automated execution only; other users may continue only if their independent health and gates pass.

#### Capital and risk policy defaults (owner-selected proposal)

To resolve the general capital-policy questions conservatively without inventing exchange-specific rules, the proposed defaults are:
- **Eligibility floor:** a user is not activated for automated trading unless the verified available Futures-margin balance is at least **USD 20 equivalent**. A balance below USD 20 equivalent is ineligible; an unknown, stale, unconvertible, or unverified balance is also ineligible. This is a system eligibility floor, not a claim that every exchange permits an order at USD 20.
- **Allocation basis:** use the verified available balance of the selected Futures account/margin wallet, denominated in a canonical valuation currency (USD-equivalent only when a trustworthy conversion price is available). Do not use the full account-wide equity or unrelated Spot balances as implicitly available Futures capital. Risk checks must separately account for equity, unrealized PnL, margin used, maintenance margin, and open-order reservations.
- **Allocation defaults:** default per-user allocation is **10%** of the verified eligible basis; administrator may configure a user-specific value, but the hard application ceiling is **50%**. Values must be greater than 0% and no greater than 50%; missing or invalid configuration blocks that user's new automated trades. These are policy caps, not a promise to deploy the full allocation.
- **Exposure is separate:** allocation caps the capital budget assigned to this bot for the user; it is not the same as notional exposure. Notional exposure, leverage, margin, per-instrument limits, per-trade risk, and aggregate open risk require separate controls. No leverage value may be inferred from the allocation.
- **Conservative risk defaults:** proposed initial maximum planned loss per trade is 0.5% of the user's allocated capital; aggregate planned loss across open positions and pending orders is capped at 2% of allocated capital; reaching a 3% daily loss from the configured daily baseline pauses new automated entries for that user until an authorized reset at the next configured risk period. These limits must be computed from verified stop-loss/risk semantics, include fees/funding/slippage buffers where estimable, and fail closed if a valid loss bound cannot be computed. They do not guarantee a maximum realized loss in gaps, outages, or liquidation events.
- **Minimum order rules:** each order must satisfy the selected exchange's current Futures instrument filters, including minimum notional/quantity, tick size, lot step, contract multiplier, and account/margin mode. Some exchanges/instruments may enforce minimums around USD 5 or USD 10, but those are examples only: never hardcode them as universal rules. Read and validate authoritative exchange metadata once the owner selects the exchanges; if metadata is unavailable or stale, reject the order. The USD 20 user eligibility floor never overrides an exchange's minimum-order rule.
- **No implicit full-balance trade:** the order-sizing and reservation path must prove that required margin plus fees/buffers fits within the user's bot allocation and exchange-available funds. If not, reject; never automatically raise allocation, leverage, or order size to force an order through.
- **Capacity and invitations:** capacity counts active, approved users only. Pending invitations do not trade and do not consume active capacity until approved/activated; activation must re-check capacity and the USD 20 eligibility floor.
- **Roles and language:** initial language is Persian. Only the owner role may change global automation, market toggles, user capacity, user registration/credential records, and global policy ceilings. Ordinary users may view only their own account status and request changes that require owner approval; they cannot toggle global controls or modify risk ceilings. Additional administrator roles require a separate explicit grant by the owner.
- **Switch confirmations:** global ON requires a second confirmation showing active markets, number of eligible users, health readiness, and the fact that real orders may be submitted. Global OFF is immediate after server-side authorization. Per-market/per-user ON also requires confirmation and readiness checks; OFF/pause is immediate. No switch bypasses any risk or execution gate.

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
- allocation boundaries (unset, zero, default 10%, maximum 50%, above 50%, 100%), USD 20 eligibility boundary (below, exactly at, above), stale/unconvertible balance, and allocation recalculation;
- risk boundaries (per-trade 0.5%, aggregate open risk 2%, daily loss pause at 3%), concurrent-order reservation, fees/funding/slippage buffers, and fail-closed behavior when risk cannot be bounded;
- exchange instrument-filter validation for minimum notional/quantity, tick, lot step, contract multiplier, and stale/missing metadata; prove USD 20 eligibility does not bypass exchange-specific order minimums;
- admin manual credential registration through the secure vault path, account-owner confirmation, permission verification, rotation/revocation, and proof secrets never enter Telegram messages, callbacks, logs, or audit records;
- prove that no order can consume the full account funds or exceed the explicit per-user allocation ceiling, while all separate Risk gates remain mandatory;
- callback replay, duplicate delivery, concurrency, stale callback, and unauthorized actor cases;
- immediate prevention of new intents after disable/revoke, without implicit position liquidation or order cancellation;
- health-state aggregation, stale/unknown components, per-market data freshness, and no test-order side effects;
- audit event schema, UTC timestamps, idempotency, and secret/privacy redaction;
- Windows/Linux behavior and full CI/same-SHA evidence under the existing quality floors.

Tests must not be skipped/xfail'd, thresholds lowered, or gates bypassed.

## 8. Resolved policy decisions and remaining exchange-specific dependency

The following conservative defaults are selected for this proposal:
1. **Capital basis:** verified available balance in the user's selected Futures margin account, converted to USD-equivalent only with a trustworthy, fresh conversion source; unrelated Spot balances are excluded.
2. **Minimum eligibility balance:** at least USD 20 equivalent of verified available Futures-margin balance. Below USD 20, stale/unknown balances, or failed conversion means no automated activation/trading for that user.
3. **Allocation:** default 10% per user; owner may configure individually; hard ceiling 50%; values above 50%, 100%, zero, missing, or invalid are rejected. Allocation budget and notional exposure are distinct.
4. **Risk defaults:** planned risk per trade ≤0.5% of allocated capital; total planned open risk including pending orders ≤2%; a 3% daily loss from the configured baseline pauses new entries for that user. These limits do not guarantee maximum realized loss under gaps, liquidation, or infrastructure failure.
5. **Capacity:** active approved users only; pending invitations do not consume capacity until activation, which re-checks capacity and eligibility.
6. **Roles:** owner-only administrator initially; ordinary users cannot change global/market switches, capacity, credentials, or risk ceilings.
7. **Confirmation:** global ON and per-market/per-user ON require explicit confirmation and a readiness summary; OFF/pause takes effect immediately after authorization.
8. **Menu language:** Persian initially.
9. **Credential entry:** user supplies their own credentials to the owner/admin, who manually registers them through a dedicated secure secret-entry interface/vault initiated by the Telegram admin menu. Secrets must not be sent/stored in ordinary Telegram chat or callback data.
10. **Minimum order:** use current authoritative filters for each selected exchange and instrument; USD 5/USD 10 are not universal constants and must not be hardcoded. Every order must independently satisfy exchange minimum notional/quantity and all Futures contract filters.

Still unresolved because it cannot safely be inferred: **the exchange list and each exchange's actual Futures API permission model, instrument metadata, minimums, account mode, and supported market/contract types.** Implementation of exchange-specific validation remains paused until the owner provides the list. No specific exchange or instrument rules may be guessed.

## 9. Migration and rollback

Implement only after Phase 1 exit criteria and governance approvals are evidenced. Introduce the control-state contract and tests first, then application orchestration, then the Telegram adapter and health reporting, and only later connect approved exchange adapters. Rollback must default global automation to OFF, preserve authorization/audit records, and never auto-liquidate positions or cancel orders as a side effect.

## 10. Explicit approval / reconfirmation

**Pending.** This is a proposed requirements and impact document, not approval to change architecture or implement production trading controls. The exchange list and exchange-specific metadata/permission behavior must be supplied before exchange-specific implementation; all selected policy defaults still require the project's formal governance/Phase 1 exit gates before production implementation.