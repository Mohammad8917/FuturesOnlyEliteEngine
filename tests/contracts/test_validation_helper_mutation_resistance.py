"""Direct fail-closed tests for shared numeric, identity, and time validators.

These helpers implement contract-level safety boundaries reused by public
Futures specifications. Their error diagnostics are part of the fail-closed
contract and are tested so mutation changes cannot silently erase them.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from contracts.futures.accounting import (
    AccountingValidationError,
    _asset as accounting_asset,
    _decimal as accounting_decimal,
    _sequence as accounting_sequence,
    _text as accounting_text,
)
from contracts.futures.contract_specification import (
    ContractSpecificationValidationError,
    _decimal as contract_decimal,
    _positive_decimal as contract_positive_decimal,
)
from contracts.futures.exposure import (
    ExposureValidationError,
    _positive_decimal as exposure_positive_decimal,
    _utc as exposure_utc,
)
from contracts.futures.funding import (
    FundingValidationError,
    _decimal as funding_decimal,
    _utc as funding_utc,
)
from contracts.futures.initial_margin import (
    InitialMarginValidationError,
    _asset as initial_margin_asset,
    _positive_decimal as initial_margin_positive_decimal,
)
from contracts.futures.instrument import (
    InstrumentValidationError,
    _asset as instrument_asset,
)
from contracts.futures.leverage import (
    LeverageValidationError,
    _positive_decimal as leverage_positive_decimal,
)
from contracts.futures.liquidation import (
    LiquidationValidationError,
    _positive_decimal as liquidation_positive_decimal,
)
from contracts.futures.liquidation_event import (
    LiquidationEventValidationError,
    _identifier as liquidation_event_identifier,
    _non_negative_integer as liquidation_event_non_negative_integer,
    _positive_decimal as liquidation_event_positive_decimal,
    _utc as liquidation_event_utc,
)
from contracts.futures.maintenance_margin import (
    MaintenanceMarginValidationError,
    _asset as maintenance_margin_asset,
    _positive_decimal as maintenance_margin_positive_decimal,
)
from contracts.futures.margin import (
    MarginValidationError,
    _asset as margin_asset,
    _positive_decimal as margin_positive_decimal,
)
from contracts.futures.pnl import (
    PnLValidationError,
    _positive_decimal as pnl_positive_decimal,
    _utc as pnl_utc,
)
from contracts.futures.position_side import (
    PositionSide,
    PositionSideValidationError,
    validate_position_side,
)
from contracts.futures.price_quantity import (
    PriceQuantityValidationError,
    _positive_decimal as price_quantity_positive_decimal,
)
from contracts.futures.settlement import (
    SettlementValidationError,
    _asset as settlement_asset,
    _positive_decimal as settlement_positive_decimal,
)
from contracts.futures.settlement_accounting import (
    _decimal as settlement_accounting_decimal,
    _sequence as settlement_accounting_sequence,
    _text as settlement_accounting_text,
)

UTC = timezone.utc

POSITIVE_DECIMAL_HELPERS = [
    (contract_positive_decimal, ContractSpecificationValidationError),
    (exposure_positive_decimal, ExposureValidationError),
    (initial_margin_positive_decimal, InitialMarginValidationError),
    (leverage_positive_decimal, LeverageValidationError),
    (liquidation_positive_decimal, LiquidationValidationError),
    (liquidation_event_positive_decimal, LiquidationEventValidationError),
    (maintenance_margin_positive_decimal, MaintenanceMarginValidationError),
    (margin_positive_decimal, MarginValidationError),
    (pnl_positive_decimal, PnLValidationError),
    (price_quantity_positive_decimal, PriceQuantityValidationError),
    (settlement_positive_decimal, SettlementValidationError),
]

ASSET_HELPERS = [
    (accounting_asset, AccountingValidationError),
    (initial_margin_asset, InitialMarginValidationError),
    (instrument_asset, InstrumentValidationError),
    (maintenance_margin_asset, MaintenanceMarginValidationError),
    (margin_asset, MarginValidationError),
    (settlement_asset, SettlementValidationError),
]

UTC_HELPERS = [
    (exposure_utc, ExposureValidationError),
    (funding_utc, FundingValidationError),
    (liquidation_event_utc, LiquidationEventValidationError),
    (pnl_utc, PnLValidationError),
]

DECIMAL_HELPERS = [
    (accounting_decimal, AccountingValidationError),
    (contract_decimal, ContractSpecificationValidationError),
    (funding_decimal, FundingValidationError),
    (settlement_accounting_decimal, AccountingValidationError),
]

SEQUENCE_HELPERS = [
    (accounting_sequence, AccountingValidationError),
    (settlement_accounting_sequence, AccountingValidationError),
]

TEXT_HELPERS = [
    (accounting_text, AccountingValidationError),
    (settlement_accounting_text, AccountingValidationError),
]


@pytest.mark.parametrize(("helper", "error"), POSITIVE_DECIMAL_HELPERS)
def test_positive_decimal_helpers_reject_binary_float_with_field_error(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(0.1, "quantity")  # type: ignore[operator]
    assert "quantity" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), POSITIVE_DECIMAL_HELPERS)
def test_positive_decimal_helpers_report_malformed_numeric_text(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper("not-a-decimal", "quantity")  # type: ignore[operator]
    assert "quantity" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), POSITIVE_DECIMAL_HELPERS)
def test_positive_decimal_helpers_reject_zero_with_field_error(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(Decimal("0"), "quantity")  # type: ignore[operator]
    assert "quantity" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), POSITIVE_DECIMAL_HELPERS)
def test_positive_decimal_helpers_reject_non_finite_decimal(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(Decimal("NaN"), "quantity")  # type: ignore[operator]
    assert "quantity" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), ASSET_HELPERS)
def test_asset_helpers_normalize_and_reject_invalid_types_and_spot(
    helper: object,
    error: type[ValueError],
) -> None:
    assert helper(" usdt ", "margin_asset") == "USDT"  # type: ignore[operator]

    with pytest.raises(error) as caught:
        helper(object(), "margin_asset")  # type: ignore[operator]
    assert "margin_asset" in str(caught.value)

    with pytest.raises(error) as caught:
        helper("SPOTUSDT", "margin_asset")  # type: ignore[operator]
    assert "margin_asset" in str(caught.value)

    with pytest.raises(error) as caught:
        helper("USDT!", "margin_asset")  # type: ignore[operator]
    assert "margin_asset" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), UTC_HELPERS)
def test_utc_helpers_reject_non_datetime_runtime_values(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(object(), "observed_at")  # type: ignore[operator]
    assert "observed_at" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), UTC_HELPERS)
def test_utc_helpers_reject_naive_and_non_utc_datetimes(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(datetime(2026, 1, 1, 12), "observed_at")  # type: ignore[operator]
    assert "observed_at" in str(caught.value)

    non_utc = datetime(
        2026,
        1,
        1,
        13,
        tzinfo=timezone(timedelta(hours=1)),
    )
    with pytest.raises(error) as caught:
        helper(non_utc, "observed_at")  # type: ignore[operator]
    assert "observed_at" in str(caught.value)

    valid_utc = datetime(2026, 1, 1, 12, tzinfo=UTC)
    assert helper(valid_utc, "observed_at") == valid_utc  # type: ignore[operator]


@pytest.mark.parametrize(("helper", "error"), DECIMAL_HELPERS)
def test_decimal_helpers_reject_binary_float_with_field_error(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(0.1, "amount")  # type: ignore[operator]
    assert "amount" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), DECIMAL_HELPERS)
def test_decimal_helpers_report_malformed_numeric_text(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper("not-a-decimal", "amount")  # type: ignore[operator]
    assert "amount" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), DECIMAL_HELPERS)
def test_decimal_helpers_reject_non_finite_values_with_field_error(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper(Decimal("NaN"), "amount")  # type: ignore[operator]
    assert "amount" in str(caught.value)


def test_zero_funding_rate_and_non_positive_accounting_semantics_are_explicit() -> None:
    assert funding_decimal(Decimal("0"), "funding_rate") == Decimal("0")
    assert accounting_decimal(Decimal("0"), "balance") == Decimal("0")
    assert contract_decimal(Decimal("0"), "quantity") == Decimal("0")
    with pytest.raises(AccountingValidationError) as caught:
        settlement_accounting_decimal(Decimal("0"), "settlement_amount")
    assert "settlement_amount" in str(caught.value)


@pytest.mark.parametrize(("helper", "error"), SEQUENCE_HELPERS)
def test_sequence_helpers_reject_float_bool_and_negative_values(
    helper: object,
    error: type[ValueError],
) -> None:
    for invalid in (1.5, True, -1):
        with pytest.raises(error) as caught:
            helper(invalid, "sequence")  # type: ignore[operator]
        assert "sequence" in str(caught.value)
    assert helper(0, "sequence") == 0  # type: ignore[operator]


@pytest.mark.parametrize(("helper", "error"), TEXT_HELPERS)
def test_text_helpers_reject_empty_text_and_trim_valid_values(
    helper: object,
    error: type[ValueError],
) -> None:
    with pytest.raises(error) as caught:
        helper("   ", "account_id")  # type: ignore[operator]
    assert "account_id" in str(caught.value)
    assert helper(" account-1 ", "account_id") == "account-1"  # type: ignore[operator]


@pytest.mark.parametrize(
    ("helper", "error"),
    [
        (accounting_asset, AccountingValidationError),
        (initial_margin_asset, InitialMarginValidationError),
        (maintenance_margin_asset, MaintenanceMarginValidationError),
        (margin_asset, MarginValidationError),
        (settlement_asset, SettlementValidationError),
    ],
)
def test_asset_helpers_preserve_supported_underscore_symbols(
    helper: object,
    error: type[ValueError],
) -> None:
    assert helper("USD_T", "asset") == "USD_T"  # type: ignore[operator]


def test_liquidation_identifier_has_meaningful_fail_closed_diagnostic() -> None:
    with pytest.raises(LiquidationEventValidationError) as caught:
        liquidation_event_identifier(" ", "event_id")
    assert "event_id" in str(caught.value)
    assert liquidation_event_identifier(" event-1 ", "event_id") == "event-1"


def test_liquidation_non_negative_integer_rejects_positive_float() -> None:
    with pytest.raises(LiquidationEventValidationError) as caught:
        liquidation_event_non_negative_integer(1.5, "sequence")  # type: ignore[arg-type]
    assert "sequence" in str(caught.value)
    assert liquidation_event_non_negative_integer(0, "sequence") == 0


def test_position_side_validator_preserves_meaningful_error_message() -> None:
    with pytest.raises(PositionSideValidationError) as caught:
        validate_position_side("LONG")  # type: ignore[arg-type]
    assert str(caught.value) == "position side must be LONG or SHORT"
    assert validate_position_side(PositionSide.LONG) is PositionSide.LONG
