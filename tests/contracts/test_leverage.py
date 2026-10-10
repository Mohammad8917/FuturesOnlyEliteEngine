"""Contract tests for canonical Futures leverage semantics."""

from decimal import Decimal

import pytest

from contracts.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    FuturesLeverageSpecification,
    LeverageUnit,
    LeverageValidationError,
    Market,
)


def _instrument(
    market: Market = Market.CRYPTO, family: ContractFamily = ContractFamily.LINEAR
):
    if market is Market.CRYPTO:
        base, quote, settlement, margin = "btc", "usdt", "usdt", "usdt"
    elif market is Market.FOREX:
        base, quote, settlement, margin = "eur", "usd", "usd", "usd"
    else:
        base, quote, settlement, margin = "xau", "usd", "usd", "usd"
    return FuturesInstrumentIdentity.create(
        market=market,
        symbol=CanonicalFuturesSymbol(
            base_asset=base,
            quote_asset=quote,
            contract_family=family,
            settlement_asset=settlement,
        ),
        margin_asset=margin,
    )


def test_leverage_is_exact_and_within_explicit_bounds() -> None:
    spec = FuturesLeverageSpecification(
        market=Market.CRYPTO,
        instrument=_instrument(),
        leverage_unit=LeverageUnit.RATIO,
        leverage=Decimal("12.5"),
        minimum_leverage=Decimal("1"),
        maximum_leverage=Decimal("20"),
    )
    assert spec.leverage == Decimal("12.5")
    assert spec.is_within_contract_bounds is True


@pytest.mark.parametrize("market", [Market.CRYPTO, Market.FOREX, Market.GOLD])
@pytest.mark.parametrize("family", [ContractFamily.LINEAR, ContractFamily.INVERSE])
def test_leverage_applies_to_all_supported_markets_and_families(
    market: Market, family: ContractFamily
) -> None:
    spec = FuturesLeverageSpecification(
        market=market,
        instrument=_instrument(market, family),
        leverage_unit=LeverageUnit.RATIO,
        leverage=Decimal("2"),
        minimum_leverage=Decimal("1"),
        maximum_leverage=Decimal("5"),
    )
    assert spec.is_within_contract_bounds is True


@pytest.mark.parametrize(
    "leverage",
    [0.1, True, Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity")],
)
def test_invalid_leverage_fails_closed(leverage: Decimal) -> None:
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            leverage_unit=LeverageUnit.RATIO,
            leverage=leverage,
            minimum_leverage=Decimal("1"),
            maximum_leverage=Decimal("20"),
        )


@pytest.mark.parametrize(
    "minimum,maximum",
    [
        (0.1, Decimal("20")),
        (True, Decimal("20")),
        (Decimal("0"), Decimal("20")),
        (Decimal("-1"), Decimal("20")),
        (Decimal("1"), Decimal("0")),
        (Decimal("1"), Decimal("-1")),
        (Decimal("1"), Decimal("NaN")),
        (Decimal("1"), Decimal("Infinity")),
    ],
)
def test_invalid_contract_bounds_fail_closed(
    minimum: Decimal, maximum: Decimal
) -> None:
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            leverage_unit=LeverageUnit.RATIO,
            leverage=Decimal("2"),
            minimum_leverage=minimum,
            maximum_leverage=maximum,
        )


def test_reversed_bounds_fail_closed() -> None:
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            leverage_unit=LeverageUnit.RATIO,
            leverage=Decimal("2"),
            minimum_leverage=Decimal("10"),
            maximum_leverage=Decimal("5"),
        )


@pytest.mark.parametrize(
    "leverage",
    [Decimal("0.99"), Decimal("20.01")],
)
def test_leverage_outside_explicit_bounds_fails_closed(leverage: Decimal) -> None:
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            leverage_unit=LeverageUnit.RATIO,
            leverage=leverage,
            minimum_leverage=Decimal("1"),
            maximum_leverage=Decimal("20"),
        )


def test_market_mismatch_fails_closed() -> None:
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            market=Market.FOREX,
            instrument=_instrument(Market.CRYPTO),
            leverage_unit=LeverageUnit.RATIO,
            leverage=Decimal("2"),
            minimum_leverage=Decimal("1"),
            maximum_leverage=Decimal("20"),
        )


def test_non_ratio_unit_fails_closed() -> None:
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            leverage_unit="RATIO",
            leverage=Decimal("2"),
            minimum_leverage=Decimal("1"),
            maximum_leverage=Decimal("20"),
        )


def test_decimal_conversion_is_exact_and_immutable() -> None:
    spec = FuturesLeverageSpecification(
        market=Market.CRYPTO,
        instrument=_instrument(),
        leverage_unit=LeverageUnit.RATIO,
        leverage="12.500",
        minimum_leverage="1",
        maximum_leverage="20",
    )
    assert spec.leverage == Decimal("12.500")
    with pytest.raises((AttributeError, TypeError)):
        spec.leverage = Decimal("5")
