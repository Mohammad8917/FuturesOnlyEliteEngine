"""Contract tests for canonical Futures multiplier/specification semantics."""

from __future__ import annotations

from decimal import Decimal

import pytest

from contracts.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    ContractSpecificationValidationError,
    FuturesContractSpecification,
    Market,
    QuantityUnit,
)


def _linear() -> FuturesContractSpecification:
    return FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=CanonicalFuturesSymbol(
            base_asset="btc",
            quote_asset="usdt",
            contract_family=ContractFamily.LINEAR,
            settlement_asset="usdt",
        ),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier =Decimal("0.001"),  # type: ignore[misc]
        price_quote_asset="usdt",
    )


def _inverse() -> FuturesContractSpecification:
    return FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=CanonicalFuturesSymbol(
            base_asset="btc",
            quote_asset="usd",
            contract_family=ContractFamily.INVERSE,
            settlement_asset="btc",
        ),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier =Decimal("100"),  # type: ignore[misc]
        price_quote_asset="usd",
    )


@pytest.mark.parametrize("market", [Market.CRYPTO, Market.FOREX, Market.GOLD])
def test_multiplier_contract_is_explicit_for_all_supported_futures_markets(
    market: Market,
) -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="eur" if market is Market.FOREX else "btc" if market is Market.CRYPTO else "xau",
        quote_asset="usd" if market is not Market.CRYPTO else "usdt",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usd" if market is not Market.CRYPTO else "usdt",
    )
    spec = FuturesContractSpecification(
        market=market,
        symbol=symbol,
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier =Decimal("1.25"),  # type: ignore[misc]
        price_quote_asset=symbol.quote_asset,
    )

    assert spec.quantity_unit is QuantityUnit.CONTRACTS
    assert spec.contract_size == Decimal("1.25")


def test_linear_notional_and_base_exposure_are_dimensionally_explicit() -> None:
    spec = _linear()

    assert spec.notional(quantity=Decimal("10"), price=Decimal("50000")) == Decimal("500")
    assert spec.base_exposure(quantity=Decimal("10"), price=Decimal("50000")) == Decimal("0.010")


def test_inverse_notional_and_base_exposure_are_distinct() -> None:
    spec = _inverse()

    assert spec.notional(quantity=Decimal("10"), price=Decimal("50000")) == Decimal("1000")
    assert spec.base_exposure(quantity=Decimal("10"), price=Decimal("50000")) == Decimal("0.02")


def test_decimal_math_is_exact_and_does_not_require_float_conversion() -> None:
    spec = _linear()

    value = spec.notional(quantity=Decimal("3"), price=Decimal("0.1"))
    assert value == Decimal("0.0003")
    assert isinstance(value, Decimal)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("contract_multiplier", Decimal("0")),
        ("contract_multiplier", Decimal("-1")),
        ("contract_multiplier", Decimal("NaN")),
        ("contract_multiplier", Decimal("Infinity")),
    ],
)
def test_invalid_multiplier_fails_closed(field: str, value: Decimal) -> None:
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(
            market=Market.CRYPTO,
            symbol=_linear().symbol,
            quantity_unit=QuantityUnit.CONTRACTS,
            contract_multiplier =value,  # type: ignore[misc]
            price_quote_asset="usdt",
        )


@pytest.mark.parametrize(
    ("quantity", "price"),
    [
        (Decimal("0"), Decimal("100")),
        (Decimal("-1"), Decimal("100")),
        (Decimal("1"), Decimal("0")),
        (Decimal("1"), Decimal("-100")),
    ],
)
def test_non_positive_quantity_or_price_fails_closed(
    quantity: Decimal, price: Decimal
) -> None:
    with pytest.raises(ContractSpecificationValidationError):
        _linear().notional(quantity=quantity, price=price)


def test_quote_denomination_mismatch_fails_closed() -> None:
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(
            market=Market.CRYPTO,
            symbol=_linear().symbol,
            quantity_unit=QuantityUnit.CONTRACTS,
            contract_multiplier =Decimal("1"),  # type: ignore[misc]
            price_quote_asset="usd",
        )


def test_specification_is_immutable() -> None:
    spec = _linear()

    with pytest.raises(AttributeError):
        spec.contract_multiplier = Decimal("2")
