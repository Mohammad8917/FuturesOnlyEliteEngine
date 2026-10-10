"""Contract regression tests for the authoritative Futures responsibility map."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "docs" / "architecture" / "futures-responsibility-map.md"

REQUIRED_MARKERS = (
    "The product is Futures-only.",
    "CRYPTO, FOREX, and GOLD",
    "Linear Futures and Inverse Futures are first-class contract families.",
    "Domain code contains business semantics",
    "Risk decisions are fail-closed.",
    "Execution is downstream of an explicit execution contract and risk gate.",
    "No generic adapter may erase meaningful exchange differences.",
    "Exchange-confirmed live account/order/position state is authoritative",
    "execution owns idempotency identity, duplicate suppression, concurrency/version checks, restart/failover recovery",
    "execution also owns the scoped/global trading halt boundary",
    "A dedicated time/clock boundary supplies UTC timestamps",
    "Audit evidence is owned by the execution/audit boundary and must be append-only/tamper-evident",
    "The configuration/security boundary owns all operational configuration and secret material.",
    "Telegram/email delivery",
    "Every primary owner must define inputs, outputs, units, precision, timestamps, validation state, failure behavior",
)


def test_authoritative_responsibility_map_is_present_and_nonempty() -> None:
    assert MAP.is_file()
    assert MAP.read_text(encoding="utf-8").strip()


def test_responsibility_map_contains_non_negotiable_ownership() -> None:
    text = MAP.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    assert not missing, "Missing responsibility-map requirements: " + ", ".join(missing)
