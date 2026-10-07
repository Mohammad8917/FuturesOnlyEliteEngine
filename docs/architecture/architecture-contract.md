# Elite Architecture Contract

**Navigation:** Start with `docs/architecture/ARCHITECTURE-MASTER-INDEX.md` for the single project path. This contract remains authoritative for contract and quality requirements within the source-of-truth hierarchy.

## Product identity

FuturesOnlyEliteEngine is a production-grade, Futures-only professional trading engine for CRYPTO Futures, FOREX Futures, GOLD Futures, Linear Futures, Inverse Futures, and 15 independent exchange adapters.

## Runtime and deployment contract

### Python runtime

- **Required Python version: 3.13**.
- Python 3.13 is the declared production and CI runtime baseline unless changed through the architecture-change process.

### Deployment targets

The production engine must support:
- Windows Server
- Linux Server
- Windows Home/Desktop

Platform-specific behavior must remain behind explicit infrastructure boundaries. Cross-platform support must not weaken security, risk controls, execution validation, reconciliation, observability, or fail-closed behavior.

### Operational capabilities

The system is required to support both:

1. **Automated Futures trading** through the governed execution pipeline.
2. **Signal/operational notification delivery** through Telegram and email.

Notifications are observability/delivery outputs, not execution authority. Telegram or email failures must never be interpreted as successful order execution, and notification channels must not bypass risk/execution gates.


## Configuration, hardcoding, and sensitive information

- Secrets and sensitive values must never be embedded in production code, tests, fixtures, examples, documentation, logs, or committed configuration.
- Environment/deployment/account/exchange-specific operational values must be supplied through the explicit configuration/security boundary rather than hard-coded in business or infrastructure logic.
- Safety-critical configurable values must have typed validation, provenance, and fail-closed behavior; missing or malformed values cannot silently fall back to source-code defaults.
- Hard-coded constants are acceptable only for immutable domain vocabulary or true invariants whose semantics cannot vary by environment, account, deployment, or exchange configuration.
- Security scanning and architecture tests must enforce the boundary and detect accidental credential/token/key material and forbidden operational hardcoding.
## Architectural completeness requirements

Before production implementation of any capability, the architecture must explicitly define:

- canonical vocabulary and stable contract ownership;
- exact inputs, outputs, units, precision, timestamps, validation status, and failure semantics at critical boundaries;
- Linear/Inverse applicability and financial meaning;
- CRYPTO/FOREX/GOLD applicability;
- risk, execution, order lifecycle, reconciliation, and audit ownership;
- configuration/secrets and security ownership;
- data freshness/provenance and fail-closed behavior;
- idempotency and unknown-state handling where external state changes are involved;
- observability, operational error classification, and notification semantics;
- resilience rules for timeout, retry, partial failure, duplicate delivery, and contradictory external state;
- architecture-test and CI-enforcement expectations;
- phase/gate entry and exit evidence requirements;
- migration, rollback, and compatibility impact for approved architecture changes.

No critical behavior may remain governed only by convention, an implementation detail, or an undocumented assumption.

## Quality bar

Acceptance requires evidence. No marketing claim of world-class quality substitutes for deterministic tests, architecture enforcement, mutation evidence, security evidence, integration/resilience evidence, and release verification.

## Quality gates

| Gate | Required standard |
|---|---|
| G01 Format/Lint | Strict, zero unexplained violations |
| G02 Typecheck | Strict, zero unexplained type errors |
| G03 Unit/Contract | Full required contract suite |
| G04 Architecture/Dependency | Boundary rules enforced |
| G05 Coverage | >= 98% official minimum |
| G06 Security/Supply Chain | Required security checks pass |
| G07 Integration/Resilience | Required integration and failure-path evidence |
| G08 Release/Mutation | >= 90% mutation minimum |

Coverage may not be raised by deleting tests, excluding production code, lowering thresholds, weakening assertions, or using artificial tests.

## Core pipeline

MARKET -> FUTURES INSTRUMENT -> MARKET ADAPTER -> MARKET DATA -> DATA VALIDATION -> REGIME PROBABILITY -> MTF STRUCTURE -> SETUP -> TREND/MOMENTUM -> CONFIRMATION -> COST/LIQUIDITY -> FUTURES RISK -> POSITION SIZING -> OPPORTUNITY RANKING -> DECISION -> SIGNAL CONTRACT -> EXECUTION RISK GATE -> EXECUTION CONTRACT -> EXCHANGE ADAPTER -> ORDER -> POSITION/ORDER RECONCILIATION -> AUDIT

## Futures semantic requirements

Every applicable production Futures path must explicitly model contract family, Linear/Inverse, multiplier, settlement asset, margin asset, leverage, initial margin, maintenance margin, funding, realized PnL, unrealized PnL, exposure, liquidation, position side, position mode, precision, exchange limits, and reconciliation semantics.

Implicit defaults are prohibited when they can change financial meaning.

## Fail-closed requirements

Unknown, invalid, stale, contradictory, or incomplete critical Futures state must stop the relevant operation. Failure must never silently produce an order, accepted signal, valid-looking position, false reconciliation success, Spot fallback, or guessed contract specification.

## Phase/gate evidence rule

A phase or gate is complete only when its required evidence is tied to the current repository HEAD. Historical runs, stale branches, local-only results, or claims without reproducible evidence do not establish completion.

The required proof chain is:

ARCHITECTURE RULE → CONTRACT → PRODUCTION IMPLEMENTATION → TEST → CI ENFORCEMENT → SAME-SHA EVIDENCE

For architecture-only governance work, production implementation may legitimately remain pending; in that case the missing enforcement stage must be explicitly recorded as a future phase rather than implied to be complete.

## Build-order versus runtime-order rule

The phase/build order and the runtime pipeline are intentionally different concepts. The build order controls dependency-safe implementation; the runtime pipeline controls production execution flow. No document may infer that Phase order changes runtime ownership or that runtime ordering permits skipping a build phase.

## Implementation sequence

1. Architecture contract
2. Responsibility maps
3. Dependency rules
4. Domain contracts
5. Infrastructure ports
6. Production implementation
7. Unit/contract tests
8. Architecture tests
9. Integration/resilience tests
10. Security/supply-chain checks
11. Mutation verification
12. Release verification

No production implementation should precede a clearly owned contract.
