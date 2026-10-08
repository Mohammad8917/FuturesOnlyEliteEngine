"""Canonical Futures position-mode vocabulary and side semantics."""

from __future__ import annotations

import typing

from dataclasses import dataclass
from enum import StrEnum

from .position_side import PositionSide


class PositionModeValidationError(ValueError):
    """Raised when a Futures position-mode value is invalid or ambiguous."""


class PositionMode(StrEnum):
    ONE_WAY = "ONE_WAY"
    HEDGE = "HEDGE"


@dataclass(frozen=True, slots=True)
class FuturesPositionModeSpecification:
    """Immutable contract for position-mode interpretation.

    ONE_WAY has one net position side at a time.
    HEDGE permits independently addressed LONG and SHORT positions.

    This contract does not infer mode from exchange/account state and does
    not perform order submission, position mutation, or exchange mapping.
    """

    mode: PositionMode

    def __post_init__(self) -> None:
        if not isinstance(typing.cast(object, self.mode), PositionMode):
            raise PositionModeValidationError(
                "mode must be ONE_WAY or HEDGE"
            )

    @property
    def allowed_sides(self) -> tuple[PositionSide, ...]:
        return (PositionSide.LONG, PositionSide.SHORT)

    @property
    def supports_independent_long_short(self) -> bool:
        """Whether LONG and SHORT positions may coexist independently."""
        return self.mode is PositionMode.HEDGE

    def accepts(self, side: PositionSide) -> bool:
        if not isinstance(typing.cast(object, side), PositionSide):
            raise PositionModeValidationError(
                "position side must be LONG or SHORT"
            )
        return side in self.allowed_sides
