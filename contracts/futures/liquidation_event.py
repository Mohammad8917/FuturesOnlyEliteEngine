"""Canonical Futures liquidation-trigger event semantics."""

from __future__ import annotations

import typing

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .instrument import CanonicalFuturesSymbol, ContractFamily, Market
from .liquidation import LiquidationDenomination
from .position_mode import FuturesPositionModeSpecification, PositionMode
from .position_side import PositionSide


class LiquidationEventValidationError(ValueError):
    """Raised when a liquidation-trigger event is invalid or ambiguous."""


class LiquidationTrigger(StrEnum):
    NOT_TRIGGERED = "NOT_TRIGGERED"
    TRIGGERED = "TRIGGERED"


def _positive_decimal(value: object, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise LiquidationEventValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise LiquidationEventValidationError(
            f"{field} must be an exact Decimal value"
        ) from exc
    if not result.is_finite() or result <= 0:
        raise LiquidationEventValidationError(
            f"{field} must be finite and greater than zero"
        )
    return result


def _utc(value: object, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise LiquidationEventValidationError(f"{field} must be an aware UTC datetime")
    return value


def _identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LiquidationEventValidationError(f"{field} must be a non-empty identifier")
    return value.strip()


def _non_negative_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LiquidationEventValidationError(f"{field} must be a non-negative integer")
    return value


@dataclass(frozen=True, slots=True)
class FuturesLiquidationTriggerSpecification:
    """Immutable, exchange-independent liquidation-trigger boundary.

    This contract evaluates an explicit liquidation-price output against an
    explicitly sourced reference price. It emits no order, mutates no account
    or position, performs no network I/O, and owns no exchange-specific
    mark-price, fee, tier, funding, or execution policy.
    """

    market: Market
    symbol: CanonicalFuturesSymbol

    def __post_init__(self) -> None:
        if not isinstance(typing.cast(object, self.market), Market):
            raise LiquidationEventValidationError(
                "market must be a supported Futures market"
            )
        if not isinstance(typing.cast(object, self.symbol), CanonicalFuturesSymbol):
            raise LiquidationEventValidationError(
                "symbol must be CanonicalFuturesSymbol"
            )
        if self.symbol.contract_family not in (
            ContractFamily.LINEAR,
            ContractFamily.INVERSE,
        ):
            raise LiquidationEventValidationError("unsupported contract family")

    def evaluate(
        self,
        *,
        account_id: str,
        position_id: str,
        event_id: str,
        causation_id: str,
        state_version: int,
        contract_family: ContractFamily,
        position_mode: PositionMode,
        position_side: PositionSide,
        quantity: Decimal | int | str,
        entry_price: Decimal | int | str,
        margin_amount: Decimal | int | str,
        margin_denomination: LiquidationDenomination,
        maintenance_margin_ratio: Decimal | int | str,
        liquidation_price: Decimal | int | str,
        reference_price: Decimal | int | str,
        reference_price_source: str,
        observed_at: datetime,
        as_of: datetime,
        max_age: timedelta,
        previous_event_sequence: int,
        event_sequence: int,
    ) -> "FuturesLiquidationTriggerEvaluation":
        account = _identifier(account_id, "account_id")
        position = _identifier(position_id, "position_id")
        event = _identifier(event_id, "event_id")
        causation = _identifier(causation_id, "causation_id")
        version = _non_negative_integer(state_version, "state_version")
        previous_sequence = _non_negative_integer(
            previous_event_sequence, "previous_event_sequence"
        )
        sequence = _non_negative_integer(event_sequence, "event_sequence")
        if sequence < previous_sequence:
            raise LiquidationEventValidationError(
                "event_sequence must not move backwards"
            )

        if contract_family is not self.symbol.contract_family:
            raise LiquidationEventValidationError(
                "contract_family does not match the canonical symbol"
            )
        if not isinstance(typing.cast(object, position_mode), PositionMode):
            raise LiquidationEventValidationError(
                "position_mode must be ONE_WAY or HEDGE"
            )
        if not isinstance(typing.cast(object, position_side), PositionSide):
            raise LiquidationEventValidationError("position_side must be LONG or SHORT")
        try:
            FuturesPositionModeSpecification(position_mode).accepts(position_side)
        except ValueError as exc:
            raise LiquidationEventValidationError(str(exc)) from exc

        qty = _positive_decimal(quantity, "quantity")
        entry = _positive_decimal(entry_price, "entry_price")
        margin = _positive_decimal(margin_amount, "margin_amount")
        mmr = _positive_decimal(maintenance_margin_ratio, "maintenance_margin_ratio")
        liquidation = _positive_decimal(liquidation_price, "liquidation_price")
        reference = _positive_decimal(reference_price, "reference_price")

        if not isinstance(
            typing.cast(object, margin_denomination), LiquidationDenomination
        ):
            raise LiquidationEventValidationError(
                "margin_denomination must be explicitly BASE or QUOTE"
            )
        expected_denomination = (
            LiquidationDenomination.QUOTE
            if self.symbol.contract_family is ContractFamily.LINEAR
            else LiquidationDenomination.BASE
        )
        if margin_denomination is not expected_denomination:
            raise LiquidationEventValidationError(
                "margin_denomination does not match contract family"
            )
        if mmr >= Decimal("1"):
            raise LiquidationEventValidationError(
                "maintenance_margin_ratio must be less than one"
            )

        if position_side is PositionSide.LONG and liquidation >= entry:
            raise LiquidationEventValidationError(
                "long liquidation price must be below entry price"
            )
        if position_side is PositionSide.SHORT and liquidation <= entry:
            raise LiquidationEventValidationError(
                "short liquidation price must be above entry price"
            )

        source = _identifier(reference_price_source, "reference_price_source")
        observed = _utc(observed_at, "observed_at")
        current = _utc(as_of, "as_of")
        if not isinstance(
            typing.cast(object, max_age), timedelta
        ) or max_age <= timedelta(0):
            raise LiquidationEventValidationError("max_age must be positive")
        if current < observed or current - observed > max_age:
            raise LiquidationEventValidationError(
                "reference price is stale or time ordering is invalid"
            )

        if position_side is PositionSide.LONG:
            triggered = reference <= liquidation
        else:
            triggered = reference >= liquidation
        if triggered and sequence <= previous_sequence:
            raise LiquidationEventValidationError(
                "triggered event sequence must advance beyond the previous sequence"
            )

        return FuturesLiquidationTriggerEvaluation(
            trigger=(
                LiquidationTrigger.TRIGGERED
                if triggered
                else LiquidationTrigger.NOT_TRIGGERED
            ),
            event=(
                FuturesLiquidationTriggerEvent(
                    account_id=account,
                    position_id=position,
                    event_id=event,
                    causation_id=causation,
                    state_version=version,
                    event_sequence=sequence,
                    market=self.market,
                    symbol=self.symbol,
                    position_mode=position_mode,
                    position_side=position_side,
                    quantity=qty,
                    entry_price=entry,
                    margin_amount=margin,
                    margin_denomination=margin_denomination,
                    maintenance_margin_ratio=mmr,
                    liquidation_price=liquidation,
                    reference_price=reference,
                    reference_price_source=source,
                    observed_at=observed,
                    as_of=current,
                    max_age=max_age,
                )
                if triggered
                else None
            ),
        )


@dataclass(frozen=True, slots=True)
class FuturesLiquidationTriggerEvent:
    """Immutable event emitted only when the explicit trigger condition holds."""

    account_id: str
    position_id: str
    event_id: str
    causation_id: str
    state_version: int
    event_sequence: int
    market: Market
    symbol: CanonicalFuturesSymbol
    position_mode: PositionMode
    position_side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    margin_amount: Decimal
    margin_denomination: LiquidationDenomination
    maintenance_margin_ratio: Decimal
    liquidation_price: Decimal
    reference_price: Decimal
    reference_price_source: str
    observed_at: datetime
    as_of: datetime
    max_age: timedelta

    def __post_init__(self) -> None:
        _identifier(self.account_id, "account_id")
        _identifier(self.position_id, "position_id")
        _identifier(self.event_id, "event_id")
        _identifier(self.causation_id, "causation_id")
        _non_negative_integer(self.state_version, "state_version")
        _non_negative_integer(self.event_sequence, "event_sequence")
        if not isinstance(typing.cast(object, self.market), Market):
            raise LiquidationEventValidationError(
                "market must be a supported Futures market"
            )
        if not isinstance(typing.cast(object, self.symbol), CanonicalFuturesSymbol):
            raise LiquidationEventValidationError(
                "symbol must be CanonicalFuturesSymbol"
            )
        if self.symbol.contract_family not in (
            ContractFamily.LINEAR,
            ContractFamily.INVERSE,
        ):
            raise LiquidationEventValidationError("unsupported contract family")
        if not isinstance(typing.cast(object, self.position_mode), PositionMode):
            raise LiquidationEventValidationError(
                "position_mode must be ONE_WAY or HEDGE"
            )
        if not isinstance(typing.cast(object, self.position_side), PositionSide):
            raise LiquidationEventValidationError("position_side must be LONG or SHORT")
        FuturesPositionModeSpecification(self.position_mode).accepts(self.position_side)
        _positive_decimal(self.quantity, "quantity")
        entry = _positive_decimal(self.entry_price, "entry_price")
        _positive_decimal(self.margin_amount, "margin_amount")
        mmr = _positive_decimal(
            self.maintenance_margin_ratio, "maintenance_margin_ratio"
        )
        liquidation = _positive_decimal(self.liquidation_price, "liquidation_price")
        reference = _positive_decimal(self.reference_price, "reference_price")
        if not isinstance(
            typing.cast(object, self.margin_denomination), LiquidationDenomination
        ):
            raise LiquidationEventValidationError(
                "margin_denomination must be explicit"
            )
        expected = (
            LiquidationDenomination.QUOTE
            if self.symbol.contract_family is ContractFamily.LINEAR
            else LiquidationDenomination.BASE
        )
        if self.margin_denomination is not expected:
            raise LiquidationEventValidationError(
                "margin_denomination does not match contract family"
            )
        if mmr >= Decimal("1"):
            raise LiquidationEventValidationError(
                "maintenance_margin_ratio must be less than one"
            )
        if self.position_side is PositionSide.LONG and liquidation >= entry:
            raise LiquidationEventValidationError(
                "long liquidation price must be below entry price"
            )
        if self.position_side is PositionSide.SHORT and liquidation <= entry:
            raise LiquidationEventValidationError(
                "short liquidation price must be above entry price"
            )
        if (self.position_side is PositionSide.LONG and reference > liquidation) or (
            self.position_side is PositionSide.SHORT and reference < liquidation
        ):
            raise LiquidationEventValidationError(
                "event reference price does not satisfy the trigger direction"
            )
        _identifier(self.reference_price_source, "reference_price_source")
        observed = _utc(self.observed_at, "observed_at")
        current = _utc(self.as_of, "as_of")
        if not isinstance(
            typing.cast(object, self.max_age), timedelta
        ) or self.max_age <= timedelta(0):
            raise LiquidationEventValidationError("max_age must be positive")
        if current < observed or current - observed > self.max_age:
            raise LiquidationEventValidationError(
                "event reference price is stale or time ordering is invalid"
            )


@dataclass(frozen=True, slots=True)
class FuturesLiquidationTriggerEvaluation:
    """Deterministic trigger result; execution remains outside this boundary."""

    trigger: LiquidationTrigger
    event: FuturesLiquidationTriggerEvent | None

    def __post_init__(self) -> None:
        if not isinstance(typing.cast(object, self.trigger), LiquidationTrigger):
            raise LiquidationEventValidationError("trigger must be explicit")
        if self.trigger is LiquidationTrigger.TRIGGERED and self.event is None:
            raise LiquidationEventValidationError(
                "triggered evaluation must contain an event"
            )
        if self.trigger is LiquidationTrigger.NOT_TRIGGERED and self.event is not None:
            raise LiquidationEventValidationError(
                "non-triggered evaluation must not contain an event"
            )
