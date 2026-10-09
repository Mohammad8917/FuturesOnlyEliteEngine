"""Contract tests for canonical Futures settlement semantics."""

from decimal import Decimal

import pytest

from domain.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesSettlementSpecification,
    Market,
    SettlementUnit,
    SettlementValidationError,
)


def _symbol() -> CanonicalFuturesSymbol:
    return CanonicalFuturesSymbol(
        base_asset="btc",
        quote_asset="usdt",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usdt",
    )


def test_same_asset_settlement_requires_no_conversion() -> None:
    spec = FuturesSettlementSpecification(
        market=Market.CRYPTO,
        symbol=_symbol(),
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset="usdt",
        source_asset="usdt",
    )

    assert spec.conversion_required is False
    assert spec.settle_amount(Decimal("12.5")) == Decimal("12.5")


def test_cross_asset_settlement_requires_explicit_rate() -> None:
    spec = FuturesSettlementSpecification(
        market=Market.CRYPTO,
        symbol=_symbol(),
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset="usdt",
        source_asset="usd",
        conversion_rate=Decimal("1.01"),
    )

    assert spec.conversion_required is True
    assert spec.settle_amount(Decimal("100")) == Decimal("101")


@pytest.mark.parametrize("market", [Market.CRYPTO, Market.FOREX, Market.GOLD])
def test_settlement_contract_applies_to_all_supported_futures_markets(
    market: Market,
) -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="btc"
        if market is Market.CRYPTO
        else "eur"
        if market is Market.FOREX
        else "xau",
        quote_asset="usdt" if market is Market.CRYPTO else "usd",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usdt" if market is Market.CRYPTO else "usd",
    )
    spec = FuturesSettlementSpecification(
        market=market,
        symbol=symbol,
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset=symbol.settlement_asset,
        source_asset=symbol.settlement_asset,
    )

    assert spec.settlement_asset == symbol.settlement_asset


def test_settlement_asset_mismatch_fails_closed() -> None:
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            market=Market.CRYPTO,
            symbol=_symbol(),
            settlement_unit=SettlementUnit.ASSET,
            settlement_asset="btc",
            source_asset="btc",
        )


def test_missing_cross_asset_rate_fails_closed() -> None:
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            market=Market.CRYPTO,
            symbol=_symbol(),
            settlement_unit=SettlementUnit.ASSET,
            settlement_asset="usdt",
            source_asset="usd",
        )


def test_unexpected_same_asset_rate_fails_closed() -> None:
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            market=Market.CRYPTO,
            symbol=_symbol(),
            settlement_unit=SettlementUnit.ASSET,
            settlement_asset="usdt",
            source_asset="usdt",
            conversion_rate=Decimal("1"),
        )


@pytest.mark.parametrize(
    "rate", [Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity")]
)
def test_invalid_conversion_rate_fails_closed(rate: Decimal) -> None:
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            market=Market.CRYPTO,
            symbol=_symbol(),
            settlement_unit=SettlementUnit.ASSET,
            settlement_asset="usdt",
            source_asset="usd",
            conversion_rate=rate,
        )


@pytest.mark.parametrize("amount", [1, "1", 1.0, True])
def test_non_decimal_amount_fails_closed(amount: object) -> None:
    spec = FuturesSettlementSpecification(
        market=Market.CRYPTO,
        symbol=_symbol(),
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset="usdt",
        source_asset="usdt",
    )

    with pytest.raises(SettlementValidationError):
        spec.settle_amount(amount)  # type: ignore[arg-type]


def test_non_positive_amount_fails_closed() -> None:
    spec = FuturesSettlementSpecification(
        market=Market.CRYPTO,
        symbol=_symbol(),
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset="usdt",
        source_asset="usdt",
    )

    with pytest.raises(SettlementValidationError):
        spec.settle_amount(Decimal("0"))
