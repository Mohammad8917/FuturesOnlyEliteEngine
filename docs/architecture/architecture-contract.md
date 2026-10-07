# Elite Architecture Contract

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
