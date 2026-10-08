"""Canonical Futures liquidation-price constraint semantics."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import cast

from .contract_specification import FuturesContractSpecification
from .instrument import CanonicalFuturesSymbol, ContractFamily, Market
from .position_side import PositionSide


class LiquidationValidationError(ValueError):
    """Raised when liquidation-price constraint inputs are invalid or ambiguous."""


class LiquidationDenomination(StrEnum):
    BASE = "BASE"
    QUOTE = "QUOTE"


def _positive_decimal(value: object, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise LiquidationValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise LiquidationValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise LiquidationValidationError(f"{field} must be finite and greater than zero")
    return result


@dataclass(frozen=True, slots=True)
class FuturesLiquidationSpecification:
    """Deterministic position-level liquidation-price constraint.

    This is not an exchange liquidation event, trigger engine, mark-price
    source, risk-tier resolver, fee model, funding model, or account mutator.
    It solves the explicit equality between position equity and an explicit
    maintenance requirement using only supplied position terms.
    """

    market: Market
    symbol: CanonicalFuturesSymbol

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.market), Market):
            raise LiquidationValidationError("market must be a supported Futures market")
        if not isinstance(cast(object, self.symbol), CanonicalFuturesSymbol):
            raise LiquidationValidationError("symbol must be CanonicalFuturesSymbol")
        if self.symbol.contract_family not in (
            ContractFamily.LINEAR,
            ContractFamily.INVERSE,
        ):
            raise LiquidationValidationError("unsupported contract family")

    def _validate_contract(
        self, contract: FuturesContractSpecification
    ) -> FuturesContractSpecification:
        if not isinstance(cast(object, contract), FuturesContractSpecification):
            raise LiquidationValidationError(
                "contract must be FuturesContractSpecification"
            )
        if contract.market is not self.market or contract.symbol != self.symbol:
            raise LiquidationValidationError("contract identity does not match specification")
        return contract

    def liquidation_price(
        self,
        *,
        contract: FuturesContractSpecification,
        quantity: Decimal | int | str,
        entry_price: Decimal | int | str,
        margin_amount: Decimal | int | str,
        margin_denomination: LiquidationDenomination,
        maintenance_margin_ratio: Decimal | int | str,
        position_side: PositionSide,
    ) -> Decimal:
        spec = self._validate_contract(contract)
        qty = _positive_decimal(quantity, "quantity")
        entry = _positive_decimal(entry_price, "entry_price")
        margin = _positive_decimal(margin_amount, "margin_amount")
        mmr = _positive_decimal(maintenance_margin_ratio, "maintenance_margin_ratio")

        if not isinstance(cast(object, margin_denomination), LiquidationDenomination):
            raise LiquidationValidationError(
                "margin_denomination must be explicitly BASE or QUOTE"
            )
        if not isinstance(cast(object, position_side), PositionSide):
            raise LiquidationValidationError("position_side must be explicit")
        if mmr >= Decimal("1"):
            raise LiquidationValidationError(
                "maintenance_margin_ratio must be less than one for a finite constraint"
            )

        multiplier = _positive_decimal(spec.contract_multiplier, "contract_multiplier")
        contract_value = qty * multiplier

        if spec.symbol.contract_family is ContractFamily.LINEAR:
            if margin_denomination is not LiquidationDenomination.QUOTE:
                raise LiquidationValidationError(
                    "Linear liquidation margin must be denominated in QUOTE"
                )
            if position_side is PositionSide.LONG:
                denominator = contract_value * (Decimal("1") - mmr)
                numerator = contract_value * entry - margin
            else:
                denominator = contract_value * (Decimal("1") + mmr)
                numerator = contract_value * entry + margin
        else:
            if margin_denomination is not LiquidationDenomination.BASE:
                raise LiquidationValidationError(
                    "Inverse liquidation margin must be denominated in BASE"
                )
            if position_side is PositionSide.LONG:
                numerator = contract_value * (Decimal("1") + mmr)
                denominator = margin + contract_value / entry
            else:
                numerator = contract_value * (Decimal("1") - mmr)
                denominator = contract_value / entry - margin

        if denominator <= 0:
            raise LiquidationValidationError(
                "liquidation-price denominator must be positive"
            )
        price = numerator / denominator
        if not price.is_finite() or price <= 0:
            raise LiquidationValidationError(
                "liquidation price must be finite and greater than zero"
            )

        if position_side is PositionSide.LONG and price >= entry:
            raise LiquidationValidationError(
                "long liquidation constraint must be below entry price"
            )
        if position_side is PositionSide.SHORT and price <= entry:
            raise LiquidationValidationError(
                "short liquidation constraint must be above entry price"
            )
        return price
