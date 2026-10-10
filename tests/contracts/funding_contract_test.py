from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from contracts.futures.funding import (
    FundingRateUnit,
    FundingSignConvention,
    FundingValidationError,
    FuturesFundingSpecification,
)
from contracts.futures.instrument import CanonicalFuturesSymbol, ContractFamily, Market
from contracts.futures.position_side import PositionSide


UTC = timezone.utc


def symbol(family):
    return CanonicalFuturesSymbol(
        base_asset="BTC",
        quote_asset="USDT",
        settlement_asset="USDT",
        contract_family=family,
    )


def funding(family=ContractFamily.LINEAR, rate=Decimal("0.000125")):
    return FuturesFundingSpecification(
        market=Market.CRYPTO,
        symbol=symbol(family),
        funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
        funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
        funding_rate=rate,
        interval_start=datetime(2026, 1, 1, tzinfo=UTC),
        interval_end=datetime(2026, 1, 1, 8, tzinfo=UTC),
        rate_source="synthetic-test-source",
        observed_at=datetime(2026, 1, 1, 7, 30, tzinfo=UTC),
        notional_denomination="USDT",
    )


@pytest.mark.parametrize("family", [ContractFamily.LINEAR, ContractFamily.INVERSE])
@pytest.mark.parametrize("market", list(Market))
def test_contract_is_explicit_across_markets_and_families(family, market):
    spec = FuturesFundingSpecification(
        market=market,
        symbol=CanonicalFuturesSymbol(
            base_asset="BTC",
            quote_asset="USD",
            settlement_asset="USD",
            contract_family=family,
        ),
        funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
        funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
        funding_rate=Decimal("0.00000125"),
        interval_start=datetime(2026, 1, 1, tzinfo=UTC),
        interval_end=datetime(2026, 1, 1, 8, tzinfo=UTC),
        rate_source="synthetic-test-source",
        observed_at=datetime(2026, 1, 1, 7, tzinfo=UTC),
        notional_denomination="USD",
    )
    assert spec.interval == timedelta(hours=8)


def test_positive_rate_long_pays_and_exact_amount():
    payment = funding().calculate_payment(
        notional=Decimal("123456789.123456789"),
        position_side=PositionSide.LONG,
    )
    assert payment is not None
    assert payment.payer is PositionSide.LONG
    assert payment.receiver is PositionSide.SHORT
    assert payment.amount == Decimal("15432.098640432098625")
    assert payment.denomination == "USDT"


def test_negative_rate_reverses_payer():
    payment = funding(rate=Decimal("-0.000125")).calculate_payment(
        notional=Decimal("1000"),
        position_side=PositionSide.LONG,
    )
    assert payment is not None
    assert payment.payer is PositionSide.SHORT
    assert payment.receiver is PositionSide.LONG
    assert payment.amount == Decimal("0.125")


def test_zero_rate_is_valid_but_creates_no_transfer():
    assert funding(rate=Decimal("0")).calculate_payment(
        notional=Decimal("1000"),
        position_side=PositionSide.LONG,
    ) is None


@pytest.mark.parametrize(
    "value",
    [True, False, 0.1, float("nan"), float("inf"), Decimal("NaN"), Decimal("Infinity")],
)
def test_binary_float_bool_and_nonfinite_rate_are_rejected(value):
    with pytest.raises(FundingValidationError):
        funding(rate=value)


@pytest.mark.parametrize("value", [True, False, 0, -1, 0.0, None, Decimal("NaN")])
def test_invalid_notional_is_rejected(value):
    with pytest.raises(FundingValidationError):
        funding().calculate_payment(
            notional=value,
            position_side=PositionSide.LONG,
        )


def test_utc_and_interval_are_fail_closed():
    with pytest.raises(FundingValidationError):
        FuturesFundingSpecification(
            market=Market.CRYPTO,
            symbol=symbol(ContractFamily.LINEAR),
            funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
            funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
            funding_rate=Decimal("0.1"),
            interval_start=datetime(2026, 1, 1),
            interval_end=datetime(2026, 1, 1, 8),
            rate_source="synthetic",
            observed_at=datetime(2026, 1, 1, 7, tzinfo=UTC),
            notional_denomination="USDT",
        )


def test_freshness_is_explicit_and_fail_closed():
    spec = funding()
    spec.validate_freshness(
        as_of=datetime(2026, 1, 1, 7, 45, tzinfo=UTC),
        max_age=timedelta(hours=1),
    )
    with pytest.raises(FundingValidationError):
        spec.validate_freshness(
            as_of=datetime(2026, 1, 1, 9, tzinfo=UTC),
            max_age=timedelta(hours=1),
        )


def test_missing_provenance_and_denomination_are_rejected():
    with pytest.raises(FundingValidationError):
        FuturesFundingSpecification(
            market=Market.CRYPTO,
            symbol=symbol(ContractFamily.LINEAR),
            funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
            funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
            funding_rate=Decimal("0.1"),
            interval_start=datetime(2026, 1, 1, tzinfo=UTC),
            interval_end=datetime(2026, 1, 1, 8, tzinfo=UTC),
            rate_source="",
            observed_at=datetime(2026, 1, 1, 7, tzinfo=UTC),
            notional_denomination="USDT",
        )


def test_specification_is_immutable():
    spec = funding()
    with pytest.raises((AttributeError, TypeError)):
        spec.funding_rate = Decimal("1")


def test_rate_vocabulary_is_frozen():
    assert FundingRateUnit.INTERVAL_RATE.value == "INTERVAL_RATE"
    assert FundingSignConvention.POSITIVE_LONG_PAYS.value == "POSITIVE_LONG_PAYS"



@pytest.mark.parametrize(
    ("rate", "position_side", "expected_payer", "expected_receiver"),
    [
        (Decimal("0.01"), PositionSide.LONG, PositionSide.LONG, PositionSide.SHORT),
        (Decimal("0.01"), PositionSide.SHORT, PositionSide.LONG, PositionSide.SHORT),
        (Decimal("-0.01"), PositionSide.LONG, PositionSide.SHORT, PositionSide.LONG),
        (Decimal("-0.01"), PositionSide.SHORT, PositionSide.SHORT, PositionSide.LONG),
    ],
)
def test_funding_payer_is_determined_by_rate_not_callers_position(
    rate, position_side, expected_payer, expected_receiver
):
    payment = funding(rate=rate).calculate_payment(
        notional=Decimal("1000"),
        position_side=position_side,
    )
    assert payment is not None
    assert payment.payer is expected_payer
    assert payment.receiver is expected_receiver
    assert payment.amount == Decimal("10")
