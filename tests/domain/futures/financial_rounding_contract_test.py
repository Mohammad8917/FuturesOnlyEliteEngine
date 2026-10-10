from decimal import (
    Decimal,
    Inexact,
    ROUND_UP,
    Rounded,
    getcontext,
    localcontext,
)

import pytest

from contracts.futures.instrument import Market
from contracts.futures.position_side import PositionSide
from domain.futures.financial_rounding import (
    FinancialRiskBoundaryError,
    FinancialRoundingAuditRecord,
    FinancialRoundingError,
    FinancialRoundingResult,
    controlled_decimal_context,
    round_funding,
    round_liquidation_price,
    round_margin_ratio,
    round_pnl,
)


def test_controlled_context_is_independent_and_traps_intermediate_loss() -> None:
    with localcontext() as ambient:
        ambient.prec = 3
        ambient.rounding = ROUND_UP
        ambient.traps[Inexact] = False
        ambient.traps[Rounded] = False

        with controlled_decimal_context() as controlled:
            assert controlled.prec == 28
            assert controlled.rounding != ROUND_UP
            assert controlled.traps[Inexact]
            assert controlled.traps[Rounded]
            with pytest.raises(Inexact):
                Decimal("1") / Decimal("3")


def test_pnl_rounding_uses_explicit_scale_and_records_audit_fact() -> None:
    result = round_pnl(
        Decimal("123.456789129"),
        market=Market.CRYPTO,
        scale=8,
        max_reasonable_pnl=Decimal("1000"),
    )
    assert result.value == Decimal("123.45678912")
    assert result.value.as_tuple().exponent == -8
    assert result.audit_record == FinancialRoundingAuditRecord(
        boundary="PNL",
        input_value="1.23456789129E+2",
        output_value="1.2345678912E+2",
        rounding_mode="ROUND_DOWN",
        scale_or_tick="scale=8",
    )


def test_pnl_round_down_is_toward_zero_for_negative_values() -> None:
    result = round_pnl(
        Decimal("-1.239"),
        market=Market.GOLD,
        scale=2,
        max_reasonable_pnl=Decimal("10"),
    )
    assert result.value == Decimal("-1.23")
    assert result.audit_record.rounding_mode == "ROUND_DOWN"


@pytest.mark.parametrize(
    ("market", "scale", "expected"),
    [
        (Market.CRYPTO, 8, Decimal("1.12345678")),
        (Market.FOREX, 2, Decimal("1.12")),
        (Market.GOLD, 2, Decimal("1.12")),
    ],
)
def test_pnl_supports_the_adr_market_baseline_scales(market, scale, expected) -> None:
    result = round_pnl(
        Decimal("1.123456789"),
        market=market,
        scale=scale,
        max_reasonable_pnl=Decimal("10"),
    )
    assert result.value == expected


def test_pnl_scale_can_be_explicitly_overridden_by_policy() -> None:
    result = round_pnl(
        Decimal("1.23456"),
        market=Market.CRYPTO,
        scale=4,
        max_reasonable_pnl=Decimal("10"),
    )
    assert result.value == Decimal("1.2345")


@pytest.mark.parametrize(
    ("value", "scale", "maximum", "market"),
    [
        (Decimal("10.01"), 2, Decimal("10"), Market.CRYPTO),
        (Decimal("1"), True, Decimal("10"), Market.CRYPTO),
        (Decimal("1"), -1, Decimal("10"), Market.CRYPTO),
        (Decimal("1"), 2, Decimal("0"), Market.CRYPTO),
        (Decimal("1"), 2, None, Market.CRYPTO),
        (Decimal("1"), 2, Decimal("10"), "CRYPTO"),
        (Decimal("NaN"), 2, Decimal("10"), Market.CRYPTO),
        (Decimal("Infinity"), 2, Decimal("10"), Market.CRYPTO),
    ],
)
def test_pnl_rejects_invalid_or_out_of_policy_inputs(
    value, scale, maximum, market
) -> None:
    with pytest.raises(FinancialRoundingError):
        round_pnl(
            value,
            market=market,
            scale=scale,
            max_reasonable_pnl=maximum,
        )


def test_pnl_fails_closed_when_configured_scale_exceeds_working_precision() -> None:
    with pytest.raises(FinancialRoundingError):
        round_pnl(
            Decimal("1"),
            market=Market.CRYPTO,
            scale=100,
            max_reasonable_pnl=Decimal("10"),
        )


def test_funding_round_half_up_and_audit_value_are_exact() -> None:
    result = round_funding(
        Decimal("1.234567895"),
        funding_rate=Decimal("0.001"),
        max_funding_rate=Decimal("0.01"),
        scale=8,
    )
    assert result.value == Decimal("1.23456790")
    assert result.value.as_tuple().exponent == -8
    assert result.audit_record.rounding_mode == "ROUND_HALF_UP"
    assert result.audit_record.input_value == "1.234567895"
    assert result.audit_record.output_value == "1.2345679"


def test_funding_rejects_rate_over_policy_limit_and_negative_amount() -> None:
    with pytest.raises(FinancialRiskBoundaryError):
        round_funding(
            Decimal("1"),
            funding_rate=Decimal("-0.02"),
            max_funding_rate=Decimal("0.01"),
            scale=8,
        )
    with pytest.raises(FinancialRoundingError):
        round_funding(
            Decimal("-1"),
            funding_rate=Decimal("0.001"),
            max_funding_rate=Decimal("0.01"),
            scale=8,
        )


@pytest.mark.parametrize(
    ("amount", "rate", "maximum", "scale"),
    [
        (Decimal("1"), Decimal("NaN"), Decimal("1"), 8),
        (Decimal("1"), Decimal("0.1"), Decimal("0"), 8),
        (Decimal("1"), Decimal("0.1"), Decimal("1"), True),
        (Decimal("1"), Decimal("0.1"), Decimal("1"), -1),
        (Decimal("1"), Decimal("0.1"), None, 8),
        (Decimal("1"), Decimal("0.1"), Decimal("1"), 100),
    ],
)
def test_funding_fails_closed_on_invalid_policy_or_values(
    amount, rate, maximum, scale
) -> None:
    with pytest.raises(FinancialRoundingError):
        round_funding(
            amount,
            funding_rate=rate,
            max_funding_rate=maximum,
            scale=scale,
        )


def test_margin_ratio_is_rounded_for_comparison_only_and_rejects_unsafe_interval() -> (
    None
):
    with pytest.raises(FinancialRiskBoundaryError) as captured:
        round_margin_ratio(
            Decimal("0.075000004"),
            maintenance_margin_ratio=Decimal("0.05"),
            liquidation_ratio=Decimal("0.10"),
        )
    assert captured.value.audit_record is not None
    assert captured.value.audit_record.boundary == "MARGIN_RATIO"


@pytest.mark.parametrize("ratio", [Decimal("0.05"), Decimal("0.10")])
def test_margin_ratio_accepts_strict_interval_boundaries(ratio) -> None:
    result = round_margin_ratio(
        ratio,
        maintenance_margin_ratio=Decimal("0.05"),
        liquidation_ratio=Decimal("0.10"),
    )
    assert result.value == ratio.quantize(Decimal("0.00000001"))
    assert result.audit_record.scale_or_tick == "scale=8"


@pytest.mark.parametrize(
    ("ratio", "maintenance", "liquidation"),
    [
        (Decimal("-0.01"), Decimal("0.05"), Decimal("0.10")),
        (Decimal("0.07"), Decimal("0.10"), Decimal("0.05")),
        (Decimal("0.07"), Decimal("0.05"), Decimal("0.05")),
        (Decimal("NaN"), Decimal("0.05"), Decimal("0.10")),
    ],
)
def test_margin_ratio_rejects_invalid_values_and_threshold_order(
    ratio, maintenance, liquidation
) -> None:
    with pytest.raises(FinancialRoundingError):
        round_margin_ratio(
            ratio,
            maintenance_margin_ratio=maintenance,
            liquidation_ratio=liquidation,
        )


def test_liquidation_rounding_uses_exact_tick_multiples_and_direction() -> None:
    long_result = round_liquidation_price(
        Decimal("100.14"),
        tick_size=Decimal("0.05"),
        position_side=PositionSide.LONG,
        last_price=Decimal("101"),
        position_is_liquidated=False,
    )
    short_result = round_liquidation_price(
        Decimal("100.14"),
        tick_size=Decimal("0.05"),
        position_side=PositionSide.SHORT,
        last_price=Decimal("99"),
        position_is_liquidated=False,
    )
    assert long_result.value == Decimal("100.10")
    assert short_result.value == Decimal("100.15")
    assert long_result.audit_record.rounding_mode == "ROUND_DOWN"
    assert short_result.audit_record.rounding_mode == "ROUND_UP"
    assert long_result.audit_record.scale_or_tick == "tick=5E-2"


def test_liquidation_rounding_handles_exact_tick_without_moving_it() -> None:
    result = round_liquidation_price(
        Decimal("100.25"),
        tick_size=Decimal("0.25"),
        position_side=PositionSide.LONG,
        last_price=Decimal("101"),
        position_is_liquidated=False,
    )
    assert result.value == Decimal("100.25")


@pytest.mark.parametrize(
    ("side", "last_price"),
    [
        (PositionSide.LONG, Decimal("100.10")),
        (PositionSide.SHORT, Decimal("100.20")),
    ],
)
def test_liquidation_fails_closed_when_trigger_is_crossed(side, last_price) -> None:
    with pytest.raises(FinancialRiskBoundaryError) as captured:
        round_liquidation_price(
            Decimal("100.14"),
            tick_size=Decimal("0.05"),
            position_side=side,
            last_price=last_price,
            position_is_liquidated=False,
        )
    assert captured.value.audit_record is not None
    assert captured.value.audit_record.boundary == "LIQUIDATION_PRICE"


def test_liquidation_crossing_is_not_reclassified_if_already_liquidated() -> None:
    result = round_liquidation_price(
        Decimal("100.14"),
        tick_size=Decimal("0.05"),
        position_side=PositionSide.LONG,
        last_price=Decimal("100"),
        position_is_liquidated=True,
    )
    assert result.value == Decimal("100.10")


@pytest.mark.parametrize(
    ("price", "tick", "side", "last", "liquidated"),
    [
        (Decimal("0"), Decimal("0.1"), PositionSide.LONG, Decimal("1"), False),
        (Decimal("1"), Decimal("0"), PositionSide.LONG, Decimal("2"), False),
        (Decimal("1"), Decimal("0.1"), "LONG", Decimal("2"), False),
        (Decimal("1"), Decimal("0.1"), PositionSide.LONG, Decimal("2"), 0),
        (Decimal("1"), Decimal("0.1"), PositionSide.LONG, Decimal("0"), False),
        (Decimal("1"), Decimal("0.1"), PositionSide.LONG, Decimal("0.5"), False),
    ],
)
def test_liquidation_rejects_invalid_inputs(
    price, tick, side, last, liquidated
) -> None:
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price(
            price,
            tick_size=tick,
            position_side=side,
            last_price=last,
            position_is_liquidated=liquidated,
        )


def test_liquidation_fails_closed_when_tick_result_exceeds_working_precision() -> None:
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price(
            Decimal("12345678901234567890123456789"),
            tick_size=Decimal("1"),
            position_side=PositionSide.LONG,
            last_price=Decimal("1"),
            position_is_liquidated=False,
        )


def test_audit_result_cannot_claim_a_different_output() -> None:
    record = FinancialRoundingAuditRecord(
        boundary="PNL",
        input_value="1",
        output_value="2",
        rounding_mode="ROUND_DOWN",
        scale_or_tick="scale=2",
    )
    with pytest.raises(FinancialRoundingError):
        FinancialRoundingResult(value=Decimal("1"), audit_record=record)



@pytest.mark.parametrize("value", [True, False, 0.1, float("inf"), "not-a-decimal"])
def test_pnl_rejects_non_decimal_or_malformed_values(value) -> None:
    with pytest.raises(FinancialRoundingError):
        round_pnl(
            value,
            market=Market.CRYPTO,
            scale=8,
            max_reasonable_pnl=Decimal("10"),
        )


def test_pnl_accepts_exact_integer_and_decimal_text_inputs() -> None:
    integer_result = round_pnl(
        2,
        market=Market.CRYPTO,
        scale=2,
        max_reasonable_pnl=Decimal("10"),
    )
    text_result = round_pnl(
        "1.239",
        market=Market.CRYPTO,
        scale=2,
        max_reasonable_pnl=Decimal("10"),
    )
    assert integer_result.value == Decimal("2.00")
    assert text_result.value == Decimal("1.23")


@pytest.mark.parametrize("value", [True, 0.1, float("inf"), "malformed"])
def test_funding_rejects_non_decimal_or_malformed_amount(value) -> None:
    with pytest.raises(FinancialRoundingError):
        round_funding(
            value,
            funding_rate=Decimal("0.001"),
            max_funding_rate=Decimal("0.01"),
            scale=8,
        )


def test_funding_accepts_zero_amount_without_inventing_a_transfer() -> None:
    result = round_funding(
        Decimal("0"),
        funding_rate=Decimal("0"),
        max_funding_rate=Decimal("0.01"),
        scale=8,
    )
    assert result.value == Decimal("0E-8")


@pytest.mark.parametrize(
    "field,value",
    [
        ("boundary", ""),
        ("input_value", " "),
        ("output_value", None),
        ("rounding_mode", ""),
        ("scale_or_tick", ""),
    ],
)
def test_audit_record_rejects_missing_required_fields(field, value) -> None:
    fields = {
        "boundary": "PNL",
        "input_value": "1",
        "output_value": "1",
        "rounding_mode": "ROUND_DOWN",
        "scale_or_tick": "scale=2",
    }
    fields[field] = value
    with pytest.raises(FinancialRoundingError):
        FinancialRoundingAuditRecord(**fields)


@pytest.mark.parametrize("value", [1, Decimal("NaN"), Decimal("Infinity")])
def test_rounding_result_rejects_non_finite_or_non_decimal_values(value) -> None:
    record = FinancialRoundingAuditRecord(
        boundary="PNL",
        input_value="1",
        output_value="1",
        rounding_mode="ROUND_DOWN",
        scale_or_tick="scale=0",
    )
    with pytest.raises(FinancialRoundingError):
        FinancialRoundingResult(value=value, audit_record=record)


def test_rounding_result_rejects_missing_audit_record() -> None:
    with pytest.raises(FinancialRoundingError):
        FinancialRoundingResult(
            value=Decimal("1"),
            audit_record=None,
        )


def test_liquidation_fails_closed_when_long_tick_rounds_to_zero() -> None:
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price(
            Decimal("0.01"),
            tick_size=Decimal("0.1"),
            position_side=PositionSide.LONG,
            last_price=Decimal("1"),
            position_is_liquidated=False,
        )


def test_controlled_context_does_not_mutate_ambient_context() -> None:
    original = getcontext().prec
    with controlled_decimal_context() as context:
        context.prec = 12
    assert getcontext().prec == original



def test_audit_record_rejects_noncanonical_decimal_text() -> None:
    with pytest.raises(FinancialRoundingError):
        FinancialRoundingAuditRecord(
            boundary="PNL",
            input_value="1.0",
            output_value="1",
            rounding_mode="ROUND_DOWN",
            scale_or_tick="scale=0",
        )
