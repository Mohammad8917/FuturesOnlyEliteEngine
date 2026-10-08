"""Contract tests for Futures position side and position mode."""

import pytest

from contracts.futures import (
    FuturesPositionModeSpecification,
    PositionMode,
    PositionModeValidationError,
    PositionSide,
    PositionSideValidationError,
    validate_position_side,
)


@pytest.mark.parametrize("side", [PositionSide.LONG, PositionSide.SHORT])
def test_position_side_is_explicit_and_validated(side: PositionSide) -> None:
    assert validate_position_side(side) is side


@pytest.mark.parametrize("value", ["LONG", "SHORT", "BOTH", True, None])
def test_invalid_position_side_fails_closed(value: object) -> None:
    with pytest.raises(PositionSideValidationError):
        validate_position_side(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("mode", [PositionMode.ONE_WAY, PositionMode.HEDGE])
def test_position_mode_is_explicit_and_immutable(mode: PositionMode) -> None:
    spec = FuturesPositionModeSpecification(mode)
    assert spec.mode is mode
    assert spec.allowed_sides == (PositionSide.LONG, PositionSide.SHORT)
    assert spec.supports_independent_long_short is (mode is PositionMode.HEDGE)
    with pytest.raises((AttributeError, TypeError)):
        setattr(spec, "mode", PositionMode.HEDGE)


@pytest.mark.parametrize("value", ["ONE_WAY", "HEDGE", "NET", True, None])
def test_invalid_position_mode_fails_closed(value: object) -> None:
    with pytest.raises(PositionModeValidationError):
        FuturesPositionModeSpecification(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("mode", [PositionMode.ONE_WAY, PositionMode.HEDGE])
@pytest.mark.parametrize("side", [PositionSide.LONG, PositionSide.SHORT])
def test_supported_modes_accept_explicit_sides(
    mode: PositionMode, side: PositionSide
) -> None:
    assert FuturesPositionModeSpecification(mode).accepts(side)


def test_position_mode_does_not_infer_exchange_or_account_state() -> None:
    spec = FuturesPositionModeSpecification(PositionMode.ONE_WAY)
    assert spec.mode is PositionMode.ONE_WAY
    assert spec.accepts(PositionSide.LONG)
    assert spec.accepts(PositionSide.SHORT)
