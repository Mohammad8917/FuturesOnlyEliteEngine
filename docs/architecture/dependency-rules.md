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
