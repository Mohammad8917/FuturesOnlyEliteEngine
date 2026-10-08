"""Canonical Futures leverage vocabulary and contract-level constraints.

This module defines explicit leverage as a dimensionless ratio and validates
the requested leverage against explicit contract-level bounds. It does not
infer exchange defaults, account leverage, margin requirements, liquidation,
risk policy, or position sizing.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import FuturesInstrumentIdentity, Market


class LeverageValidationError(ValueError):
    """Raised when Futures leverage terms are invalid or ambiguous."""


class LeverageUnit(StrEnum):
    """Canonical leverage denomination."""

    RATIO = "RATIO"


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise LeverageValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise LeverageValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise LeverageValidationError(f"{field} must be finite and greater than zero")
    return result


@dataclass(frozen=True, slots=True)
class FuturesLeverageSpecification:
    """Immutable, explicit Futures leverage and contract-level bounds.

    leverage, minimum_leverage, and maximum_leverage are exact positive
    Decimal ratios. No bound has a hidden default. The requested leverage
    must be within the explicit inclusive interval.

    The contract applies to all supported Futures markets and both Linear and
    Inverse families because leverage denomination is independent of family.
    """

    market: Market
    instrument: FuturesInstrumentIdentity
    leverage_unit: LeverageUnit
    leverage: Decimal
    minimum_leverage: Decimal
    maximum_leverage: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise LeverageValidationError("market must be a supported Futures market")
        if not isinstance(self.instrument, FuturesInstrumentIdentity):
            raise LeverageValidationError(
                "instrument must be FuturesInstrumentIdentity"
            )
        if self.instrument.market is not self.market:
            raise LeverageValidationError("market must match the instrument identity")
        if not isinstance(self.leverage_unit, LeverageUnit):
            raise LeverageValidationError("leverage_unit must be RATIO")

        leverage = _positive_decimal(self.leverage, "leverage")
        minimum = _positive_decimal(self.minimum_leverage, "minimum_leverage")
        maximum = _positive_decimal(self.maximum_leverage, "maximum_leverage")

        if minimum > maximum:
            raise LeverageValidationError(
                "minimum_leverage must not exceed maximum_leverage"
            )
        if leverage < minimum or leverage > maximum:
            raise LeverageValidationError(
                "leverage must be within the explicit contract-level bounds"
            )

        object.__setattr__(self, "leverage", leverage)
        object.__setattr__(self, "minimum_leverage", minimum)
        object.__setattr__(self, "maximum_leverage", maximum)

    @property
    def is_within_contract_bounds(self) -> bool:
        return self.minimum_leverage <= self.leverage <= self.maximum_leverage
