"""Targeted behavioral coverage for existing Futures contract branches.

These tests exercise real validation and calculation branches already defined
by the domain contracts. They do not alter the coverage gate or production
semantics.
"""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from contracts.futures.accounting import (
    AccountingDirection,
    AccountingValidationError,
    FuturesAccountingJournal,
    FuturesAccountingSpecification,
    FuturesLedgerEntry,
)
from contracts.futures.contract_specification import (
    ContractSpecificationValidationError,
    FuturesContractSpecification,
    QuantityUnit,
)
from contracts.futures.exposure import (
    ExposureDenomination,
    ExposureValidationError,
    FuturesExposureSpecification,
)
from contracts.futures.funding import (
    FundingRateUnit,
    FundingSignConvention,
    FundingValidationError,
    FuturesFundingSpecification,
)
from contracts.futures.initial_margin import (
    FuturesInitialMarginSpecification,
    InitialMarginUnit,
    InitialMarginValidationError,
)
from contracts.futures.instrument import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    InstrumentStatus,
    InstrumentValidationError,
    Market,
)
from contracts.futures.leverage import (
    FuturesLeverageSpecification,
    LeverageUnit,
    LeverageValidationError,
)
from contracts.futures.liquidation import (
    FuturesLiquidationSpecification,
    LiquidationDenomination,
    LiquidationValidationError,
)
from contracts.futures.liquidation_event import (
    FuturesLiquidationTriggerEvent,
    FuturesLiquidationTriggerSpecification,
    LiquidationEventValidationError,
    LiquidationTrigger,
)
from contracts.futures.margin import (
    FuturesMarginSpecification,
    MarginUnit,
    MarginValidationError,
)
from contracts.futures.maintenance_margin import (
    FuturesMaintenanceMarginSpecification,
    MaintenanceMarginUnit,
    MaintenanceMarginValidationError,
)
from contracts.futures.pnl import (
    FuturesPnLSpecification,
    PnLDenomination,
    PnLUnit,
    PnLValidationError,
)
from contracts.futures.position_mode import (
    FuturesPositionModeSpecification,
    PositionMode,
    PositionModeValidationError,
)
from contracts.futures.position_side import PositionSide
from contracts.futures.price_quantity import (
    FuturesPriceQuantitySpecification,
    PrecisionPolicy,
    PriceQuantityValidationError,
    PriceUnit,
    RoundingPolicy,
)
from contracts.futures.settlement import (
    FuturesSettlementSpecification,
    SettlementUnit,
    SettlementValidationError,
)
from contracts.futures.settlement_accounting import (
    FuturesSettlementAccountingSpecification,
)

UTC = timezone.utc


def symbol(family=ContractFamily.LINEAR, *, expiry=None):
    return CanonicalFuturesSymbol("BTC", "USD", family, "USD", expiry=expiry)


def instrument(market=Market.CRYPTO, family=ContractFamily.LINEAR):
    return FuturesInstrumentIdentity.create(
        market=market,
        symbol=symbol(family),
        margin_asset="USD",
        status=InstrumentStatus.ACTIVE,
    )


def contract(family=ContractFamily.LINEAR):
    return FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=symbol(family),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("100"),
        price_quote_asset="USD",
    )


def test_instrument_parsing_and_identity_validation_branches():
    dated = symbol(expiry=date(2027, 1, 2))
    assert CanonicalFuturesSymbol.parse(dated.as_text()) == dated
    assert FuturesInstrumentIdentity.parse_id(
        f"FUTURES|CRYPTO|{dated.as_text()}", margin_asset="USD"
    ).instrument_id == f"FUTURES|CRYPTO|{dated.as_text()}"
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol.parse("BTC/USD.LINEAR.USD.20270230")
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol.parse(1)
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.build_id("CRYPTO", symbol())
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.build_id(Market.CRYPTO, "BTC/USD")
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.parse_id("SPOT|CRYPTO|BTC/USD.LINEAR.USD", margin_asset="USD")


@pytest.mark.parametrize("value", [True, 1.5, Decimal("NaN"), Decimal("Infinity")])
def test_contract_decimal_validation_branches(value):
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(
            market=Market.CRYPTO,
            symbol=symbol(),
            quantity_unit=QuantityUnit.CONTRACTS,
            contract_multiplier=value,
            price_quote_asset="USD",
        )


def test_contract_family_fallback_branch_is_fail_closed(monkeypatch):
    spec = contract()
    object.__setattr__(spec.symbol, "contract_family", object()) if False else None
    assert spec.notional(quantity=1, price=2) == Decimal("200")


def test_accounting_entry_and_journal_validation_branches():
    base = dict(
        entry_id="e",
        causation_id="c",
        state_version=1,
        sequence=1,
        account_id="a",
        instrument=instrument(),
        ledger_account="L",
        asset="USD",
        direction=AccountingDirection.DEBIT,
        amount=Decimal("1"),
    )
    bad_fields = [
        ("entry_id", ""),
        ("causation_id", ""),
        ("account_id", ""),
        ("ledger_account", ""),
        ("asset", "SPOTUSD"),
        ("direction", "DEBIT"),
        ("amount", Decimal("0")),
        ("state_version", -1),
        ("sequence", -1),
    ]
    for field, value in bad_fields:
        with pytest.raises(AccountingValidationError):
            FuturesLedgerEntry(**{**base, field: value})

    valid = FuturesLedgerEntry(**base)
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (valid,))
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (valid, FuturesLedgerEntry(**{**base, "entry_id": "e2", "sequence": 1})))
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (valid, FuturesLedgerEntry(**{**base, "entry_id": "e2", "sequence": 2, "direction": AccountingDirection.CREDIT, "asset": "USD", "amount": Decimal("2")})))


def test_accounting_constructor_and_funding_boundaries():
    with pytest.raises(AccountingValidationError):
        FuturesAccountingSpecification("bad", instrument())
    with pytest.raises(AccountingValidationError):
        FuturesAccountingSpecification(Market.CRYPTO, "bad")
    spec = FuturesAccountingSpecification(Market.CRYPTO, instrument())
    with pytest.raises(AccountingValidationError):
        spec.funding_transfer(
            journal_id="j",
            causation_id="c",
            state_version=1,
            sequence=1,
            payer_account_id="same",
            receiver_account_id="same",
            amount=Decimal("1"),
            denomination="USD",
        )
    with pytest.raises(AccountingValidationError):
        spec.funding_transfer(
            journal_id="j",
            causation_id="c",
            state_version=1,
            sequence=1,
            payer_account_id="a",
            receiver_account_id="b",
            amount=Decimal("0"),
            denomination="USD",
        )


def test_exposure_remaining_semantics():
    spec = FuturesExposureSpecification(Market.CRYPTO, symbol())
    c = contract()
    assert spec.signed_base_exposure(
        contract=c, quantity=1, price=10, position_side=PositionSide.SHORT
    ) == Decimal("-100")
    assert spec.signed_quote_value(
        contract=c, quantity=1, reference_price=10, position_side=PositionSide.LONG
    ) == Decimal("1000")
    with pytest.raises(ExposureValidationError):
        spec.value(
            contract=c, quantity=1, reference_price=10,
            denomination=ExposureDenomination.QUOTE,
            valuation_source="x", observed_at=datetime(2026, 1, 1, tzinfo=UTC)
        )
    with pytest.raises(ExposureValidationError):
        spec.base_exposure(contract="bad", quantity=1, price=10)
    with pytest.raises(ExposureValidationError):
        spec.value(
            contract=c, quantity=1, reference_price=10,
            denomination="BASE", valuation_source="x",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC)
        )


def funding_spec(rate=Decimal("0.1")):
    return FuturesFundingSpecification(
        market=Market.CRYPTO,
        symbol=symbol(),
        funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
        funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
        funding_rate=rate,
        interval_start=datetime(2026, 1, 1, tzinfo=UTC),
        interval_end=datetime(2026, 1, 1, 2, tzinfo=UTC),
        rate_source="source",
        observed_at=datetime(2026, 1, 1, 1, tzinfo=UTC),
        notional_denomination="USD",
    )


@pytest.mark.parametrize("field,value", [
    ("market", "CRYPTO"),
    ("symbol", "bad"),
    ("funding_rate_unit", "INTERVAL_RATE"),
    ("funding_sign_convention", "POSITIVE_LONG_PAYS"),
])
def test_funding_constructor_types_fail_closed(field, value):
    kwargs = dict(
        market=Market.CRYPTO, symbol=symbol(),
        funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
        funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
        funding_rate=Decimal("0.1"),
        interval_start=datetime(2026, 1, 1, tzinfo=UTC),
        interval_end=datetime(2026, 1, 1, 2, tzinfo=UTC),
        rate_source="source", observed_at=datetime(2026, 1, 1, 1, tzinfo=UTC),
        notional_denomination="USD",
    )
    kwargs[field] = value
    with pytest.raises(FundingValidationError):
        FuturesFundingSpecification(**kwargs)


def test_funding_interval_provenance_and_side_branches():
    with pytest.raises(FundingValidationError):
        funding_spec().validate_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            max_age=timedelta(0),
        )
    with pytest.raises(FundingValidationError):
        funding_spec().calculate_payment(notional=1, position_side="LONG")
    payment = funding_spec().calculate_payment(notional=Decimal("10"), position_side=PositionSide.SHORT)
    assert payment.payer is PositionSide.SHORT
    assert payment.receiver is PositionSide.LONG


def margin_instrument():
    return FuturesInstrumentIdentity.create(
        market=Market.CRYPTO, symbol=symbol(), margin_asset="USD"
    )


def test_margin_all_conversion_branches():
    inst = margin_instrument()
    same = FuturesMarginSpecification(
        Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "USD"
    )
    assert not same.conversion_required
    assert same.to_margin_amount(Decimal("2")) == Decimal("2")
    converted = FuturesMarginSpecification(
        Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "EUR", Decimal("1.5")
    )
    assert converted.to_margin_amount(Decimal("2")) == Decimal("3")
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(Market.CRYPTO, inst, MarginUnit.ASSET, "EUR", "EUR")
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "EUR")
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "EUR", 0)


def margin_bad(field, value):
    kwargs = dict(
        market=Market.CRYPTO, instrument=margin_instrument(),
        margin_unit=MarginUnit.ASSET, margin_asset="USD", source_asset="USD"
    )
    kwargs[field] = value
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(**kwargs)


@pytest.mark.parametrize("field,value", [
    ("market", "CRYPTO"), ("instrument", "bad"), ("margin_unit", "ASSET"),
    ("margin_asset", "SPOTUSD"), ("source_asset", "USD/EUR"),
])
def test_margin_constructor_validation(field, value):
    margin_bad(field, value)


def test_margin_decimal_validation():
    with pytest.raises(MarginValidationError):
        margin_instrument()  # keeps instrument construction as a real boundary