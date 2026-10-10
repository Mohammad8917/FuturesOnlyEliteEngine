"""Contract regression tests for the authoritative dependency rules."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "docs" / "architecture" / "dependency-rules.md"


REQUIRED_MARKERS = (
    "Infrastructure must never become a dependency of domain.",
    "Domain owns pure Futures financial semantics.",
    "Risk owns policy decisions and risk acceptance/rejection.",
    "No execution layer exists in the product; signal lifecycle/audit owns signal state only and cannot submit orders.",
    "Infrastructure owns read-only market-data transport and mapping only.",
    "Strategy/analysis owns analytical decisions only and cannot submit orders.",
    "Configuration/security owns validation and secret boundaries; only read-only market-data credentials are permitted",
    "Observability/notification owns reporting/delivery only; it cannot authorize trading.",
    "If a responsibility cannot be assigned to exactly one primary owner, implementation is blocked until ownership is resolved.",
    "Domain modules must not import exchange SDKs, HTTP clients, database clients, message brokers",
    "Risk logic must not place orders or mutate exchange state.",
    "Analysis/strategy logic must not submit orders, call execution adapters, or silently mutate positions.",
    "Notification code must not authorize, retry into, or represent execution success.",
    "Configuration code must not silently change Futures/Spot scope, risk policy, provider identity, or introduce live execution/order-write authority.",
    "hard-coded credentials, API keys, tokens, passwords, private/signing keys",
    "No dependency may introduce Spot instrument types, Spot provider routes, Spot order endpoints, Spot market scopes, permissive futures-false switches, or Futures-to-Spot fallback.",
    "A provider failure must fail closed, never downgrade market type.",
    "Stale, malformed, contradictory, incomplete, or out-of-order critical data must not flow into executable decisions.",
    "Signal lifecycle must detect duplicate/out-of-order transitions and invalidate signals on stale or contradictory critical data; no dependency may convert uncertainty into a valid signal.",
)


def test_authoritative_dependency_rules_are_present_and_nonempty() -> None:
    assert RULES.is_file()
    assert RULES.read_text(encoding="utf-8").strip()


def test_dependency_rules_contain_non_negotiable_boundaries() -> None:
    text = RULES.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    assert not missing, "Missing dependency-rule requirements: " + ", ".join(missing)
