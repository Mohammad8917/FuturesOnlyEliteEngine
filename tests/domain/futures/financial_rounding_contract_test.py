from decimal import Decimal, Inexact, ROUND_UP, localcontext
import pytest

from contracts.futures.instrument import Market
from contracts.futures.position_side import PositionSide
from domain.futures.financial_rounding import (
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
def test_pnl_uses_approved_market_scale_and_rounds_toward_zero(
    market, value, expected
):
    policy = PnLRoundingPolicy(market=market, max_reasonable_pnl="100")
    assert round_pnl(value, policy) == Decimal(expected)


def test_pnl_scale_override_is_explicit_and_validated():
    policy = PnLRoundingPolicy(
        market=Market.CRYPTO, max_reasonable_pnl="100", scale_override=3
    )
    assert round_pnl("1.2349", policy) == Decimal("1.234")
    with pytest.raises(FinancialRoundingError):
        PnLRoundingPolicy(market=Market.CRYPTO, max_reasonable_pnl="100", scale_override=True)


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
