"""Canonical Futures funding-rate semantics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, DecimalException, InvalidOperation
from enum import StrEnum

from .instrument import CanonicalFuturesSymbol, ContractFamily, Market
from .position_side import PositionSide


class FundingValidationError(ValueError):
    """Invalid, stale, unknown, or ambiguous funding state."""


class FundingRateUnit(StrEnum):
    INTERVAL_RATE = "INTERVAL_RATE"


class FundingSignConvention(StrEnum):
    POSITIVE_LONG_PAYS = "POSITIVE_LONG_PAYS"


def _decimal(value, field, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise FundingValidationError(f"{field} must be an exact Decimal value")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise FundingValidationError(f"{field} must be an exact Decimal value") from exc
    if not result.is_finite() or (positive and result <= 0):
        raise FundingValidationError(f"{field} is invalid")
    return result


def _utc(value, field):
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise FundingValidationError(f"{field} must be an aware UTC datetime")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class FundingPayment:
    payer: PositionSide
    receiver: PositionSide
    amount: Decimal
    denomination: str

    def __post_init__(self):
        if (
            not isinstance(self.payer, PositionSide)
            or not isinstance(self.receiver, PositionSide)
            or self.payer is self.receiver
        ):
            raise FundingValidationError("payer and receiver must be distinct explicit sides")
        if (
            not isinstance(self.amount, Decimal)
            or not self.amount.is_finite()
            or self.amount <= 0
        ):
            raise FundingValidationError("payment amount must be positive")
        if not isinstance(self.denomination, str) or not self.denomination.strip():
            raise FundingValidationError("payment denomination must be explicit")
        object.__setattr__(self, "denomination", self.denomination.strip().upper())


@dataclass(frozen=True, slots=True)
class FuturesFundingSpecification:
    market: Market
    symbol: CanonicalFuturesSymbol
    funding_rate_unit: FundingRateUnit
    funding_sign_convention: FundingSignConvention
    funding_rate: Decimal | int | str
    interval_start: datetime
    interval_end: datetime
    rate_source: str
    observed_at: datetime
    notional_denomination: str

    def __post_init__(self):
        if not isinstance(self.market, Market):
            raise FundingValidationError("market must be a supported Futures market")
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise FundingValidationError("symbol must be canonical")
        if self.symbol.contract_family not in (
            ContractFamily.LINEAR,
            ContractFamily.INVERSE,
        ):
            raise FundingValidationError("unsupported contract family")
        if not isinstance(self.funding_rate_unit, FundingRateUnit):
            raise FundingValidationError("funding_rate_unit must be INTERVAL_RATE")
        if not isinstance(self.funding_sign_convention, FundingSignConvention):
            raise FundingValidationError("funding sign convention must be explicit")

        rate = _decimal(self.funding_rate, "funding_rate")
        start = _utc(self.interval_start, "interval_start")
        end = _utc(self.interval_end, "interval_end")
        observed = _utc(self.observed_at, "observed_at")

        if end <= start:
            raise FundingValidationError("funding interval must have positive duration")

        source = self.rate_source.strip() if isinstance(self.rate_source, str) else ""
        denomination = (
            self.notional_denomination.strip().upper()
            if isinstance(self.notional_denomination, str)
            else ""
        )
        if not source or not denomination:
            raise FundingValidationError(
                "funding provenance and denomination must be explicit"
            )

        object.__setattr__(self, "funding_rate", rate)
        object.__setattr__(self, "interval_start", start)
        object.__setattr__(self, "interval_end", end)
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "rate_source", source)
        object.__setattr__(self, "notional_denomination", denomination)

    @property
    def interval(self) -> timedelta:
        return self.interval_end - self.interval_start

    def validate_freshness(self, *, as_of: datetime, max_age: timedelta) -> None:
        current = _utc(as_of, "as_of")
        if not isinstance(max_age, timedelta) or max_age <= timedelta(0):
            raise FundingValidationError("max_age must be positive")
        if current < self.observed_at or current - self.observed_at > max_age:
            raise FundingValidationError(
                "funding observation is stale or time ordering is invalid"
            )

    def calculate_payment(
        self, *, notional, position_side: PositionSide
    ) -> FundingPayment | None:
        amount = _decimal(notional, "notional", positive=True)
        if not isinstance(position_side, PositionSide):
            raise FundingValidationError("position_side must be explicit")

        # Zero is a valid, meaningful funding rate: it produces no transfer.
        if self.funding_rate == 0:
            return None

        try:
            payment = amount * abs(self.funding_rate)
        except DecimalException as exc:
            raise FundingValidationError("funding payment is invalid") from exc
        if not payment.is_finite() or payment <= 0:
            raise FundingValidationError("funding payment is invalid")

        # Payer/receiver are determined by the signed market rate, never by
        # which position the caller is valuing. position_side validates context
        # only; using it to flip the market-wide sign convention is incorrect.
        payer = (
            PositionSide.LONG
            if self.funding_rate > 0
            else PositionSide.SHORT
        )
        receiver = (
            PositionSide.SHORT
            if payer is PositionSide.LONG
            else PositionSide.LONG
        )
        return FundingPayment(
            payer,
            receiver,
            payment,
            self.notional_denomination,
        )
