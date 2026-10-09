"""Canonical Futures accounting journal semantics.

Pure domain contracts only: immutable journal facts, balanced batches, and
deterministic accounting composition. No persistence, transport, exchange SDK,
order submission, or account mutation is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .instrument import FuturesInstrumentIdentity, Market


class AccountingValidationError(ValueError):
    """Raised when canonical accounting facts are invalid or ambiguous."""


class AccountingDirection(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


def _decimal(value: Decimal, field: str, *, positive: bool = False) -> Decimal:
    if type(value) is not Decimal:
        raise AccountingValidationError(f"{field} must be an exact Decimal value")
    if not value.is_finite():
        raise AccountingValidationError(f"{field} must be finite")
    if positive and value <= 0:
        raise AccountingValidationError(f"{field} must be greater than zero")
    return value


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AccountingValidationError(f"{field} must be non-empty")
    return value.strip()


def _asset(value: str, field: str) -> str:
    asset = _text(value, field).upper()
    if asset.startswith("SPOT") or not asset.replace("_", "").isalnum():
        raise AccountingValidationError(f"{field} is invalid")
    return asset


def _sequence(value: int, field: str) -> int:
    if type(value) is not int or value < 0:
        raise AccountingValidationError(f"{field} must be a non-negative integer")
    return value


@dataclass(frozen=True, slots=True)
class FuturesLedgerEntry:
    """One immutable positive journal fact."""

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

    def __post_init__(self) -> None:
        _text(self.entry_id, "entry_id")
        _text(self.causation_id, "causation_id")
        _sequence(self.state_version, "state_version")
        _sequence(self.sequence, "sequence")
        _text(self.account_id, "account_id")
        if not isinstance(self.instrument, FuturesInstrumentIdentity):
            raise AccountingValidationError(
                "instrument must be FuturesInstrumentIdentity"
            )
        _text(self.ledger_account, "ledger_account")
        _asset(self.asset, "asset")
        if not isinstance(self.direction, AccountingDirection):
            raise AccountingValidationError("direction must be DEBIT or CREDIT")
        _decimal(self.amount, "amount", positive=True)


@dataclass(frozen=True, slots=True)
class FuturesAccountingJournal:
    """Immutable balanced journal batch, balanced independently by asset."""

    journal_id: str
    entries: tuple[FuturesLedgerEntry, ...]

    def __post_init__(self) -> None:
        _text(self.journal_id, "journal_id")
        if not self.entries:
            raise AccountingValidationError("journal must contain entries")
        if any(not isinstance(entry, FuturesLedgerEntry) for entry in self.entries):
            raise AccountingValidationError("all entries must be FuturesLedgerEntry")

        seen: set[str] = set()
        prior_sequence = -1
        debit_totals: dict[str, Decimal] = {}
        credit_totals: dict[str, Decimal] = {}
        for entry in self.entries:
            if entry.entry_id in seen:
                raise AccountingValidationError("duplicate entry_id in journal")
            seen.add(entry.entry_id)
            if entry.sequence <= prior_sequence:
                raise AccountingValidationError(
                    "journal sequence must be strictly increasing"
                )
            prior_sequence = entry.sequence
            totals = (
                debit_totals
                if entry.direction is AccountingDirection.DEBIT
                else credit_totals
            )
            totals[entry.asset] = totals.get(entry.asset, Decimal("0")) + entry.amount

        for asset in set(debit_totals) | set(credit_totals):
            if debit_totals.get(asset, Decimal("0")) != credit_totals.get(
                asset, Decimal("0")
            ):
                raise AccountingValidationError(
                    f"journal is unbalanced for asset {asset}"
                )

    @property
    def asset_balances(self) -> dict[str, Decimal]:
        balances: dict[str, Decimal] = {}
        for asset in {entry.asset for entry in self.entries}:
            debit = sum(
                (
                    entry.amount
                    for entry in self.entries
                    if entry.asset == asset
                    and entry.direction is AccountingDirection.DEBIT
                ),
                start=Decimal("0"),
            )
            credit = sum(
                (
                    entry.amount
                    for entry in self.entries
                    if entry.asset == asset
                    and entry.direction is AccountingDirection.CREDIT
                ),
                start=Decimal("0"),
            )
            balances[asset] = debit - credit
        return balances


@dataclass(frozen=True, slots=True)
class FuturesAccountingSpecification:
    """Compose explicit validated financial facts into balanced journal facts."""

    market: Market
    instrument: FuturesInstrumentIdentity

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise AccountingValidationError("market must be a supported Futures market")
        if not isinstance(self.instrument, FuturesInstrumentIdentity):
            raise AccountingValidationError(
                "instrument must be FuturesInstrumentIdentity"
            )
        if self.instrument.market is not self.market:
            raise AccountingValidationError("market must match instrument")

    def _pair(
        self,
        *,
        journal_id: str,
        entry_prefix: str,
        causation_id: str,
        state_version: int,
        sequence: int,
        debit_account_id: str,
        credit_account_id: str,
        asset: str,
        amount: Decimal,
        debit_ledger: str,
        credit_ledger: str,
    ) -> FuturesAccountingJournal:
        value = _decimal(amount, "amount", positive=True)
        return FuturesAccountingJournal(
            journal_id=_text(journal_id, "journal_id"),
            entries=(
                FuturesLedgerEntry(
                    entry_id=f"{entry_prefix}:debit",
                    causation_id=_text(causation_id, "causation_id"),
                    state_version=_sequence(state_version, "state_version"),
                    sequence=_sequence(sequence, "sequence"),
                    account_id=_text(debit_account_id, "debit_account_id"),
                    instrument=self.instrument,
                    ledger_account=debit_ledger,
                    asset=_asset(asset, "asset"),
                    direction=AccountingDirection.DEBIT,
                    amount=value,
                ),
                FuturesLedgerEntry(
                    entry_id=f"{entry_prefix}:credit",
                    causation_id=_text(causation_id, "causation_id"),
                    state_version=_sequence(state_version, "state_version"),
                    sequence=_sequence(sequence + 1, "sequence"),
                    account_id=_text(credit_account_id, "credit_account_id"),
                    instrument=self.instrument,
                    ledger_account=credit_ledger,
                    asset=_asset(asset, "asset"),
                    direction=AccountingDirection.CREDIT,
                    amount=value,
                ),
            ),
        )

    def realized_pnl(
        self,
        *,
        journal_id: str,
        causation_id: str,
        state_version: int,
        sequence: int,
        account_id: str,
        pnl_amount: Decimal,
        denomination: str,
    ) -> FuturesAccountingJournal:
        """Account an explicit signed realized-PnL fact without recomputing it."""
        asset = _asset(denomination, "denomination")
        value = _decimal(pnl_amount, "pnl_amount")
        if value == 0:
            raise AccountingValidationError(
                "zero realized PnL is valid but creates no journal"
            )
        if value > 0:
            return self._pair(
                journal_id=journal_id,
                entry_prefix=f"{journal_id}:realized-profit",
                causation_id=causation_id,
                state_version=state_version,
                sequence=sequence,
                debit_account_id=account_id,
                credit_account_id=account_id,
                asset=asset,
                amount=value,
                debit_ledger="FUTURES_CASH_OR_RECEIVABLE",
                credit_ledger="FUTURES_REALIZED_PNL",
            )
        return self._pair(
            journal_id=journal_id,
            entry_prefix=f"{journal_id}:realized-loss",
            causation_id=causation_id,
            state_version=state_version,
            sequence=sequence,
            debit_account_id=account_id,
            credit_account_id=account_id,
            asset=asset,
            amount=-value,
            debit_ledger="FUTURES_REALIZED_PNL",
            credit_ledger="FUTURES_CASH_OR_RECEIVABLE",
        )

    def funding_transfer(
        self,
        *,
        journal_id: str,
        causation_id: str,
        state_version: int,
        sequence: int,
        payer_account_id: str,
        receiver_account_id: str,
        amount: Decimal,
        denomination: str,
    ) -> FuturesAccountingJournal:
        """Account an explicit payer-to-receiver funding fact."""
        payer = _text(payer_account_id, "payer_account_id")
        receiver = _text(receiver_account_id, "receiver_account_id")
        if payer == receiver:
            raise AccountingValidationError("payer and receiver must differ")
        return self._pair(
            journal_id=journal_id,
            entry_prefix=f"{journal_id}:funding",
            causation_id=causation_id,
            state_version=state_version,
            sequence=sequence,
            debit_account_id=payer,
            credit_account_id=receiver,
            asset=_asset(denomination, "denomination"),
            amount=amount,
            debit_ledger="FUTURES_FUNDING_EXPENSE",
            credit_ledger="FUTURES_FUNDING_RECEIVABLE",
        )
