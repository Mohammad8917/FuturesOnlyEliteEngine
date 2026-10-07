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
