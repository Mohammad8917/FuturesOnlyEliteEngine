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

## Approval record

- Safe Entry and Risky Entry: requested by owner.
- Hybrid mode (Option C): selected by owner on 2026-10-09.
- Automated execution must select one candidate, never both.
- Exact Hybrid selection criteria and cross-contract compatibility must be validated before executable implementation.
