"""Canonical Futures exposure and position-valuation semantics."""
from __future__ import annotations

from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .contract_specification import FuturesContractSpecification
from .instrument import CanonicalFuturesSymbol, ContractFamily, Market
from .position_side import PositionSide


class ExposureValidationError(ValueError):
    """Raised when exposure or valuation inputs are invalid or ambiguous."""


class ExposureDenomination(StrEnum):
    BASE = "BASE"
    QUOTE = "QUOTE"


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise ExposureValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ExposureValidationError(f"{field} must be an exact Decimal value") from exc
    if not result.is_finite() or result <= 0:
        raise ExposureValidationError(f"{field} must be finite and greater than zero")
    return result


def _utc(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ExposureValidationError(f"{field} must be an aware UTC datetime")
    return value


@dataclass(frozen=True, slots=True)
class FuturesExposureSpecification:
    """Immutable exposure and position valuation boundary."""

    market: Market
    symbol: CanonicalFuturesSymbol

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise ExposureValidationError("market must be a supported Futures market")
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise ExposureValidationError("symbol must be CanonicalFuturesSymbol")
        if self.symbol.contract_family not in (ContractFamily.LINEAR, ContractFamily.INVERSE):
            raise ExposureValidationError("unsupported contract family")
        object.__setattr__(self, "market", self.market)
        object.__setattr__(self, "symbol", self.symbol)

    def _validate_contract(
        self, contract: FuturesContractSpecification
    ) -> FuturesContractSpecification:
        if not isinstance(contract, FuturesContractSpecification):
            raise ExposureValidationError("contract must be FuturesContractSpecification")
        if contract.market is not self.market or contract.symbol != self.symbol:
            raise ExposureValidationError("contract identity does not match exposure specification")
        return contract

    def base_exposure(
        self,
        *,
        contract: FuturesContractSpecification,
        quantity: Decimal | int | str,
        price: Decimal | int | str,
    ) -> Decimal:
        spec = self._validate_contract(contract)
        result = spec.base_exposure(quantity=quantity, price=price)
        if not result.is_finite() or result <= 0:
            raise ExposureValidationError("base exposure must be finite and greater than zero")
        return result

    def quote_value(
        self,
        *,
        contract: FuturesContractSpecification,
        quantity: Decimal | int | str,
        reference_price: Decimal | int | str,
    ) -> Decimal:
        spec = self._validate_contract(contract)
        result = spec.notional(quantity=quantity, price=reference_price)
        if not result.is_finite() or result <= 0:
            raise ExposureValidationError("quote value must be finite and greater than zero")
        return result

    def signed_base_exposure(
        self,
        *,
        contract: FuturesContractSpecification,
        quantity: Decimal | int | str,
        price: Decimal | int | str,
        position_side: PositionSide,
    ) -> Decimal:
        if not isinstance(position_side, PositionSide):
            raise ExposureValidationError("position_side must be explicit")
        magnitude = self.base_exposure(
            contract=contract, quantity=quantity, price=price
        )
        return magnitude if position_side is PositionSide.LONG else -magnitude

    def signed_quote_value(
        self,
        *,
        contract: FuturesContractSpecification,
        quantity: Decimal | int | str,
        reference_price: Decimal | int | str,
        position_side: PositionSide,
    ) -> Decimal:
        if not isinstance(position_side, PositionSide):
            raise ExposureValidationError("position_side must be explicit")
        magnitude = self.quote_value(
            contract=contract, quantity=quantity, reference_price=reference_price
        )
        return magnitude if position_side is PositionSide.LONG else -magnitude

    def value(
        self,
        *,
        contract: FuturesContractSpecification,
        quantity: Decimal | int | str,
        reference_price: Decimal | int | str,
        denomination: ExposureDenomination,
        valuation_source: str,
        observed_at: datetime,
    ) -> Decimal:
        if not isinstance(denomination, ExposureDenomination):
            raise ExposureValidationError("denomination must be explicitly BASE or QUOTE")
        source = valuation_source.strip() if isinstance(valuation_source, str) else ""
        if not source:
            raise ExposureValidationError("valuation_source must be explicit")
        _utc(observed_at, "observed_at")
        price = _positive_decimal(reference_price, "reference_price")
        if denomination is ExposureDenomination.BASE:
            return self.base_exposure(contract=contract, quantity=quantity, price=price)
        if denomination is ExposureDenomination.QUOTE:
            return self.quote_value(
                contract=contract, quantity=quantity, reference_price=price
            )
        raise ExposureValidationError("unsupported valuation denomination")

    def validate_reference_freshness(
        self,
        *,
        as_of: datetime,
        observed_at: datetime,
        max_age: timedelta,
    ) -> None:
        current = _utc(as_of, "as_of")
        observed = _utc(observed_at, "observed_at")
        if not isinstance(max_age, timedelta) or max_age <= timedelta(0):
            raise ExposureValidationError("max_age must be positive")
        if current < observed or current - observed > max_age:
            raise ExposureValidationError(
                "valuation reference is stale or time ordering is invalid"
            )
