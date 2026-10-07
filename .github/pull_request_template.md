## Architecture / Safety Gate

- [ ] I verified the current architecture source-of-truth before changing code.
- [ ] This change does not reintroduce operational Spot.
- [ ] This change preserves Linear/Inverse semantic separation.
- [ ] This change preserves fail-closed risk/execution/reconciliation behavior.
- [ ] No secrets, credentials, tokens, private keys, account identifiers, or environment-specific safety configuration are hard-coded.
- [ ] No test/gate/threshold was weakened, skipped, deleted, excluded, or bypassed.
- [ ] If architecture ownership, dependency direction, financial semantics, execution authority, or release criteria changed, an approved ADR exists.
- [ ] Required checks are evaluated on the exact PR HEAD before merge.

### Required evidence

PR:
HEAD SHA:
Gates/checks:
ADR (if applicable):
