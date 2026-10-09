# ADR-0003: Exact, Context-Independent Futures Financial Arithmetic

- **Status:** PROPOSED — not approved; no implementation authorized
- **Date:** 2026-10-09
- **Proposer:** AI-assisted repository audit; repository owner is the decision authority

## 1. Problem

The Phase 1 contract requires exact financial arithmetic and prohibits implicit rounding/quantization. Python `Decimal` arithmetic is affected by the active decimal context; division and operations exceeding the context precision can return rounded results. A non-terminating quotient such as 1/3 cannot be represented exactly as a finite decimal. The current contract types and calculation paths therefore need an explicitly governed policy, not an assumption that using `Decimal` alone guarantees exact arithmetic.

## 2. Current architecture

The financial meaning of Linear and Inverse Futures, settlement/margin denomination, PnL, liquidation, exposure, and accounting is frozen by the approved source-of-truth documents. No formula, unit, owner, rounding boundary, or output contract may be changed silently. This ADR must be explicitly approved before implementation.

## 3. Decision required from the repository owner

Choose and explicitly approve one primary policy, including any narrowly scoped combination:

### Option A — Exact rational intermediate arithmetic
Represent intermediate values as exact rational numbers (or equivalent integer numerator/denominator arithmetic), and define how/where results may be converted to the existing public Decimal contracts. This avoids context rounding in intermediate rational calculations, but requires a deliberate output-boundary policy and careful API compatibility analysis.

### Option B — Decimal-only with fail-closed inexact operations
Keep Decimal as the calculation representation and trap/detect every inexact or rounded operation, failing closed when a result cannot be represented exactly under the approved contract. This is simpler at boundaries but can reject mathematically valid financial inputs when an exact finite Decimal result does not exist.

### Option C — Explicit, owner-approved rounding boundaries
Permit rounding only at explicitly specified, contractually justified boundaries, with the rounding mode, precision, denomination, and provenance declared in the contract. This option conflicts with any current invariant that prohibits such rounding unless the owner first approves the corresponding architecture/contract change through this ADR.

The owner must choose the policy and clarify whether exactness applies to all intermediate values, externally visible outputs, or both. No default is inferred from exchange conventions.

## 4. Non-negotiable constraints for any approved option

- No binary floating-point conversion in critical financial calculations.
- No dependence on ambient mutable Decimal context for financial meaning.
- No silent rounding, quantization, truncation, or precision loss.
- Non-finite, invalid, unsupported, ambiguous, or unrepresentable critical results fail closed according to the approved policy.
- Linear and Inverse formulas and denominations remain distinct and explicit.
- Public contract compatibility and migration must be analyzed before implementation.
- Existing G05 >= 98%, G08 >= 90%, all tests, and all other gate strengths remain unchanged.
- No production readiness or Phase 2 authorization follows merely from approving this ADR.

## 5. Affected invariants and contracts

- Exact monetary and contract calculations.
- Explicit units, denomination, precision, and rounding semantics.
- Linear/Inverse formula separation.
- Fail-closed behavior for untrusted or unrepresentable financial state.
- Architecture-change governance and same-SHA evidence.

## 6. Affected implementation surfaces

Initial audit targets:
- `contracts/futures/contract_specification.py`
- `contracts/futures/pnl.py`
- `contracts/futures/liquidation.py`
- `contracts/futures/settlement.py`
- `contracts/futures/funding.py`
- `contracts/futures/initial_margin.py`
- `contracts/futures/maintenance_margin.py`
- `contracts/futures/margin.py`
- `contracts/futures/accounting.py`
- `contracts/futures/price_quantity.py`
- corresponding financial contract tests and architecture/gate tests.

This list is an audit scope, not authorization to modify these files.

## 7. Alternatives considered

- Assume Decimal is exact — rejected; context precision affects arithmetic.
- Increase the global Decimal precision arbitrarily — rejected; this does not establish context-independent exactness and cannot make a non-terminating quotient finite.
- Silently quantize to an exchange tick/precision — rejected; this would introduce financial policy without an approved contract.
- Choose an explicit policy through this ADR before implementation — proposed.

## 8. Risk analysis

Rational intermediate arithmetic may change types, performance, serialization, and downstream interfaces. Fail-closed Decimal arithmetic may reject calculations that previously returned approximate values. Explicit rounding boundaries can alter financial results and are prohibited unless precisely approved. Every selected policy needs adversarial tests for changed ambient context, high-precision operands, terminating/non-terminating division, overflow/exponent limits, Linear/Inverse PnL and liquidation, accounting balance, and output conversion.

## 9. Migration and verification plan

No implementation is authorized while this ADR is PROPOSED. After explicit owner approval/reconfirmation:
1. update the governed source-of-truth documents and public contract expectations;
2. implement the selected policy in a shared, narrowly owned arithmetic boundary without changing formula semantics;
3. add regression/property tests for context independence and every affected financial path;
4. run relevant unit/contract tests and all applicable CI gates;
5. verify exact same-SHA G01–G08 applicability and results, preserving G05 >= 98% and G08 >= 90%;
6. keep Phase 2+ blocked until all independent blockers and final-main requirements are resolved.

## 10. Rollback plan

If the approved implementation changes financial meaning, violates compatibility, or cannot meet the exactness contract, stop the candidate and revert through the reviewed PR process. Never restore green CI by weakening tests, thresholds, or fail-closed behavior.

## 11. Explicit approval / reconfirmation

**Pending.** Repository owner must explicitly select the arithmetic policy and approve/reject this ADR before implementation. General authorization to continue the project does not select a financial arithmetic policy.
