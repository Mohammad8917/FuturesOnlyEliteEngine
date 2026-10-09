# Proposal — Telegram Operations Control Plane

**Status:** PROPOSED — not approved, not implemented  
**Date:** 2026-10-10  
**Proposer:** Project owner requirements captured from the current discussion  
**Scope:** FuturesOnlyEliteEngine Telegram operations menu for automated-trading controls, market selection, authorized-user management, and bot health visibility.

## 1. Problem

The owner requires all routine operational controls to be available from the Telegram menu, without requiring shell or source-code edits for these actions:
- enable or disable automated trading globally;
- independently enable or disable CRYPTO Futures, FOREX Futures, and GOLD Futures, allowing any non-empty combination (one, two, or all three markets);
- add and remove people authorized for automated trading, with a hard maximum of 100 active authorized users;
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
   - show current count as `N / 100`;
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

### 3.3 Authorized-user management (maximum 100)

- Hard limit: at most 100 active authorized users; the 101st addition is rejected without partial state changes.
- Add/remove operations must be authenticated, authorized, confirmed for destructive changes, audited, and idempotent.
- Use stable Telegram numeric user IDs as identity; usernames/display names are mutable and must not be identity keys.
- Unknown users cannot change switches or invoke trading controls.
- Removing/revoking a user takes effect for future control requests and new automated intents associated with that user's authorization. It must not silently cancel or liquidate positions already open.
- A failed persistence write must not report success or leave an ambiguous authorization state.
- Never accept exchange API keys, passwords, or secrets through ordinary Telegram menu messages; never display secrets in status or audit output.
- Authorization policy must distinguish the owner/admin who can change global controls and the allowed users who may use approved trading functions. The precise role model is an unresolved decision and must be explicitly approved before implementation.

### 3.4 Bot status and health

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

Telegram controls create a privileged operational control plane over automated Futures execution. A compromised Telegram account, authorization race, stale toggle state, replayed callback, duplicate update, or failed persistence operation could enable unauthorized trading or misreport that trading is disabled.

Mitigations required before implementation:
- verify actor identity and role on every callback at the server side; hiding menu buttons is not authorization;
- persist control changes atomically and audit actor, action, old/new state, UTC timestamp, outcome, and correlation/idempotency key;
- make repeated/replayed callbacks idempotent and reject stale or malformed callback data;
- use explicit confirmation for enabling global automation and for removing users;
- fail closed on unreadable/ambiguous state and never infer ON from defaults;
- preserve Risk, Execution, reconciliation, and audit gates; Telegram cannot call exchange APIs directly;
- do not claim health or readiness when required checks are unknown or stale;
- rate-limit and bound user-management/control operations; never log secrets or unnecessary personal data.

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
- user-capacity boundary (0, 1, 100, 101), duplicate add, revoke, and persistence failure;
- callback replay, duplicate delivery, concurrency, stale callback, and unauthorized actor cases;
- immediate prevention of new intents after disable/revoke, without implicit position liquidation or order cancellation;
- health-state aggregation, stale/unknown components, per-market data freshness, and no test-order side effects;
- audit event schema, UTC timestamps, idempotency, and secret/privacy redaction;
- Windows/Linux behavior and full CI/same-SHA evidence under the existing quality floors.

Tests must not be skipped/xfail'd, thresholds lowered, or gates bypassed.

## 8. Unresolved decisions — do not guess

1. Which Futures exchanges will be supported? Exchange-specific connectivity/readiness cannot be completed until the owner names them.
2. What is the exact authorization role model: owner-only administrator, additional administrators, and what ordinary authorized users may do?
3. Does the 100-user cap count only active authorized users, or also pending invitations? Proposed default: active authorized users only, with pending invitations not yet permitted to trade.
4. Should users be able to trade independently under their own exchange accounts, or are they authorized users of one owner-controlled account? This affects account isolation and must be decided before any multi-user execution design.
5. What is the required confirmation flow for enabling global automation and for disabling it? Proposed safe default: confirm enable; allow disable immediately after server-side authorization.
6. Which language(s) should the menu and health messages support? Proposed initial default: Persian.

No exchange, account model, credentials workflow, trading permissions, or market-specific metadata may be inferred.

## 9. Migration and rollback

Implement only after Phase 1 exit criteria and governance approvals are evidenced. Introduce the control-state contract and tests first, then application orchestration, then the Telegram adapter and health reporting, and only later connect approved exchange adapters. Rollback must default global automation to OFF, preserve authorization/audit records, and never auto-liquidate positions or cancel orders as a side effect.

## 10. Explicit approval / reconfirmation

**Pending.** This is a proposed requirements and impact document, not approval to change architecture or implement production trading controls. Owner reconfirmation and resolution of the required open decisions are needed before implementation.