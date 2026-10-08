"""Canonical Futures settlement-accounting semantics.

This boundary composes an explicit source amount and an already-validated
Futures settlement specification into balanced journal facts. It performs no
rate discovery, persistence, transport, exchange calls, or account mutation.
"""

from __future__ import annotations

import typing

from dataclasses import dataclass
from decimal import Decimal

from .accounting import (
    AccountingDirection,
    AccountingValidationError,
    FuturesAccountingJournal,
    FuturesLedgerEntry,
)
from .instrument import FuturesInstrumentIdentity, Market
from .settlement import FuturesSettlementSpecification


def _text(value: str, field: str) -> str:
    if not isinstance(typing.cast(object, value), str) or not value.strip():
        raise AccountingValidationError(f"{field} must be non-empty")
    return value.strip()


def _decimal(value: Decimal, field: str) -> Decimal:
    if isinstance(typing.cast(object, value), bool) or not isinstance(typing.cast(object, value), Decimal):
        raise AccountingValidationError(f"{field} must be an exact Decimal value")
    if not value.is_finite() or value <= 0:
        raise AccountingValidationError(f"{field} must be finite and greater than zero")
    return value


def _sequence(value: int, field: str) -> int:
    if isinstance(typing.cast(object, value), bool) or not isinstance(typing.cast(object, value), int) or value < 0:
        raise AccountingValidationError(f"{field} must be a non-negative integer")
    return value


@dataclass(frozen=True, slots=True)
class FuturesSettlementAccountingSpecification:
    """Immutable settlement-transfer accounting boundary."""

    market: Market
    instrument: FuturesInstrumentIdentity
    settlement: FuturesSettlementSpecification

    def __post_init__(self) -> None:
        if not isinstance(typing.cast(object, self.market), Market):
            raise AccountingValidationError("market must be a supported Futures market")
        if not isinstance(typing.cast(object, self.instrument), FuturesInstrumentIdentity):
            raise AccountingValidationError("instrument must be FuturesInstrumentIdentity")
        if self.instrument.market is not self.market:
            raise AccountingValidationError("market must match instrument")
        if not isinstance(typing.cast(object, self.settlement), FuturesSettlementSpecification):
            raise AccountingValidationError(
                "settlement must be FuturesSettlementSpecification"
            )
        if self.settlement.market is not self.market:
            raise AccountingValidationError("settlement market must match")
        if self.settlement.symbol != self.instrument.symbol:
            raise AccountingValidationError("settlement symbol must match instrument")

    def transfer(
        self,
        *,
        journal_id: str,
        causation_id: str,
        state_version: int,
        sequence: int,
        account_id: str,
        settlement_counterparty_account_id: str,
        source_amount: Decimal,
        source_asset: str,
    ) -> FuturesAccountingJournal:
        """Create a balanced same-asset or explicit conversion settlement journal."""
        account = _text(account_id, "account_id")
        counterparty = _text(
            settlement_counterparty_account_id,
            "settlement_counterparty_account_id",
        )
        if account == counterparty:
            raise AccountingValidationError(
                "settlement counterparty must be distinct"
            )
        _sequence(state_version, "state_version")
        start = _sequence(sequence, "sequence")
        source_value = _decimal(source_amount, "source_amount")
        source = _text(source_asset, "source_asset").upper()

        if source != self.settlement.source_asset:
            raise AccountingValidationError(
                "source_asset must match the settlement specification"
            )

        destination_value = self.settlement.settle_amount(source_value)
        destination = self.settlement.settlement_asset

        if source == destination:
            if destination_value != source_value:
                raise AccountingValidationError(
                    "same-asset settlement must preserve amount exactly"
                )
            entries = (
                FuturesLedgerEntry(
                    entry_id=f"{journal_id}:settlement:debit",
                    causation_id=causation_id,
                    state_version=state_version,
                    sequence=start,
                    account_id=account,
                    instrument=self.instrument,
                    ledger_account="FUTURES_SETTLEMENT_RECEIVABLE",
                    asset=destination,
                    direction=AccountingDirection.DEBIT,
                    amount=destination_value,
                ),
                FuturesLedgerEntry(
                    entry_id=f"{journal_id}:settlement:credit",
                    causation_id=causation_id,
                    state_version=state_version,
                    sequence=start + 1,
                    account_id=counterparty,
                    instrument=self.instrument,
                    ledger_account="FUTURES_SETTLEMENT_SOURCE",
                    asset=destination,
                    direction=AccountingDirection.CREDIT,
                    amount=destination_value,
                ),
            )
        else:
            # Conversion is represented by two independently balanced asset legs.
            # The clearing account is a domain ledger fact, not an account mutation.
            entries = (
                FuturesLedgerEntry(
                    entry_id=f"{journal_id}:settlement:source-credit",
                    causation_id=causation_id,
                    state_version=state_version,
                    sequence=start,
                    account_id=counterparty,
                    instrument=self.instrument,
                    ledger_account="FUTURES_SETTLEMENT_SOURCE",
                    asset=source,
                    direction=AccountingDirection.CREDIT,
                    amount=source_value,
                ),
                FuturesLedgerEntry(
                    entry_id=f"{journal_id}:settlement:source-debit",
                    causation_id=causation_id,
                    state_version=state_version,
                    sequence=start + 1,
                    account_id=account,
                    instrument=self.instrument,
                    ledger_account="FUTURES_SETTLEMENT_CONVERSION_CLEARING",
                    asset=source,
                    direction=AccountingDirection.DEBIT,
                    amount=source_value,
                ),
                FuturesLedgerEntry(
                    entry_id=f"{journal_id}:settlement:destination-debit",
                    causation_id=causation_id,
                    state_version=state_version,
                    sequence=start + 2,
                    account_id=account,
                    instrument=self.instrument,
                    ledger_account="FUTURES_SETTLEMENT_RECEIVABLE",
                    asset=destination,
                    direction=AccountingDirection.DEBIT,
                    amount=destination_value,
                ),
                FuturesLedgerEntry(
                    entry_id=f"{journal_id}:settlement:destination-credit",
                    causation_id=causation_id,
                    state_version=state_version,
                    sequence=start + 3,
                    account_id=counterparty,
                    instrument=self.instrument,
                    ledger_account="FUTURES_SETTLEMENT_CONVERSION_CLEARING",
                    asset=destination,
                    direction=AccountingDirection.CREDIT,
                    amount=destination_value,
                ),
            )

        return FuturesAccountingJournal(
            journal_id=_text(journal_id, "journal_id"),
            entries=entries,
        )
