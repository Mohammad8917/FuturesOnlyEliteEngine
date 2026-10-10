from decimal import Decimal, Inexact, ROUND_UP, localcontext
from operator import setitem
import pytest

from contracts.futures.instrument import Market
from contracts.futures.position_side import PositionSide
from domain.futures.financial_rounding import (
    DEFAULT_PNL_SCALES,
    FinancialRiskBoundaryError,
    FinancialRoundingError,
    FundingRoundingPolicy,
    LiquidationPriceRoundingPolicy,
    MarginRatioRoundingPolicy,
    PnLRoundingPolicy,
    financial_working_context,
    round_funding,
    round_liquidation_price,
    round_margin_ratio,
    round_pnl,
    _scale,
)


def test_working_context_isolated_and_traps_intermediate_inexactness():
    with localcontext() as ambient:
        ambient.prec = 3
        ambient.rounding = ROUND_UP
        with financial_working_context() as controlled:
            assert controlled.prec == 28
            assert controlled.rounding != ambient.rounding
            with pytest.raises(Inexact):
                Decimal("1") / Decimal("3")


@pytest.mark.parametrize(
    ("market", "value", "expected"),
    [
        (Market.CRYPTO, "12.123456789", "12.12345678"),
        (Market.GOLD, "12.129", "12.12"),
        (Market.FOREX, "-12.129", "-12.12"),
        (Market.CRYPTO, "-0.000000019", "-0.00000001"),
    ],
)
def test_pnl_uses_approved_market_scale_and_rounds_toward_zero(market, value, expected):
    policy = PnLRoundingPolicy(market=market, max_reasonable_pnl="100")
    assert round_pnl(value, policy) == Decimal(expected)


def test_pnl_scale_override_is_explicit_and_validated():
    policy = PnLRoundingPolicy(
        market=Market.CRYPTO, max_reasonable_pnl="100", scale_override=3
    )
    assert round_pnl("1.2349", policy) == Decimal("1.234")
    with pytest.raises(FinancialRoundingError):
        PnLRoundingPolicy(
            market=Market.CRYPTO, max_reasonable_pnl="100", scale_override=True
        )


def test_pnl_fails_closed_when_maximum_is_missing_invalid_or_exceeded():
    with pytest.raises(FinancialRoundingError):
        PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="0")
    policy = PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="10")
    with pytest.raises(FinancialRiskBoundaryError):
        round_pnl("-10.00000001", policy)


def test_boundary_rounding_does_not_inherit_ambient_context():
    policy = PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="100")
    with localcontext() as ambient:
        ambient.prec = 2
        ambient.rounding = ROUND_UP
        result = round_pnl("1.239999999", policy)
    assert result == Decimal("1.23999999")
    assert result.as_tuple().exponent == -8


@pytest.mark.parametrize(
    ("payment", "expected"),
    [
        ("1.000000005", "1.00000001"),
        ("-1.000000005", "-1.00000001"),
        ("0.0000000049", "0E-8"),
    ],
)
def test_funding_payment_uses_eight_places_half_up(payment, expected):
    policy = FundingRoundingPolicy(max_funding_rate="0.1")
    assert round_funding(payment, "0.01", policy) == Decimal(expected)


def test_funding_rejects_missing_policy_and_out_of_policy_rate():
    with pytest.raises(FinancialRoundingError):
        FundingRoundingPolicy(max_funding_rate="0")
    policy = FundingRoundingPolicy(max_funding_rate="0.01")
    with pytest.raises(FinancialRiskBoundaryError):
        round_funding("1", "-0.0100001", policy)


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        ("0.2", "0.20000000"),
        ("0.4", "0.40000000"),
        ("0.6", "0.60000000"),
    ],
)
def test_margin_ratio_is_rounded_for_comparison_and_threshold_equality_is_allowed(
    ratio, expected
):
    policy = MarginRatioRoundingPolicy(
        maintenance_margin_ratio="0.4", liquidation_ratio="0.6"
    )
    assert round_margin_ratio(ratio, policy) == Decimal(expected)


def test_margin_ratio_fails_closed_inside_critical_range():
    policy = MarginRatioRoundingPolicy(
        maintenance_margin_ratio="0.4", liquidation_ratio="0.6"
    )
    with pytest.raises(FinancialRiskBoundaryError):
        round_margin_ratio("0.500000001", policy)


def test_margin_ratio_thresholds_must_be_ordered():
    with pytest.raises(FinancialRoundingError):
        MarginRatioRoundingPolicy(
            maintenance_margin_ratio="0.6", liquidation_ratio="0.4"
        )


@pytest.mark.parametrize(
    ("side", "expected"),
    [
        (PositionSide.LONG, "100.00"),
        (PositionSide.SHORT, "100.05"),
    ],
)
def test_liquidation_price_rounds_to_configured_non_power_of_ten_tick(side, expected):
    policy = LiquidationPriceRoundingPolicy(tick_size="0.05", position_side=side)
    assert round_liquidation_price("100.023", policy) == Decimal(expected)


def test_liquidation_price_keeps_exact_tick_and_does_not_change_it():
    policy = LiquidationPriceRoundingPolicy(
        tick_size="0.1", position_side=PositionSide.SHORT
    )
    assert round_liquidation_price("100.2", policy) == Decimal("100.2")


def test_liquidation_price_requires_explicit_valid_tick_and_side():
    with pytest.raises(FinancialRoundingError):
        LiquidationPriceRoundingPolicy(tick_size="0", position_side=PositionSide.LONG)
    with pytest.raises(FinancialRoundingError):
        LiquidationPriceRoundingPolicy(tick_size="0.1", position_side="LONG")


def test_all_helpers_reject_binary_float_inputs():
    with pytest.raises(FinancialRoundingError):
        round_pnl(1.25, PnLRoundingPolicy(Market.CRYPTO, "100"))
    with pytest.raises(FinancialRoundingError):
        round_funding(1.25, "0.01", FundingRoundingPolicy("0.1"))
    with pytest.raises(FinancialRoundingError):
        round_margin_ratio(0.5, MarginRatioRoundingPolicy("0.4", "0.6"))
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price(
            100.0, LiquidationPriceRoundingPolicy("0.1", PositionSide.LONG)
        )


def test_decimal_input_validation_rejects_wrong_type_malformed_and_nonfinite_values():
    policy = PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="100")
    with pytest.raises(FinancialRoundingError):
        round_pnl(None, policy)
    with pytest.raises(FinancialRoundingError):
        round_pnl("not-a-number", policy)
    with pytest.raises(FinancialRoundingError):
        round_pnl(Decimal("NaN"), policy)


def test_pnl_policy_rejects_unsupported_market_and_wrong_policy_object():
    with pytest.raises(FinancialRoundingError):
        PnLRoundingPolicy(market="CRYPTO", max_reasonable_pnl="100")
    with pytest.raises(FinancialRoundingError):
        round_pnl("1", object())


def test_pnl_fails_closed_when_quantized_result_exceeds_working_precision():
    huge = Decimal("1" + "0" * 40)
    policy = PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl=huge)
    with pytest.raises(FinancialRoundingError):
        round_pnl(huge, policy)


def test_funding_rejects_wrong_policy_object():
    with pytest.raises(FinancialRoundingError):
        round_funding("1", "0.01", object())


def test_margin_ratio_rejects_wrong_policy_and_negative_ratio():
    policy = MarginRatioRoundingPolicy(
        maintenance_margin_ratio="0.4", liquidation_ratio="0.6"
    )
    with pytest.raises(FinancialRoundingError):
        round_margin_ratio("0.5", object())
    with pytest.raises(FinancialRoundingError):
        round_margin_ratio("-0.1", policy)


def test_liquidation_rejects_wrong_policy_and_zero_tick_result():
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price("100", object())
    policy = LiquidationPriceRoundingPolicy(
        tick_size="1", position_side=PositionSide.LONG
    )
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price("0.01", policy)


def test_liquidation_fails_closed_when_tick_result_exceeds_working_precision():
    tick = Decimal("12345678901234567890123456789")
    policy = LiquidationPriceRoundingPolicy(
        tick_size=tick, position_side=PositionSide.LONG
    )
    with pytest.raises(FinancialRoundingError):
        round_liquidation_price(tick, policy)


def test_default_pnl_scales_are_immutable():
    with pytest.raises(TypeError):
        setitem(DEFAULT_PNL_SCALES, Market.CRYPTO, 2)
    assert DEFAULT_PNL_SCALES[Market.CRYPTO] == 8


def test_error_contracts_are_stable_for_invalid_boundary_policies():
    cases = [
        (lambda: round_pnl("1", object()), "policy must be PnLRoundingPolicy"),
        (
            lambda: round_funding("1", "0.01", object()),
            "policy must be FundingRoundingPolicy",
        ),
        (
            lambda: round_margin_ratio("0.5", object()),
            "policy must be MarginRatioRoundingPolicy",
        ),
        (
            lambda: round_liquidation_price("100", object()),
            "policy must be LiquidationPriceRoundingPolicy",
        ),
    ]
    for invoke, message in cases:
        with pytest.raises(FinancialRoundingError, match=f"^{message}$"):
            invoke()


def test_decimal_input_validation_error_message_is_stable():
    policy = PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="100")
    with pytest.raises(
        FinancialRoundingError, match="^pnl must be an exact Decimal value$"
    ):
        round_pnl(None, policy)
    with pytest.raises(
        FinancialRoundingError, match="^pnl must be an exact Decimal value$"
    ):
        round_pnl("not-a-number", policy)


@pytest.mark.parametrize("scale", [-1, 29, True, 1.0])
def test_scale_validation_rejects_invalid_scale_types_and_bounds(scale):
    with pytest.raises(FinancialRoundingError):
        _scale(scale)


@pytest.mark.parametrize("scale", [0, 8, 28])
def test_scale_validation_accepts_supported_scale_boundaries(scale):
    assert _scale(scale) == scale


def test_scale_validation_uses_stable_default_field_name():
    with pytest.raises(
        FinancialRoundingError,
        match="^scale must be an integer between 0 and 28$",
    ):
        _scale(-1)


def test_pnl_maximum_equality_is_permitted_but_exceeding_it_is_not():
    policy = PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="10")
    assert round_pnl("10", policy) == Decimal("10.00000000")


def test_funding_rate_equal_to_configured_maximum_is_permitted():
    policy = FundingRoundingPolicy(max_funding_rate="0.01")
    assert round_funding("-1.000000005", "-0.01", policy) == Decimal("-1.00000001")


def test_margin_ratio_compares_after_rounding_at_equality_boundaries():
    policy = MarginRatioRoundingPolicy(
        maintenance_margin_ratio="0.4", liquidation_ratio="0.6"
    )
    assert round_margin_ratio("0.399999999", policy) == Decimal("0.40000000")
    assert round_margin_ratio("0.599999995", policy) == Decimal("0.60000000")
    with pytest.raises(FinancialRiskBoundaryError):
        round_margin_ratio("0.400000005", policy)

