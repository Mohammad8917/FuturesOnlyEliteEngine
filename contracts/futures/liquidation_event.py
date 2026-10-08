"""Canonical Futures liquidation-trigger contract tests."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from contracts.futures.instrument import CanonicalFuturesSymbol, ContractFamily, Market
from contracts.futures.liquidation import LiquidationDenomination
from contracts.futures.liquidation_event import (
    FuturesLiquidationTriggerEvent,
    FuturesLiquidationTriggerSpecification,
    LiquidationEventValidationError,
    LiquidationTrigger,
)
from contracts.futures.position_mode import PositionMode
from contracts.futures.position_side import PositionSide


UTC = timezone.utc
OBSERVED = datetime(2026, 10, 8, 10, 0, tzinfo=UTC)
AS_OF = OBSERVED + timedelta(seconds=5)


def make_symbol(market: Market, family: ContractFamily) -> CanonicalFuturesSymbol:
    base = "BTC" if market is Market.CRYPTO else "XAU"
    return CanonicalFuturesSymbol(base, "USD", family, "USD")


def evaluate(
    *,
    market=Market.CRYPTO,
    family=ContractFamily.LINEAR,
    side=PositionSide.LONG,
    mode=PositionMode.ONE_WAY,
    reference=Decimal("40"),
    liquidation=Decimal("42"),
    previous_sequence=4,
    event_sequence=5,
    **overrides,
):
    spec = FuturesLiquidationTriggerSpecification(market, make_symbol(market, family))
    values = dict(
        account_id="account-1",
        position_id="position-1",
        event_id="liq-event-1",
        causation_id="valuation-1",
        state_version=12,
        contract_family=family,
        position_mode=mode,
        position_side=side,
        quantity=Decimal("2"),
        entry_price=Decimal("50"),
        margin_amount=Decimal("900") if family is ContractFamily.LINEAR else Decimal("1"),
        margin_denomination=(
            LiquidationDenomination.QUOTE
            if family is ContractFamily.LINEAR
            else LiquidationDenomination.BASE
        ),
        maintenance_margin_ratio=Decimal("0.05"),
        liquidation_price=liquidation,
        reference_price=reference,
        reference_price_source="validated-mark-price",
        observed_at=OBSERVED,
        as_of=AS_OF,
        max_age=timedelta(minutes=1),
        previous_event_sequence=previous_sequence,
        event_sequence=event_sequence,
    )
    values.update(overrides)
    return spec.evaluate(**values)


@pytest.mark.parametrize("market", list(Market))
@pytest.mark.parametrize("family", list(ContractFamily))
@pytest.mark.parametrize("mode", list(PositionMode))
@pytest.mark.parametrize("side", list(PositionSide))
def test_scope_and_side_mode_are_explicit(market, family, mode, side):
    liquidation = Decimal("42") if side is PositionSide.LONG else Decimal("58")
    reference = Decimal("40") if side is PositionSide.LONG else Decimal("60")
    result = evaluate(
        market=market,
        family=family,
        mode=mode,
        side=side,
        liquidation=liquidation,
        reference=reference,
    )
    assert result.trigger is LiquidationTrigger.TRIGGERED
    assert result.event is not None
    assert result.event.position_mode is mode
    assert result.event.position_side is side
    assert result.event.market is market
    assert result.event.symbol.contract_family is family


def test_long_trigger_is_downward_and_not_triggered_above_liquidation():
    triggered = evaluate(side=PositionSide.LONG, reference=Decimal("42"))
    assert triggered.trigger is LiquidationTrigger.TRIGGERED
    assert triggered.event is not None

    not_triggered = evaluate(side=PositionSide.LONG, reference=Decimal("42.01"))
    assert not_triggered.trigger is LiquidationTrigger.NOT_TRIGGERED
    assert not_triggered.event is None


def test_short_trigger_is_upward_and_not_triggered_below_liquidation():
    triggered = evaluate(
        side=PositionSide.SHORT,
        liquidation=Decimal("58"),
        reference=Decimal("58"),
    )
    assert triggered.trigger is LiquidationTrigger.TRIGGERED
    assert triggered.event is not None

    not_triggered = evaluate(
        side=PositionSide.SHORT,
        liquidation=Decimal("58"),
        reference=Decimal("57.99"),
    )
    assert not_triggered.trigger is LiquidationTrigger.NOT_TRIGGERED
    assert not_triggered.event is None


@pytest.mark.parametrize(
    "field",
    [
        "account_id",
        "position_id",
        "event_id",
        "causation_id",
        "reference_price_source",
    ],
)
def test_missing_provenance_or_identity_fails_closed(field):
    with pytest.raises(LiquidationEventValidationError):
        evaluate(**{field: ""})


@pytest.mark.parametrize(
    "field",
    ["reference_price", "liquidation_price", "quantity", "margin_amount", "maintenance_margin_ratio"],
)
@pytest.mark.parametrize("value", [True, False, 0, -1, 0.1, float("nan"), Decimal("NaN")])
def test_numeric_boundaries_reject_bool_float_and_invalid_values(field, value):
    with pytest.raises(LiquidationEventValidationError):
        evaluate(**{field: value})


def test_freshness_and_utc_are_fail_closed():
    with pytest.raises(LiquidationEventValidationError):
        evaluate(as_of=AS_OF + timedelta(minutes=2))

    with pytest.raises(LiquidationEventValidationError):
        evaluate(
            observed_at=OBSERVED.replace(tzinfo=None),
        )

    with pytest.raises(LiquidationEventValidationError):
        evaluate(
            observed_at=AS_OF + timedelta(seconds=1),
            as_of=AS_OF,
        )


def test_triggered_event_requires_monotonic_sequence():
    with pytest.raises(LiquidationEventValidationError):
        evaluate(previous_sequence=5, event_sequence=5)

    with pytest.raises(LiquidationEventValidationError):
        evaluate(previous_sequence=6, event_sequence=5)


def test_non_triggered_evaluation_can_keep_same_sequence_without_emitting_event():
    result = evaluate(
        reference=Decimal("45"),
        previous_sequence=5,
        event_sequence=5,
    )
    assert result.trigger is LiquidationTrigger.NOT_TRIGGERED
    assert result.event is None


def test_family_denomination_mismatch_fails_closed():
    with pytest.raises(LiquidationEventValidationError):
        evaluate(
            family=ContractFamily.LINEAR,
            margin_denomination=LiquidationDenomination.BASE,
        )
    with pytest.raises(LiquidationEventValidationError):
        evaluate(
            family=ContractFamily.INVERSE,
            margin_denomination=LiquidationDenomination.QUOTE,
        )


def test_contradictory_contract_family_and_symbol_fails_closed():
    with pytest.raises(LiquidationEventValidationError):
        evaluate(family=ContractFamily.INVERSE, contract_family=ContractFamily.LINEAR)


def test_invalid_liquidation_direction_fails_closed():
    with pytest.raises(LiquidationEventValidationError):
        evaluate(side=PositionSide.LONG, liquidation=Decimal("50"), reference=Decimal("40"))

    with pytest.raises(LiquidationEventValidationError):
        evaluate(side=PositionSide.SHORT, liquidation=Decimal("50"), reference=Decimal("60"))


def test_event_is_immutable_and_contains_audit_provenance():
    result = evaluate()
    assert result.event is not None
    event = result.event
    assert isinstance(event, FuturesLiquidationTriggerEvent)
    assert event.reference_price_source == "validated-mark-price"
    assert event.observed_at == OBSERVED
    assert event.as_of == AS_OF
    assert event.max_age == timedelta(minutes=1)
    with pytest.raises((AttributeError, TypeError)):
        event.reference_price = Decimal("1")  # type: ignore[misc]


def test_direct_event_cannot_claim_trigger_without_crossing_liquidation_price():
    with pytest.raises(LiquidationEventValidationError):
        FuturesLiquidationTriggerEvent(
            account_id="account-1",
            position_id="position-1",
            event_id="event-1",
            causation_id="cause-1",
            state_version=1,
            event_sequence=1,
            market=Market.CRYPTO,
            symbol=make_symbol(Market.CRYPTO, ContractFamily.LINEAR),
            position_mode=PositionMode.ONE_WAY,
            position_side=PositionSide.LONG,
            quantity=Decimal("2"),
            entry_price=Decimal("50"),
            margin_amount=Decimal("900"),
            margin_denomination=LiquidationDenomination.QUOTE,
            maintenance_margin_ratio=Decimal("0.05"),
            liquidation_price=Decimal("42"),
            reference_price=Decimal("43"),
            reference_price_source="source",
            observed_at=OBSERVED,
            as_of=AS_OF,
            max_age=timedelta(minutes=1),
        )
