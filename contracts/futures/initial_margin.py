"""Canonical Futures initial-margin requirement semantics.

This module defines a deterministic, exchange-independent initial-margin
requirement rate and its calculation from an explicit Futures notional.
It does not infer leverage, collateral policy, liquidation, risk limits,
or exchange-specific margin rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import FuturesInstrumentIdentity, Market


class InitialMarginValidationError(ValueError):
    """Raised when initial-margin terms are invalid or ambiguous."""


class InitialMarginUnit(StrEnum):
    """Canonical initial-margin requirement-rate denomination."""

    RATIO = "RATIO"


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if type(value) not in (Decimal, int, str):
        raise InitialMarginValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise InitialMarginValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise InitialMarginValidationError(
            f"{field} must be finite and greater than zero"
        )
    return result


def _asset(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise InitialMarginValidationError(f"{field} must be an asset symbol")
    normalized = value.strip().upper()
    if not normalized or normalized.startswith("SPOT"):
        raise InitialMarginValidationError(f"{field} must be a valid Futures asset")
    if not normalized.replace("_", "").isalnum():
        raise InitialMarginValidationError(f"{field} contains invalid characters")
    return normalized


@dataclass(frozen=True, slots=True)
class FuturesInitialMarginSpecification:
    """Immutable initial-margin requirement-rate contract.

    The caller supplies an already-canonicalized positive Futures notional
    and explicitly declares its denomination. The requirement amount is:

        initial_margin_amount = notional * initial_margin_ratio

    The result retains the notional denomination. This contract introduces
    no implicit rounding, conversion, leverage inference, or exchange rule.
    """

    market: Market
    instrument: FuturesInstrumentIdentity
    initial_margin_unit: InitialMarginUnit
    initial_margin_ratio: Decimal
    notional_asset: str

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise InitialMarginValidationError(
                "market must be a supported Futures market"
            )
        if not isinstance(self.instrument, FuturesInstrumentIdentity):
            raise InitialMarginValidationError(
                "instrument must be FuturesInstrumentIdentity"
            )
        if self.instrument.market is not self.market:
            raise InitialMarginValidationError(
                "market must match the instrument identity"
            )
        if not isinstance(self.initial_margin_unit, InitialMarginUnit):
            raise InitialMarginValidationError("initial_margin_unit must be RATIO")

        ratio = _positive_decimal(self.initial_margin_ratio, "initial_margin_ratio")
        notional_asset = _asset(self.notional_asset, "notional_asset")

        object.__setattr__(self, "initial_margin_ratio", ratio)
        object.__setattr__(self, "notional_asset", notional_asset)

    @property
    def symbol(self):
        """Return the canonical Futures symbol."""
        return self.instrument.symbol

    def calculate(self, notional: Decimal | int | str) -> Decimal:
        """Calculate initial margin in the notional's explicit denomination."""
        value = _positive_decimal(notional, "notional")
        return value * self.initial_margin_ratio
