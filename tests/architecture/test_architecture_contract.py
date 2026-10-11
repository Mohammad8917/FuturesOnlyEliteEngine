"""Contract regression tests for the authoritative architecture contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "architecture" / "architecture-contract.md"


REQUIRED_MARKERS = (
    "production-grade, Futures-only",
    "CRYPTO Futures",
    "FOREX Futures",
    "GOLD Futures",
    "Linear Futures",
    "Inverse Futures",
    "read-only market-data access",
    "Python version: 3.13",
    "Windows Server",
    "Linux Server",
    "Windows Home/Desktop",
    "permanent signal-only product",
    "Telegram and email",
    "Notifications are delivery-only and cannot authorize or execute trades",
    "Secrets and sensitive values must never be embedded",
    "typed validation, provenance, and fail-closed behavior",
    "idempotency and unknown-state handling",
    "append-only/tamper-evident audit",
    "G01 Format/Lint",
    "G05 Coverage",
    "G08 Release/Mutation",
    ">= 98%",
    ">= 90%",
    "Unknown, invalid, stale, contradictory, or incomplete critical Futures state",
    "ARCHITECTURE RULE → CONTRACT → PRODUCTION IMPLEMENTATION → TEST → CI ENFORCEMENT → SAME-SHA EVIDENCE",
    "Live automated trading, live order writes, and account mutation are permanently prohibited.",
)


def test_authoritative_architecture_contract_is_present_and_nonempty() -> None:
    assert CONTRACT.is_file()
    assert CONTRACT.read_text(encoding="utf-8").strip()


def test_architecture_contract_contains_non_negotiable_requirements() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    assert not missing, "Missing architecture-contract requirements: " + ", ".join(missing)
