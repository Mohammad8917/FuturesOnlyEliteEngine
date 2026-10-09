# Architecture Change Guard

This is a repository-level guardrail. It does not replace GitHub branch protection or repository rulesets; platform controls are required for technical enforcement.

## Protected surfaces

- `docs/architecture/**`
- Futures-only product boundary and CRYPTO/FOREX/GOLD Futures scope
- Linear/Inverse semantics
- dependency direction and ownership
- risk/execution authority boundary
- order lifecycle, idempotency, reconciliation, restart recovery, and execution halt
- configuration/secrets/security boundary
- G01–G08 quality thresholds, including G05 >= 98% and G08 >= 90%
- release and same-SHA verification rules

## Mandatory change rule

No direct change to a protected surface is considered authorized merely because a contributor has repository write access. Changes must arrive through a pull request, receive required owner review, pass required checks on the exact HEAD, and use the ADR process whenever an architectural invariant or ownership rule changes.

## Prohibited shortcuts

- direct pushes to protected branches;
- force-pushes/history rewriting;
- bypassing required reviews/checks;
- weakening thresholds;
- deleting/skipping/xfailing tests;
- adding ignores/excludes/noqa solely to obtain green checks;
- operational Spot fallback;
- hard-coded secrets or safety-critical environment/account/exchange configuration;
- architecture changes without reconciling project-state and the source-of-truth hierarchy.

## Platform enforcement required

The repository administrator must configure GitHub branch protection/rulesets for `main` with at minimum:

1. Pull requests required; no direct pushes.
2. Required Code Owner review for protected files.
3. Required applicable G01–G08 status checks before merge.
4. Force pushes prohibited.
5. Branch deletion prohibited.
6. Required conversation resolution.
7. Bypass permissions minimized; ideally none for ordinary contributors.
8. Administrator bypass disabled where GitHub plan/settings permit it.
9. Ruleset administration restricted to repository administrators.

The repository is **not technically locked** until these platform controls are enabled and verified.

## Phase 1 accounting / settlement-accounting semantic lock

Historical transition record (not live authorization): at that recorded stage, the next Phase 1 unit was **Futures accounting and settlement accounting semantics**. Current authorization is controlled exclusively by `docs/architecture/project-state.md` → `Current authoritative state`.

Frozen baseline:
- owner: Futures domain/contract boundary for deterministic accounting facts and settlement-accounting facts; application/infrastructure own persistence, external settlement transport, exchange mapping, and account mutation;
- accounting is represented as immutable, append-only journal facts; the canonical contract does not write a database, mutate an account, call a network, or submit an order;
- every journal entry has explicit entry identity, causation identity, state version, sequence, account scope, instrument identity, asset denomination, debit/credit direction, and exact finite Decimal amount;
- an entry has exactly one positive amount and one explicit debit/credit direction; a journal batch must be balanced per explicit asset denomination;
- realized PnL is consumed as an already-validated signed fact; the accounting boundary does not recompute PnL, multiplier, price, margin, liquidation, or funding;
- funding transfers are consumed as explicit payer/receiver facts with explicit denomination; settlement transfers are explicit source/settlement denomination facts and require explicit conversion semantics from the already-closed settlement contract;
- Linear/Inverse, CRYPTO/FOREX/GOLD, and BASE/QUOTE/settlement denomination remain explicit; no family or denomination is inferred from a generic number;
- zero transfer is meaningful only where the upstream contract explicitly declares a zero-valued semantic fact; journal entries themselves require strictly positive amounts;
- exact Decimal arithmetic is mandatory; bool, binary float, non-finite, zero/negative, missing, contradictory, unsupported, or ambiguous critical financial state fails closed; no rounding or quantization;
- ordering is monotonic within the declared account/instrument scope; duplicate entry identity or reused causation/version combination cannot silently create a second accounting fact;
- contradictory balances or external settlement outcomes are divergence, not success; reconciliation remains a later boundary and may not silently overwrite canonical facts;
- settlement accounting records denomination-preserving transfers and explicit cross-asset conversions only when an explicit positive conversion rate is supplied by the settlement contract;
- no exchange-specific fee, tier, balance, settlement timing, wallet, collateral, or ledger policy is guessed into the canonical contract;
- meaningful contract tests, Phase 1 CI, Architecture Invariants CI, G01 CI, and same-SHA evidence are mandatory before the cursor advances.


## Phase 1 accounting / settlement-accounting closure evidence

Futures accounting and settlement accounting semantics are implemented at the canonical Futures domain/contract boundary. The implementation is immutable and deterministic: it records balanced journal facts, consumes already-validated realized-PnL, funding, and settlement facts, preserves explicit asset denomination, Linear/Inverse identity, CRYPTO/FOREX/GOLD applicability, exact Decimal behavior, and fail-closed validation. No persistence, network, exchange SDK, order submission, account mutation, or exchange-specific accounting policy is introduced.

Evidence boundary:
- production: `contracts/futures/accounting.py`, `contracts/futures/settlement_accounting.py`;
- tests: `tests/contracts/accounting_contract_test.py`;
- CI: Phase 1 Domain Contracts, Architecture Invariants, and G01 Dependency Architecture on the same verification SHA;
- no threshold reduction, test weakening, skip/xfail, assertion removal, or dependency-boundary weakening.

Cross-journal idempotency and durable sequence enforcement remain downstream persistence/reconciliation responsibilities; the canonical domain journal enforces immutable entry identity, explicit causation/version data, and monotonic sequence within each declared journal batch. Contradictory external outcomes remain divergence rather than success.

## Phase 1 completeness correction

The Phase 1 completeness audit recognizes `position_side.py` and `position_mode.py` as separate production boundaries covered by the combined position-side/mode contract test. Gate thresholds remain immutable: G05 >= 98% and G08 >= 90%.


## CI action pin closure

The Phase 1/G01/Architecture Invariants workflows pin `actions/setup-python` to the verified `v5.6.0` commit `a26af69be951a213d495a4c3e4e4022e16d87065`. Any future action-pin change requires the same strict CI verification; no floating action reference is permitted.


## Current-state authority and historical-transition control

Historical phase-unit entries in this document preserve chronology. Their earlier “active unit”, “next authorized unit”, or “next step” wording is not live authorization and must not override `docs/architecture/project-state.md` → `Current authoritative state`. The Phase 1 candidate completeness/evidence audit is recorded as closed on the candidate branch only; PR #35 owner review/authorized merge and exact-resulting-SHA verification on `main` remain pending. Phase 2+ production implementation stays blocked until those governance and `main` verification steps are complete and the historical G05 false-green is corrected. No gate skip, threshold reduction, test weakening, or Spot operational path is permitted.


## Phase-scoped gate applicability hold — 2026-10-09

On candidate SHA `458079b915cc6395f266675b13b4893b323cf55b`, G07 fails closed because later-phase production layers and integration/resilience suites are absent. This conflicts operationally with the rule that Phase 2+ is blocked until PR #35 merges, while the workflow runs G07 on every PR. Proposed ADR-0001 documents the unresolved applicability decision. No gate may be skipped or weakened, no placeholder implementation may be added, and no Phase 2+ work or merge authorization may be inferred until the owner reviews/reconfirms the proposal and the resulting same-SHA checks are verified.
