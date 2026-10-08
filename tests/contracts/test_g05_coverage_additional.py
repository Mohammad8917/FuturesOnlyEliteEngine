"""Additional targeted tests for uncovered real Futures contract branches.

These tests only exercise existing production semantics; no coverage
configuration or production behavior is changed.
"""
from datetime import datetime, timedelta, timezone
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
    FundingPayment,
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
    FuturesLiquidationTriggerEvaluation,
    FuturesLiquidationTriggerSpecification,
    LiquidationEventValidationError,
    LiquidationTrigger,
)
from contracts.futures.maintenance_margin import (
    FuturesMaintenanceMarginSpecification,
    MaintenanceMarginUnit,
    MaintenanceMarginValidationError,
)
from contracts.futures.margin import (
    FuturesMarginSpecification,
    MarginUnit,
    MarginValidationError,
)
from contracts.futures.pnl import (
    FuturesPnLSpecification,
    PnLUnit,
    PnLValidationError,
)
from contracts.futures.position_mode import PositionMode
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


def symbol(family=ContractFamily.LINEAR):
    return CanonicalFuturesSymbol("BTC", "USD", family, "USD")


def instrument(family=ContractFamily.LINEAR):
    return FuturesInstrumentIdentity.create(
        market=Market.CRYPTO,
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


def test_accounting_success_and_entry_type_branches():
    base = dict(
        entry_id="e1", causation_id="c", state_version=1, sequence=1,
        account_id="a", instrument=instrument(), ledger_account="L",
        asset="USD", direction=AccountingDirection.DEBIT, amount=Decimal("2"),
    )
    with pytest.raises(AccountingValidationError):
        FuturesLedgerEntry(**{**base, "instrument": "bad"})
    with pytest.raises(AccountingValidationError):
        FuturesLedgerEntry(**{**base, "amount": True})
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (base,))
    spec = FuturesAccountingSpecification(Market.CRYPTO, instrument())
    profit = spec.realized_pnl(
        journal_id="jp", causation_id="c", state_version=1, sequence=1,
        account_id="a", pnl_amount=Decimal("2"), denomination="USD",
    )
    loss = spec.realized_pnl(
        journal_id="jl", causation_id="c", state_version=1, sequence=1,
        account_id="a", pnl_amount=Decimal("-2"), denomination="USD",
    )
    assert profit.asset_balances == {"USD": Decimal("0")}
    assert loss.asset_balances == {"USD": Decimal("0")}


def test_contract_validation_and_inverse_calculation_branches():
    base = dict(
        market=Market.CRYPTO, symbol=symbol(),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"), price_quote_asset="USD",
    )
    for field, value in [
        ("market", "CRYPTO"), ("symbol", "bad"),
        ("quantity_unit", "CONTRACTS"),
    ]:
        with pytest.raises(ContractSpecificationValidationError):
            FuturesContractSpecification(**{**base, field: value})
    inverse = FuturesContractSpecification(
        market=Market.CRYPTO, symbol=symbol(ContractFamily.INVERSE),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"), price_quote_asset="USD",
    )
    assert inverse.notional(quantity=3, price=10) == Decimal("6")
    assert inverse.base_exposure(quantity=3, price=10) == Decimal("0.6")
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(**{**base, "contract_multiplier": Decimal("0")})
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(**{**base, "price_quote_asset": "EUR"})


def test_instrument_asset_and_identity_validation_branches():
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol(1, "USD", ContractFamily.LINEAR, "USD")
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol("SPOT", "USD", ContractFamily.LINEAR, "USD")
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol("BTC", "BTC", ContractFamily.LINEAR, "USD")
    with pytest.raises(InstrumentValidationError):
        CanonicalFuturesSymbol("BTC", "USD", ContractFamily.LINEAR, "USD", expiry="20270101")
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity(
            "CRYPTO", symbol(), "USD", InstrumentStatus.ACTIVE
        )
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity(Market.CRYPTO, "bad", "USD")
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity(Market.CRYPTO, symbol(), "USD", "ACTIVE")


def test_exposure_validation_and_freshness_branches():
    spec = FuturesExposureSpecification(Market.CRYPTO, symbol())
    c = contract()
    with pytest.raises(ExposureValidationError):
        spec.base_exposure(contract=c, quantity=True, price=10)
    with pytest.raises(ExposureValidationError):
        spec.base_exposure(contract=c, quantity=1, price=0)
    with pytest.raises(ExposureValidationError):
        spec.base_exposure(contract=contract(ContractFamily.INVERSE), quantity=1, price=10)
    with pytest.raises(ExposureValidationError):
        spec.signed_base_exposure(
            contract=c, quantity=1, price=10, position_side="LONG"
        )
    with pytest.raises(ExposureValidationError):
        spec.signed_quote_value(
            contract=c, quantity=1, reference_price=10, position_side="LONG"
        )
    with pytest.raises(ExposureValidationError):
        spec.value(
            contract=c, quantity=1, reference_price=10,
            denomination="BASE", valuation_source="x",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    with pytest.raises(ExposureValidationError):
        spec.value(
            contract=c, quantity=1, reference_price=10,
            denomination=ExposureDenomination.BASE, valuation_source="",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    with pytest.raises(ExposureValidationError):
        spec.validate_reference_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            max_age=timedelta(hours=2),
        )


def test_funding_validation_and_zero_rate_branches():
    for value in [True, object(), Decimal("NaN")]:
        with pytest.raises(FundingValidationError):
            funding_spec(value)
    with pytest.raises(FundingValidationError):
        funding_spec().validate_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            max_age=timedelta(hours=-1),
        )
    with pytest.raises(FundingValidationError):
        FundingPayment(PositionSide.LONG, PositionSide.LONG, Decimal("1"), "USD")
    with pytest.raises(FundingValidationError):
        FundingPayment("LONG", PositionSide.SHORT, Decimal("1"), "USD")
    with pytest.raises(FundingValidationError):
        FundingPayment(PositionSide.LONG, PositionSide.SHORT, Decimal("0"), "USD")
    assert funding_spec(Decimal("0")).calculate_payment(
        notional=Decimal("10"), position_side=PositionSide.LONG
    ) is None
    negative = funding_spec(Decimal("-0.1")).calculate_payment(
        notional=Decimal("10"), position_side=PositionSide.LONG
    )
    assert negative is not None
    assert negative.payer is PositionSide.SHORT
    with pytest.raises(FundingValidationError):
        funding_spec().calculate_payment(notional=True, position_side=PositionSide.LONG)


def test_margin_initial_maintenance_and_leverage_error_branches():
    inst = instrument()
    for value in [True, object()]:
        with pytest.raises(InitialMarginValidationError):
            FuturesInitialMarginSpecification(
                Market.CRYPTO, inst, InitialMarginUnit.RATIO, value, "USD"
            )
        with pytest.raises(MaintenanceMarginValidationError):
            FuturesMaintenanceMarginSpecification(
                Market.CRYPTO, inst, MaintenanceMarginUnit.RATIO, value, "USD"
            )
        with pytest.raises(LeverageValidationError):
            FuturesLeverageSpecification(
                Market.CRYPTO, inst, LeverageUnit.RATIO,
                value, Decimal("1"), Decimal("5")
            )


def test_margin_extra_validation_branches():
    inst = instrument()
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "USD", Decimal("1")
        )
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "EUR", Decimal("NaN")
        )
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "EUR", True
        )
    same = FuturesMarginSpecification(
        Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "USD"
    )
    with pytest.raises(MarginValidationError):
        same.to_margin_amount(0)


def liquidation_args(family=ContractFamily.LINEAR, side=PositionSide.LONG):
    return dict(
        contract=contract(family), quantity=Decimal("1"),
        entry_price=Decimal("100"), margin_amount=Decimal("500"),
        margin_denomination=(
            LiquidationDenomination.QUOTE
            if family is ContractFamily.LINEAR
            else LiquidationDenomination.BASE
        ),
        maintenance_margin_ratio=Decimal("0.1"), position_side=side,
    )


def test_liquidation_extra_validation_branches():
    linear = FuturesLiquidationSpecification(Market.CRYPTO, symbol())
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "quantity": True})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "contract": "bad"})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "maintenance_margin_ratio": Decimal("0")})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "position_side": "LONG"})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "margin_denomination": LiquidationDenomination.BASE})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "margin_amount": Decimal("10000")})
    short = linear.liquidation_price(**liquidation_args(side=PositionSide.SHORT))
    assert short > Decimal("100")


def test_liquidation_event_more_validation_branches():
    spec = FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol())
    kwargs = dict(
        account_id="a", position_id="p", event_id="e", causation_id="c",
        state_version=1, contract_family=ContractFamily.LINEAR,
        position_mode=PositionMode.ONE_WAY, position_side=PositionSide.LONG,
        quantity=Decimal("1"), entry_price=Decimal("100"), margin_amount=Decimal("20"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.1"), liquidation_price=Decimal("80"),
        reference_price=Decimal("75"), reference_price_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
        max_age=timedelta(hours=2), previous_event_sequence=1, event_sequence=2,
    )
    for field, value in [
        ("quantity", True), ("entry_price", 0), ("margin_amount", Decimal("0")),
        ("maintenance_margin_ratio", Decimal("1")),
        ("liquidation_price", Decimal("100")),
        ("reference_price_source", ""),
        ("max_age", timedelta(0)),
    ]:
        with pytest.raises(LiquidationEventValidationError):
            spec.evaluate(**{**kwargs, field: value})
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**{**kwargs, "contract_family": ContractFamily.INVERSE})
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**{**kwargs, "margin_denomination": LiquidationDenomination.BASE})
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**{**kwargs, "reference_price": Decimal("90"), "event_sequence": 1})
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**{**kwargs, "as_of": datetime(2026, 1, 1, tzinfo=UTC)})
    result = spec.evaluate(**kwargs)
    assert result.trigger is LiquidationTrigger.TRIGGERED
    assert result.event is not None


def test_liquidation_event_dataclass_validation_and_evaluation():
    result = FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
        account_id="a", position_id="p", event_id="e", causation_id="c",
        state_version=1, contract_family=ContractFamily.LINEAR,
        position_mode=PositionMode.ONE_WAY, position_side=PositionSide.LONG,
        quantity=Decimal("1"), entry_price=Decimal("100"), margin_amount=Decimal("20"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.1"), liquidation_price=Decimal("80"),
        reference_price=Decimal("75"), reference_price_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
        max_age=timedelta(hours=2), previous_event_sequence=1, event_sequence=2,
    )
    event = result.event
    assert event is not None
    data = {name: getattr(event, name) for name in event.__dataclass_fields__}
    for field, value in [
        ("market", "CRYPTO"), ("symbol", "bad"),
        ("position_mode", "ONE_WAY"), ("position_side", "LONG"),
        ("quantity", Decimal("0")), ("margin_denomination", "QUOTE"),
        ("maintenance_margin_ratio", Decimal("1")),
        ("reference_price", Decimal("0")),
        ("reference_price_source", ""),
        ("max_age", timedelta(0)),
    ]:
        with pytest.raises((LiquidationEventValidationError, ValueError)):
            FuturesLiquidationTriggerEvent(**{**data, field: value})
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerEvaluation("bad", None)
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerEvaluation(LiquidationTrigger.TRIGGERED, None)
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerEvaluation(LiquidationTrigger.NOT_TRIGGERED, event)


def test_pnl_inverse_and_freshness_branches():
    inverse = FuturesPnLSpecification(
        Market.CRYPTO, symbol(ContractFamily.INVERSE), PnLUnit.REALIZED_OR_UNREALIZED
    )
    assert inverse.calculate_realized(
        quantity=2, multiplier=3, entry_price=100, exit_price=120,
        position_side=PositionSide.LONG,
    ) > Decimal("0")
    with pytest.raises(PnLValidationError):
        inverse.calculate_realized(
            quantity=1, multiplier=1, entry_price=100, exit_price=0,
            position_side=PositionSide.LONG,
        )
    with pytest.raises(PnLValidationError):
        inverse.validate_valuation_freshness(
            as_of=datetime(2026, 1, 1, tzinfo=UTC),
            observed_at=datetime(2025, 12, 1, tzinfo=UTC),
            max_age=timedelta(hours=1),
        )


def test_price_quantity_and_settlement_branches():
    with pytest.raises(PriceQuantityValidationError):
        FuturesPriceQuantitySpecification(
            Market.CRYPTO, symbol(), PriceUnit.QUOTE_PER_BASE, QuantityUnit.CONTRACTS,
            "USD", PrecisionPolicy.EXACT, "NONE"
        )
    pq = FuturesPriceQuantitySpecification(
        Market.CRYPTO, symbol(), PriceUnit.QUOTE_PER_BASE, QuantityUnit.CONTRACTS,
        "USD", PrecisionPolicy.EXACT, RoundingPolicy.NONE
    )
    with pytest.raises(PriceQuantityValidationError):
        pq.validate_quantity(object())
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "USD/EUR", "USD"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "USD", "EUR"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "USD", "EUR", Decimal("0")
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "USD", "EUR", True
        )


def test_settlement_accounting_same_and_cross_asset_success():
    inst = instrument()
    same = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "USD"
    )
    same_accounting = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, same
    )
    same_journal = same_accounting.transfer(
        journal_id="js", causation_id="c", state_version=1, sequence=1,
        account_id="a", settlement_counterparty_account_id="b",
        source_amount=Decimal("2"), source_asset="USD",
    )
    assert same_journal.asset_balances == {"USD": Decimal("0")}

    cross = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "EUR", Decimal("2")
    )
    cross_accounting = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, cross
    )
    cross_journal = cross_accounting.transfer(
        journal_id="jc", causation_id="c", state_version=1, sequence=1,
        account_id="a", settlement_counterparty_account_id="b",
        source_amount=Decimal("2"), source_asset="EUR",
    )
    assert cross_journal.asset_balances == {
        "EUR": Decimal("0"), "USD": Decimal("0")
    }
