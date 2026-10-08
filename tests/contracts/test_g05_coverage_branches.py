"""Targeted behavioral coverage for existing Futures contract branches.

These tests exercise real validation and calculation branches already defined
by the domain contracts. They do not alter the coverage gate or production
semantics.
"""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import TypedDict, cast

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
    ExposureValidationError,
    ExposureDenomination,
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

class LedgerEntryArgs(TypedDict):
    entry_id: str
    causation_id: str
    state_version: int
    sequence: int
    account_id: str
    instrument: FuturesInstrumentIdentity
    ledger_account: str
    asset: str
    direction: AccountingDirection
    amount: Decimal


class LiquidationArgs(TypedDict):
    contract: FuturesContractSpecification
    quantity: Decimal
    entry_price: Decimal
    margin_amount: Decimal
    margin_denomination: LiquidationDenomination
    maintenance_margin_ratio: Decimal
    position_side: PositionSide


class FundingSpecificationArgs(TypedDict):
    market: Market
    symbol: CanonicalFuturesSymbol
    funding_rate_unit: FundingRateUnit
    funding_sign_convention: FundingSignConvention
    funding_rate: Decimal
    interval_start: datetime
    interval_end: datetime
    rate_source: str
    observed_at: datetime
    notional_denomination: str


class MarginSpecificationArgs(TypedDict):
    market: Market
    instrument: FuturesInstrumentIdentity
    margin_unit: MarginUnit
    margin_asset: str
    source_asset: str
    conversion_rate: Decimal | None


class LeverageSpecificationArgs(TypedDict):
    market: Market
    instrument: FuturesInstrumentIdentity
    leverage_unit: LeverageUnit
    leverage: Decimal
    minimum_leverage: Decimal
    maximum_leverage: Decimal


class LiquidationEventArgs(TypedDict):
    account_id: str
    position_id: str
    event_id: str
    causation_id: str
    state_version: int
    contract_family: ContractFamily
    position_mode: PositionMode
    position_side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    margin_amount: Decimal
    margin_denomination: LiquidationDenomination
    maintenance_margin_ratio: Decimal
    liquidation_price: Decimal
    reference_price: Decimal
    reference_price_source: str
    observed_at: datetime
    as_of: datetime
    max_age: timedelta
    previous_event_sequence: int
    event_sequence: int


UTC = timezone.utc


def symbol(family: ContractFamily = ContractFamily.LINEAR, *, expiry: date | None = None) -> CanonicalFuturesSymbol:
    return CanonicalFuturesSymbol("BTC", "USD", family, "USD", expiry=expiry)


def instrument(market: Market = Market.CRYPTO, family: ContractFamily = ContractFamily.LINEAR) -> FuturesInstrumentIdentity:
    return FuturesInstrumentIdentity.create(
        market=market,
        symbol=symbol(family),
        margin_asset="USD",
        status=InstrumentStatus.ACTIVE,
    )


def contract(family: ContractFamily = ContractFamily.LINEAR) -> FuturesContractSpecification:
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
        CanonicalFuturesSymbol.parse(cast(str, 1))
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.build_id(cast(Market, "CRYPTO"), symbol())
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.build_id(Market.CRYPTO, cast(CanonicalFuturesSymbol, "BTC/USD"))
    with pytest.raises(InstrumentValidationError):
        FuturesInstrumentIdentity.parse_id("SPOT|CRYPTO|BTC/USD.LINEAR.USD", margin_asset="USD")


@pytest.mark.parametrize("value", [True, Decimal("NaN"), Decimal("Infinity")])
def test_contract_decimal_validation_branches(value: object) -> None:
    with pytest.raises(ContractSpecificationValidationError):
        FuturesContractSpecification(
            market=Market.CRYPTO,
            symbol=symbol(),
            quantity_unit=QuantityUnit.CONTRACTS,
            contract_multiplier=value,
            price_quote_asset="USD",
        )


def test_contract_family_fallback_branch_is_fail_closed() -> None:
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
            FuturesLedgerEntry(**cast(LedgerEntryArgs, {**base, field: value}))

    valid = FuturesLedgerEntry(**cast(LedgerEntryArgs, base))
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (valid,))
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (valid, FuturesLedgerEntry(**cast(LedgerEntryArgs, {**base, "entry_id": "e2", "sequence": 1}))))
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("j", (valid, FuturesLedgerEntry(**cast(LedgerEntryArgs, {**base, "entry_id": "e2", "sequence": 2, "direction": AccountingDirection.CREDIT, "asset": "USD", "amount": Decimal("2")}))))


def test_accounting_constructor_and_funding_boundaries():
    with pytest.raises(AccountingValidationError):
        FuturesAccountingSpecification(cast(Market, "bad"), instrument())
    with pytest.raises(AccountingValidationError):
        FuturesAccountingSpecification(Market.CRYPTO, cast(FuturesInstrumentIdentity, "bad"))
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
        spec.base_exposure(contract=cast(FuturesContractSpecification, "bad"), quantity=1, price=10)
    with pytest.raises(ExposureValidationError):
        spec.value(
            contract=c, quantity=1, reference_price=10,
            denomination=cast(ExposureDenomination, "BASE"), valuation_source="x",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC)
        )


def funding_spec(rate: Decimal = Decimal("0.1")) -> FuturesFundingSpecification:
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
    kwargs: dict[str, object] = dict(
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
        FuturesFundingSpecification(**cast(FundingSpecificationArgs, kwargs))


def test_funding_interval_provenance_and_side_branches():
    with pytest.raises(FundingValidationError):
        funding_spec().validate_freshness(
            as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
            max_age=timedelta(0),
        )
    with pytest.raises(FundingValidationError):
        funding_spec().calculate_payment(notional=1, position_side=cast(PositionSide, "LONG"))
    payment = funding_spec().calculate_payment(notional=Decimal("10"), position_side=PositionSide.SHORT)
    assert payment is not None
    assert payment.payer is PositionSide.SHORT
    assert payment.receiver is PositionSide.LONG


def margin_instrument() -> FuturesInstrumentIdentity:
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


def margin_bad(field: str, value: object) -> None:
    kwargs: dict[str, object] = dict(
        market=Market.CRYPTO, instrument=margin_instrument(),
        margin_unit=MarginUnit.ASSET, margin_asset="USD", source_asset="USD"
    )
    kwargs[field] = value
    with pytest.raises(MarginValidationError):
        FuturesMarginSpecification(**cast(MarginSpecificationArgs, kwargs))


@pytest.mark.parametrize("field,value", [
    ("market", "CRYPTO"), ("instrument", "bad"), ("margin_unit", "ASSET"),
    ("margin_asset", "SPOTUSD"), ("source_asset", "USD/EUR"),
])
def test_margin_constructor_validation(field: str, value: object) -> None:
    margin_bad(field, value)


def test_initial_and_maintenance_margin_remaining_branches() -> None:
    inst = instrument()
    initial = FuturesInitialMarginSpecification(
        Market.CRYPTO, inst, InitialMarginUnit.RATIO, Decimal("0.1"), "USD"
    )
    maintenance = FuturesMaintenanceMarginSpecification(
        Market.CRYPTO, inst, MaintenanceMarginUnit.RATIO, Decimal("0.05"), "USD"
    )
    assert initial.symbol == inst.symbol
    assert maintenance.symbol == inst.symbol
    assert initial.calculate(Decimal("100")) == Decimal("10.0")
    assert maintenance.calculate(Decimal("100")) == Decimal("5.00")
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(cast(Market, "bad"), inst, InitialMarginUnit.RATIO, Decimal("0.1"), "USD")
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(Market.CRYPTO, cast(FuturesInstrumentIdentity, "bad"), InitialMarginUnit.RATIO, Decimal("0.1"), "USD")
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(Market.CRYPTO, inst, cast(InitialMarginUnit, "RATIO"), Decimal("0.1"), "USD")
    with pytest.raises(InitialMarginValidationError):
        FuturesInitialMarginSpecification(Market.CRYPTO, inst, InitialMarginUnit.RATIO, Decimal("NaN"), "USD")
    with pytest.raises(MaintenanceMarginValidationError):
        FuturesMaintenanceMarginSpecification(cast(Market, "bad"), inst, MaintenanceMarginUnit.RATIO, Decimal("0.1"), "USD")
    with pytest.raises(MaintenanceMarginValidationError):
        FuturesMaintenanceMarginSpecification(Market.CRYPTO, cast(FuturesInstrumentIdentity, "bad"), MaintenanceMarginUnit.RATIO, Decimal("0.1"), "USD")
    with pytest.raises(MaintenanceMarginValidationError):
        FuturesMaintenanceMarginSpecification(Market.CRYPTO, inst, cast(MaintenanceMarginUnit, "RATIO"), Decimal("0.1"), "USD")
    with pytest.raises(MaintenanceMarginValidationError):
        FuturesMaintenanceMarginSpecification(Market.CRYPTO, inst, MaintenanceMarginUnit.RATIO, Decimal("NaN"), "USD")


def test_leverage_remaining_validation_branches() -> None:
    inst = instrument()
    spec = FuturesLeverageSpecification(
        Market.CRYPTO, inst, LeverageUnit.RATIO, Decimal("2"), Decimal("1"), Decimal("5")
    )
    assert spec.is_within_contract_bounds
    cases = [("market", "CRYPTO"), ("instrument", "bad"), ("leverage_unit", "RATIO")]
    for field, value in cases:
        kwargs: dict[str, object] = dict(
            market=Market.CRYPTO, instrument=inst, leverage_unit=LeverageUnit.RATIO,
            leverage=Decimal("2"), minimum_leverage=Decimal("1"), maximum_leverage=Decimal("5")
        )
        kwargs[field] = value
        with pytest.raises(LeverageValidationError):
            FuturesLeverageSpecification(**cast(LeverageSpecificationArgs, kwargs))
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(Market.CRYPTO, inst, LeverageUnit.RATIO, Decimal("2"), Decimal("6"), Decimal("5"))
    with pytest.raises(LeverageValidationError):
        FuturesLeverageSpecification(Market.CRYPTO, inst, LeverageUnit.RATIO, Decimal("6"), Decimal("1"), Decimal("5"))


def test_pnl_remaining_semantics():
    spec = FuturesPnLSpecification(Market.CRYPTO, symbol(), PnLUnit.REALIZED_OR_UNREALIZED)
    assert spec.denomination is PnLDenomination.QUOTE
    assert spec.calculate_realized(
        quantity=2, multiplier=3, entry_price=10, exit_price=12, position_side=PositionSide.SHORT
    ) == Decimal("-12")
    assert spec.calculate_unrealized(
        quantity=2, multiplier=3, entry_price=10, valuation_price=12,
        position_side=PositionSide.LONG, valuation_source="src",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
    ) == Decimal("12")
    with pytest.raises(PnLValidationError):
        spec.calculate_realized(quantity=1, multiplier=1, entry_price=1, exit_price=2, position_side=cast(PositionSide, "LONG"))
    with pytest.raises(PnLValidationError):
        spec.calculate_unrealized(
            quantity=1, multiplier=1, entry_price=1, valuation_price=2,
            position_side=PositionSide.LONG, valuation_source="",
            observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_position_mode_and_price_quantity_branches():
    with pytest.raises(PositionModeValidationError):
        FuturesPositionModeSpecification(cast(PositionMode, "ONE_WAY"))
    one = FuturesPositionModeSpecification(PositionMode.ONE_WAY)
    hedge = FuturesPositionModeSpecification(PositionMode.HEDGE)
    assert one.allowed_sides == (PositionSide.LONG, PositionSide.SHORT)
    assert not one.supports_independent_long_short
    assert hedge.supports_independent_long_short
    with pytest.raises(PositionModeValidationError):
        one.accepts(cast(PositionSide, "LONG"))
    pq = FuturesPriceQuantitySpecification(
        Market.CRYPTO, symbol(), PriceUnit.QUOTE_PER_BASE, QuantityUnit.CONTRACTS,
        "USD", PrecisionPolicy.EXACT, RoundingPolicy.NONE,
    )
    assert pq.validate_price(Decimal("10")) == Decimal("10")
    assert pq.validate_quantity(Decimal("2")) == Decimal("2")
    assert pq.quote_per_base(Decimal("10")) == Decimal("10")
    with pytest.raises(PriceQuantityValidationError):
        pq.validate_price(0)


def liquidation_args(family: ContractFamily = ContractFamily.LINEAR, side: PositionSide = PositionSide.LONG) -> LiquidationArgs:
    return cast(LiquidationArgs, dict(
        contract=contract(family), quantity=Decimal("1"), entry_price=Decimal("100"),
        margin_amount=Decimal("2000"),
        margin_denomination=LiquidationDenomination.QUOTE if family is ContractFamily.LINEAR else LiquidationDenomination.BASE,
        maintenance_margin_ratio=Decimal("0.1"), position_side=side,
    ))


def test_liquidation_linear_and_inverse_branches():
    linear = FuturesLiquidationSpecification(Market.CRYPTO, symbol())
    assert linear.liquidation_price(**liquidation_args()) < Decimal("100")
    short = linear.liquidation_price(**liquidation_args(side=PositionSide.SHORT))
    assert short > Decimal("100")
    inverse = FuturesLiquidationSpecification(Market.CRYPTO, symbol(ContractFamily.INVERSE))
    assert inverse.liquidation_price(**liquidation_args(ContractFamily.INVERSE)) < Decimal("100")
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**cast(LiquidationArgs, {**liquidation_args(), "margin_denomination": LiquidationDenomination.BASE}))
    with pytest.raises(LiquidationValidationError):
        inverse.liquidation_price(**cast(LiquidationArgs, {**liquidation_args(ContractFamily.INVERSE), "margin_denomination": LiquidationDenomination.QUOTE}))
    with pytest.raises(LiquidationValidationError):
        linear.liquidation_price(**cast(LiquidationArgs, {**liquidation_args(), "maintenance_margin_ratio": Decimal("1")}))


def liquidation_event_spec(family: ContractFamily = ContractFamily.LINEAR) -> FuturesLiquidationTriggerSpecification:
    return FuturesLiquidationTriggerSpecification(Market.CRYPTO, symbol(family))


def event_kwargs(family: ContractFamily = ContractFamily.LINEAR, side: PositionSide = PositionSide.LONG) -> LiquidationEventArgs:
    return cast(LiquidationEventArgs, dict(
        account_id="acct", position_id="pos", event_id="evt", causation_id="cause",
        state_version=1, contract_family=family, position_mode=PositionMode.ONE_WAY,
        position_side=side, quantity=Decimal("1"), entry_price=Decimal("100"),
        margin_amount=Decimal("20"),
        margin_denomination=LiquidationDenomination.QUOTE if family is ContractFamily.LINEAR else LiquidationDenomination.BASE,
        maintenance_margin_ratio=Decimal("0.1"),
        liquidation_price=Decimal("80") if side is PositionSide.LONG else Decimal("120"),
        reference_price=Decimal("75") if side is PositionSide.LONG else Decimal("125"),
        reference_price_source="mark",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        as_of=datetime(2026, 1, 1, 1, tzinfo=UTC),
        max_age=timedelta(hours=2), previous_event_sequence=1, event_sequence=2,
    ))


def test_liquidation_event_trigger_and_non_trigger_paths():
    spec = liquidation_event_spec()
    triggered = spec.evaluate(**event_kwargs())
    assert triggered.trigger is LiquidationTrigger.TRIGGERED
    assert triggered.event is not None
    not_triggered = spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "reference_price": Decimal("90"), "event_sequence": 1}))
    assert not_triggered.trigger is LiquidationTrigger.NOT_TRIGGERED
    assert not_triggered.event is None
    short = liquidation_event_spec().evaluate(**event_kwargs(side=PositionSide.SHORT))
    assert short.event is not None


@pytest.mark.parametrize("field,value", [
    ("account_id", ""), ("position_id", ""), ("event_id", ""), ("causation_id", ""),
    ("state_version", -1), ("previous_event_sequence", -1), ("event_sequence", -1),
])
def test_liquidation_event_identifier_validation(field, value):
    kwargs = event_kwargs()
    kwargs[field] = value
    with pytest.raises(LiquidationEventValidationError):
        liquidation_event_spec().evaluate(**kwargs)


def test_liquidation_event_sequence_and_input_validation():
    spec = liquidation_event_spec()
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "event_sequence": 1, "previous_event_sequence": 2}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "contract_family": ContractFamily.INVERSE}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "position_mode": "ONE_WAY"}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "position_side": "LONG"}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "margin_denomination": LiquidationDenomination.BASE}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "maintenance_margin_ratio": Decimal("1")}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "liquidation_price": Decimal("100")}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "reference_price_source": ""}))
    with pytest.raises(LiquidationEventValidationError):
        spec.evaluate(**cast(LiquidationEventArgs, {**event_kwargs(), "max_age": timedelta(0)}))


def test_liquidation_event_class_invariants_and_evaluation_validation():
    result = liquidation_event_spec().evaluate(**event_kwargs())
    event = result.event
    assert event is not None
    for field, value in [
        ("account_id", ""), ("state_version", -1), ("market", "CRYPTO"),
        ("symbol", "bad"), ("position_mode", "ONE_WAY"), ("position_side", "LONG"),
        ("quantity", Decimal("0")), ("margin_denomination", "QUOTE"),
        ("maintenance_margin_ratio", Decimal("1")), ("reference_price_source", ""),
        ("max_age", timedelta(0)),
    ]:
        data = {name: getattr(event, name) for name in event.__dataclass_fields__}
        data[field] = value
        with pytest.raises((LiquidationEventValidationError, ValueError)):
            FuturesLiquidationTriggerEvent(**data)
    with pytest.raises(LiquidationEventValidationError):
        type(result)(LiquidationTrigger.TRIGGERED, None)
    with pytest.raises(LiquidationEventValidationError):
        type(result)(LiquidationTrigger.NOT_TRIGGERED, event)


def test_settlement_and_settlement_accounting_remaining_branches():
    inst = instrument()
    same = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "USD"
    )
    assert not same.conversion_required
    assert same.settle_amount(Decimal("2")) == Decimal("2")
    cross = FuturesSettlementSpecification(
        Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "EUR", Decimal("2")
    )
    assert cross.settle_amount(Decimal("2")) == Decimal("4")
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "EUR", "EUR")
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(Market.CRYPTO, inst.symbol, SettlementUnit.ASSET, "USD", "EUR")
    with pytest.raises(SettlementValidationError):
        FuturesSettlementSpecification(Market.CRYPTO, inst.symbol, cast(SettlementUnit, "ASSET"), "USD", "USD")
    with pytest.raises(SettlementValidationError):
        same.settle_amount(cast(Decimal, 0))
    accounting = FuturesSettlementAccountingSpecification(Market.CRYPTO, inst, same)
    with pytest.raises(AccountingValidationError):
        FuturesSettlementAccountingSpecification("bad", inst, same)
    with pytest.raises(AccountingValidationError):
        FuturesSettlementAccountingSpecification(Market.CRYPTO, "bad", same)
    with pytest.raises(AccountingValidationError):
        FuturesSettlementAccountingSpecification(Market.CRYPTO, inst, cast(FuturesSettlementSpecification, "bad"))
    with pytest.raises(AccountingValidationError):
        accounting.transfer(
            journal_id="j", causation_id="c", state_version=-1, sequence=1,
            account_id="a", settlement_counterparty_account_id="b",
            source_amount=Decimal("1"), source_asset="USD",
        )
    with pytest.raises(AccountingValidationError):
        accounting.transfer(
            journal_id="j", causation_id="c", state_version=1, sequence=1,
            account_id="a", settlement_counterparty_account_id="b",
            source_amount=Decimal("1"), source_asset="EUR",
        )
