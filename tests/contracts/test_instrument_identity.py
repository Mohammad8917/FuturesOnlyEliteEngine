"""Contract tests for canonical Futures instrument identity."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from contracts.futures import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    InstrumentValidationError,
    Market,
)


def test_linear_perpetual_symbol_is_canonical_and_round_trips() -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="btc",
        quote_asset="usdt",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usdt",
    )

    assert symbol.as_text() == "BTC/USDT.LINEAR.USDT"
    assert CanonicalFuturesSymbol.parse(symbol.as_text()) == symbol


def test_inverse_dated_symbol_is_canonical_and_round_trips() -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="btc",
        quote_asset="usd",
        contract_family=ContractFamily.INVERSE,
        settlement_asset="btc",
        expiry=date(2026, 12, 25),
    )

    assert symbol.as_text() == "BTC/USD.INVERSE.BTC.20261225"
    assert CanonicalFuturesSymbol.parse(symbol.as_text()) == symbol


def test_identity_is_exchange_independent_and_deterministic() -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="eur",
        quote_asset="usd",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usd",
    )

    first = FuturesInstrumentIdentity.create(
        market=Market.FOREX,
        symbol=symbol,
    )
    second = FuturesInstrumentIdentity.create(
        market=Market.FOREX,
        symbol=symbol,
    )

    assert first.instrument_id == "FUTURES|FOREX|EUR/USD.LINEAR.USD"
    assert first == second


def test_identity_round_trip_from_canonical_id() -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="xau",
        quote_asset="usd",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usd",
    )
    identity = FuturesInstrumentIdentity.create(
        market=Market.GOLD,
        symbol=symbol,
    )

    parsed = FuturesInstrumentIdentity.parse_id(identity.instrument_id)

    assert parsed == identity


@pytest.mark.parametrize(
    "value",
    [
        "BTC/USDT.SPOT.USDT",
        "BTC-USDT",
        "BTC/USDT.LINEAR",
        "BTC/USDT.LINEAR.USDT.20261301",
        "SPOT/USDT.LINEAR.USDT",
    ],
)
def test_invalid_or_spot_symbol_fails_closed(value: str) -> None:
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol.parse(value)


def test_linear_identity_does_not_infer_economic_terms_from_symbol() -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="btc",
        quote_asset="usd",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="btc",
    )

    identity = FuturesInstrumentIdentity.create(
        market=Market.CRYPTO,
        symbol=symbol,
    )

    assert identity.instrument_id == "FUTURES|CRYPTO|BTC/USD.LINEAR.BTC"


def test_datetime_is_not_accepted_as_a_date_expiry() -> None:
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol(
            base_asset="btc",
            quote_asset="usd",
            contract_family=ContractFamily.INVERSE,
            settlement_asset="btc",
            expiry=datetime(2026, 12, 25),
        )


def test_instrument_id_cannot_be_rebound_to_another_symbol() -> None() -> None:
    symbol = CanonicalFuturesSymbol(
        base_asset="btc",
        quote_asset="usdt",
        contract_family=ContractFamily.LINEAR,
        settlement_asset="usdt",
    )

    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity(
            instrument_id="FUTURES|CRYPTO|ETH/USDT.LINEAR.USDT",
            market=Market.CRYPTO,
            symbol=symbol,
            )
