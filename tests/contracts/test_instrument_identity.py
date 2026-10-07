"""Contract tests for canonical Futures instrument identity."""

from __future__ import annotations

from datetime import date

import pytest

from contracts.futures.instrument import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    InstrumentStatus,
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
        margin_asset="usd",
    )
    second = FuturesInstrumentIdentity.create(
        market=Market.FOREX,
        symbol=symbol,
        margin_asset="usd",
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
        margin_asset="usd",
        status=InstrumentStatus.ACTIVE,
    )

    parsed = FuturesInstrumentIdentity.parse_id(
        identity.instrument_id,
        margin_asset="usd",
    )

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


def test_linear_base_settlement_ambiguity_fails_closed() -> None:
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol(
            base_asset="btc",
            quote_asset="usdt",
            contract_family=ContractFamily.LINEAR,
            settlement_asset="btc",
        )


def test_instrument_id_cannot_be_rebound_to_another_symbol() -> None:
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
            margin_asset="usdt",
        )
