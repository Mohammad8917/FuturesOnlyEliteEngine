"""Canonical Futures maintenance-margin requirement semantics.

This module defines an explicit, exchange-independent maintenance-margin
requirement rate and its deterministic calculation from an explicit Futures
notional. It does not infer leverage, liquidation, risk policy, account
state, exchange tiers, or exchange-specific defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import CanonicalFuturesSymbol, FuturesInstrumentIdentity, Market


class MaintenanceMarginValidationError(ValueError):
    """Raised when maintenance-margin terms are invalid or ambiguous."""


class MaintenanceMarginUnit(StrEnum):
    """Canonical maintenance-margin requirement-rate denomination."""

    RATIO = "RATIO"


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if type(value) not in (Decimal, int, str):
        raise MaintenanceMarginValidationError(
            f"{field} must be an exact Decimal value"
        )
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MaintenanceMarginValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise MaintenanceMarginValidationError(
            f"{field} must be finite and greater than zero"
        )
    return result


def _asset(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise MaintenanceMarginValidationError(f"{field} must be an asset symbol")
    normalized = value.strip().upper()
    if not normalized or normalized.startswith("SPOT"):
        raise MaintenanceMarginValidationError(f"{field} must be a valid Futures asset")
    if not normalized.replace("_", "").isalnum():
        raise MaintenanceMarginValidationError(f"{field} contains invalid characters")
    return normalized


@dataclass(frozen=True, slots=True)
class FuturesMaintenanceMarginSpecification:
    """Immutable maintenance-margin requirement-rate contract.

    The caller supplies an already-canonicalized positive Futures notional
    and explicitly declares its denomination. The requirement amount is:

        maintenance_margin_amount = notional * maintenance_margin_ratio

    The result retains the notional denomination. No exchange-specific tier,
    rate, offset, rounding rule, leverage, or liquidation rule is inferred.
    """

    market: Market
    instrument: FuturesInstrumentIdentity
    maintenance_margin_unit: MaintenanceMarginUnit
    maintenance_margin_ratio: Decimal
    notional_asset: str

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise MaintenanceMarginValidationError(
                "market must be a supported Futures market"
            )
        if not isinstance(self.instrument, FuturesInstrumentIdentity):
            raise MaintenanceMarginValidationError(
                "instrument must be FuturesInstrumentIdentity"
            )
        if self.instrument.market is not self.market:
            raise MaintenanceMarginValidationError(
                "market must match the instrument identity"
            )
        if not isinstance(self.maintenance_margin_unit, MaintenanceMarginUnit):
            raise MaintenanceMarginValidationError(
                "maintenance_margin_unit must be RATIO"
            )

        ratio = _positive_decimal(
            self.maintenance_margin_ratio, "maintenance_margin_ratio"
        )
        notional_asset = _asset(self.notional_asset, "notional_asset")

        object.__setattr__(self, "maintenance_margin_ratio", ratio)
        object.__setattr__(self, "notional_asset", notional_asset)

    @property
    def symbol(self) -> CanonicalFuturesSymbol:
        """Return the canonical Futures symbol."""
        return self.instrument.symbol

    def calculate(self, notional: Decimal | int | str) -> Decimal:
        """Calculate maintenance margin in the notional's denomination."""
        value = _positive_decimal(notional, "notional")
        return value * self.maintenance_margin_ratio
