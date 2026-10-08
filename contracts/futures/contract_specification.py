"""Canonical Futures contract specification and multiplier semantics.

The domain contract is exchange-independent. Infrastructure maps exchange
metadata into this specification; it may not redefine its financial meaning.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import (
    CanonicalFuturesSymbol,
    ContractFamily,
    InstrumentValidationError,
    Market,
)


class ContractSpecificationValidationError(InstrumentValidationError):
    """Raised when a Futures contract specification is invalid or ambiguous."""


class QuantityUnit(StrEnum):
    """Canonical order/position quantity unit."""

    CONTRACTS = "CONTRACTS"


def _decimal(value: Decimal | int | str, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise ContractSpecificationValidationError(
            f"{field} must be an exact Decimal value"
        )
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ContractSpecificationValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite():
        raise ContractSpecificationValidationError(f"{field} must be finite")
    return result


def _positive_decimal(value: Decimal | int | str, field: str) -> Decimal:
    result = _decimal(value, field)
    if result <= 0:
        raise ContractSpecificationValidationError(f"{field} must be greater than zero")
    return result


@dataclass(frozen=True, slots=True)
class FuturesContractSpecification:
    """Immutable, exchange-independent multiplier/contract specification.

    contract_multiplier is the exact contract size expressed per one contract.
    Linear: base-asset units per contract.
    Inverse: quote-price-denomination units per contract.

    Quantity is expressed in contracts at this boundary. Exchange lot sizes,
    tick sizes, and exchange-specific precision belong to later contracts.

    Linear:
        base exposure = quantity * multiplier
        quote notional = base exposure * price

    Inverse:
        quote notional = quantity * multiplier
        base exposure = quote notional / price

    These calculations do not infer margin or settlement behavior.
    """

    market: Market
    symbol: CanonicalFuturesSymbol
    quantity_unit: QuantityUnit
    contract_multiplier: Decimal
    price_quote_asset: str

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise ContractSpecificationValidationError(
                "market must be a supported Futures market"
            )
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise ContractSpecificationValidationError(
                "symbol must be CanonicalFuturesSymbol"
            )
        if not isinstance(self.quantity_unit, QuantityUnit):
            raise ContractSpecificationValidationError(
                "quantity_unit must be CONTRACTS"
            )

        multiplier = _positive_decimal(self.contract_multiplier, "contract_multiplier")

        quote = (
            self.price_quote_asset.strip().upper()
            if isinstance(self.price_quote_asset, str)
            else ""
        )
        if not quote or quote != self.symbol.quote_asset:
            raise ContractSpecificationValidationError(
                "price_quote_asset must equal the symbol quote asset"
            )

        object.__setattr__(self, "contract_multiplier", multiplier)
        object.__setattr__(self, "price_quote_asset", quote)

    @property
    def contract_size(self) -> Decimal:
        """Return the canonical contract size/multiplier."""
        return self.contract_multiplier

    def notional(
        self,
        *,
        quantity: Decimal | int | str,
        price: Decimal | int | str,
    ) -> Decimal:
        """Return quote-denominated notional without rounding or float conversion."""
        qty = _positive_decimal(quantity, "quantity")
        px = _positive_decimal(price, "price")

        if self.symbol.contract_family is ContractFamily.LINEAR:
            return qty * self.contract_multiplier * px
        if self.symbol.contract_family is ContractFamily.INVERSE:
            return qty * self.contract_multiplier
        raise ContractSpecificationValidationError("unsupported contract family")

    def base_exposure(
        self,
        *,
        quantity: Decimal | int | str,
        price: Decimal | int | str,
    ) -> Decimal:
        """Return base-asset exposure without rounding."""
        qty = _positive_decimal(quantity, "quantity")
        px = _positive_decimal(price, "price")

        if self.symbol.contract_family is ContractFamily.LINEAR:
            return qty * self.contract_multiplier
        if self.symbol.contract_family is ContractFamily.INVERSE:
            return (qty * self.contract_multiplier) / px
        raise ContractSpecificationValidationError("unsupported contract family")
