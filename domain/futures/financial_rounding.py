"""Pure, exchange-independent financial rounding primitives for ADR-0003.

These primitives intentionally do not authorize downstream use of rounded
values. ADR-0003 requires a durable audit record at each boundary, but the
repository has not yet approved a callable audit port and its failure/recovery
contract. Production consumers must not be wired to these helpers until that
outer-layer integration is approved. Domain code must remain free of I/O.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from decimal import (
    Context,
    Decimal,
    DecimalException,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    ROUND_DOWN,
    ROUND_HALF_UP,
    ROUND_HALF_EVEN,
    ROUND_UP,
    Rounded,
    Underflow,
    localcontext,
)
from enum import StrEnum

from contracts.futures.instrument import Market
from contracts.futures.position_side import PositionSide


WORKING_PRECISION = 28
DEFAULT_PNL_SCALES = {
    Market.CRYPTO: 8,
    Market.GOLD: 2,
    Market.FOREX: 2,
}


class FinancialRoundingError(ValueError):
    """Invalid policy or arithmetic that cannot be safely represented."""


class FinancialRiskBoundaryError(FinancialRoundingError):
    """A rounded financial value violates an explicit risk-boundary contract."""


class RoundingMode(StrEnum):
    """Only the explicitly approved ADR-0003 modes exposed by this module."""

    TOWARD_ZERO = ROUND_DOWN
    HALF_UP = ROUND_HALF_UP
    AWAY_FROM_ZERO = ROUND_UP


def financial_working_context() -> AbstractContextManager:
    """Return an isolated precision-28 context that traps intermediate loss.

    The returned context does not inherit caller precision, rounding, or trap
    settings. Inexact/Rounded may be suppressed only inside the final named
    quantization operation.
    """
    return localcontext(
        Context(
            prec=WORKING_PRECISION,
            rounding=ROUND_HALF_EVEN,
            traps=[
                InvalidOperation,
                DivisionByZero,
                Overflow,
                Underflow,
                Inexact,
                Rounded,
            ],
        )
    )


def _decimal(value: Decimal | int | str, field: str) -> Decimal:
    if type(value) not in (Decimal, int, str):
        raise FinancialRoundingError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise FinancialRoundingError(f"{field} must be an exact Decimal value") from exc
    if not result.is_finite():
        raise FinancialRoundingError(f"{field} must be finite")
    return result


def _positive(value: Decimal | int | str, field: str) -> Decimal:
    result = _decimal(value, field)
    if result <= 0:
        raise FinancialRoundingError(f"{field} must be greater than zero")
    return result


def _scale(value: int, field: str = "scale") -> int:
    if type(value) is not int or value < 0 or value > WORKING_PRECISION:
        raise FinancialRoundingError(
            f"{field} must be an integer between 0 and {WORKING_PRECISION}"
        )
    return value


def _quantize(value: Decimal, scale: int, rounding: str) -> Decimal:
    exponent = Decimal((0, (1,), -scale))
    try:
        with financial_working_context() as ctx:
            # Inexact/Rounded are permitted only for this named final boundary.
            ctx.traps[Inexact] = False
            ctx.traps[Rounded] = False
            result = value.quantize(exponent, rounding=rounding, context=ctx)
    except DecimalException as exc:
        raise FinancialRoundingError(
            "value cannot be represented at the approved boundary scale"
        ) from exc
    if not result.is_finite():
        raise FinancialRoundingError("rounded result must be finite")
    return result


@dataclass(frozen=True, slots=True)
class PnLRoundingPolicy:
    market: Market
    max_reasonable_pnl: Decimal | int | str
    scale_override: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise FinancialRoundingError("market must be an explicit supported Market")
        maximum = _positive(self.max_reasonable_pnl, "max_reasonable_pnl")
        if self.scale_override is not None:
            _scale(self.scale_override, "scale_override")
        object.__setattr__(self, "max_reasonable_pnl", maximum)

    @property
    def scale(self) -> int:
        return (
            self.scale_override
            if self.scale_override is not None
            else DEFAULT_PNL_SCALES[self.market]
        )


def round_pnl(value: Decimal | int | str, policy: PnLRoundingPolicy) -> Decimal:
    """Round PnL toward zero at the approved market scale; require explicit cap."""
    if not isinstance(policy, PnLRoundingPolicy):
        raise FinancialRoundingError("policy must be PnLRoundingPolicy")
    amount = _decimal(value, "pnl")
    if amount.copy_abs() > policy.max_reasonable_pnl:
        raise FinancialRiskBoundaryError("absolute PnL exceeds configured maximum")
    return _quantize(amount, policy.scale, ROUND_DOWN)


@dataclass(frozen=True, slots=True)
class FundingRoundingPolicy:
    max_funding_rate: Decimal | int | str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "max_funding_rate",
            _positive(self.max_funding_rate, "max_funding_rate"),
        )


def round_funding(
    payment: Decimal | int | str,
    funding_rate: Decimal | int | str,
    policy: FundingRoundingPolicy,
) -> Decimal:
    """Round the wallet-balance funding payment to 8 places, half away from zero."""
    if not isinstance(policy, FundingRoundingPolicy):
        raise FinancialRoundingError("policy must be FundingRoundingPolicy")
    amount = _decimal(payment, "funding_payment")
    rate = _decimal(funding_rate, "funding_rate")
    if rate.copy_abs() > policy.max_funding_rate:
        raise FinancialRiskBoundaryError("absolute funding rate exceeds configured maximum")
    return _quantize(amount, 8, ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class MarginRatioRoundingPolicy:
    maintenance_margin_ratio: Decimal | int | str
    liquidation_ratio: Decimal | int | str

    def __post_init__(self) -> None:
        maintenance = _decimal(
            self.maintenance_margin_ratio, "maintenance_margin_ratio"
        )
        liquidation = _decimal(self.liquidation_ratio, "liquidation_ratio")
        if maintenance < 0 or liquidation <= maintenance:
            raise FinancialRoundingError(
                "thresholds must satisfy 0 <= maintenance < liquidation"
            )
        object.__setattr__(self, "maintenance_margin_ratio", maintenance)
        object.__setattr__(self, "liquidation_ratio", liquidation)


def round_margin_ratio(
    ratio: Decimal | int | str,
    policy: MarginRatioRoundingPolicy,
) -> Decimal:
    """Round a comparison-only ratio; fail closed inside the approved critical range."""
    if not isinstance(policy, MarginRatioRoundingPolicy):
        raise FinancialRoundingError("policy must be MarginRatioRoundingPolicy")
    value = _decimal(ratio, "margin_ratio")
    if value < 0:
        raise FinancialRoundingError("margin_ratio must not be negative")
    rounded = _quantize(value, 8, ROUND_HALF_UP)
    if (
        policy.maintenance_margin_ratio < rounded < policy.liquidation_ratio
    ):
        raise FinancialRiskBoundaryError(
            "margin ratio lies strictly inside the configured critical range"
        )
    return rounded


@dataclass(frozen=True, slots=True)
class LiquidationPriceRoundingPolicy:
    tick_size: Decimal | int | str
    position_side: PositionSide

    def __post_init__(self) -> None:
        tick = _positive(self.tick_size, "tick_size")
        if not isinstance(self.position_side, PositionSide):
            raise FinancialRoundingError("position_side must be explicit LONG or SHORT")
        object.__setattr__(self, "tick_size", tick)


def round_liquidation_price(
    price: Decimal | int | str,
    policy: LiquidationPriceRoundingPolicy,
) -> Decimal:
    """Round a positive price to configured ticks: LONG down, SHORT up.

    Integer-ratio arithmetic avoids context-rounded division when determining
    the tick count. The final multiplication remains under the trapped
    precision-28 context, so an unrepresentable result fails closed.
    """
    if not isinstance(policy, LiquidationPriceRoundingPolicy):
        raise FinancialRoundingError("policy must be LiquidationPriceRoundingPolicy")
    amount = _positive(price, "liquidation_price")
    price_num, price_den = amount.as_integer_ratio()
    tick_num, tick_den = policy.tick_size.as_integer_ratio()
    numerator = price_num * tick_den
    denominator = price_den * tick_num
    ticks, remainder = divmod(numerator, denominator)
    if policy.position_side is PositionSide.SHORT and remainder:
        ticks += 1
    try:
        with financial_working_context():
            result = policy.tick_size * Decimal(ticks)
    except DecimalException as exc:
        raise FinancialRoundingError(
            "tick-rounded liquidation price exceeds exact working precision"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise FinancialRoundingError("rounded liquidation price must be positive and finite")
    return result
