"""Pure, fail-closed rounding boundaries for Futures financial outputs.

This module deliberately performs no I/O and owns no exchange-specific policy.
Each operation returns both the Decimal value and an immutable audit fact so
an approved application-level audit boundary can persist it. A returned audit
fact is not evidence of durable persistence; consumers must not treat it as such.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from decimal import (
    MAX_EMAX,
    MIN_EMIN,
    Context,
    Decimal,
    DecimalException,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    localcontext,
    Overflow,
    ROUND_DOWN,
    ROUND_HALF_EVEN,
    ROUND_UP,
    Rounded,
    Subnormal,
    Underflow,
)
from typing import Iterator

from contracts.futures.instrument import Market
from contracts.futures.position_side import PositionSide

WORKING_PRECISION = 28
MARGIN_RATIO_SCALE = 8
FUNDING_ROUNDING_MODE = "ROUND_HALF_UP"
PNL_ROUNDING_MODE = "ROUND_DOWN"
MARGIN_RATIO_ROUNDING_MODE = "ROUND_HALF_UP"


def _decimal_text(value: Decimal) -> str:
    """Serialize a finite Decimal as a canonical, exact scientific decimal string."""
    if not value.is_finite():
        raise FinancialRoundingError("audit values must be finite Decimal values")
    if value.is_zero():
        return "0"
    sign, digits, exponent = value.as_tuple()
    significant = list(digits)
    while significant[-1] == 0:
        significant.pop()
        exponent += 1
    coefficient = str(significant[0])
    if len(significant) > 1:
        coefficient += "." + "".join(str(digit) for digit in significant[1:])
    adjusted_exponent = exponent + len(significant) - 1
    if adjusted_exponent:
        coefficient += f"E{adjusted_exponent:+d}"
    return ("-" if sign else "") + coefficient


class FinancialRoundingError(ValueError):
    """Raised when a financial rounding boundary is invalid or unrepresentable."""


class FinancialRiskBoundaryError(FinancialRoundingError):
    """Raised for explicit risk violations while retaining any rounding audit fact."""

    def __init__(
        self,
        message: str,
        *,
        audit_record: FinancialRoundingAuditRecord | None = None,
    ) -> None:
        self.audit_record = audit_record
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class FinancialRoundingAuditRecord:
    """Immutable, exact-decimal audit fact; persistence belongs outside Domain."""

    boundary: str
    input_value: str
    output_value: str
    rounding_mode: str
    scale_or_tick: str

    def __post_init__(self) -> None:
        for field_name in (
            "boundary",
            "input_value",
            "output_value",
            "rounding_mode",
            "scale_or_tick",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialRoundingError(f"{field_name} must be non-empty")
            object.__setattr__(self, field_name, value.strip())
        for field_name in ("input_value", "output_value"):
            text_value = getattr(self, field_name)
            try:
                parsed = Decimal(text_value)
            except InvalidOperation as exc:
                raise FinancialRoundingError(
                    f"{field_name} must be a canonical finite decimal string"
                ) from exc
            if not parsed.is_finite() or _decimal_text(parsed) != text_value:
                raise FinancialRoundingError(
                    f"{field_name} must be a canonical finite decimal string"
                )


@dataclass(frozen=True, slots=True)
class FinancialRoundingResult:
    """A rounded Decimal paired with the audit fact describing that operation."""

    value: Decimal
    audit_record: FinancialRoundingAuditRecord

    def __post_init__(self) -> None:
        if type(self.value) is not Decimal or not self.value.is_finite():
            raise FinancialRoundingError("rounded value must be a finite Decimal")
        if not isinstance(self.audit_record, FinancialRoundingAuditRecord):
            raise FinancialRoundingError("audit_record must be explicit")
        if self.audit_record.output_value != _decimal_text(self.value):
            raise FinancialRoundingError("audit output must match the rounded value")


@contextmanager
def controlled_decimal_context() -> Iterator[Context]:
    """Provide a caller-independent Decimal context that rejects intermediate loss.

    Intermediate operations trap both Inexact and Rounded. Only the final
    quantize operation inside a named boundary may deliberately suppress those
    two signals. The context is not shared with or inherited from the caller.
    """
    context = Context(
        prec=WORKING_PRECISION,
        rounding=ROUND_HALF_EVEN,
        Emin=MIN_EMIN,
        Emax=MAX_EMAX,
        capitals=1,
        clamp=0,
    )
    context.traps[Inexact] = True
    context.traps[Rounded] = True
    context.traps[Underflow] = True
    context.traps[Subnormal] = True
    context.traps[Overflow] = True
    context.traps[InvalidOperation] = True
    context.traps[DivisionByZero] = True
    with localcontext(context) as active:
        yield active


def _decimal(value: Decimal | int | str, field: str) -> Decimal:
    if type(value) not in (Decimal, int, str):
        raise FinancialRoundingError(f"{field} must be Decimal, int, or decimal text")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise FinancialRoundingError(f"{field} must be an exact decimal value") from exc
    if not result.is_finite():
        raise FinancialRoundingError(f"{field} must be finite")
    return result


def _positive(value: Decimal | int | str, field: str) -> Decimal:
    result = _decimal(value, field)
    if result <= 0:
        raise FinancialRoundingError(f"{field} must be greater than zero")
    return result


def _non_negative(value: Decimal | int | str, field: str) -> Decimal:
    result = _decimal(value, field)
    if result < 0:
        raise FinancialRoundingError(f"{field} must be non-negative")
    return result


def _scale(value: int, field: str) -> int:
    if type(value) is not int or value < 0:
        raise FinancialRoundingError(f"{field} must be a non-negative integer")
    return value


def _quantum(scale: int) -> Decimal:
    return Decimal((0, (1,), -scale))


def _quantize(
    value: Decimal,
    *,
    quantum: Decimal,
    rounding: str,
    boundary: str,
    scale_or_tick: str,
) -> FinancialRoundingResult:
    try:
        with controlled_decimal_context() as context:
            # The only authorized suppression: explicit final boundary rounding.
            context.traps[Inexact] = False
            context.traps[Rounded] = False
            output = value.quantize(quantum, rounding=rounding, context=context)
    except DecimalException as exc:
        raise FinancialRoundingError(
            f"{boundary} cannot represent the value under the approved Decimal context"
        ) from exc
    if not output.is_finite():
        raise FinancialRoundingError(f"{boundary} produced a non-finite result")
    return FinancialRoundingResult(
        value=output,
        audit_record=FinancialRoundingAuditRecord(
            boundary=boundary,
            input_value=_decimal_text(value),
            output_value=_decimal_text(output),
            rounding_mode=rounding,
            scale_or_tick=scale_or_tick,
        ),
    )


def round_pnl(
    value: Decimal | int | str,
    *,
    market: Market,
    scale: int,
    max_reasonable_pnl: Decimal | int | str,
) -> FinancialRoundingResult:
    """Round a PnL output toward zero at an explicitly configured decimal scale.

    The ADR-approved market baselines are CRYPTO=8 and GOLD/FOREX=2 places.
    The scale is nevertheless explicit so an instrument policy can override it;
    no scale or maximum-PnL risk limit is silently inferred here.
    """
    if not isinstance(market, Market):
        raise FinancialRoundingError(
            "market must be an explicit supported Futures market"
        )
    places = _scale(scale, "scale")
    amount = _decimal(value, "pnl")
    maximum = _positive(max_reasonable_pnl, "max_reasonable_pnl")
    if amount.copy_abs() > maximum:
        raise FinancialRiskBoundaryError("absolute PnL exceeds configured maximum")
    return _quantize(
        amount,
        quantum=_quantum(places),
        rounding=PNL_ROUNDING_MODE,
        boundary="PNL",
        scale_or_tick=f"scale={places}",
    )


def round_funding(
    amount: Decimal | int | str,
    *,
    funding_rate: Decimal | int | str,
    max_funding_rate: Decimal | int | str,
    scale: int,
) -> FinancialRoundingResult:
    """Round a non-negative funding transfer using explicit rate-bound policy."""
    places = _scale(scale, "scale")
    payment = _non_negative(amount, "funding amount")
    rate = _decimal(funding_rate, "funding_rate")
    maximum = _positive(max_funding_rate, "max_funding_rate")
    if rate.copy_abs() > maximum:
        raise FinancialRiskBoundaryError(
            "absolute funding rate exceeds configured maximum"
        )
    return _quantize(
        payment,
        quantum=_quantum(places),
        rounding=FUNDING_ROUNDING_MODE,
        boundary="FUNDING",
        scale_or_tick=f"scale={places}",
    )


def round_margin_ratio(
    value: Decimal | int | str,
    *,
    maintenance_margin_ratio: Decimal | int | str,
    liquidation_ratio: Decimal | int | str,
) -> FinancialRoundingResult:
    """Round a ratio for comparison only; reject the ADR-defined unsafe interval."""
    ratio = _non_negative(value, "margin_ratio")
    maintenance = _positive(maintenance_margin_ratio, "maintenance_margin_ratio")
    liquidation = _positive(liquidation_ratio, "liquidation_ratio")
    if maintenance >= liquidation:
        raise FinancialRoundingError("risk thresholds must be strictly ordered")
    result = _quantize(
        ratio,
        quantum=_quantum(MARGIN_RATIO_SCALE),
        rounding=MARGIN_RATIO_ROUNDING_MODE,
        boundary="MARGIN_RATIO",
        scale_or_tick=f"scale={MARGIN_RATIO_SCALE}",
    )
    if maintenance < result.value < liquidation:
        raise FinancialRiskBoundaryError(
            "rounded margin ratio lies strictly between maintenance and liquidation thresholds",
            audit_record=result.audit_record,
        )
    return result


def _tick_rounded_value(
    value: Decimal, tick_size: Decimal, side: PositionSide
) -> Decimal:
    """Round a positive price to an exact tick multiple without quotient rounding."""
    rounding = ROUND_DOWN if side is PositionSide.LONG else ROUND_UP
    try:
        with controlled_decimal_context():
            # Integral quotient and remainder are exact; a repeating price/tick
            # quotient is never materialized as a rounded Decimal.
            quotient = value // tick_size
            remainder = value % tick_size
            if rounding == ROUND_UP and remainder != 0:
                quotient += Decimal("1")
            output = quotient * tick_size
            if not output.is_finite() or output <= 0:
                raise FinancialRoundingError(
                    "rounded liquidation price must be positive and finite"
                )
            return output
    except DecimalException as exc:
        raise FinancialRoundingError(
            "liquidation price cannot be represented under the approved Decimal context"
        ) from exc


def round_liquidation_price(
    value: Decimal | int | str,
    *,
    tick_size: Decimal | int | str,
    position_side: PositionSide,
    last_price: Decimal | int | str,
    position_is_liquidated: bool,
) -> FinancialRoundingResult:
    """Round to the explicit instrument tick and fail closed on crossed triggers."""
    price = _positive(value, "liquidation_price")
    tick = _positive(tick_size, "tick_size")
    last = _positive(last_price, "last_price")
    if not isinstance(position_side, PositionSide):
        raise FinancialRoundingError("position_side must be explicitly LONG or SHORT")
    if type(position_is_liquidated) is not bool:
        raise FinancialRoundingError("position_is_liquidated must be an explicit bool")

    output = _tick_rounded_value(price, tick, position_side)
    mode = ROUND_DOWN if position_side is PositionSide.LONG else ROUND_UP
    result = FinancialRoundingResult(
        value=output,
        audit_record=FinancialRoundingAuditRecord(
            boundary="LIQUIDATION_PRICE",
            input_value=_decimal_text(price),
            output_value=_decimal_text(output),
            rounding_mode=mode,
            scale_or_tick=f"tick={_decimal_text(tick)}",
        ),
    )
    crossed = last <= output if position_side is PositionSide.LONG else last >= output
    if crossed and not position_is_liquidated:
        raise FinancialRiskBoundaryError(
            "liquidation trigger is crossed while position is reported as not liquidated",
            audit_record=result.audit_record,
        )
    return result
