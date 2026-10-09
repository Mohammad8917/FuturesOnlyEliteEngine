# Proposal: Financial Audit Port Contract and Fail-Closed Consumption Boundary

**Status:** PROPOSED — open for architecture review; not approved  
**Date:** 2026-10-10  
**Proposer/Owner:** Repository owner request, recorded for review  
**Scope:** Governance proposal only. No runtime implementation is authorized by this document.

> **CRITICAL ARCHITECTURE WARNING**
>
> The current financial-arithmetic proposal (ADR-0003) requires explicit audit records at rounding boundaries, but the current main-branch search did not establish an approved executable Audit Port contract or a verified durable audit implementation. Connecting domain calculations directly to persistence, logging I/O, an exchange SDK, or an unapproved port would violate the pure-domain/dependency boundary. Conversely, allowing Risk, Execution, or account mutation to consume an audit-required result before durable audit confirmation could permit unaudited financial actions. This is an unresolved architecture boundary, not permission to invent a port or silently add I/O.

## 1. Problem

The repository needs a precise, testable boundary for recording financially material calculation and policy decisions, especially explicit rounding/quantization boundaries described by ADR-0003. The contract must support durable audit evidence, retries, idempotency, failure recovery, and safe behavior when the persistence outcome is unknown—without introducing I/O into `domain/futures/`.

The latest reviewed candidate PR #42 also moves financial calculations to `domain/futures/`. This proposal does not resolve or override the separate frozen Source-of-Truth path mismatch documented on PR #42.

## 2. Current Architecture and Evidence

- Canonical financial calculations are intended to remain deterministic and free of network, persistence, clock, notification, exchange SDK, and account-mutation dependencies.
- ADR-0003 proposes four explicit rounding helpers: `round_pnl()`, `round_funding()`, `round_margin_ratio()`, and `round_liquidation_price()`, and requires audit records at those boundaries.
- A read-only search of the current default branch for `audit port`, `outbox`, and `AuditEvent` did not establish an approved executable port or durable implementation. This is a bounded search finding, not proof that no related code exists anywhere in every branch.
- The ADR process in `docs/architecture/adr/README.md` is mandatory. A proposal is not approval.
- No protected architecture source-of-truth file is modified by this proposal.

## 3. Proposed Change

Establish a versioned, application-facing **Financial Audit Port contract** and a durable infrastructure implementation only after explicit owner approval. Domain calculations remain pure. The application/service boundary records the calculation facts and controls whether an audit-required result may be consumed by Risk, Execution, or account mutation.

The contract should define, at minimum:

1. **Ownership and dependency direction**
   - Domain calculation functions return deterministic results and do not call the audit port.
   - An application/use-case boundary coordinates calculation, audit persistence, and downstream consumption.
   - Infrastructure implements the approved port; domain code must not import persistence, transport, logging backends, clocks, or infrastructure adapters.
   - The port must not be smuggled into the domain as a generic callback that permits arbitrary I/O.

2. **Versioned event schema**
   - Stable schema name and version; explicit event type and calculation/rounding boundary.
   - Stable event ID and idempotency key, with explicit correlation and causation identifiers.
   - Canonical instrument/market/contract family and denomination/asset unit where relevant.
   - Exact input/output financial values serialized as canonical decimal strings—not binary floats.
   - Explicit rounding mode and scale/tick policy identifier where applicable; no invented tick size or exchange metadata.
   - Explicit policy/configuration version and a UTC event/observation timestamp supplied at the approved application boundary.
   - Outcome and reason code for success, rejection, or failure.
   - No secrets, API keys, credentials, or unnecessary personal data in audit payloads.

3. **Durability and idempotency semantics**
   - Same key + same canonical payload must be safely idempotent.
   - Same key + conflicting payload must fail closed and raise an auditable conflict; it must not overwrite the original event.
   - Timeout or connection loss after a write must be treated as **INDETERMINATE**, not assumed failed or successful.
   - An indeterminate result must be reconciled by stable event identity before retry or downstream consumption; no blind duplicate writes and no optimistic success.
   - Concurrency, ordering/scope, restart recovery, and retention/availability guarantees must be explicitly defined before implementation.

4. **Consumption boundary**
   - Pure computation may produce an in-memory deterministic candidate result, but that result is not authorization to execute or mutate an account.
   - Where audit is mandatory for a financial action, Risk/Execution/account mutation must not consume the result until durable audit confirmation is established.
   - Audit failure or indeterminate persistence must stop the affected action. Recovery/reconciliation must resolve the event before resuming.
   - The implementation must not silently convert an audit outage into success, drop the audit record, or use an in-memory-only queue as evidence of durable recording.
   - The ADR must explicitly decide whether every calculation, only policy/rounding decisions, or only action-authorizing decisions require synchronous durable confirmation. Do not assume all calculation paths require the same policy.

5. **Failure taxonomy**
   - At minimum distinguish `PENDING`, `CONFIRMED`, `FAILED`, and `INDETERMINATE` at the application/infrastructure boundary.
   - `CONFIRMED` means the persistence contract's stated durability guarantee was met—not merely that a method returned without raising.
   - Unknown status, malformed response, schema mismatch, identity conflict, unavailable store, and unresolvable recovery state fail closed for any audit-gated action.

## 4. Why Current Architecture Is Insufficient

The current rules correctly prohibit I/O in the domain, but ADR-0003's audit requirement needs an explicit owner, schema, persistence guarantee, idempotency contract, and application-level consumption rule. Without those details, implementers could accidentally add domain I/O, log incomplete or non-reproducible financial values, double-record after timeouts, or allow financial actions despite uncertain audit state.

## 5. Alternatives Considered

### A. Direct logging/persistence from domain calculations — REJECT

Violates domain purity and dependency direction, makes deterministic functions operationally coupled, and risks leaking sensitive data. It must not be implemented.

### B. Best-effort logging with execution continuing on audit failure — REJECT for audit-gated actions

It cannot guarantee required evidence and may permit unaudited financial actions. It may only be considered for explicitly non-authoritative diagnostics under a separate approved policy, never as a substitute for mandatory financial audit.

### C. Application-level Audit Port with durable adapter — CANDIDATE

Preserves domain purity and makes persistence/failure semantics testable. Requires explicit contract and durable implementation evidence.

### D. Transactional Outbox — INVESTIGATE, NOT PRESELECTED

An Outbox may be appropriate if the relevant business state and audit intent can be committed atomically in the same transactional store. If no shared transaction exists, an Outbox alone does not prove atomicity or guarantee that a calculation was durably audited before an external side effect. Review the actual transaction boundary, delivery semantics, ordering, recovery, and operational dependencies before choosing it.

### E. Synchronous durable write before action — INVESTIGATE

May provide a clear gate when no shared transaction exists, but needs explicit latency, availability, retry, timeout, and indeterminate-outcome semantics. It must not be described as atomic with an external exchange action unless that guarantee is actually achievable.

The ADR must document the chosen alternative and why it matches the actual persistence and execution boundaries. Do not implement Outbox or another pattern merely because it is familiar.

## 6. Affected Invariants

Potentially affected and requiring explicit impact review:

- Domain purity and dependency direction.
- Exact Decimal and explicit rounding policy.
- Fail-closed Risk/Execution/reconciliation.
- Idempotency, replay, ordering, and state reconciliation.
- No hidden defaults, unapproved I/O, or exchange-specific assumptions.
- Futures-only applicability and explicit Linear/Inverse and CRYPTO/FOREX/GOLD semantics.
- No weakening of CI floors or tests.
- Phase 2+ implementation and release gates remain in force.

This proposal does not change any invariant by itself.

## 7. Affected Contracts and Dependencies

Review must identify the exact call sites and owners for:
- ADR-0003 rounding helpers and other financial audit-worthy decisions;
- application/use-case coordination;
- Risk and Execution consumption boundaries;
- persistence adapter and transaction boundary;
- event schema/versioning and stable identity;
- recovery/reconciliation workflows;
- approved logging/metrics ports, if any, without treating diagnostics as durable audit.

No specific database, queue, Outbox technology, exchange, clock provider, or infrastructure package is selected here.

## 8. Required Tests and Gates

Before approval of implementation, define and add tests for:

- Domain purity: no audit I/O or infrastructure imports in domain modules.
- Event schema required fields, schema version, canonical Decimal encoding, units/denomination, and prohibited sensitive fields.
- Stable event identity, idempotent same-payload retry, and conflicting-payload rejection.
- Persistence success, explicit failure, timeout-before-write, timeout-after-write, malformed response, and indeterminate outcomes.
- No Risk/Execution/account mutation consuming an audit-gated result before confirmation.
- Recovery/reconciliation after restart and after indeterminate writes.
- Concurrent duplicate requests, ordering/state-version conflicts, and replay behavior.
- Adapter contract tests proving the documented durability guarantee.
- Outbox atomicity/delivery/recovery tests only if Outbox is explicitly selected.
- Regression tests proving no test skips/xfails, assertion weakening, threshold reduction, or bypass of existing gates.

Required existing quality floors remain unchanged: G01–G05 at least 98%; G06, G07, and G08 mutation at least 90% where applicable. Operational G07 skipped/not applicable must not be represented as a pass. Relevant CI must be checked on the exact final candidate SHA.

## 9. Risk Analysis

- **Domain coupling:** mitigated by keeping the port outside domain and enforcing dependency tests.
- **Duplicate or conflicting audit events:** mitigated by stable idempotency keys and conflict detection.
- **Unknown write outcome:** mitigated by explicit INDETERMINATE state and reconciliation before consumption.
- **Audit outage halting financial actions:** an intentional fail-closed trade-off for audit-gated actions; availability policy and operator recovery must be documented, not bypassed.
- **False durability claims:** mitigated by adapter contract tests and documented storage guarantees.
- **Sensitive data leakage:** mitigated by schema allowlisting and redaction tests.
- **Outbox mistaken for universal solution:** mitigated by deciding only after the real transaction boundary is mapped.
- **Cross-PR drift:** implementation must be checked against ADR-0003, PR #42's ownership candidate, and the frozen Source-of-Truth mismatch without modifying protected documents.

## 10. Migration Plan (Proposed)

1. Complete a read-only call-site and dependency audit; enumerate every audit-required decision and its consumer.
2. Map the real persistence and external-side-effect transaction boundaries.
3. Compare synchronous durable write, transactional Outbox where applicable, and other viable alternatives.
4. Draft the formal ADR with a selected contract, exact failure semantics, schema, idempotency, durability promise, and operational recovery procedure.
5. Present the impact analysis and **CRITICAL ARCHITECTURE WARNING** to the repository owner.
6. Obtain explicit owner reconfirmation of the exact ADR and selected alternative.
7. Only after approval, update any architecture documents through the authorized governance path; do not silently modify protected source-of-truth files.
8. Implement the port and infrastructure adapter outside the domain, then add contract, failure-injection, recovery, and dependency tests.
9. Run required gates without weakening policy; verify all applicable evidence on the same final SHA.
10. Close the blocker only after code, tests, docs, and CI evidence agree.

## 11. Rollback Plan (Proposed)

- Keep the proposal and implementation in a separate branch/PR until approved.
- If tests reveal unsafe semantics, revert the implementation commit or disable the new integration at the application boundary while preserving fail-closed behavior; do not restore best-effort audit for mandatory actions.
- Do not roll back by adding I/O to the domain, skipping tests, reducing thresholds, or bypassing Risk/Execution gates.
- Preserve audit records already durably written; any repair/replay must use stable identity and explicit reconciliation rather than deleting conflicting evidence.

## 12. Explicit Approval / Reconfirmation

**NOT APPROVED.** The owner's instruction to continue authorizes preparing this proposal for review only. It does not approve the final port contract, select Outbox, authorize implementation, change protected architecture documents, or authorize Phase 2+.

Required future decision:
- Approve, reject, or request changes to the formal ADR.
- Explicitly select or reject the proposed durability/consumption policy and implementation alternative after the transaction-boundary analysis.
- Reconfirm before protected documentation changes and before implementation.

Until then, keep the audit integration blocker **OPEN**. Do not connect financial calculations to an unapproved audit port, do not let audit-gated results authorize Risk/Execution/account mutation before durable confirmation, and do not claim implementation, CI green, or closure.
