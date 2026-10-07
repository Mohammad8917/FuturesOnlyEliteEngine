"""Canonical Futures settlement-asset semantics.

This module defines denomination and explicit conversion semantics only.
It does not perform exchange settlement, account mutation, persistence,
network I/O, or scheduling.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import CanonicalFuturesSymbol, InstrumentValidationError, Market


class SettlementValidationError(InstrumentValidationError):
    """Raised when settlement terms are invalid or ambiguous."""


class SettlementUnit(StrEnum):
    """Canonical settlement quantity denomination."""

    ASSET = "ASSET"


def _asset(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise SettlementValidationError(f"{field} must be an asset symbol")
    value = value.strip().upper()
    if not value or value.startswith("SPOT"):
        raise SettlementValidationError(f"{field} must be a valid Futures asset")
    if not value.replace("_", "").isalnum():
        raise SettlementValidationError(f"{field} contains invalid characters")
    return value


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if isinstance(value, bool):
        raise SettlementValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise SettlementValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise SettlementValidationError(f"{field} must be finite and greater than zero")
    return result


@dataclass(frozen=True, slots=True)
class FuturesSettlementSpecification:
    """Immutable settlement denomination and conversion contract.

    settlement_asset is the authoritative settlement denomination declared
    by the canonical Futures instrument. source_asset identifies the asset
    in which an upstream settlement amount is expressed.

    If source and settlement assets are equal, no conversion is permitted or
    required. If they differ, an explicit conversion rate is mandatory and is
    defined as settlement-asset units per one source-asset unit.

    This contract never fetches a rate, selects an exchange, schedules a
    settlement event, or mutates account state.
    """

    market: Market
    symbol: CanonicalFuturesSymbol
    settlement_unit: SettlementUnit
    settlement_asset: str
    source_asset: str
    conversion_rate: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise SettlementValidationError("market must be a supported Futures market")
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise SettlementValidationError("symbol must be CanonicalFuturesSymbol")
        if not isinstance(self.settlement_unit, SettlementUnit):
            raise SettlementValidationError("settlement_unit must be ASSET")

        settlement_asset = _asset(self.settlement_asset, "settlement_asset")
        source_asset = _asset(self.source_asset, "source_asset")

        if settlement_asset != self.symbol.settlement_asset:
            raise SettlementValidationError(
                "settlement_asset must equal the canonical symbol settlement asset"
            )

        if settlement_asset == source_asset:
            if self.conversion_rate is not None:
                raise SettlementValidationError(
                    "conversion_rate must be absent when source and settlement assets match"
                )
        else:
            if self.conversion_rate is None:
                raise SettlementValidationError(
                    "conversion_rate is required when source and settlement assets differ"
                )
            rate = _positive_decimal(self.conversion_rate, "conversion_rate")
            object.__setattr__(self, "conversion_rate", rate)

        object.__setattr__(self, "settlement_asset", settlement_asset)
        object.__setattr__(self, "source_asset", source_asset)

    @property
    def conversion_required(self) -> bool:
        return self.source_asset != self.settlement_asset

    def settle_amount(self, amount: Decimal | int | str) -> Decimal:
        """Convert a positive source-asset amount into settlement-asset units."""
        value = _positive_decimal(amount, "amount")
        if not self.conversion_required:
            return value
        assert self.conversion_rate is not None
        return value * self.conversion_rate
