# FuturesOnlyEliteEngine

Elite Futures-Only Professional Trading Engine — production-grade architecture for CRYPTO, FOREX, and GOLD futures across Linear and Inverse contracts, with strict risk, execution, validation, and quality gates.

## Architecture

Governance and constitutional controls:
- `docs/architecture/architecture-invariants.md`
- `docs/architecture/project-state.md`
- `docs/architecture/adr/README.md`

## Architecture baseline

The project is being built from architecture-first principles. Production implementation does not begin until ownership and dependency boundaries are explicit.

### Authoritative architecture and project-control documents

- [Master Roadmap & Architecture Governance](docs/architecture/master-roadmap-and-governance.md)
- [Architecture Contract](docs/architecture/architecture-contract.md)
- [Futures Responsibility Map](docs/architecture/futures-responsibility-map.md)
- [Dependency Rules](docs/architecture/dependency-rules.md)

### Non-negotiable scope

- Futures-only; no operational Spot path.
- CRYPTO, FOREX, and GOLD.
- Linear and Inverse Futures with explicit semantic separation.
- 15 independent exchange adapters.
- Fail-closed risk and execution boundaries.
- Single Responsibility at module level.
- No placeholder, simulation, random logic, fake success, or test weakening.

### Quality gates

- G01 Format/Lint
- G02 Typecheck
- G03 Unit/Contract
- G04 Architecture/Dependency
- G05 Coverage: **>= 98% official minimum**
- G06 Security/Supply Chain
- G07 Integration/Resilience
- G08 Release/Mutation: **>= 90% mutation minimum**

Quality is established by evidence, not by gate manipulation.
