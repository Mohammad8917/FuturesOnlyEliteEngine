# ADR-0003: Exact Arithmetic Policy for Futures Financial Contracts

- **Status:** PROPOSED — no arithmetic implementation change is authorized until the repository owner explicitly selects and reconfirms a policy.
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit; repository owner is the decision authority.
- **Tracking:** Issue #37

## 1. Problem

The frozen Phase 1 contracts require exact finite Decimal inputs and prohibit implicit rounding or quantization. Ordinary Python `Decimal` operations are governed by the active decimal context. Division can produce a rounded finite approximation for a non-terminating quotient, and arithmetic can be context-sensitive for sufficiently high-precision values. The current `PrecisionPolicy.EXACT` / `RoundingPolicy.NONE` vocabulary does not by itself enforce context-independent arithmetic.

This is a financial correctness blocker. It is not acceptable to silently choose a precision, rounding mode, or exchange-specific policy.

## 2. Current Architecture

Canonical financial contracts expose explicit denomination and Decimal-valued facts. Linear and Inverse calculations have distinct formulas. The authoritative contract says no implicit rounding/quantization and requires fail-closed behavior for invalid or ambiguous financial state. Accounting consumes financial facts and requires exact amounts. Any arithmetic policy must preserve denomination, Linear/Inverse semantics, and downstream accounting integrity.

## 3. Proposed Change

Select one globally coherent arithmetic policy, then apply it consistently to financial calculation contracts and their downstream boundaries. The decision must specify:
- whether exact intermediate values may use a representation other than Decimal;
- how and when a result may become a Decimal amount;
- behavior for non-terminating rational results;
- context independence for addition, subtraction, multiplication, division, and sums;
- overflow/resource limits and rejection behavior;
- how accounting journal amounts consume and validate calculated values;
- compatibility requirements for existing public contracts.

No option is selected by this proposal. The repository owner must explicitly choose one after reviewing the trade-offs below.

## 4. Why Current Architecture Is Insufficient

The labels EXACT and NONE do not prevent Python's active Decimal context from rounding intermediate arithmetic. A finite Decimal output for a repeating quotient such as 1/3 is an approximation, not the exact rational value. Current terminating-value tests alone do not establish correctness under changed contexts or repeating results.

## 5. Alternatives Considered

### Option A — Exact rational arithmetic at calculation boundaries

Represent rational intermediate results exactly (for example, with numerator/denominator integers or a rigorously constrained rational type). Define an explicit, separately approved conversion boundary before any contract requiring finite Decimal journal amounts. Reject conversion where the target cannot represent the value exactly unless a future approved policy explicitly authorizes otherwise.

Benefits: exact intermediate mathematics and independence from Decimal context.

Costs/risks: public types and interfaces may need careful design; denominator growth and computational/resource limits must be bounded; rational-to-Decimal conversion cannot silently approximate repeating values; downstream accounting still needs a clear representability rule.

### Option B — Explicit precision and rounding policy

Define explicit output precision and rounding mode, make them validated contract inputs or governed configuration, and apply them only at named calculation boundaries.

Benefits: practical finite outputs for non-terminating calculations.

Costs/risks: this changes the current RoundingPolicy.NONE invariant and requires an explicit architecture decision defining where rounding is legally/semantically permitted, denomination-specific policy, and downstream reconciliation. No default or exchange policy may be guessed.

### Option C — Fail closed when exact finite Decimal representation is impossible

Use context-independent arithmetic for operations whose results can be represented exactly as finite Decimal values, and reject any result that would require rounding, including non-terminating division.

Benefits: preserves the strongest interpretation of the current no-rounding contract and avoids silently approximate financial results.

Costs/risks: common Inverse PnL, exposure, or liquidation calculations may fail for valid inputs whose exact result is repeating. This may block useful calculations until a later policy is explicitly approved.

## 6. Affected Invariants

- Exact finite financial inputs; no implicit rounding/quantization.
- Explicit Linear/Inverse formulas and denomination.
- Fail-closed behavior for unsupported or unrepresentable results.
- Immutable G01–G08 quality floors; G05 >= 98%, G08 >= 90%.
- No test skips/xfails, weakened assertions, hidden precision defaults, or operational Spot fallback.

## 7. Affected Contracts

At minimum, audit:
- `contracts/futures/contract_specification.py`
- `contracts/futures/pnl.py`
- `contracts/futures/liquidation.py`
- `contracts/futures/settlement.py`
- `contracts/futures/funding.py`
- `contracts/futures/initial_margin.py`
- `contracts/futures/maintenance_margin.py`
- `contracts/futures/margin.py`
- `contracts/futures/accounting.py`
- `contracts/futures/settlement_accounting.py`
- `contracts/futures/price_quantity.py`

This list is an audit scope, not authorization to move ownership or change formulas. Issue #38 independently tracks ownership placement.

## 8. Affected Dependencies

Potentially affected public numeric types, financial calculation modules, accounting boundaries, validation contracts, architecture docs, test fixtures, and CI. Domain ownership must remain consistent with the approved responsibility map; the arithmetic decision does not authorize moving ownership by itself.

## 9. Affected Tests and Gates

After an explicit decision, regression tests must cover:
- repeating quotients such as 1/3 and reciprocal-price formulas;
- operands with precision beyond the default Decimal context;
- altered Decimal contexts (precision and rounding mode);
- exact addition/subtraction/multiplication and journal balance sums;
- Linear and Inverse formulas across CRYPTO, FOREX, and GOLD;
- representable versus non-representable Decimal outputs under the chosen policy;
- denomination preservation and accounting consistency;
- fail-closed behavior and deterministic diagnostics.

All applicable CI must pass on the exact resulting SHA. G05 remains >= 98%, G08 remains >= 90%; no skips/xfails, exclusions, threshold reductions, or weakened assertions.

## 10. Risk Analysis

A silent approximation can alter PnL, liquidation prices, exposure, funding, margin, or ledger balances. Conversely, a strict fail-closed policy may reject legitimate calculations if the selected output type cannot represent a mathematically exact result. A rounding policy can be viable only when its authorized boundaries and semantics are explicitly approved. The implementation must not conflate mathematical exactness with a Decimal representation.

## 11. Migration Plan

1. Repository owner explicitly selects Option A, B, or C, or supplies a different fully specified policy.
2. Record the decision and any invariant changes in this ADR before implementation.
3. Implement a shared, deterministic arithmetic policy without introducing hidden defaults.
4. Add regression and mutation-sensitive tests across every affected financial contract.
5. Reconcile Source-of-Truth documents only to reflect the approved decision.
6. Run all applicable gates and verify exact-SHA evidence.
7. Keep Phase 2+ blocked until this issue, ownership reconciliation, independent review, main protection, and resulting-main verification are resolved.

## 12. Rollback Plan

If the selected implementation fails exactness tests or any applicable gate, revert through a reviewed PR. Do not restore green status by lowering thresholds, skipping tests, or silently changing financial semantics.

## 13. Explicit Approval / Reconfirmation

**Pending repository-owner decision.** Select one:
- **A — Exact rational intermediates with explicit exact-conversion boundary**
- **B — Explicit precision/rounding policy (requires explicit amendment of the no-rounding invariant)**
- **C — Fail closed when exact finite Decimal representation is impossible**

Until the owner explicitly selects and reconfirms a policy, do not change financial arithmetic, claim Phase 1 financial completeness, merge the candidate as complete, or authorize Phase 2+.
