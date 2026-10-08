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
- authoritative external-state semantics, idempotency identity, concurrency/versioning, restart/recovery reconciliation, and scoped/global execution-halt behavior;
- trusted clock/freshness/skew semantics and safety-critical configuration provenance/versioning;
- append-only/tamper-evident audit evidence and release artifact/source/dependency provenance;
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

## Phase 1 domain contract baseline

The authorized Phase 1 Domain Contracts foundation must explicitly define, with production ownership and failure semantics:

- instrument identity and canonical Futures symbol semantics;
- contract family and explicit Linear/Inverse applicability;
- multiplier and contract specification;
- settlement asset and settlement semantics;
- margin asset and margin semantics;
- leverage vocabulary and contract-level constraints;
- position side and position mode;
- price, quantity, monetary units, denomination, precision, and rounding semantics;
- funding-rate value, interval, and funding calculation semantics;
- realized PnL and unrealized PnL;
- exposure and position valuation semantics;
- liquidation price and liquidation constraints;
- Futures accounting and settlement accounting;
- validation status, provenance/freshness where applicable, and explicit failure semantics.

Every Phase 1 contract follows the implementation unit protocol: Responsibility → Owner → Inputs → Outputs → Units/Precision/UTC → Allowed Dependencies → Forbidden Dependencies → Linear/Inverse Applicability → Market Applicability → Failure Semantics → Test Boundary → Downstream Consumers.

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

## Multiplier / contract-specification contract

The canonical Phase 1 multiplier contract uses `CONTRACTS` as the quantity unit and exact finite positive Decimal arithmetic.

Linear Futures:
- multiplier = base-asset units per contract;
- base exposure = quantity × multiplier;
- quote notional = quantity × multiplier × price.

Inverse Futures:
- multiplier = quote-price-denomination units per contract;
- quote notional = quantity × multiplier;
- base exposure = (quantity × multiplier) ÷ price.

The price quote asset must equal the canonical Futures symbol quote asset. Margin and settlement semantics are separate contracts and must not be inferred from multiplier data. Invalid, zero, negative, non-finite, contradictory, ambiguous, or unsupported specifications fail closed. Exchange-specific lot/tick/precision metadata is mapped later and cannot redefine this domain meaning.

## Phase 1 cursor — settlement

The multiplier/contract-specification, settlement, margin, and leverage contracts are complete and evidenced on main. The next incomplete Phase 1 contract is initial margin semantics. It must explicitly define formula inputs, denomination, ownership, Linear/Inverse applicability, market applicability, precision requirements, and fail-closed behavior before production implementation.
\n## Phase 1 settlement asset / settlement semantics

Settlement is an explicit domain contract, not an exchange-side guess.

The canonical settlement asset comes from the Futures instrument identity and must match the settlement specification. Every settlement amount declares its source asset. If source and settlement assets match, conversion is forbidden. If they differ, a positive finite Decimal conversion rate is mandatory; the rate is defined as settlement-asset units per source-asset unit.

The settlement contract performs no network access, rate discovery, exchange selection, scheduling, persistence, account mutation, or margin inference. Those concerns belong to later application/infrastructure contracts. Missing or contradictory settlement terms fail closed.
\n## Phase 1 cursor — margin

The leverage vocabulary/contract-level constraints contract is complete and evidenced on main. The next incomplete Phase 1 contract is maintenance margin semantics. It must explicitly define formula inputs, denomination, ownership, Linear/Inverse applicability, market applicability, tier/rate/amount semantics where applicable, validation, precision, and fail-closed behavior before production implementation.


## Phase 1 margin asset / margin semantics contract

Margin is an explicit Futures domain contract. The canonical instrument identity is authoritative for the margin asset; margin asset and settlement asset are independent explicit denominations and must not be silently equated.

Every upstream margin amount declares its source asset. Same-asset amounts require no conversion and reject a supplied conversion rate. Cross-asset amounts require an explicit positive finite Decimal conversion rate defined as margin-asset units per source-asset unit.

This contract applies to CRYPTO/FOREX/GOLD and Linear/Inverse Futures. It performs no leverage, initial-margin, maintenance-margin, liquidation, risk-limit, or exchange-specific collateral inference. Network access, rate discovery, exchange selection, persistence, account mutation, runtime configuration, and hidden defaults are forbidden. Invalid or ambiguous terms fail closed.

The production boundary is contracts/futures/margin.py; meaningful contract tests are in tests/contracts/test_margin.py; CI enforcement is through .github/workflows/phase1-domain-contracts.yml.

## Phase 1 initial margin semantics contract

Initial margin is an explicit deterministic requirement derived from an already-canonicalized Futures notional and an explicit initial-margin ratio.

The contract is:
- unit: RATIO for the initial-margin requirement rate;
- numeric representation: exact finite Decimal;
- inputs: canonical Futures instrument identity, matching market, positive finite notional, and positive finite initial-margin ratio;
- formula: `initial_margin_amount = notional × initial_margin_ratio`;
- output denomination: the same declared denomination as the notional input;
- precision: exact Decimal multiplication with no implicit rounding or quantization;
- applicability: CRYPTO/FOREX/GOLD and Linear/Inverse Futures;
- ownership: Futures domain/contract boundary;
- canonical multiplier/contract-specification semantics are consumed and never redefined;
- initial-margin ratio is not derived from leverage, exchange defaults, account state, maintenance margin, liquidation, risk policy, or position sizing;
- no hidden ratio bounds or exchange-specific collateral policy;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account-state dependency;
- invalid or ambiguous inputs fail closed.

The production boundary is `contracts/futures/initial_margin.py`; meaningful contract tests are in `tests/contracts/test_initial_margin.py`; CI enforcement is through `.github/workflows/phase1-domain-contracts.yml`.

## Phase 1 cursor — maintenance margin

Initial-margin semantics are complete and evidenced on main merge SHA `4bf8eb7f54f08b372d0dd30efe1068e258aa1f8f`. The next incomplete Phase 1 contract is maintenance margin semantics.

Maintenance margin must not be treated as a leverage alias. Its canonical contract must explicitly define formula inputs, denomination, precision, Linear/Inverse and market applicability, and any tier/rate/offset semantics before implementation. Unknown or contradictory critical terms must fail closed.


## Phase 1 maintenance margin semantic lock

Maintenance margin is an explicit Futures domain/contract requirement. It is distinct from leverage, initial margin, liquidation, risk policy, and exchange-specific collateral policy.

Frozen semantics:
- owner: Futures domain/contract boundary;
- unit: RATIO for the maintenance-margin requirement rate;
- numeric representation: exact finite Decimal;
- inputs: canonical Futures instrument identity, matching market, explicit positive finite notional, and explicit positive finite maintenance-margin ratio;
- formula: `maintenance_margin_amount = notional × maintenance_margin_ratio`;
- output denomination: identical to the explicit notional denomination;
- precision: exact Decimal multiplication with no implicit rounding or quantization;
- applicability: CRYPTO Futures, FOREX Futures, GOLD Futures; Linear and Inverse;
- the notional is consumed from canonical multiplier/contract-specification semantics and is not redefined here;
- exchange-specific tiers, rates, offsets, brackets, notional bands, or collateral rules are not guessed or silently defaulted by this canonical contract;
- no inference from leverage, initial margin, account state, liquidation, risk policy, exchange defaults, or position sizing;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation dependency;
- missing, invalid, zero, negative, non-finite, contradictory, unsupported, stale, or ambiguous critical terms fail closed;
- meaningful contract tests, CI enforcement, and same-SHA evidence are required before the cursor can advance.

Production boundary: `contracts/futures/maintenance_margin.py`.
Test boundary: `tests/contracts/test_maintenance_margin.py`.
CI boundary: `.github/workflows/phase1-domain-contracts.yml`.

The canonical implementation does not claim exchange-specific tier schedules. Such schedules may be mapped later through explicit exchange/infrastructure contracts only when their provenance, tier selection semantics, denomination, precision, freshness, and failure behavior are explicit.


## Phase 1 maintenance margin closure evidence

Maintenance-margin semantics are COMPLETE on main merge SHA `7f647c4105738d7dfe298b283841e3eaec6524a7`.

Evidence on the exact merge SHA:
- production boundary: `contracts/futures/maintenance_margin.py`;
- test boundary: `tests/contracts/test_maintenance_margin.py`;
- Phase 1 Domain Contracts CI: green;
- Architecture Invariants CI: green;
- G01 Dependency Architecture CI: green.

The frozen contract remains:
- explicit RATIO requirement rate;
- exact finite Decimal arithmetic;
- explicit positive finite notional and maintenance-margin ratio;
- deterministic `notional × maintenance_margin_ratio`;
- unchanged notional denomination;
- CRYPTO/FOREX/GOLD and Linear/Inverse coverage;
- no guessed exchange-specific tiers/rates/offsets;
- fail-closed invalid, ambiguous, stale, contradictory, unsupported, or missing critical terms;
- no threshold reduction, test weakening, skip/xfail, or dependency-boundary weakening.

The next authorized Phase 1 unit is **position side and position mode semantics**. No Phase 2+ production implementation is authorized before the preceding Phase 1 exit criteria are evidenced.


## Phase 1 position side / position mode semantic lock

Maintenance-margin semantics are closed. The next Phase 1 unit is position side and position mode semantics.

Frozen baseline:
- owner: Futures domain/contract boundary;
- position side vocabulary: explicit LONG or SHORT only;
- position mode vocabulary: explicit ONE_WAY or HEDGE only;
- both are immutable, exchange-independent boundary vocabulary;
- ONE_WAY means one net position side at a time; HEDGE permits independently addressed LONG and SHORT positions;
- BOTH, NET, Spot, or implicit third states are rejected by the canonical contract;
- mode and side must be explicitly supplied; neither may be inferred from exchange/account state, order payloads, leverage, margin, or strategy behavior;
- exact financial calculation is not performed by this vocabulary contract;
- applicable to CRYPTO Futures, FOREX Futures, and GOLD Futures, and to Linear and Inverse Futures;
- no network, exchange SDK, persistence, runtime configuration, clock, notification, or account mutation dependency;
- invalid, missing, contradictory, unsupported, or ambiguous values fail closed;
- exchange-specific mapping may translate external mode/side representations only at infrastructure boundaries and may not redefine canonical meaning;
- meaningful contract tests, CI enforcement, and same-SHA evidence are required before the cursor advances.

Production boundaries: contracts/futures/position_side.py, contracts/futures/position_mode.py.
Test boundary: tests/contracts/test_position_side_mode.py.
CI boundary: .github/workflows/phase1-domain-contracts.yml.
