"""Additional targeted tests for uncovered real Futures contract branches.

These tests only exercise existing production semantics; no coverage
configuration or production behavior is changed.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from domain.futures.accounting import (
    AccountingDirection,
    AccountingValidationError,
    FuturesAccountingJournal,
    FuturesAccountingSpecification,
    FuturesLedgerEntry,
)
from domain.futures.contract_specification import (
    ContractSpecificationValidationError,
    FuturesContractSpecification,
    QuantityUnit,
)
from domain.futures.exposure import (
    ExposureDenomination,
    ExposureValidationError,
    FuturesExposureSpecification,
)
from domain.futures.funding import (
    FundingRateUnit,
    FundingSignConvention,
    FundingValidationError,
    FundingPayment,
    FuturesFundingSpecification,
)
from domain.futures.initial_margin import (
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
from domain.futures.leverage import (
    FuturesLeverageSpecification,
    LeverageUnit,
    LeverageValidationError,
)
from domain.futures.liquidation import (
    FuturesLiquidationSpecification,
    LiquidationDenomination,
    LiquidationValidationError,
)
from domain.futures.liquidation_event import (
    FuturesLiquidationTriggerEvent,
    FuturesLiquidationTriggerEvaluation,
    FuturesLiquidationTriggerSpecification,
    LiquidationEventValidationError,
    LiquidationTrigger,
)
from domain.futures.maintenance_margin import (
    FuturesMaintenanceMarginSpecification,
    MaintenanceMarginUnit,
    MaintenanceMarginValidationError,
)
from domain.futures.margin import (
    FuturesMarginSpecification,
    MarginUnit,
    MarginValidationError,
)
from domain.futures.pnl import (
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
from domain.futures.settlement import (
    FuturesSettlementSpecification,
    SettlementUnit,
    SettlementValidationError,
)
from domain.futures.settlement_accounting import (
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
        entry_id="e1",
        causation_id="c",
        state_version=1,
        sequence=1,
        account_id="a",
        instrument=instrument(),
        ledger_account="L",
        asset="USD",
        direction=AccountingDirection.DEBIT,
        amount=Decimal("2"),
    )
    with pytest.raises(AccountingValidationError):
        FuturesLedgerEntry(**{**base, "instrument": "bad"})
    with pytest.raises(AccountingValidationError):
        FuturesLedgerEntry(**{**base, "amount": True})
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (base,))
    spec = FuturesAccountingSpecification(Market.CRYPTO, instrument())
    profit = spec.realized_pnl(
        journal_id="jp",
        causation_id="c",
        state_version=1,
        sequence=1,
        account_id="a",
        pnl_amount=Decimal("2"),
        denomination="USD",
    )
    loss = spec.realized_pnl(
        journal_id="jl",
        causation_id="c",
        state_version=1,
        sequence=1,
        account_id="a",
        pnl_amount=Decimal("-2"),
        denomination="USD",
    )
    assert profit.asset_balances == {"USD": Decimal("0")}
    assert loss.asset_balances == {"USD": Decimal("0")}


@pytest.mark.parametrize(
    ("family", "valid_denomination", "invalid_denomination"),
    [
        (ContractFamily.LINEAR, "USD", "BTC"),
        (ContractFamily.INVERSE, "BTC", "USD"),
    ],
)
def test_realized_pnl_accounting_denomination_matches_contract_family(
    family, valid_denomination, invalid_denomination
):
    spec = FuturesAccountingSpecification(Market.CRYPTO, instrument(family))
    journal = spec.realized_pnl(
        journal_id="pnl-valid",
        causation_id="cause",
        state_version=1,
        sequence=1,
        account_id="account",
        pnl_amount=Decimal("1"),
        denomination=valid_denomination,
    )
    assert {entry.asset for entry in journal.entries} == {valid_denomination}

    with pytest.raises(
        AccountingValidationError,
        match="realized PnL denomination must match the contract-family PnL asset",
    ):
        spec.realized_pnl(
            journal_id="pnl-invalid",
            causation_id="cause",
            state_version=1,
            sequence=1,
            account_id="account",
            pnl_amount=Decimal("1"),
            denomination=invalid_denomination,
        )


def test_contract_validation_and_inverse_calculation_branches():
    base = dict(
        market=Market.CRYPTO,
        symbol=symbol(),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"),
        price_quote_asset="USD",
    )
    for field, value in [
        ("market", "CRYPTO"),
        ("symbol", "bad"),
        ("quantity_unit", "CONTRACTS"),
    ]:
        with pytest.raises(ContractSpecificationValidationError):
            FuturesContractSpecification(**{**base, field: value})
    inverse = FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=symbol(ContractFamily.INVERSE),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"),
        price_quote_asset="USD",
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
        CanonicalFuturesSymbol(
            "BTC", "USD", ContractFamily.LINEAR, "USD", expiry="20270101"
        )
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity("CRYPTO", symbol(), "USD", InstrumentStatus.ACTIVE)
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
        spec.base_exposure(
            contract=contract(ContractFamily.INVERSE), quantity=1, price=10
        )
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
            contract=c,
            quantity=1,
            reference_price=10,
            denomination="BASE",
            valuation_source="x",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    with pytest.raises(ExposureValidationError):
        spec.value(
            contract=c,
            quantity=1,
            reference_price=10,
            denomination=ExposureDenomination.BASE,
            valuation_source="",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    assert (
        spec.validate_reference_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            max_age=timedelta(hours=2),
        )
        is None
    )
    with pytest.raises(ExposureValidationError):
        spec.validate_reference_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            observed_at=datetime(2025, 12, 31, 22, tzinfo=UTC),
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
    assert (
        funding_spec(Decimal("0")).calculate_payment(
            notional=Decimal("10"), position_side=PositionSide.LONG
        )
        is None
    )
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
                Market.CRYPTO,
                inst,
                LeverageUnit.RATIO,
                value,
                Decimal("1"),
                Decimal("5"),
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
        contract=contract(family),
        quantity=Decimal("1"),
        entry_price=Decimal("100"),
        margin_amount=Decimal("2000"),
        margin_denomination=(
            LiquidationDenomination.QUOTE
            if family is ContractFamily.LINEAR
            else LiquidationDenomination.BASE
        ),
        maintenance_margin_ratio=Decimal("0.1"),
        position_side=side,
    )


def event_args():
    return dict(
        account_id="a",
        position_id="p",
        event_id="e",
        causation_id="c",
        state_version=1,
        contract_family=ContractFamily.LINEAR,
        position_mode=PositionMode.ONE_WAY,
        position_side=PositionSide.LONG,
        quantity=Decimal("1"),
        entry_price=Decimal("100"),
        margin_amount=Decimal("20"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.1"),
        liquidation_price=Decimal("80"),
        reference_price=Decimal("75"),
        reference_price_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
        max_age=timedelta(hours=2),
        previous_event_sequence=1,
        event_sequence=1,
    )


def test_liquidation_extra_validation_branches():
    linear = FuturesLiquidationSpecification(Market.CRYPTO, symbol())
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "quantity": True})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "contract": "bad"})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(
            **{**liquidation_args(), "maintenance_margin_ratio": Decimal("0")}
        )
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**{**liquidation_args(), "position_side": "LONG"})
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(
            **{
                **liquidation_args(),
                "margin_denomination": LiquidationDenomination.BASE,
            }
        )
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(
            **{**liquidation_args(), "margin_amount": Decimal("10000")}
        )
    short = linear.liquidation_price(**liquidation_args(side=PositionSide.SHORT))
    assert short > Decimal("100")


def test_liquidation_event_more_validation_branches():
    spec = FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol())
    kwargs = dict(
        account_id="a",
        position_id="p",
        event_id="e",
        causation_id="c",
        state_version=1,
        contract_family=ContractFamily.LINEAR,
        position_mode=PositionMode.ONE_WAY,
        position_side=PositionSide.LONG,
        quantity=Decimal("1"),
        entry_price=Decimal("100"),
        margin_amount=Decimal("20"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.1"),
        liquidation_price=Decimal("80"),
        reference_price=Decimal("75"),
        reference_price_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
        max_age=timedelta(hours=2),
        previous_event_sequence=1,
        event_sequence=2,
    )
    for field, value in [
        ("quantity", True),
        ("entry_price", 0),
        ("margin_amount", Decimal("0")),
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
        spec.evaluate(
            **{**kwargs, "reference_price": Decimal("70"), "event_sequence": 1}
        )
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**{**kwargs, "as_of": datetime(2025, 12, 31, tzinfo=UTC)})
    result = spec.evaluate(**kwargs)
    assert result.trigger is LiquidationTrigger.TRIGGERED
    assert result.event is not None


def test_liquidation_event_dataclass_validation_and_evaluation():
    result = FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
        account_id="a",
        position_id="p",
        event_id="e",
        causation_id="c",
        state_version=1,
        contract_family=ContractFamily.LINEAR,
        position_mode=PositionMode.ONE_WAY,
        position_side=PositionSide.LONG,
        quantity=Decimal("1"),
        entry_price=Decimal("100"),
        margin_amount=Decimal("20"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.1"),
        liquidation_price=Decimal("80"),
        reference_price=Decimal("75"),
        reference_price_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
        max_age=timedelta(hours=2),
        previous_event_sequence=1,
        event_sequence=2,
    )
    event = result.event
    assert event is not None
    data = {name: getattr(event, name) for name in event.__dataclass_fields__}
    for field, value in [
        ("market", "CRYPTO"),
        ("symbol", "bad"),
        ("position_mode", "ONE_WAY"),
        ("position_side", "LONG"),
        ("quantity", Decimal("0")),
        ("margin_denomination", "QUOTE"),
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
        quantity=2,
        multiplier=3,
        entry_price=100,
        exit_price=120,
        position_side=PositionSide.LONG,
    ) > Decimal("0")
    with pytest.raises(PnLValidationError):
        inverse.calculate_realized(
            quantity=1,
            multiplier=1,
            entry_price=100,
            exit_price=0,
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
            Market.CRYPTO,
            symbol(),
            PriceUnit.QUOTE_PER_BASE,
            QuantityUnit.CONTRACTS,
            "USD",
            PrecisionPolicy.EXACT,
            "NONE",
        )
    pq = FuturesPriceQuantitySpecification(
        Market.CRYPTO,
        symbol(),
        PriceUnit.QUOTE_PER_BASE,
        QuantityUnit.CONTRACTS,
        "USD",
        PrecisionPolicy.EXACT,
        RoundingPolicy.NONE,
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
        journal_id="js",
        causation_id="c",
        state_version=1,
        sequence=1,
        account_id="a",
        settlement_counterparty_account_id="b",
        source_amount=Decimal("2"),
        source_asset="USD",
    )
    assert same_journal.asset_balances == {"USD": Decimal("0")}

    cross = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "EUR", Decimal("2")
    )
    cross_accounting = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, cross
    )
    cross_journal = cross_accounting.transfer(
        journal_id="jc",
        causation_id="c",
        state_version=1,
        sequence=1,
        account_id="a",
        settlement_counterparty_account_id="b",
        source_amount=Decimal("2"),
        source_asset="EUR",
    )
    assert cross_journal.asset_balances == {"EUR": Decimal("0"), "USD": Decimal("0")}


def test_g05_targeted_validation_and_calculation_branches():
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(
            market=Market.CRYPTO,
            symbol=symbol(),
            quantity_unit=QuantityUnit.CONTRACTS,
            contract_multiplier="not-a-decimal",
            price_quote_asset="USD",
        )

    exposure = FuturesExposureSpecification(Market.CRYPTO, symbol())
    with pytest.raises(ExposureValidationError):
        exposure.base_exposure(contract=contract(), quantity="not-a-decimal", price=10)
    with pytest.raises(ExposureValidationError):
        exposure.quote_value(contract=contract(), quantity=1, reference_price=0)
    assert exposure.quote_value(
        contract=contract(), quantity=2, reference_price=10
    ) == Decimal("2000")
    assert exposure.value(
        contract=contract(),
        quantity=2,
        reference_price=10,
        denomination=ExposureDenomination.QUOTE,
        valuation_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
    ) == Decimal("2000")
    with pytest.raises(ExposureValidationError):
        FuturesExposureSpecification("bad", symbol())
    with pytest.raises(ExposureValidationError):
        FuturesExposureSpecification(Market.CRYPTO, "bad")
    with pytest.raises(ExposureValidationError):
        exposure.validate_reference_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            max_age=timedelta(0),
        )

    with pytest.raises(FundingValidationError):
        funding_spec("not-a-rate")
    with pytest.raises(FundingValidationError):
        FundingPayment(PositionSide.LONG, PositionSide.SHORT, Decimal("1"), "")
    with pytest.raises(FundingValidationError):
        FuturesFundingSpecification(
            market=Market.CRYPTO,
            symbol=symbol(),
            funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
            funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
            funding_rate=Decimal("0.1"),
            interval_start=datetime(2026, 1, 1, tzinfo=UTC),
            interval_end=datetime(2026, 1, 1, tzinfo=UTC),
            rate_source="source",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            notional_denomination="USD",
        )

    inverse = FuturesLiquidationSpecification(
        Market.CRYPTO, symbol(ContractFamily.INVERSE)
    )
    inverse_long = inverse.liquidation_price(
        **{
            **liquidation_args(ContractFamily.INVERSE, PositionSide.LONG),
            "margin_amount": Decimal("0.2"),
        }
    )
    assert inverse_long < Decimal("100")
    with pytest.raises(LiquidationValidationError):
        inverse.liquidation_price(
            **{
                **liquidation_args(ContractFamily.INVERSE, PositionSide.SHORT),
                "margin_amount": Decimal("0.001"),
            }
        )
    with pytest.raises(LiquidationValidationError):
        FuturesLiquidationSpecification("bad", symbol())
    with pytest.raises(LiquidationValidationError):
        FuturesLiquidationSpecification(Market.CRYPTO, "bad")
    with pytest.raises(LiquidationValidationError):
        inverse.liquidation_price(
            **{
                **liquidation_args(ContractFamily.INVERSE, PositionSide.SHORT),
                "margin_denomination": LiquidationDenomination.QUOTE,
            }
        )

    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification("bad", symbol())
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification(
            Market.CRYPTO, symbol(ContractFamily.INVERSE)
        ).evaluate(
            account_id="a",
            position_id="p",
            event_id="e",
            causation_id="c",
            state_version=1,
            contract_family=ContractFamily.INVERSE,
            position_mode=PositionMode.ONE_WAY,
            position_side=PositionSide.SHORT,
            quantity=1,
            entry_price=100,
            margin_amount=1,
            margin_denomination=LiquidationDenomination.BASE,
            maintenance_margin_ratio=Decimal("0.1"),
            liquidation_price=Decimal("120"),
            reference_price=Decimal("130"),
            reference_price_source="mark",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            max_age=timedelta(hours=2),
            previous_event_sequence=1,
            event_sequence=1,
        )


def test_g05_remaining_validation_and_boundary_branches():
    """Exercise remaining real validation/boundary semantics without changing production behavior."""
    inst = instrument()
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(
            Market.CRYPTO, inst, InitialMarginUnit.RATIO, "bad", "USD"
        )
    with pytest.raises(MaintenanceMarginValidationError):
        FuturesMaintenanceMarginSpecification(
            Market.CRYPTO, inst, MaintenanceMarginUnit.RATIO, "bad", "USD"
        )
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(
            Market.CRYPTO, inst, LeverageUnit.RATIO, "bad", Decimal("1"), Decimal("5")
        )
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(
            Market.CRYPTO, inst, MarginUnit.ASSET, "USD", "EUR", "bad"
        )
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(Market.CRYPTO, inst, MarginUnit.ASSET, 1, "USD")

    pnl = FuturesPnLSpecification(
        Market.CRYPTO, symbol(), PnLUnit.REALIZED_OR_UNREALIZED
    )
    with pytest.raises(PnLValidationError):
        pnl.calculate_realized(
            quantity="bad",
            multiplier=1,
            entry_price=100,
            exit_price=110,
            position_side=PositionSide.LONG,
        )
    with pytest.raises(PnLValidationError):
        pnl.validate_valuation_freshness(
            as_of=datetime(2026, 1, 1, tzinfo=UTC),
            observed_at=datetime(2026, 1, 1),
            max_age=timedelta(hours=1),
        )

    pq = FuturesPriceQuantitySpecification(
        Market.CRYPTO,
        symbol(),
        PriceUnit.QUOTE_PER_BASE,
        QuantityUnit.CONTRACTS,
        "USD",
        PrecisionPolicy.EXACT,
        RoundingPolicy.NONE,
    )
    with pytest.raises(PriceQuantityValidationError):
        pq.validate_price("bad")

    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "bad", "USD"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "USD", "EUR", "bad"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, symbol(), SettlementUnit.ASSET, "USD", "EUR", Decimal("NaN")
        )

    with pytest.raises(AccountingValidationError):
        FuturesAccountingSpecification(Market.FOREX, instrument())

    linear = FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=symbol(),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"),
        price_quote_asset="USD",
    )
    assert linear.base_exposure(quantity=3, price=10) == Decimal("6")

    settlement = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "EUR", Decimal("2")
    )
    accounting = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, settlement
    )
    with pytest.raises(AccountingValidationError):
        accounting.transfer(
            journal_id="j",
            causation_id="c",
            state_version=1,
            sequence=1,
            account_id="a",
            settlement_counterparty_account_id="a",
            source_amount=Decimal("1"),
            source_asset="EUR",
        )
    with pytest.raises(AccountingValidationError):
        accounting.transfer(
            journal_id="j",
            causation_id="c",
            state_version=1,
            sequence=1,
            account_id="a",
            settlement_counterparty_account_id="b",
            source_amount=Decimal("1"),
            source_asset="USD",
        )

    liquidation = FuturesLiquidationSpecification(Market.CRYPTO, symbol())
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(**{**liquidation_args(), "entry_price": "bad"})
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(
            **{**liquidation_args(), "maintenance_margin_ratio": "bad"}
        )
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(
            **{**liquidation_args(), "margin_denomination": "QUOTE"}
        )
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(
            **{**liquidation_args(), "margin_amount": Decimal("-1")}
        )

    with pytest.raises(FundingValidationError):
        funding_spec().validate_freshness(
            as_of=datetime(2026, 1, 1, tzinfo=UTC), max_age=timedelta(0)
        )
    with pytest.raises(FundingValidationError):
        FuturesFundingSpecification(
            market=Market.CRYPTO,
            symbol=symbol(),
            funding_rate_unit=FundingRateUnit.INTERVAL_RATE,
            funding_sign_convention=FundingSignConvention.POSITIVE_LONG_PAYS,
            funding_rate=Decimal("0.1"),
            interval_start=datetime(2026, 1, 1, tzinfo=UTC),
            interval_end=datetime(2026, 1, 1, 2, tzinfo=UTC),
            rate_source="",
            observed_at=datetime(2026, 1, 1, 1, tzinfo=UTC),
            notional_denomination="USD",
        )


def test_g05_close_remaining_contract_validation_paths():
    inst = instrument()
    contract = FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=symbol(),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"),
        price_quote_asset="USD",
    )
    inverse_contract = FuturesContractSpecification(
        market=Market.CRYPTO,
        symbol=symbol(ContractFamily.INVERSE),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("2"),
        price_quote_asset="USD",
    )
    assert contract.notional(quantity=2, price=10) == Decimal("40")
    assert inverse_contract.notional(quantity=2, price=10) == Decimal("4")
    assert inverse_contract.base_exposure(quantity=2, price=10) == Decimal("0.4")

    exposure = FuturesExposureSpecification(Market.CRYPTO, symbol())
    with pytest.raises(ExposureValidationError):
        FuturesExposureSpecification("bad", symbol())
    with pytest.raises(ExposureValidationError):
        exposure.base_exposure(contract=object(), quantity=1, price=10)
    with pytest.raises(ExposureValidationError):
        exposure.quote_value(contract=object(), quantity=1, reference_price=10)
    with pytest.raises(ExposureValidationError):
        exposure.value(
            contract=contract,
            quantity=1,
            reference_price=10,
            denomination=ExposureDenomination.QUOTE,
            valuation_source="",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    liquidation = FuturesLiquidationSpecification(Market.CRYPTO, symbol())
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(**{**liquidation_args(), "contract": object()})
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(**{**liquidation_args(), "position_side": "LONG"})
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(
            **{
                **liquidation_args(),
                "margin_denomination": LiquidationDenomination.BASE,
            }
        )

    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
            **{**event_args(), "margin_denomination": LiquidationDenomination.BASE}
        )
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
            **{**event_args(), "maintenance_margin_ratio": Decimal("1")}
        )
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
            **{**event_args(), "reference_price_source": ""}
        )
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
            **{**event_args(), "max_age": timedelta(0)}
        )
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol()).evaluate(
            **{**event_args(), "as_of": datetime(2025, 1, 1, tzinfo=UTC)}
        )

    settlement = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "USD"
    )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "SPOTUSD", "USD"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "USD", Decimal("1")
        )
    assert settlement.settle_amount(Decimal("2")) == Decimal("2")

    settlement_accounting = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, settlement
    )
    with pytest.raises(AccountingValidationError):
        settlement_accounting.transfer(
            journal_id="",
            causation_id="c",
            state_version=0,
            sequence=0,
            account_id="a",
            settlement_counterparty_account_id="b",
            source_amount=Decimal("1"),
            source_asset="USD",
        )
    with pytest.raises(AccountingValidationError):
        settlement_accounting.transfer(
            journal_id="j",
            causation_id="c",
            state_version=-1,
            sequence=0,
            account_id="a",
            settlement_counterparty_account_id="b",
            source_amount=Decimal("1"),
            source_asset="USD",
        )
    with pytest.raises(AccountingValidationError):
        settlement_accounting.transfer(
            journal_id="j",
            causation_id="c",
            state_version=0,
            sequence=0,
            account_id="a",
            settlement_counterparty_account_id="b",
            source_amount=Decimal("1"),
            source_asset="EUR",
        )

    with pytest.raises(FundingValidationError):
        funding_spec().calculate_payment(notional=Decimal("10"), position_side="LONG")

    # Cover remaining valid boundary semantics without changing production behavior.
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.create(
            market=Market.CRYPTO,
            symbol=symbol(),
            margin_asset="BAD-ASSET",
            status=InstrumentStatus.ACTIVE,
        )

    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(
            **{**liquidation_args(), "margin_amount": Decimal("100")}
        )
    with pytest.raises(LiquidationValidationError):
        liquidation.liquidation_price(
            **{
                **liquidation_args(ContractFamily.INVERSE, PositionSide.SHORT),
                "margin_amount": Decimal("1"),
            }
        )

    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, 123, "USD"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            "bad", inst.symbol, SettlementUnit.ASSET, "USD", "USD"
        )
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(
            Market.CRYPTO, "bad", SettlementUnit.ASSET, "USD", "USD"
        )

    with pytest.raises(AccountingValidationError):
        settlement_accounting.transfer(
            journal_id="j",
            causation_id="c",
            state_version=0,
            sequence=0,
            account_id="a",
            settlement_counterparty_account_id="a",
            source_amount=Decimal("1"),
            source_asset="USD",
        )
    with pytest.raises(AccountingValidationError):
        settlement_accounting.transfer(
            journal_id="j",
            causation_id="c",
            state_version=0,
            sequence=0,
            account_id="a",
            settlement_counterparty_account_id="b",
            source_amount=Decimal("0"),
            source_asset="USD",
        )
    mismatched_market_settlement = FuturesSettlementSpecification(
        Market.GOLD, inst.symbol, SettlementUnit.ASSET, "USD", "USD"
    )
    with pytest.raises(AccountingValidationError):
        FuturesSettlementAccountingSpecification(
            Market.CRYPTO, inst, mismatched_market_settlement
        )
    mismatched_symbol_settlement = FuturesSettlementSpecification(
        Market.CRYPTO,
        symbol(ContractFamily.INVERSE),
        SettlementUnit.ASSET,
        "USD",
        "USD",
    )
    with pytest.raises(AccountingValidationError):
        FuturesSettlementAccountingSpecification(
            Market.CRYPTO, inst, mismatched_symbol_settlement
        )
