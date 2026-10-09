# ADR-0003: Explicit Boundary Rounding for Futures Financial Arithmetic

- **Status:** OWNER-SELECTED POLICY — boundary contract details remain open; implementation must not begin until those details are specified.
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit
- **Decision authority:** Repository owner
- **Owner decision recorded:** 2026-10-09 — Option C, subject to the mandatory constraints below.

## 1. Problem

The Phase 1 financial contract requires explicit precision and rounding semantics. Python `Decimal` alone does not guarantee context-independent exactness: division and operations exceeding the active context precision can round. An arbitrary increase to ambient precision does not solve non-terminating quotients and does not define a financial output contract.

## 2. Owner-selected decision

The repository owner selected **Option C — explicit, owner-approved rounding boundaries**, with these constraints:

1. Use `Decimal` arithmetic with a controlled working context of **`prec=28`**. Do not rely on a caller's ambient mutable Decimal context.
2. Rounding is permitted **only at explicitly declared financial output boundaries**, initially:
   - PnL;
   - Funding payment;
   - Margin ratio;
   - Liquidation price.
3. Each boundary must declare its output precision/scale, rounding mode, denomination/unit, and conversion semantics. These details are **not inferred** from exchange conventions.
4. Risk and execution paths must **fail closed** when an input, calculation, or boundary result is invalid, unsupported, ambiguous, or cannot be produced under the approved boundary contract.
5. `float` and built-in `round()` are prohibited in `domain/futures/`. Financial arithmetic must not convert through binary floating point.
6. Linear and Inverse Futures formulas and denominations remain distinct. This ADR does not authorize formula changes.
7. No other implicit rounding, quantization, truncation, or precision loss is permitted.

## 3. Required clarification before implementation

The owner-selected policy is recorded, but it is **not yet sufficiently specified for safe implementation**. For each of the four named boundaries, the contract must state:

- the exact output scale or significant-digit precision;
- the explicit rounding mode;
- whether the boundary result is a public/API value, an internal risk value, or both;
- how the rounded result is represented and consumed downstream;
- what conditions must fail closed.

The `prec=28` working context must not silently become permission to round arbitrary intermediate operations. The implementation must distinguish permitted boundary rounding from intermediate inexactness and must prove that behavior with tests. Where an intermediate operation cannot safely be represented before a declared boundary, the implementation must use a controlled approach or fail closed; it must not silently round.

**No developer may choose missing per-boundary modes or scales unilaterally.** The policy choice (Option C) is owner-approved; these remaining details are implementation blockers, not permission to choose defaults.

## 4. Non-negotiable constraints

- No binary floating-point conversion in critical financial calculations.
- No dependence on ambient mutable Decimal context for financial meaning.
- No implicit rounding, quantization, truncation, or precision loss outside the approved boundaries.
- `float` and built-in `round()` are forbidden under `domain/futures/`.
- Invalid, unsupported, ambiguous, or unsafe critical results fail closed in Risk/Execution.
- Explicit units and denomination; no mixing of Linear and Inverse semantics.
- Existing G05 >= 98%, G08 >= 90%, all tests, and all other gate strengths remain unchanged.
- No production-readiness or Phase 2 authorization follows from this ADR.

## 5. Affected invariants and contracts

- Exact monetary and contract arithmetic except for the expressly approved output boundaries.
- Explicit units, denomination, precision, and rounding semantics.
- Linear/Inverse formula separation.
- Fail-closed behavior for untrusted or unsafe financial state.
- Architecture-change governance and same-SHA CI evidence.

## 6. Affected implementation surfaces

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

This list defines audit scope; it does not authorize unrelated formula, API, or architecture changes.

## 7. Alternatives considered

- Assume Decimal is exact — rejected.
- Increase global Decimal precision arbitrarily — rejected.
- Silently quantize to exchange tick/precision — rejected.
- Explicit owner-approved rounding at named output boundaries — selected, subject to the outstanding boundary specifications above.

## 8. Required regression tests

Before implementation can be considered complete, tests must cover:

- changed ambient Decimal contexts and deterministic behavior;
- `prec=28` working-context behavior;
- high-precision operands and intermediate inexactness;
- terminating and repeating quotients;
- every named rounding boundary with its approved mode and output scale;
- Linear and Inverse PnL/liquidation and denomination separation;
- Funding, Margin ratio, settlement, and downstream accounting;
- invalid and unrepresentable values failing closed in Risk/Execution;
- static enforcement that `float` and built-in `round()` are absent from `domain/futures/`.

No tests may be skipped/xfail'ed, exclusions added, thresholds reduced, or gates bypassed.

## 9. Migration and verification plan

1. Complete and approve the per-boundary precision, rounding-mode, denomination, and downstream representation contracts.
2. Update governed source-of-truth contracts through the authorized architecture-change process; do not silently edit locked documents.
3. Implement a narrow, shared arithmetic boundary and preserve formula/API semantics unless separately approved.
4. Add the regression tests above.
5. Run all relevant unit/contract tests and applicable CI gates.
6. Verify exact same-SHA G01–G08 applicability/results, preserving G05 >= 98% and G08 >= 90%; operational G07 must not be represented as passed when skipped/not applicable.
7. Keep Phase 2+, production readiness, and merge blocked until all independent blockers are resolved.

## 10. Rollback plan

If the implementation changes financial meaning, violates a frozen contract, rounds outside an approved boundary, depends on ambient context, or fails the required gates, stop and revert through the reviewed PR process. Never restore green CI by weakening tests, thresholds, or fail-closed behavior.

## 11. Approval record

- **Option C:** selected by repository owner on 2026-10-09.
- **`Decimal` working context `prec=28`:** selected.
- **Named rounding boundaries:** PnL, Funding payment, Margin ratio, Liquidation price.
- **Fail-Closed Risk/Execution:** required.
- **Ban `float` and built-in `round()` in `domain/futures/`:** required.
- **Per-boundary output scales, rounding modes, and downstream representations:** pending explicit contract specification.
- **Implementation authorization:** pending completion of the remaining boundary contracts and required governance updates.
