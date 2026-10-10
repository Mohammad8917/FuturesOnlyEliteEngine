# FuturesOnlyEliteEngine

Elite Futures-Only Signal Engine — signal generation only for **CRYPTO Futures, FOREX Futures, and GOLD Futures**, with explicit Linear/Inverse semantics, read-only market data, Telegram/email signal delivery, strict validation, and quality gates.

**Runtime:** Python 3.13.  **Deployment targets:** Windows Server, Linux Server, and Windows Home/Desktop.

## Architecture

**Single navigation path:** `docs/architecture/ARCHITECTURE-MASTER-INDEX.md`

Start there. It defines the unified reading order, upgrade path, dependency path, responsibility path, and architecture-change path; it does not override the constitutional source-of-truth hierarchy.

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

- **100% Futures-only; no operational Spot path.**
- **CRYPTO Futures, FOREX Futures, and GOLD Futures — all three are Futures.**
- Permanent signal-only product; live order execution and account mutation are prohibited.
- Telegram and email signal/operational notifications.
- Python 3.13.
- Windows Server, Linux Server, and Windows Home/Desktop support.
- Linear and Inverse Futures with explicit semantic separation.
- Read-only market-data adapters only; supported providers are configured explicitly and never assumed.
- Fail-closed signal validation and advisory risk-estimation boundaries.
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

## Permanent signal-only boundary

The product never submits/amends/cancels/retries live orders, mutates real positions/accounts, changes leverage, transfers funds, allocates live capital, or exposes execution controls. Market-data access is read-only. Risk/position-size figures in a signal are advisory estimates, not guarantees. See [ADR-0006](docs/architecture/adr/ADR-0006-signal-only-product-scope.md).
