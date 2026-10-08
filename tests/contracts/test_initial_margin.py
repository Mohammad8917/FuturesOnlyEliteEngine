"""Contract tests for canonical Futures initial-margin semantics."""

from decimal import Decimal

import pytest

from contracts.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInitialMarginSpecification,
    FuturesInstrumentIdentity,
    InitialMarginUnit,
    InitialMarginValidationError,
    Market,
)


def _instrument(
    market: Market = Market.CRYPTO,
    family: ContractFamily = ContractFamily.LINEAR,
) -> FuturesInstrumentIdentity:
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


def test_initial_margin_calculation_is_exact_and_preserves_denomination() -> None:
    spec = FuturesInitialMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument(),
        initial_margin_unit=InitialMarginUnit.RATIO,
        initial_margin_ratio =Decimal("0.125"),
        notional_asset="USDT",
    )
    assert spec.calculate(Decimal("800.00")) == Decimal("100.00000")
    assert spec.notional_asset == "USDT"


@pytest.mark.parametrize("market", [Market.CRYPTO, Market.FOREX, Market.GOLD])
@pytest.mark.parametrize("family", [ContractFamily.LINEAR, ContractFamily.INVERSE])
def test_initial_margin_applies_to_all_supported_markets_and_families(
    market: Market, family: ContractFamily
) -> None:
    spec = FuturesInitialMarginSpecification(
        market=market,
        instrument=_instrument(market, family),
        initial_margin_unit=InitialMarginUnit.RATIO,
        initial_margin_ratio =Decimal("0.1"),
        notional_asset="USD" if market is not Market.CRYPTO else "USDT",
    )
    assert spec.calculate(Decimal("1000")) == Decimal("100.0")


@pytest.mark.parametrize(
    "ratio",
    [0.1, True, Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity")],
)
def test_invalid_initial_margin_ratio_fails_closed(ratio: object) -> None:
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            initial_margin_unit=InitialMarginUnit.RATIO,
            initial_margin_ratio =ratio,  # type: ignore[arg-type]
            notional_asset="USDT",
        )


@pytest.mark.parametrize(
    "notional",
    [0.1, True, Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity")],
)
def test_invalid_notional_fails_closed(notional: object) -> None:
    spec = FuturesInitialMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument(),
        initial_margin_unit=InitialMarginUnit.RATIO,
        initial_margin_ratio =Decimal("0.1"),
        notional_asset="USDT",
    )
    with pytest.raises(InitialMarginValidationError):
        spec.calculate(notional)  # type: ignore[arg-type]


@pytest.mark.parametrize("asset", ["", "SPOTUSDT", "USD/USDT", 1])
def test_invalid_notional_denomination_fails_closed(asset: object) -> None:
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            initial_margin_unit=InitialMarginUnit.RATIO,
            initial_margin_ratio =Decimal("0.1"),
            notional_asset=asset,  # type: ignore[arg-type]
        )


def test_market_mismatch_fails_closed() -> None:
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(
            market=Market.FOREX,
            instrument=_instrument(Market.CRYPTO),
            initial_margin_unit=InitialMarginUnit.RATIO,
            initial_margin_ratio =Decimal("0.1"),
            notional_asset="USD",
        )


def test_non_ratio_unit_fails_closed() -> None:
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument(),
            initial_margin_unit="RATIO",  # type: ignore[arg-type]
            initial_margin_ratio =Decimal("0.1"),
            notional_asset="USDT",
        )


def test_decimal_inputs_are_exact_and_immutable() -> None:
    spec = FuturesInitialMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument(),
        initial_margin_unit=InitialMarginUnit.RATIO,
        initial_margin_ratio="0.1250",  # type: ignore[arg-type]
        notional_asset="usdt",
    )
    assert spec.initial_margin_ratio == Decimal("0.1250")
    assert spec.notional_asset == "USDT"
    with pytest.raises((AttributeError, TypeError)):
        spec.initial_margin_ratio = Decimal("0.2")  # type: ignore[misc]


def test_initial_margin_does_not_depend_on_leverage() -> None:
    spec = FuturesInitialMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument(),
        initial_margin_unit=InitialMarginUnit.RATIO,
        initial_margin_ratio =Decimal("0.125"),
        notional_asset="USDT",
    )
    assert spec.calculate(Decimal("1600")) == Decimal("200.000")
