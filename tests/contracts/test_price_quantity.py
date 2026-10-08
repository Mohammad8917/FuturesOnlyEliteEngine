"""Contract tests for canonical Futures price/quantity semantics."""

from decimal import Decimal

import pytest

from contracts.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesPriceQuantitySpecification,
    Market,
    PrecisionPolicy,
    PriceQuantityValidationError,
    PriceUnit,
    QuantityUnit,
    RoundingPolicy,
)


def make_spec(market: Market, family: ContractFamily) -> FuturesPriceQuantitySpecification:
    return FuturesPriceQuantitySpecification(
        market,
        CanonicalFuturesSymbol("BTC", "USDT", family, "USDT"),
        PriceUnit.QUOTE_PER_BASE,
        QuantityUnit.CONTRACTS,
        "USDT",
        PrecisionPolicy.EXACT,
        RoundingPolicy.NONE,
    )


@pytest.mark.parametrize("market", list(Market))
@pytest.mark.parametrize("family", list(ContractFamily))
def test_supported_markets_and_families_are_explicit(
    market: Market, family: ContractFamily
) -> None:
    spec = make_spec(market, family)
    assert spec.market is market
    assert spec.symbol.contract_family is family


def test_price_is_exact_and_not_rounded() -> None:
    assert make_spec(
        Market.CRYPTO, ContractFamily.LINEAR
    ).quote_per_base("123.456789012345678901") == Decimal(
        "123.456789012345678901"
    )


@pytest.mark.parametrize("value", [0, -1, "NaN", "Infinity", True, 0.1, None])
def test_invalid_price_fails_closed(value: object) -> None:
    with pytest.raises(PriceQuantityValidationError):
        make_spec(
            Market.CRYPTO, ContractFamily.LINEAR
        ).validate_price(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, "NaN", "Infinity", True, 0.1, None])
def test_invalid_quantity_fails_closed(value: object) -> None:
    with pytest.raises(PriceQuantityValidationError):
        make_spec(
            Market.CRYPTO, ContractFamily.LINEAR
        ).validate_quantity(value)  # type: ignore[arg-type]


def test_quote_asset_mismatch_fails_closed() -> None:
    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(
            Market.CRYPTO,
            CanonicalFuturesSymbol(
                "BTC", "USDT", ContractFamily.LINEAR, "USDT"
            ),
            PriceUnit.QUOTE_PER_BASE,
            QuantityUnit.CONTRACTS,
            "USD",
            PrecisionPolicy.EXACT,
            RoundingPolicy.NONE,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"price_unit": "QUOTE_PER_BASE"},
        {"quantity_unit": "BASE"},
        {"precision_policy": "TICK"},
        {"rounding_policy": "HALF_UP"},
    ],
)
def test_unsupported_semantic_vocabulary_fails_closed(
    kwargs: dict[str, object],
) -> None:
    base: dict[str, object] = {
        "market": Market.CRYPTO,
        "symbol": CanonicalFuturesSymbol(
            "BTC", "USDT", ContractFamily.LINEAR, "USDT"
        ),
        "price_unit": PriceUnit.QUOTE_PER_BASE,
        "quantity_unit": QuantityUnit.CONTRACTS,
        "price_quote_asset": "USDT",
        "precision_policy": PrecisionPolicy.EXACT,
        "rounding_policy": RoundingPolicy.NONE,
    }
    base.update(kwargs)
    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(**base)  # type: ignore[arg-type]


def test_precision_and_rounding_are_explicit_and_immutable() -> None:
    spec = make_spec(Market.GOLD, ContractFamily.INVERSE)
    assert spec.precision_policy is PrecisionPolicy.EXACT
    assert spec.rounding_policy is RoundingPolicy.NONE
    with pytest.raises((AttributeError, TypeError)):
        object.__setattr__(spec, "rounding_policy", RoundingPolicy.NONE)
