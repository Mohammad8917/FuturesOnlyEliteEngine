"""Coverage regressions for defensive branches exposed by canonical formatting.

These tests exercise existing fail-closed behavior. They do not alter runtime
contracts, coverage thresholds, or production semantics.
"""
from decimal import Decimal
from typing import cast

import pytest

from contracts.futures.accounting import (
    AccountingValidationError,
    FuturesAccountingJournal,
)
from contracts.futures.contract_specification import (
    ContractSpecificationValidationError,
    FuturesContractSpecification,
    QuantityUnit,
)
from contracts.futures.exposure import (
    ExposureValidationError,
    FuturesExposureSpecification,
)
from contracts.futures.instrument import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    Market,
)
from contracts.futures.liquidation import (
    FuturesLiquidationSpecification,
    LiquidationValidationError,
)
from contracts.futures.pnl import FuturesPnLSpecification, PnLUnit, PnLValidationError
from contracts.futures.price_quantity import (
    FuturesPriceQuantitySpecification,
    PrecisionPolicy,
    PriceQuantityValidationError,
    PriceUnit,
    RoundingPolicy,
)
from contracts.futures.settlement_accounting import (
    FuturesSettlementAccountingSpecification,
)
from contracts.futures.settlement import (
    FuturesSettlementSpecification,
    SettlementUnit,
)


def make_symbol() -> CanonicalFuturesSymbol:
    return CanonicalFuturesSymbol("BTC", "USD", ContractFamily.LINEAR, "USD")


def make_contract(
    symbol: CanonicalFuturesSymbol,
) -> FuturesContractSpecification:
    return FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=symbol,
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"),
        price_quote_asset="USD",
    )


def test_empty_accounting_journal_fails_closed() -> None:
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("empty", ())


def test_contract_calculations_reject_corrupted_family_state() -> None:
    symbol = make_symbol()
    contract = make_contract(symbol)
    object.__setattr__(symbol, "contract_family", cast(ContractFamily, object()))

    with pytest.raises(ContractSpecificationValidationError):
        contract.notional(quantity=1, price=10)
    with pytest.raises(ContractSpecificationValidationError):
        contract.base_exposure(quantity=1, price=10)


def test_exposure_rejects_unsupported_contract_family() -> None:
    symbol = make_symbol()
    object.__setattr__(symbol, "contract_family", cast(ContractFamily, object()))

    with pytest.raises(ExposureValidationError):
        FuturesExposureSpecification(Market.CRYPTO, symbol)


def test_exposure_rejects_non_finite_contract_calculations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    symbol = make_symbol()
    contract = make_contract(symbol)
    specification = FuturesExposureSpecification(Market.CRYPTO, symbol)

    def non_finite_calculation(
        self: FuturesContractSpecification,
        *,
        quantity: Decimal | int | str,
        price: Decimal | int | str,
    ) -> Decimal:
        return Decimal("NaN")

    monkeypatch.setattr(
        FuturesContractSpecification, "base_exposure", non_finite_calculation
    )
    with pytest.raises(ExposureValidationError):
        specification.base_exposure(contract=contract, quantity=1, price=10)

    monkeypatch.setattr(
        FuturesContractSpecification, "notional", non_finite_calculation
    )
    with pytest.raises(ExposureValidationError):
        specification.quote_value(
            contract=contract, quantity=1, reference_price=10
        )


def test_pnl_constructor_rejects_invalid_typed_boundaries() -> None:
    symbol = make_symbol()

    with pytest.raises(PnLValidationError):
        FuturesPnLSpecification(
            cast(Market, "invalid"), symbol, PnLUnit.REALIZED_OR_UNREALIZED
        )
    with pytest.raises(PnLValidationError):
        FuturesPnLSpecification(
            Market.CRYPTO,
            cast(CanonicalFuturesSymbol, "invalid"),
            PnLUnit.REALIZED_OR_UNREALIZED,
        )
    with pytest.raises(PnLValidationError):
        FuturesPnLSpecification(
            Market.CRYPTO, symbol, cast(PnLUnit, "invalid")
        )


def test_price_quantity_constructor_rejects_invalid_typed_boundaries() -> None:
    symbol = make_symbol()
    args = (
        PriceUnit.QUOTE_PER_BASE,
        QuantityUnit.CONTRACTS,
        "USD",
        PrecisionPolicy.EXACT,
        RoundingPolicy.NONE,
    )

    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(
            cast(Market, "invalid"), symbol, *args
        )
    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(
            Market.CRYPTO, cast(CanonicalFuturesSymbol, "invalid"), *args
        )

    corrupted_symbol = make_symbol()
    object.__setattr__(
        corrupted_symbol, "contract_family", cast(ContractFamily, object())
    )
    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(
            Market.CRYPTO, corrupted_symbol, *args
        )


def test_liquidation_constructor_rejects_unsupported_family_state() -> None:
    symbol = make_symbol()
    FuturesLiquidationSpecification(Market.CRYPTO, symbol)
    object.__setattr__(symbol, "contract_family", cast(ContractFamily, object()))

    with pytest.raises(LiquidationValidationError):
        FuturesLiquidationSpecification(Market.CRYPTO, symbol)


def test_settlement_accounting_rejects_market_mismatch() -> None:
    instrument = FuturesInstrumentIdentity.create(
        market=Market.CRYPTO,
        symbol=make_symbol(),
        margin_asset="USD",
    )
    settlement = FuturesSettlementSpecification(
        market=Market.CRYPTO,
        symbol=instrument.symbol,
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset="USD",
        source_asset="USD",
    )

    with pytest.raises(AccountingValidationError):
        FuturesSettlementAccountingSpecification(Market.FOREX, instrument, settlement)
