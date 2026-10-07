"""Architecture invariants document contract tests.

These tests validate the authoritative architecture constitution itself.
They do not claim runtime enforcement; runtime enforcement belongs to
production validators and architecture tests introduced with implementation.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVARIANTS = ROOT / "docs" / "architecture" / "architecture-invariants.md"


def test_authoritative_invariants_document_exists_and_is_nonempty() -> None:
    assert INVARIANTS.is_file()
    content = INVARIANTS.read_text(encoding="utf-8")
    assert content.strip()
    assert "AUTHORITATIVE / IMMUTABLE BY DEFAULT" in content


def test_constitution_covers_required_runtime_and_product_boundaries() -> None:
    content = INVARIANTS.read_text(encoding="utf-8")
    required = (
        "Python 3.13",
        "Windows Server",
        "Linux Server",
        "Windows Home/Desktop",
        "Futures only",
        "CRYPTO",
        "FOREX",
        "GOLD",
        "Linear Futures",
        "Inverse Futures",
        "Operational Spot is forbidden.",
        "15 independent exchange adapters",
    )
    for marker in required:
        assert marker in content, marker


def test_constitution_preserves_layer_and_fail_closed_boundaries() -> None:
    content = INVARIANTS.read_text(encoding="utf-8")
    required = (
        "Responsibility flow and source-code dependency direction are distinct concepts",
        "Domain remains infrastructure-independent.",
        "Strategy/analysis must not submit orders.",
        "Risk must not place orders.",
        "Execution must not bypass risk validation.",
        "Unknown, invalid, stale, contradictory, incomplete, or untrusted critical Futures state",
        "Required behavior is fail-closed.",
        "A generic implementation that erases meaningful exchange differences is forbidden.",
    )
    for marker in required:
        assert marker in content, marker


def test_constitution_covers_safety_critical_configuration_and_financial_state() -> None:
    content = INVARIANTS.read_text(encoding="utf-8")
    required = (
        "Credentials, API keys, signing material, passwords, tokens, private keys",
        "Configuration must fail closed",
        "Every executable intent must carry an immutable, unique idempotency identity",
        "Unknown order, fill, position, balance, or account state must block new execution",
        "execution authority must remain disabled until required account/order/position reconciliation completes successfully",
        "A scoped/global trading halt (kill switch/circuit breaker)",
        "Audit evidence must be append-only/tamper-evident",
    )
    for marker in required:
        assert marker in content, marker


def test_constitution_locks_quality_floor_and_no_fake_green() -> None:
    content = INVARIANTS.read_text(encoding="utf-8")
    required = (
        "G01: zero unexplained format/lint violations",
        "G05: >= 98% coverage",
        "G08: >= 90% mutation score",
        "No actor may lower, bypass, weaken, exclude, skip, xfail",
        "deleting tests to improve results",
        "artificial coverage",
        "fake success paths",
        "placeholder tests",
    )
    for marker in required:
        assert marker in content, marker


def test_constitution_requires_rule_to_implementation_to_evidence_chain() -> None:
    content = INVARIANTS.read_text(encoding="utf-8")
    required = (
        "ARCHITECTURE RULE",
        "CONTRACT",
        "PRODUCTION IMPLEMENTATION",
        "ARCHITECTURE TEST",
        "CI ENFORCEMENT",
        "EVIDENCE",
        "Documentation alone is insufficient.",
        "There is no emergency bypass for architectural safety.",
    )
    for marker in required:
        assert marker in content, marker


def test_constitution_contains_no_frozen_test_skeleton_marker() -> None:
    content = INVARIANTS.read_text(encoding="utf-8")
    assert "Frozen skeleton; executable implementation is intentionally deferred" not in content
