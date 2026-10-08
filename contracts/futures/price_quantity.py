"""Canonical Futures price, quantity, denomination, precision and rounding semantics."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .contract_specification import QuantityUnit
from .instrument import CanonicalFuturesSymbol, ContractFamily, Market


class PriceQuantityValidationError(ValueError):
    """Invalid or ambiguous price/quantity contract input."""


class PriceUnit(StrEnum):
    QUOTE_PER_BASE = "QUOTE_PER_BASE"


class PrecisionPolicy(StrEnum):
    EXACT = "EXACT"


class RoundingPolicy(StrEnum):
    NONE = "NONE"


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise PriceQuantityValidationError(
            f"{field} must be an exact Decimal value"
        )
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise PriceQuantityValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise PriceQuantityValidationError(
            f"{field} must be finite and greater than zero"
        )
    return result


@dataclass(frozen=True, slots=True)
class FuturesPriceQuantitySpecification:
    """Freeze explicit price/quantity units and forbid implicit rounding."""

    market: Market
    symbol: CanonicalFuturesSymbol
    price_unit: PriceUnit
    quantity_unit: QuantityUnit
    price_quote_asset: str
    precision_policy: PrecisionPolicy
    rounding_policy: RoundingPolicy

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise PriceQuantityValidationError(
                "market must be a supported Futures market"
            )
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise PriceQuantityValidationError(
                "symbol must be CanonicalFuturesSymbol"
            )
        if self.symbol.contract_family not in (
            ContractFamily.LINEAR,
            ContractFamily.INVERSE,
        ):
            raise PriceQuantityValidationError("unsupported contract family")
        if not isinstance(self.price_unit, PriceUnit):
            raise PriceQuantityValidationError("price_unit must be QUOTE_PER_BASE")
        if not isinstance(self.quantity_unit, QuantityUnit):
            raise PriceQuantityValidationError("quantity_unit must be CONTRACTS")
        if not isinstance(self.precision_policy, PrecisionPolicy):
            raise PriceQuantityValidationError("precision_policy must be EXACT")
        if not isinstance(self.rounding_policy, RoundingPolicy):
            raise PriceQuantityValidationError("rounding_policy must be NONE")

        quote = (
            self.price_quote_asset.strip().upper()
            if isinstance(self.price_quote_asset, str)
            else ""
        )
        if not quote or quote != self.symbol.quote_asset:
            raise PriceQuantityValidationError(
                "price_quote_asset must equal the canonical symbol quote asset"
            )
        object.__setattr__(self, "price_quote_asset", quote)

    def validate_price(self, value: Decimal | int | str) -> Decimal:
        return _positive_decimal(value, "price")

    def validate_quantity(self, value: Decimal | int | str) -> Decimal:
        return _positive_decimal(value, "quantity")

    def quote_per_base(self, price: Decimal | int | str) -> Decimal:
        return self.validate_price(price)
