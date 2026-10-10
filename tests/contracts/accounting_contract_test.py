"""Contract tests for canonical Futures accounting semantics."""

from decimal import Decimal

import pytest

from contracts.futures.accounting import (
    AccountingDirection,
    AccountingValidationError,
    FuturesAccountingJournal,
    FuturesAccountingSpecification,
    FuturesLedgerEntry,
)
from contracts.futures.instrument import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    Market,
)
from contracts.futures.settlement import FuturesSettlementSpecification, SettlementUnit
from contracts.futures.settlement_accounting import (
    FuturesSettlementAccountingSpecification,
)


def instrument(family=ContractFamily.LINEAR):
    symbol = CanonicalFuturesSymbol("BTC", "USD", family, "USD")
    return FuturesInstrumentIdentity.create(
        market=Market.CRYPTO,
        symbol=symbol,
        margin_asset="USD",
    )


def accounting(family=ContractFamily.LINEAR):
    inst = instrument(family)
    return FuturesAccountingSpecification(Market.CRYPTO, inst)


@pytest.mark.parametrize("family", list(ContractFamily))
def test_realized_pnl_accounts_signed_fact_without_recomputing(family):
    denomination = "USD" if family is ContractFamily.LINEAR else "BTC"
    positive = accounting(family).realized_pnl(
        journal_id="j-profit",
        causation_id="pnl-1",
        state_version=1,
        sequence=10,
        account_id="acct",
        pnl_amount=Decimal("12.50"),
        denomination=denomination,
    )
    assert positive.asset_balances == {denomination: Decimal("0")}
    assert positive.entries[0].direction is AccountingDirection.DEBIT
    assert positive.entries[1].direction is AccountingDirection.CREDIT

    negative = accounting(family).realized_pnl(
        journal_id="j-loss",
        causation_id="pnl-2",
        state_version=2,
        sequence=20,
        account_id="acct",
        pnl_amount=Decimal("-7.25"),
        denomination=denomination,
    )
    assert negative.asset_balances == {denomination: Decimal("0")}
    assert negative.entries[0].ledger_account == "FUTURES_REALIZED_PNL"


def test_zero_realized_pnl_is_not_silently_recorded():
    with pytest.raises(AccountingValidationError):
        accounting().realized_pnl(
            journal_id="j-zero",
            causation_id="pnl-zero",
            state_version=1,
            sequence=1,
            account_id="acct",
            pnl_amount=Decimal("0"),
            denomination="USD",
        )


def test_funding_transfer_is_balanced_across_distinct_accounts():
    journal = accounting().funding_transfer(
        journal_id="fund-1",
        causation_id="funding-event-1",
        state_version=4,
        sequence=30,
        payer_account_id="payer",
        receiver_account_id="receiver",
        amount=Decimal("1.125"),
        denomination="USD",
    )
    assert journal.asset_balances == {"USD": Decimal("0")}
    assert journal.entries[0].account_id == "payer"
    assert journal.entries[1].account_id == "receiver"


def test_journal_rejects_empty_batch():
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("empty", ())


def test_journal_snapshots_mutable_input_and_normalizes_asset_identity():
    debit = FuturesLedgerEntry(
        entry_id=" debit ",
        causation_id=" cause ",
        state_version=1,
        sequence=1,
        account_id=" account ",
        instrument=instrument(),
        ledger_account=" debit-ledger ",
        asset=" usd ",
        direction=AccountingDirection.DEBIT,
        amount=Decimal("1"),
    )
    credit = FuturesLedgerEntry(
        entry_id="credit",
        causation_id="cause",
        state_version=1,
        sequence=2,
        account_id="account",
        instrument=instrument(),
        ledger_account="credit-ledger",
        asset="USD",
        direction=AccountingDirection.CREDIT,
        amount=Decimal("1"),
    )
    supplied_entries = [debit, credit]
    journal = FuturesAccountingJournal(" journal ", supplied_entries)

    supplied_entries.clear()

    assert journal.journal_id == "journal"
    assert isinstance(journal.entries, tuple)
    assert journal.entries == (debit, credit)
    assert journal.entries[0].entry_id == "debit"
    assert journal.entries[0].asset == "USD"
    assert journal.asset_balances == {"USD": Decimal("0")}


def test_journal_rejects_non_iterable_entries():
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("invalid", None)


def test_journal_rejects_duplicate_ids_and_unbalanced_assets():
    entry = FuturesLedgerEntry(
        entry_id="same",
        causation_id="cause",
        state_version=1,
        sequence=1,
        account_id="acct",
        instrument=instrument(),
        ledger_account="A",
        asset="USD",
        direction=AccountingDirection.DEBIT,
        amount=Decimal("1"),
    )
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("dup", (entry, entry))

    credit = FuturesLedgerEntry(
        entry_id="other",
        causation_id="cause",
        state_version=1,
        sequence=2,
        account_id="acct",
        instrument=instrument(),
        ledger_account="B",
        asset="EUR",
        direction=AccountingDirection.CREDIT,
        amount=Decimal("1"),
    )
    with pytest.raises(AccountingValidationError):
        FuturesAccountingJournal("unbalanced", (entry, credit))


@pytest.mark.parametrize(
    "field,value",
    [
        ("pnl_amount", True),
        ("pnl_amount", 1.0),
        ("pnl_amount", Decimal("NaN")),
        ("pnl_amount", Decimal("0")),
    ],
)
def test_financial_boundaries_reject_bool_float_and_invalid_decimal(field, value):
    kwargs = dict(
        journal_id="j-invalid",
        causation_id="cause",
        state_version=1,
        sequence=1,
        account_id="acct",
        pnl_amount=Decimal("1"),
        denomination="USD",
    )
    kwargs[field] = value
    with pytest.raises(AccountingValidationError):
        accounting().realized_pnl(**kwargs)


def test_linear_and_inverse_remain_explicit_in_journal_identity():
    linear = accounting(ContractFamily.LINEAR).realized_pnl(
        journal_id="linear",
        causation_id="cause-l",
        state_version=1,
        sequence=1,
        account_id="acct",
        pnl_amount=Decimal("1"),
        denomination="USD",
    )
    inverse = accounting(ContractFamily.INVERSE).realized_pnl(
        journal_id="inverse",
        causation_id="cause-i",
        state_version=1,
        sequence=1,
        account_id="acct",
        pnl_amount=Decimal("1"),
        denomination="BTC",
    )
    assert linear.entries[0].instrument.symbol.contract_family is ContractFamily.LINEAR
    assert (
        inverse.entries[0].instrument.symbol.contract_family is ContractFamily.INVERSE
    )


def settlement_spec(source_asset):
    inst = instrument()
    return FuturesSettlementSpecification(
        market=Market.CRYPTO,
        symbol=inst.symbol,
        settlement_unit=SettlementUnit.ASSET,
        settlement_asset="USD",
        source_asset=source_asset,
        conversion_rate=Decimal("100000") if source_asset != "USD" else None,
    )


def test_same_asset_settlement_preserves_amount_exactly():
    inst = instrument()
    journal = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, settlement_spec("USD")
    ).transfer(
        journal_id="set-1",
        causation_id="settle-1",
        state_version=3,
        sequence=50,
        account_id="acct",
        settlement_counterparty_account_id="settlement",
        source_amount=Decimal("25.125"),
        source_asset="USD",
    )
    assert journal.asset_balances == {"USD": Decimal("0")}
    assert [e.amount for e in journal.entries] == [
        Decimal("25.125"),
        Decimal("25.125"),
    ]


def test_cross_asset_settlement_has_explicit_balanced_legs():
    inst = instrument()
    journal = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, settlement_spec("BTC")
    ).transfer(
        journal_id="set-2",
        causation_id="settle-2",
        state_version=4,
        sequence=60,
        account_id="acct",
        settlement_counterparty_account_id="settlement",
        source_amount=Decimal("0.001"),
        source_asset="BTC",
    )
    assert journal.asset_balances == {"BTC": Decimal("0"), "USD": Decimal("0")}
    assert journal.entries[2].amount == Decimal("100")


def test_settlement_rejects_mismatched_source_and_same_account_counterparty():
    inst = instrument()
    spec = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, settlement_spec("BTC")
    )
    with pytest.raises(AccountingValidationError):
        spec.transfer(
            journal_id="bad-source",
            causation_id="cause",
            state_version=1,
            sequence=1,
            account_id="acct",
            settlement_counterparty_account_id="settlement",
            source_amount=Decimal("1"),
            source_asset="ETH",
        )
    with pytest.raises(AccountingValidationError):
        spec.transfer(
            journal_id="bad-account",
            causation_id="cause",
            state_version=1,
            sequence=1,
            account_id="acct",
            settlement_counterparty_account_id="acct",
            source_amount=Decimal("1"),
            source_asset="BTC",
        )


def test_settlement_boundary_rejects_non_decimal_source_amount():
    inst = instrument()
    spec = FuturesSettlementAccountingSpecification(
        Market.CRYPTO, inst, settlement_spec("USD")
    )
    with pytest.raises(AccountingValidationError):
        spec.transfer(
            journal_id="bad",
            causation_id="cause",
            state_version=1,
            sequence=1,
            account_id="acct",
            settlement_counterparty_account_id="settlement",
            source_amount=1.0,
            source_asset="USD",
        )
