# ADR-0003: Explicit Boundary Rounding for Futures Financial Arithmetic

- **Status:** OWNER-APPROVED POLICY — implementation authorized for exchange-independent contracts; exchange-specific instrument metadata must remain configurable and implementation must pause for owner input when exchange selection is required.
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit
- **Decision authority:** Repository owner
- **Owner decision recorded:** 2026-10-09 — Option C and the four boundary contracts below.

## 1. Problem

Python `Decimal` arithmetic is governed by a context. Division and operations whose exact result exceeds the active precision can be rounded; Decimal alone does not make all arithmetic context-independent. This ADR defines the only approved rounding boundaries and prohibits implicit rounding elsewhere.

## 2. Global decision

1. Use `Decimal` with a controlled working context of **`prec=28`** for intermediate calculations. Do not rely on a caller's ambient mutable Decimal context.
2. Rounding is permitted only at the four boundaries specified in Section 3.
3. The boundary helpers must be separate and explicit: `round_pnl()`, `round_funding()`, `round_margin_ratio()`, and `round_liquidation_price()`.
4. Risk and Execution must fail closed on invalid, unsupported, ambiguous, out-of-policy, or unsafe values.
5. `float` and built-in `round()` are prohibited under `domain/futures/`. No financial arithmetic may convert through binary floating point.
6. Linear and Inverse Futures formulas and denominations remain distinct. This ADR does not authorize formula changes or mixing their units.
7. No other implicit rounding, quantization, truncation, or precision loss is permitted. `prec=28` is an intermediate working context, not permission to accept unnoticed `Inexact` results.

## 3. Approved boundary contracts

### 3.1 PnL — `round_pnl()`

- **Output scale:** CRYPTO = 8 decimal places; GOLD and FOREX = 2 decimal places.
- **Rounding mode:** `ROUND_DOWN` (toward zero).
- **Downstream use:** The rounded value is represented as `Decimal` at the approved scale and is the value passed to subsequent consumers.
- **Fail-closed:** Reject if `abs(PnL) > MAX_REASONABLE_PNL`; reject/raise if an `Inexact` condition occurs in the margin path. Do not invent a numeric `MAX_REASONABLE_PNL`; its policy value must come from an approved, configurable risk/instrument policy.
- **Configuration:** Asset-class scale defaults are as above, but the instrument/exchange policy must be able to override supported scales without changing code. Unsupported or missing configuration fails closed.

### 3.2 Funding Payment — `round_funding()`

- **Output scale:** 8 decimal places.
- **Rounding mode:** `ROUND_HALF_UP`.
- **Downstream use:** The rounded `Decimal` payment is the exact amount added to or deducted from wallet balance; do not recalculate it downstream at a different scale.
- **Fail-closed:** Reject if `abs(funding_rate) > MAX_FUNDING_RATE`; reject/raise if an `Inexact` condition is encountered in the balance path. Do not invent a numeric `MAX_FUNDING_RATE`; source it from approved, configurable policy.
- **Configuration:** Scale and allowed funding-rate bounds must be configurable per supported instrument/exchange policy. Missing or unsupported values fail closed.

### 3.3 Margin Ratio — `round_margin_ratio()`

- **Output scale:** 8 decimal places.
- **Rounding mode:** `ROUND_HALF_UP`.
- **Downstream use:** The rounded ratio is used only for comparisons with approved thresholds (including maintenance-margin and liquidation thresholds). It must never feed another arithmetic formula.
- **Fail-closed:** If `maintenance_margin_ratio < ratio < liquidation_ratio`, raise an explicit risk exception and stop Execution. Threshold ordering, equality boundaries, and the exact comparison semantics must be validated against the existing approved risk contract; do not silently reinterpret or reverse the owner-provided inequality.
- **Configuration:** Thresholds are explicit validated policy inputs, not hardcoded guesses. Missing, inconsistent, or unordered thresholds fail closed.

### 3.4 Liquidation Price — `round_liquidation_price()`

- **Output scale:** Quantize to the configured instrument tick size. Initial owner-provided examples only: CRYPTO often 0.01 or 0.1; GOLD 0.01. These are examples, not universal exchange rules. FOREX and any actual instrument-specific tick/price precision must come from the selected exchange/instrument specification.
- **Rounding mode:** LONG = `ROUND_DOWN`; SHORT = `ROUND_UP`, as the owner-selected conservative policy.
- **Downstream use:** The rounded `Decimal` is the final liquidation trigger price; no subsequent recalculation or rounding.
- **Fail-closed:** If the liquidation price has crossed the last price while the position is still reported as not liquidated, raise an explicit invariant/risk exception and stop Execution. Validate the relevant long/short comparison direction against the existing position-side contract without changing the owner-selected rounding modes.
- **Configuration:** Tick size and price precision must be validated, explicit, and configurable per instrument/exchange. Never hardcode one exchange's tick rules as universal defaults. **When implementation reaches selection or lookup of the target exchange, stop and ask the owner which exchange's instrument specification/list to use; do not guess or continue exchange-specific integration.**

## 4. Decimal context, exactness, and error behavior

- All four helpers must use explicit Decimal operations and an explicit rounding mode; they must not call built-in `round()` or convert through `float`.
- The working context is controlled at `prec=28` and must not inherit uncontrolled caller context.
- `Inexact`/`Rounded` signals must be handled intentionally. A helper may suppress the signal only for the expressly authorized final quantization at its named boundary; intermediate inexactness must not be silently accepted. Where the arithmetic path requires an inexact intermediate result that cannot be proven safe under the approved contract, fail closed until an approved exact/intermediate strategy is available.
- Decimal exception handling must be narrow and meaningful; do not catch broad exceptions and continue with an unsafe result.
- `MAX_REASONABLE_PNL`, `MAX_FUNDING_RATE`, tick size, thresholds, and any venue-specific precision must be validated configuration/policy values. Missing or invalid policy fails closed; do not invent constants.
- The policy requires an audit record for each rounding operation containing at least: boundary name, input, output, rounding mode, and precision/scale. Use an existing approved structured logging/audit port if one exists. Do not introduce direct I/O or an unapproved logging dependency into the domain layer; if no approved port exists, stop at that integration point and report the required architecture decision.

## 5. Non-negotiable constraints

- No binary floating-point conversion in critical financial calculations.
- No dependence on ambient mutable Decimal context for financial meaning.
- No implicit rounding, quantization, truncation, or precision loss outside the four approved boundaries.
- `float` and built-in `round()` are forbidden under `domain/futures/`.
- Invalid, unsupported, ambiguous, or unsafe critical results fail closed in Risk/Execution.
- Explicit units and denomination; no mixing of Linear and Inverse semantics.
- Existing G05 >= 98%, G08 >= 90%, all tests, and all other gate strengths remain unchanged.
- No tests skipped/xfail'ed, exclusions added, thresholds reduced, or gates bypassed.
- No production-readiness or Phase 2 authorization follows from this ADR.

## 6. Affected invariants and implementation surfaces

Audit and implementation scope includes:

- `domain/futures/contract_specification.py`
- `domain/futures/pnl.py`
- `domain/futures/liquidation.py`
- `domain/futures/settlement.py`
- `domain/futures/funding.py`
- `domain/futures/initial_margin.py`
- `domain/futures/maintenance_margin.py`
- `domain/futures/margin.py`
- `domain/futures/accounting.py`
- `contracts/futures/price_quantity.py`
- corresponding financial contract tests, risk/execution boundaries, and architecture/gate tests.

This is a scoped audit/implementation list; it does not authorize unrelated formula, API, or architecture changes. Frozen source-of-truth documents must not be silently edited. Any required change to governed contracts must use the authorized architecture-change process.

## 7. Alternatives considered

- Assume Decimal is exact — rejected.
- Increase global Decimal precision arbitrarily — rejected.
- Silently quantize to exchange tick/precision — rejected.
- Explicit owner-approved rounding at the four named output boundaries — selected.

## 8. Required regression tests

Tests must cover, without skips/xfails or weakened assertions:

- deterministic behavior under changed ambient Decimal contexts;
- controlled `prec=28` working-context behavior;
- high-precision operands and intermediate inexactness;
- terminating and repeating quotients;
- exact scale and approved mode for every named boundary, including negative values for `ROUND_DOWN`;
- PnL scales for CRYPTO versus GOLD/FOREX and configurable policy overrides;
- Funding payment scale/mode and wallet-balance downstream use;
- Margin ratio being comparison-only, thresholds and fail-closed range/equality cases;
- configurable liquidation tick sizes and LONG/SHORT directional rounding;
- Linear and Inverse formula/denomination separation;
- invalid, missing, and unrepresentable policy values failing closed in Risk/Execution;
- audit event fields for each boundary without introducing domain I/O;
- static enforcement that `float` and built-in `round()` are absent from `domain/futures/`.

## 9. Implementation and verification plan

1. Implement the exchange-independent Decimal context and four boundary contracts using the approved policies above.
2. Add tests before/alongside implementation; preserve existing public APIs and formulas unless a separate approved change is required.
3. Keep venue/instrument scales, tick sizes, rate limits, PnL limits, and risk thresholds configurable and fail closed when absent.
4. **Pause and ask the repository owner for the target exchange's instrument/specification list when exchange selection is required. Do not assume an exchange or fabricate its metadata.**
5. If a structured audit/logging port is absent, stop at that integration point and request the architecture decision rather than adding direct domain I/O.
6. Run relevant unit/contract tests and all applicable CI gates; fix root causes, never weaken checks.
7. Verify exact same-SHA G01–G08 applicability/results, preserving G05 >= 98% and G08 >= 90%; operational G07 must not be represented as passed when skipped/not applicable.
8. Keep merge, Phase 2+, and production-readiness blocked until independent governance and verification blockers are resolved.

## 10. Rollback plan

If implementation changes financial meaning, violates a frozen contract, rounds outside the four approved boundaries, depends on ambient context, guesses exchange metadata, introduces unapproved domain I/O, or fails required gates, stop and revert through the reviewed PR process. Never restore green CI by weakening tests, thresholds, or fail-closed behavior.

## 11. Approval record

- **Option C:** selected by repository owner on 2026-10-09.
- **Working Decimal context:** `prec=28`.
- **PnL:** CRYPTO 8 places; GOLD/FOREX 2 places; `ROUND_DOWN`; configured maximum and fail-closed checks.
- **Funding payment:** 8 places; `ROUND_HALF_UP`; configured rate bounds and fail-closed balance checks.
- **Margin ratio:** 8 places; `ROUND_HALF_UP`; comparison-only; fail closed in the owner-specified critical range.
- **Liquidation price:** configured instrument tick size; LONG `ROUND_DOWN`, SHORT `ROUND_UP`; final trigger value.
- **Boundary helpers:** `round_pnl()`, `round_funding()`, `round_margin_ratio()`, `round_liquidation_price()`.
- **Audit record:** boundary, input, output, method, precision/scale.
- **Risk/Execution:** fail closed.
- **Domain prohibition:** no `float` or built-in `round()` under `domain/futures/`.
- **Exchange selection:** owner input required; pause and ask for the exchange's instrument/specification list.
- **Implementation authorization:** granted for exchange-independent implementation subject to this ADR, existing frozen contracts, approved architecture boundaries, tests, gates, and the stop conditions above.
