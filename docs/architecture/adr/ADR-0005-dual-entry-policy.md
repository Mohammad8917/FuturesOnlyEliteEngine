# ADR-0005: Dual Entry Types and Hybrid Selection

- Status: OWNER-SELECTED POLICY; implementation requires contract impact analysis and tests.
- Date: 2026-10-09
- Owner decision: Hybrid (Option C), selected by repository owner.

## Decision

Signals may present two candidate entry prices: Safe Entry (conservative, near a validated support/resistance or setup level; may remain unfilled) and Risky Entry (aggressive, at or near the current validated market price; higher interaction probability does not guarantee a fill or profit).

The automated engine is configured for Hybrid mode: choose exactly one candidate based on validated market conditions. It must never submit both candidates from the same signal. Hybrid selection criteria are not defined here; until a deterministic, tested selection contract exists, ambiguous conditions must fail closed and no executable entry may be selected. Safe-only mode always selects Safe Entry; Risky-only mode always selects Risky Entry.

## Persian signal fields

Every human-facing signal must use Persian labels and include:
- نماد
- بازار: بازار رمزارز / بازار فارکس / بازار طلا (internal categories: CRYPTO / FOREX / GOLD)
- جهت: خرید / فروش
- تاریخ و ساعت صدور (canonical UTC timestamp, rendered with explicit timezone)
- ورود امن
- ورود با ریسک
- نوع ورود انتخاب‌شده: ورود امن / ورود با ریسک / هنوز انتخاب نشده
- حد ضرر
- حد سود
- اهرم
- مهلت اعتبار: ۲۰ دقیقه از زمان صدور اصلی
- شناسه یکتا
- نوع سیگنال: تحلیلی / اجرایی
- وضعیت و توضیح در صورت وجود

An executable signal must have one concrete selected entry type and selected price. An analytical or unselected signal must not be executable by inference. The example below is illustrative only:

```text
نماد: BTC/USDT — جهت: خرید
بازار: بازار رمزارز
تاریخ و ساعت: ۲۰۲۶-۱۰-۰۹ ۲۳:۱۵:۰۰ (UTC)

🟢 ورود امن: ۶۴٬۸۰۰ (در صورت برگشت قیمت)
🟡 ورود با ریسک: ۶۵٬۰۵۰ (نزدیک قیمت فعلی)
🎯 نوع ورود انتخاب‌شده: ورود امن یا ورود با ریسک (در پیام واقعی فقط یکی)

حد ضرر: ۶۴٬۴۰۰
حد سود: ۶۶٬۲۰۰
اهرم: ۵ برابر
نوع سیگنال: اجرایی
مهلت اعتبار: ۲۰ دقیقه تا ۲۳:۳۵:۰۰ (UTC)
شناسه یکتا: <شناسه-یکتا>
— محمد
```

## Entry-zone monitoring, reassessment, and bounded renewal

If price has not reached the selected entry zone by the current expiry, do not immediately assume the setup is worthless and do not execute outside the zone. Reassess whether the trade remains valid using fresh market data and the already-approved, deterministic strategy/risk criteria.

- If the setup remains valid, all required data are fresh, and the Risk Gate still passes, the system may renew the signal for one additional 20-minute validity window.
- At most **three renewals** are allowed for one signal. The initial 20-minute window plus three approved renewals means a maximum total lifetime of 80 minutes from original issuance.
- Each renewal must be an explicit, auditable lifecycle transition, increment a renewal counter (0–3), record reassessment time, new expiry, market-data timestamp, decision, and reason, and preserve the original signal ID. A resend or duplicate delivery is not a renewal and must never extend expiry.
- If the setup is no longer worthwhile/valid, required criteria cannot be evaluated, data are stale or contradictory, or Risk rejects it, invalidate/cancel it immediately; do not consume a renewal to conceal a failed validation.
- If price still has not reached the entry zone when the third renewal expires, invalidate the signal with a clear reason such as **«باطل شد — پس از ۳ تمدید، قیمت به محدوده ورود نرسید»**. No fourth renewal is permitted.
- Renewal does not authorize chasing the market, silently moving the entry zone, changing stop-loss/take-profit/leverage, or placing an order outside the selected entry. Any material setup/price-level change requires a new signal ID and a fresh validation lifecycle.
- A renewed signal remains non-executable until its selected entry conditions are actually satisfied and all freshness, schema, instrument, and Risk Gate checks pass. Analytical signals remain non-executable.
- The 20-minute renewal interval and three-renewal cap are the owner-selected policy defaults. Any change requires explicit owner approval and corresponding contract/test updates.

Required tests: no renewal on resend/duplicate; renewals only after successful fresh reassessment; exact 20-minute expiry boundaries; renewal counter bounds; immediate invalidation on failed reassessment/stale data/Risk rejection; final invalidation after the third renewal; no fourth renewal; stable ID and audit history; no entry-zone drift or execution outside the selected zone; concurrent renewal idempotency.

## Safety and implementation requirements

- Validate freshness, timestamps, supported instrument, prices, leverage, and the Risk Gate independently of strategy selection.
- A signal expires exactly 20 minutes after its original issuance; resending it must not reset expiry. Expired signals cannot initiate orders.
- Carry the unique signal ID into audit and execution idempotency; repeated delivery must not create duplicate orders.
- Notifications are informational and cannot authorize execution. Strategy/analysis does not submit orders; execution proceeds only after Risk approval.
- The selector records the selected entry type, selected price, and policy version. Missing, stale, contradictory, or ambiguous inputs fail closed.
- Do not invent market thresholds, exchange metadata, tick sizes, or instrument support. When target-exchange selection or exchange-specific specifications are required, stop and ask the owner which exchange's Futures instrument/specification list to use.
- Preserve Futures-only CRYPTO/FOREX/GOLD scope, Linear/Inverse separation, all existing tests, gates, and same-SHA verification. Do not skip tests, weaken assertions, or reduce thresholds.

## Affected contracts and tests

Review signal schema, strategy/application ownership, market-data freshness, clock/timezone, Risk Gate, execution intent, idempotency/reconciliation, audit ports, and Persian notification formatting. Add tests for each Hybrid branch, exactly-one selection, ambiguous conditions failing closed, required Persian fields, expiry boundary, resends, duplicate/concurrent attempts, analytical-signal non-executability, stale data, and Risk rejection.

## Contract impact analysis — repository baseline

Inspection baseline: `main` tree SHA `87af92e1bcf2adad555e4c9187d3b2b5c613e7f2` (2026-10-09). This is a repository-tree inspection, not a claim that the feature is implemented or that CI is green.

### Existing architecture evidence

- The current `main` tree contains `contracts/futures/`, its contract tests, and authoritative architecture/governance documents.
- The inspected `main` tree does not currently contain dedicated `application/futures/`, strategy/analysis, risk, execution, market-data, infrastructure exchange-adapter, or notification/Telegram implementation paths. Therefore, ADR-0005 must not pretend existing signal lifecycle or renewal services are available.
- `docs/architecture/futures-responsibility-map.md` assigns pure Futures semantics to domain, orchestration to application, policy decisions to risk, gated order lifecycle/reconciliation/audit to execution, external transport/mapping to infrastructure, and signal analysis to strategy/analysis. Notifications are outputs only.
- `docs/architecture/dependency-rules.md` prohibits strategy from submitting orders, prevents infrastructure dependencies from entering domain, and blocks implementation where a responsibility lacks one primary owner.
- `docs/architecture/architecture-contract.md` requires Telegram/email notifications to remain non-authoritative and requires exchange/environment/account-specific values to come from validated configuration rather than hard-coded defaults.

### Required implementation sequence before exchange-specific integration

1. Define a transport-neutral signal/lifecycle contract: original UTC issuance time, immutable signal ID, selected entry type and entry zone, initial expiry, renewal count, status/reason, and audit correlation. Keep Persian formatting in the notification/presentation boundary, not in financial-domain decisions.
2. Define deterministic reassessment and lifecycle transitions in the appropriate application/strategy contracts. Reassessment must use fresh normalized market facts and explicit approved criteria; missing/stale/contradictory facts fail closed.
3. Define risk-decision and execution-intent boundaries separately. Strategy may recommend/select one candidate but cannot submit an order; only a valid entry condition plus a fresh positive Risk decision can produce an execution intent.
4. Specify idempotent renewal and expiry transitions: resend is not renewal; renewal count is bounded at three; all renewals retain the original ID; the final expired renewal invalidates the signal; concurrent attempts cannot renew twice.
5. Add contract, state-transition, concurrency/idempotency, expiry-boundary, stale-data, Risk rejection, notification rendering, and architecture-boundary tests. Preserve existing tests and all gate thresholds.
6. Only when implementing instrument resolution, exchange market-data adapters, tick/lot/contract metadata, supported product mapping, or order transport may exchange-specific assumptions be introduced. At that boundary, implementation is paused until the owner supplies the target exchange name(s) and authoritative Futures instrument/specification details. No exchange, symbol support, tick size, leverage limit, or contract behavior may be guessed.

### Impact-analysis conclusion

The policy is documented, but the current `main` repository baseline has no implementation paths for the signal lifecycle and orchestration responsibilities listed above. Proceed with transport-neutral contracts and tests only where they can be made consistent with the authoritative architecture. Do not create an exchange adapter, assume a provider, or claim executable/production readiness before the owner supplies exchange selection and specifications. This impact analysis does not amend any frozen source-of-truth document and does not substitute for same-SHA CI evidence.

## Approval record

- Safe Entry and Risky Entry: requested by owner.
- Hybrid mode (Option C): selected by owner on 2026-10-09.
- Automated execution must select one candidate, never both.
- Exact Hybrid selection criteria and cross-contract compatibility must be validated before executable implementation.
