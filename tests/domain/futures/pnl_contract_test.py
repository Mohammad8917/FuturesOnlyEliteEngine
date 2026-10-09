"""Domain tests for exact realized and unrealized Futures PnL semantics."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from contracts.futures.instrument import CanonicalFuturesSymbol, ContractFamily, Market
from domain.futures.pnl import (
    FuturesPnLSpecification,
    PnLDenomination,
    PnLUnit,
    PnLValidationError,
)
from contracts.futures.position_side import PositionSide

UTC = timezone.utc


def make_spec(
    family: ContractFamily,
    market: Market = Market.CRYPTO,
) -> FuturesPnLSpecification:
    base_asset, quote_asset = {
        Market.CRYPTO: ("BTC", "USD"),
        Market.FOREX: ("EUR", "USD"),
        Market.GOLD: ("XAU", "USD"),
    }[market]
    symbol = CanonicalFuturesSymbol(
        base_asset,
        quote_asset,
        family,
        quote_asset,
    )
    return FuturesPnLSpecification(
        market=market,
        symbol=symbol,
        pnl_unit=PnLUnit.REALIZED_OR_UNREALIZED,
    )


@pytest.mark.parametrize(
    ("family", "denomination"),
    [
        (ContractFamily.LINEAR, PnLDenomination.QUOTE),
        (ContractFamily.INVERSE, PnLDenomination.BASE),
    ],
)
@pytest.mark.parametrize("market", list(Market))
def test_market_and_contract_family_have_explicit_denomination(
    family: ContractFamily,
    denomination: PnLDenomination,
    market: Market,
) -> None:
    assert make_spec(family, market).denomination is denomination


def test_linear_realized_pnl_respects_long_and_short() -> None:
    spec = make_spec(ContractFamily.LINEAR)
    common = {
        "quantity": Decimal("10"),
        "multiplier": Decimal("0.001"),
        "entry_price": Decimal("100"),
        "exit_price": Decimal("120"),
    }
    assert spec.calculate_realized(
        **common, position_side=PositionSide.LONG
    ) == Decimal("0.2")
    assert spec.calculate_realized(
        **common, position_side=PositionSide.SHORT
    ) == Decimal("-0.2")


def test_inverse_realized_pnl_respects_long_and_short() -> None:
    spec = make_spec(ContractFamily.INVERSE)
    common = {
        "quantity": Decimal("10"),
        "multiplier": Decimal("100"),
        "entry_price": Decimal("100"),
        "exit_price": Decimal("200"),
    }
    assert spec.calculate_realized(
        **common, position_side=PositionSide.LONG
    ) == Decimal("5")
    assert spec.calculate_realized(
        **common, position_side=PositionSide.SHORT
    ) == Decimal("-5")


def test_unrealized_pnl_preserves_decimal_input_precision() -> None:
    result = make_spec(ContractFamily.LINEAR).calculate_unrealized(
        quantity=Decimal("3"),
        multiplier=Decimal("0.1"),
        entry_price=Decimal("100.00"),
        valuation_price=Decimal("100.123456789"),
        position_side=PositionSide.LONG,
        valuation_source="test-reference",
        observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
    )
    assert result == Decimal("0.0370370367")


def test_zero_pnl_is_valid() -> None:
    result = make_spec(ContractFamily.LINEAR).calculate_unrealized(
        quantity=Decimal("1"),
        multiplier=Decimal("1"),
        entry_price=Decimal("100"),
        valuation_price=Decimal("100"),
        position_side=PositionSide.LONG,
        valuation_source="test-reference",
        observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
    )
    assert result == Decimal("0")


@pytest.mark.parametrize(
    "value",
    [True, False, 0, -1, 0.1, float("nan"), Decimal("NaN")],
)
def test_invalid_quantity_fails_closed(value: object) -> None:
    with pytest.raises(PnLValidationError):
        make_spec(ContractFamily.LINEAR).calculate_realized(
            quantity=value,  # type: ignore[arg-type]
            multiplier=Decimal("1"),
            entry_price=Decimal("100"),
            exit_price=Decimal("101"),
            position_side=PositionSide.LONG,
        )


def test_unrealized_pnl_requires_source_and_utc_timestamp() -> None:
    spec = make_spec(ContractFamily.LINEAR)
    with pytest.raises(PnLValidationError):
        spec.calculate_unrealized(
            quantity=Decimal("1"),
            multiplier=Decimal("1"),
            entry_price=Decimal("100"),
            valuation_price=Decimal("101"),
            position_side=PositionSide.LONG,
            valuation_source="",
            observed_at=datetime(2026, 1, 1, 12),
        )


def test_valuation_freshness_rejects_stale_and_future_observations() -> None:
    spec = make_spec(ContractFamily.LINEAR)
    observed = datetime(2026, 1, 1, 12, tzinfo=UTC)
    spec.validate_valuation_freshness(
        as_of=datetime(2026, 1, 1, 12, 30, tzinfo=UTC),
        observed_at=observed,
        max_age=timedelta(hours=1),
    )
    with pytest.raises(PnLValidationError):
        spec.validate_valuation_freshness(
            as_of=datetime(2026, 1, 1, 14, tzinfo=UTC),
            observed_at=observed,
            max_age=timedelta(hours=1),
        )
    with pytest.raises(PnLValidationError):
        spec.validate_valuation_freshness(
            as_of=observed,
            observed_at=observed + timedelta(minutes=1),
            max_age=timedelta(hours=1),
        )


def test_pnl_specification_is_immutable() -> None:
    spec = make_spec(ContractFamily.LINEAR)
    with pytest.raises(AttributeError):
        spec.pnl_unit = PnLUnit.REALIZED_OR_UNREALIZED  # type: ignore[misc]
