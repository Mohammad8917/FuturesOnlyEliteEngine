"""Canonical Futures margin-asset and margin-denomination semantics.

This module defines the asset denomination and explicit conversion boundary
for margin amounts. It does not calculate initial/maintenance margin,
leverage, liquidation, risk limits, or exchange-specific collateral policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from contracts.futures.instrument import (
    CanonicalFuturesSymbol,
    FuturesInstrumentIdentity,
    InstrumentValidationError,
    Market,
)


class MarginValidationError(InstrumentValidationError):
    """Raised when margin terms are invalid or ambiguous."""


class MarginUnit(StrEnum):
    """Canonical margin quantity denomination."""

    ASSET = "ASSET"


def _asset(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise MarginValidationError(f"{field} must be an asset symbol")
    value = value.strip().upper()
    if not value or value.startswith("SPOT") or not value.replace("_", "").isalnum():
        raise MarginValidationError(f"{field} must be a valid Futures asset")
    return value


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if type(value) not in (Decimal, int, str):
        raise MarginValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MarginValidationError(f"{field} must be an exact Decimal value") from exc
    if not result.is_finite() or result <= 0:
        raise MarginValidationError(f"{field} must be finite and greater than zero")
    return result


@dataclass(frozen=True, slots=True)
class FuturesMarginSpecification:
    """Immutable margin denomination and conversion contract.

    The canonical instrument identity is authoritative for margin_asset.
    source_asset is the explicit denomination of an upstream margin amount.
    Same-asset amounts require no conversion. Cross-asset amounts require an
    explicit positive finite rate expressed as margin-asset units per one
    source-asset unit.

    This contract deliberately does not infer leverage, initial margin,
    maintenance margin, liquidation, or exchange-specific collateral rules.
    """

    market: Market
    instrument: FuturesInstrumentIdentity
    margin_unit: MarginUnit
    margin_asset: str
    source_asset: str
    conversion_rate: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise MarginValidationError("market must be a supported Futures market")
        if not isinstance(self.instrument, FuturesInstrumentIdentity):
            raise MarginValidationError("instrument must be FuturesInstrumentIdentity")
        if self.instrument.market is not self.market:
            raise MarginValidationError("market must match the instrument identity")
        if not isinstance(self.margin_unit, MarginUnit):
            raise MarginValidationError("margin_unit must be ASSET")

        margin_asset = _asset(self.margin_asset, "margin_asset")
        source_asset = _asset(self.source_asset, "source_asset")

        if margin_asset != self.instrument.margin_asset:
            raise MarginValidationError(
                "margin_asset must equal the canonical instrument margin asset"
            )

        if margin_asset == source_asset:
            if self.conversion_rate is not None:
                raise MarginValidationError(
                    "conversion_rate must be absent when source and margin assets match"
                )
        else:
            if self.conversion_rate is None:
                raise MarginValidationError(
                    "conversion_rate is required when source and margin assets differ"
                )
            rate = _positive_decimal(self.conversion_rate, "conversion_rate")
            object.__setattr__(self, "conversion_rate", rate)

        object.__setattr__(self, "margin_asset", margin_asset)
        object.__setattr__(self, "source_asset", source_asset)

    @property
    def symbol(self) -> CanonicalFuturesSymbol:
        return self.instrument.symbol

    @property
    def conversion_required(self) -> bool:
        return self.source_asset != self.margin_asset

    def to_margin_amount(self, amount: Decimal | int | str) -> Decimal:
        """Convert a positive source-asset amount into margin-asset units."""
        value = _positive_decimal(amount, "amount")
        if not self.conversion_required:
            return value
        if self.conversion_rate is None:
            raise MarginValidationError(
                "conversion_rate invariant is missing for cross-asset margin"
            )
        return value * self.conversion_rate
