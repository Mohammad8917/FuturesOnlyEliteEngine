"""Canonical Futures position-side vocabulary and validation."""

from __future__ import annotations

import typing

from enum import StrEnum


class PositionSideValidationError(ValueError):
    """Raised when a Futures position-side value is invalid or ambiguous."""


class PositionSide(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


def validate_position_side(value: PositionSide) -> PositionSide:
    if not isinstance(typing.cast(object, value), PositionSide):
        raise PositionSideValidationError("position side must be LONG or SHORT")
    return value
