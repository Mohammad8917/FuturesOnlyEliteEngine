"""Contract tests for canonical Futures margin semantics."""

from decimal import Decimal

import pytest

from contracts.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    FuturesMarginSpecification,
    MarginUnit,
    MarginValidationError,
    Market,
)


def _instrument(margin_asset: str = "usdt") -> FuturesInstrumentIdentity:
    symbol = CanonicalFuturesSymbol(
        base_asset="btc",
        quote_asset="usdt",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usdt",
    )
    return FuturesInstrumentIdentity.create(
        market=Market.CRYPTO,
        symbol=symbol,
        margin_asset=margin_asset,
    )


def test_same_asset_margin_requires_no_conversion() -> None:
    spec = FuturesMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument("usdt"),
        margin_unit=MarginUnit.ASSET,
        margin_asset="usdt",
        source_asset="usdt",
    )

    assert spec.conversion_required is False
    assert spec.to_margin_amount(Decimal("12.5")) == Decimal("12.5")


def test_cross_asset_margin_requires_explicit_rate() -> None:
    spec = FuturesMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument("usdt"),
        margin_unit=MarginUnit.ASSET,
        margin_asset="usdt",
        source_asset="usd",
        conversion_rate=Decimal("1.01"),
    )

    assert spec.conversion_required is True
    assert spec.to_margin_amount(Decimal("100")) == Decimal("101")


@pytest.mark.parametrize("market", [Market.CRYPTO, Market.FOREX, Market.GOLD])
@pytest.mark.parametrize("family", [ContractFamily.LINEAR, ContractFamily.INVERSE])
def test_margin_contract_applies_to_all_supported_markets_and_families(
    market: Market, family: ContractFamily
) -> None:
    if market is Market.CRYPTO:
        base, quote, settlement, margin = "btc", "usdt", "usdt", "btc"
    elif market is Market.FOREX:
        base, quote, settlement, margin = "eur", "usd", "usd", "eur"
    else:
        base, quote, settlement, margin = "xau", "usd", "usd", "usd"

    symbol = CanonicalFuturesSymbol(
        base_asset=base,
        quote_asset=quote,
        contract_family=family,
        settlement_asset=settlement,
    )
    instrument = FuturesInstrumentIdentity.create(
        market=market,
        symbol=symbol,
        margin_asset=margin,
    )
    spec = FuturesMarginSpecification(
        market=market,
        instrument=instrument,
        margin_unit=MarginUnit.ASSET,
        margin_asset=margin,
        source_asset=margin,
    )

    assert spec.margin_asset == margin
    assert spec.symbol == symbol


def test_margin_asset_mismatch_fails_closed() -> None:
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument("btc"),
            margin_unit=MarginUnit.ASSET,
            margin_asset="usdt",
            source_asset="usdt",
        )


def test_market_mismatch_fails_closed() -> None:
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            market=Market.FOREX,
            instrument=_instrument("usdt"),
            margin_unit=MarginUnit.ASSET,
            margin_asset="usdt",
            source_asset="usdt",
        )


@pytest.mark.parametrize("rate", [Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity")])
def test_invalid_conversion_rate_fails_closed(rate: Decimal) -> None:
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument("usdt"),
            margin_unit=MarginUnit.ASSET,
            margin_asset="usdt",
            source_asset="usd",
            conversion_rate=rate,
        )


def test_missing_cross_asset_rate_fails_closed() -> None:
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument("usdt"),
            margin_unit=MarginUnit.ASSET,
            margin_asset="usdt",
            source_asset="usd",
        )


def test_unexpected_same_asset_rate_fails_closed() -> None:
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            market=Market.CRYPTO,
            instrument=_instrument("usdt"),
            margin_unit=MarginUnit.ASSET,
            margin_asset="usdt",
            source_asset="usdt",
            conversion_rate=Decimal("1"),
        )


def test_non_positive_amount_fails_closed() -> None:
    spec = FuturesMarginSpecification(
        market=Market.CRYPTO,
        instrument=_instrument("usdt"),
        margin_unit=MarginUnit.ASSET,
        margin_asset="usdt",
        source_asset="usdt",
    )
    with pytest.raises(MarginValidationError):
        spec.to_margin_amount(Decimal("0"))
