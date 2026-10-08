"""Fail-closed constructor and freshness guards for canonical Futures contracts."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from contracts.futures.contract_specification import QuantityUnit
from contracts.futures.exposure import ExposureValidationError, FuturesExposureSpecification
from contracts.futures.instrument import CanonicalFuturesSymbol, ContractFamily, Market
from contracts.futures.pnl import FuturesPnLSpecification, PnLUnit, PnLValidationError
from contracts.futures.position_side import PositionSide
from contracts.futures.price_quantity import (
    FuturesPriceQuantitySpecification,
    PrecisionPolicy,
    PriceQuantityValidationError,
    PriceUnit,
    RoundingPolicy,
)

UTC = timezone.utc


def _symbol() -> CanonicalFuturesSymbol:
    return CanonicalFuturesSymbol(
        base_asset="BTC",
        quote_asset="USDT",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="USDT",
    )


@pytest.mark.parametrize(
    ("market", "symbol", "pnl_unit"),
    [
        ("CRYPTO", _symbol(), PnLUnit.REALIZED_OR_UNREALIZED),
        (Market.CRYPTO, "BTCUSDT", PnLUnit.REALIZED_OR_UNREALIZED),
        (Market.CRYPTO, _symbol(), "REALIZED_OR_UNREALIZED"),
    ],
)
def test_pnl_constructor_rejects_untrusted_runtime_types(
    market: object,
    symbol: object,
    pnl_unit: object,
) -> None:
    with pytest.raises(PnLValidationError):
        FuturesPnLSpecification(
            market=market,  # type: ignore[arg-type]
            symbol=symbol,  # type: ignore[arg-type]
            pnl_unit=pnl_unit,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("market", "symbol", "quantity_unit"),
    [
        ("CRYPTO", _symbol(), QuantityUnit.CONTRACTS),
        (Market.CRYPTO, "BTCUSDT", QuantityUnit.CONTRACTS),
        (Market.CRYPTO, _symbol(), "CONTRACTS"),
    ],
)
def test_price_quantity_constructor_rejects_untrusted_runtime_types(
    market: object,
    symbol: object,
    quantity_unit: object,
) -> None:
    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(
            market=market,  # type: ignore[arg-type]
            symbol=symbol,  # type: ignore[arg-type]
            price_unit=PriceUnit.QUOTE_PER_BASE,
            quantity_unit=quantity_unit,  # type: ignore[arg-type]
            price_quote_asset="USDT",
            precision_policy=PrecisionPolicy.EXACT,
            rounding_policy=RoundingPolicy.NONE,
        )


@pytest.mark.parametrize(
    ("market", "symbol"),
    [
        ("CRYPTO", _symbol()),
        (Market.CRYPTO, "BTCUSDT"),
    ],
)
def test_exposure_constructor_rejects_untrusted_runtime_types(
    market: object,
    symbol: object,
) -> None:
    with pytest.raises(ExposureValidationError):
        FuturesExposureSpecification(
            market=market,  # type: ignore[arg-type]
            symbol=symbol,  # type: ignore[arg-type]
        )


def test_exposure_freshness_rejects_non_positive_max_age() -> None:
    specification = FuturesExposureSpecification(Market.CRYPTO, _symbol())
    observed_at = datetime(2026, 1, 1, 12, tzinfo=UTC)

    with pytest.raises(ExposureValidationError):
        specification.validate_reference_freshness(
            as_of=observed_at,
            observed_at=observed_at,
            max_age=timedelta(0),
        )


def test_pnl_rejects_non_positive_freshness_window() -> None:
    specification = FuturesPnLSpecification(
        Market.CRYPTO,
        _symbol(),
        PnLUnit.REALIZED_OR_UNREALIZED,
    )
    observed_at = datetime(2026, 1, 1, 12, tzinfo=UTC)

    with pytest.raises(PnLValidationError):
        specification.validate_valuation_freshness(
            as_of=observed_at,
            observed_at=observed_at,
            max_age=timedelta(0),
        )


def test_exact_decimal_inputs_remain_accepted_by_numeric_contracts() -> None:
    spec = FuturesPriceQuantitySpecification(
        market=Market.CRYPTO,
        symbol=_symbol(),
        price_unit=PriceUnit.QUOTE_PER_BASE,
        quantity_unit=QuantityUnit.CONTRACTS,
        price_quote_asset="USDT",
        precision_policy=PrecisionPolicy.EXACT,
        rounding_policy=RoundingPolicy.NONE,
    )
    assert spec.validate_price(Decimal("123.4500")) == Decimal("123.4500")
