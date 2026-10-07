# Dependency Rules

## Authoritative direction

The dependency graph is intentionally one-directional:

domain -> contracts where contracts are domain-safe
application -> domain + contracts
risk -> domain + contracts
execution -> contracts + domain facts + risk decisions
infrastructure -> application/contracts/domain ports as required

Infrastructure must never become a dependency of domain.

## Forbidden dependencies

Domain modules must not import exchange SDKs, HTTP clients, database clients, message brokers, environment/config loaders, filesystem APIs, nondeterministic random values, retry/backoff transport logic, or external side effects.

Risk logic must not place orders or mutate exchange state.

Analysis/strategy logic must not submit orders, call execution adapters, or silently mutate positions.

## Exchange isolation

Exchange-specific identifiers and semantics stop at the infrastructure boundary.

Domain code must not use exchange-name conditionals to implement transport behavior. Exchange-specific mapping belongs under infrastructure/exchanges/<exchange>/ and must remain independently testable.

## Futures-only boundary

No dependency may introduce Spot instrument types, Spot provider routes, Spot order endpoints, Spot market scopes, permissive futures-false switches, or Futures-to-Spot fallback.

A provider failure must fail closed, never downgrade market type.

## Architecture tests must prove

- domain does not import infrastructure;
- domain does not import exchange SDKs;
- strategy does not import execution adapters;
- risk does not submit orders;
- Spot is not an operational dependency;
- exchange-specific code remains outside domain;
- Linear and Inverse are explicit contract semantics.
