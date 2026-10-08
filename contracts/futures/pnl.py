"""Canonical realized and unrealized Futures PnL semantics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import CanonicalFuturesSymbol, ContractFamily, Market
from .position_side import PositionSide


class PnLValidationError(ValueError):
    """Invalid, stale, unknown, or ambiguous PnL input."""


class PnLUnit(StrEnum):
    REALIZED_OR_UNREALIZED = "REALIZED_OR_UNREALIZED"


class PnLDenomination(StrEnum):
    QUOTE = "QUOTE"
    BASE = "BASE"


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise PnLValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise PnLValidationError(f"{field} must be an exact Decimal value") from exc
    if not result.is_finite() or result <= 0:
        raise PnLValidationError(f"{field} must be finite and greater than zero")
    return result


def _utc(value: datetime, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise PnLValidationError(f"{field} must be an aware UTC datetime")
    return value


@dataclass(frozen=True, slots=True)
class FuturesPnLSpecification:
    """Define canonical Linear/Inverse PnL calculations without account mutation."""

    market: Market
    symbol: CanonicalFuturesSymbol
    pnl_unit: PnLUnit

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise PnLValidationError("market must be a supported Futures market")
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise PnLValidationError("symbol must be CanonicalFuturesSymbol")
        if self.symbol.contract_family not in (
            ContractFamily.LINEAR,
            ContractFamily.INVERSE,
        ):
            raise PnLValidationError("unsupported contract family")
        if not isinstance(self.pnl_unit, PnLUnit):
            raise PnLValidationError("pnl_unit must be explicit")

    @property
    def denomination(self) -> PnLDenomination:
        if self.symbol.contract_family is ContractFamily.LINEAR:
            return PnLDenomination.QUOTE
        return PnLDenomination.BASE

    def _calculate(
        self,
        *,
        quantity: Decimal | int | str,
        multiplier: Decimal | int | str,
        entry_price: Decimal | int | str,
        reference_price: Decimal | int | str,
        position_side: PositionSide,
    ) -> Decimal:
        qty = _positive_decimal(quantity, "quantity")
        mult = _positive_decimal(multiplier, "contract_multiplier")
        entry = _positive_decimal(entry_price, "entry_price")
        reference = _positive_decimal(reference_price, "reference_price")
        if not isinstance(position_side, PositionSide):
            raise PnLValidationError("position_side must be explicit")

        if self.symbol.contract_family is ContractFamily.LINEAR:
            raw = qty * mult * (reference - entry)
        elif self.symbol.contract_family is ContractFamily.INVERSE:
            raw = qty * mult * ((Decimal("1") / entry) - (Decimal("1") / reference))
        else:
            raise PnLValidationError("unsupported contract family")

        result = raw if position_side is PositionSide.LONG else -raw
        if not result.is_finite():
            raise PnLValidationError("PnL result is non-finite")
        return result

    def calculate_realized(
        self,
        *,
        quantity: Decimal | int | str,
        multiplier: Decimal | int | str,
        entry_price: Decimal | int | str,
        exit_price: Decimal | int | str,
        position_side: PositionSide,
    ) -> Decimal:
        return self._calculate(
            quantity=quantity,
            multiplier=multiplier,
            entry_price=entry_price,
            reference_price=exit_price,
            position_side=position_side,
        )

    def calculate_unrealized(
        self,
        *,
        quantity: Decimal | int | str,
        multiplier: Decimal | int | str,
        entry_price: Decimal | int | str,
        valuation_price: Decimal | int | str,
        position_side: PositionSide,
        valuation_source: str,
        observed_at: datetime,
    ) -> Decimal:
        source = valuation_source.strip() if isinstance(valuation_source, str) else ""
        if not source:
            raise PnLValidationError("valuation_source must be explicit")
        _utc(observed_at, "observed_at")
        return self._calculate(
            quantity=quantity,
            multiplier=multiplier,
            entry_price=entry_price,
            reference_price=valuation_price,
            position_side=position_side,
        )

    def validate_valuation_freshness(
        self,
        *,
        as_of: datetime,
        observed_at: datetime,
        max_age: timedelta,
    ) -> None:
        current = _utc(as_of, "as_of")
        observed = _utc(observed_at, "observed_at")
        if not isinstance(max_age, timedelta) or max_age <= timedelta(0):
            raise PnLValidationError("max_age must be positive")
        if current < observed or current - observed > max_age:
            raise PnLValidationError("valuation is stale or time ordering is invalid")
