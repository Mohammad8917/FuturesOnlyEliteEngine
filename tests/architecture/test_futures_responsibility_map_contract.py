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
    "Live execution is prohibited; no execution contract, order lifecycle, or order-write adapter is part of the product.",
    "No generic adapter may erase meaningful exchange differences.",
    "Signal lifecycle owns signal state only; read-only market-data infrastructure supplies market observations",
    "Signal lifecycle owns duplicate suppression, version checks, restart recovery, and stale-signal invalidation.",
    "Stale, missing, contradictory, or unconfirmed market data remains unknown and blocks signal issuance or triggers invalidation.",
    "A dedicated time/clock boundary supplies UTC timestamps",
    "It has no order, account-mutation, or live execution authority.",
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
