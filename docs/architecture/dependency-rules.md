# Dependency Rules

## Authoritative direction

The dependency graph is intentionally one-directional and must be read together with ARCHITECTURE-MASTER-INDEX.md:

DOMAIN → CONTRACTS (only where contracts are domain-safe)
APPLICATION → DOMAIN + CONTRACTS
RISK → DOMAIN + CONTRACTS
EXECUTION → CONTRACTS + DOMAIN FACTS + RISK DECISIONS
INFRASTRUCTURE → APPLICATION / CONTRACTS / DOMAIN PORTS
OBSERVABILITY / NOTIFICATION → EXPLICIT OUTPUT PORTS; NEVER UPSTREAM AUTHORITY

Infrastructure must never become a dependency of domain.

## Boundary ownership

- Domain owns pure Futures financial semantics.
- Contracts own stable boundary vocabulary and validation semantics.
- Application owns use-case orchestration.
- Risk owns policy decisions and risk acceptance/rejection.
- Execution owns execution intent, gated order lifecycle, reconciliation, and audit.
- Infrastructure owns external transport and exchange mapping.
- Market/data acquisition owns external data retrieval and normalization through explicit ports; it does not own risk or execution decisions.
- Strategy/analysis owns analytical decisions only and cannot submit orders.
- Configuration/security owns configuration validation, credential handling, secret boundaries, and execution-authority configuration.
- Observability/notification owns reporting/delivery only; it cannot authorize trading.
- Architecture tests and CI enforce boundaries; they do not become financial-domain owners.

If a responsibility cannot be assigned to exactly one primary owner, implementation is blocked until ownership is resolved.

## Allowed dependency details

Domain may depend only on domain-safe contracts and standard deterministic language facilities. Domain must not depend on runtime configuration, I/O, clocks with uncontrolled behavior, transport, persistence, exchange SDKs, or notification systems.

Application may depend on domain and contracts and may depend on explicit ports for external capabilities. It must not encode exchange-specific transport.

Risk may consume validated domain/account/data facts and policy/configuration inputs through explicit contracts. Risk may return decisions, but it may not create or submit orders, call exchange transport, or mutate exchange state.

Execution may consume validated signal/intent contracts, domain facts, and risk decisions. Execution may invoke explicit exchange ports only after the execution risk gate. Unknown external state must remain unknown.

Infrastructure may implement ports and adapt external systems. Infrastructure may not redefine domain financial semantics or bypass risk/execution boundaries.

Observability/notification is downstream. It must never be a dependency that determines whether an order is authorized, accepted, or considered successful.

## Forbidden dependencies

Domain modules must not import exchange SDKs, HTTP clients, database clients, message brokers, environment/config loaders, filesystem APIs, nondeterministic random values, retry/backoff transport logic, or external side effects.

Risk logic must not place orders or mutate exchange state.

Analysis/strategy logic must not submit orders, call execution adapters, or silently mutate positions.

Notification code must not authorize, retry into, or represent execution success.

Configuration code must not silently change Futures/Spot scope, risk policy, exchange identity, or execution authority.

## Configuration, hardcoding, and secret boundary

Configuration/security is the sole owner of loading, validating, and providing operational configuration and secret material.

Forbidden:
- hard-coded credentials, API keys, tokens, passwords, private/signing keys, secret connection strings, or real account identifiers;
- hard-coded environment/deployment/account-specific operational settings inside domain, application, risk, execution, exchange adapters, tests, or documentation;
- source-code defaults that silently substitute for missing safety-critical configuration;
- tests or fixtures containing production secrets or realistic credential material.

Allowed only when genuinely immutable:
- canonical domain vocabulary;
- true protocol/contract invariants whose value cannot vary by environment, account, deployment, or exchange configuration.

Architecture/security tests and CI must enforce this boundary. Configuration may provide values to authorized consumers, but it must not grant execution authority merely by being present.

## Exchange isolation

Exchange-specific identifiers and semantics stop at the infrastructure boundary.

Domain code must not use exchange-name conditionals to implement transport behavior. Exchange-specific mapping belongs under infrastructure/exchanges/<exchange>/ and must remain independently testable.

## Futures-only boundary

No dependency may introduce Spot instrument types, Spot provider routes, Spot order endpoints, Spot market scopes, permissive futures-false switches, or Futures-to-Spot fallback.

A provider failure must fail closed, never downgrade market type.

## Data and state safety

Critical external data must carry validation/provenance/freshness semantics before use at financial boundaries.

Stale, malformed, contradictory, incomplete, or out-of-order critical data must not flow into executable decisions.

Order and position reconciliation must detect divergence and unknown state; no dependency may convert uncertainty into success.

## Phase 1 domain-contract dependency boundary

The instrument identity and canonical Futures symbol unit and multiplier/contract-specification unit are complete on the current main lineage. The next Phase 1 implementation unit is **leverage vocabulary and contract-level constraints**.

Ownership:
- domain/futures owns the pure financial meaning of multiplier and contract-size semantics.
- contracts/futures owns stable boundary vocabulary and validation semantics.
- infrastructure/exchanges/<exchange> may map exchange-specific contract metadata into the canonical contract, but may not redefine multiplier meaning or introduce Spot semantics.
- application, strategy, risk, and execution may consume the validated contract but may not create competing multiplier or contract-size rules.

Allowed dependencies remain deterministic standard-library/domain-safe facilities and domain-safe contracts only. The unit must not depend on exchange SDKs, HTTP clients, persistence, runtime configuration loaders, clocks, environment-specific values, or notification systems.

Linear/Inverse applicability and market applicability must be explicit. Unknown, zero, negative, contradictory, stale, unsupported, or ambiguous specifications must fail closed. The downstream contract cursor advances only after production implementation, meaningful contract tests, CI enforcement, and same-SHA evidence.

## Architecture tests must prove

- domain does not import infrastructure;
- domain does not import exchange SDKs;
- strategy does not import execution adapters;
- risk does not submit orders;
- execution cannot bypass risk validation;
- Spot is not an operational dependency;
- exchange-specific code remains outside domain;
- Linear and Inverse are explicit contract semantics;
- market/data boundaries cannot place orders;
- notification/observability cannot authorize execution;
- configuration cannot silently alter execution authority;
- critical dependencies respect the single-owner responsibility map.

## Multiplier / contract-specification dependency boundary

The multiplier and contract-specification contract is owned by the Futures domain/contract boundary. It may depend only on domain-safe vocabulary and deterministic standard-library numeric facilities.

Allowed:
- canonical Futures instrument identity;
- explicit market and Linear/Inverse vocabulary;
- exact Decimal arithmetic;
- immutable value objects.

Forbidden:
- exchange SDKs or transports;
- network, persistence, runtime configuration, clocks, or notifications;
- exchange-specific defaults;
- binary-float financial calculations;
- implicit margin, leverage, settlement, or precision policy.

Infrastructure maps exchange metadata into the canonical specification. It must reject incomplete or contradictory metadata rather than redefine the multiplier semantics.

## Phase 1 cursor after multiplier closure

Multiplier/contract specification is a closed domain contract with verified implementation and CI evidence. The next dependency-boundary unit is settlement asset and settlement semantics. Settlement logic must consume the explicit multiplier contract and may not redefine it.
\n## Settlement asset / settlement semantics dependency boundary

Settlement semantics are owned by the Futures domain/contract boundary. The contract may consume only canonical instrument identity, explicit market vocabulary, immutable value objects, and exact Decimal arithmetic.

Allowed:
- canonical Futures symbol settlement asset;
- explicit source asset;
- exact positive finite Decimal conversion rate;
- deterministic conversion.

Forbidden:
- exchange SDKs, HTTP/network, persistence, clocks, scheduling, runtime configuration, account mutation, or notifications;
- exchange-specific defaults;
- implicit conversion rates;
- guessed settlement denomination.

Infrastructure may supply a validated source asset and externally obtained conversion rate through a later port, but the domain contract must reject missing or contradictory values.
\n## Phase 1 cursor after settlement closure

Settlement semantics are closed with same-SHA evidence on main. The next dependency-boundary unit is margin asset and margin semantics. Margin must consume explicit instrument and settlement contracts without redefining their meaning.


## Phase 1 margin asset / margin semantics dependency boundary

Margin semantics are owned by the Futures domain/contract boundary. The margin contract may consume only the canonical Futures instrument identity, explicit market vocabulary, immutable value objects, and exact Decimal arithmetic. It may use already-closed settlement facts only as domain facts; it must not redefine settlement semantics.

Required margin inputs are explicit:
- canonical instrument identity, including its authoritative margin asset;
- source asset for any upstream margin amount;
- exact positive finite Decimal conversion rate only when source and margin assets differ.

Forbidden dependencies remain exchange SDKs, network I/O, persistence, clocks, runtime configuration, notifications, hidden defaults, leverage inference, and exchange-specific collateral policy. A margin contract must never silently substitute settlement asset for margin asset.


## Phase 1 leverage dependency boundary

Leverage vocabulary and contract-level constraints are owned by the Futures domain/contract boundary. The contract may consume canonical instrument identity and explicit margin facts as domain inputs but may not redefine their semantics.

Leverage configuration must be explicit, validated, provenance-aware, and fail closed. Exchange SDKs, network I/O, persistence, runtime configuration access, hidden defaults, risk policy, and execution mutation are forbidden dependencies of the canonical leverage contract.

## Phase 1 leverage contract dependency boundary

The leverage contract owns only leverage vocabulary and explicit contract-level bounds. It may consume canonical Futures instrument identity and explicit market vocabulary.

Required inputs are explicit: canonical instrument identity; matching market; leverage unit RATIO; requested leverage; positive minimum leverage; positive maximum leverage.

Forbidden dependencies remain exchange SDKs, network I/O, persistence, runtime configuration, clocks, notifications, hidden exchange defaults, account state, margin calculation, risk policy, position sizing, and liquidation logic.

No caller may omit bounds and rely on an exchange or runtime default. The domain contract fails closed instead.
