"""G03 guard: every production Futures contract boundary has explicit test ownership."""

from pathlib import Path

PRODUCTION = Path("contracts/futures")
TESTS = Path("tests/contracts")

# Some boundaries are intentionally tested together because their semantics are
# inseparable at this phase (for example position side + mode and accounting +
# settlement-accounting). This is explicit ownership, not filename heuristics.
TEST_OWNERS = {
    "instrument": {"test_instrument_identity.py"},
    "contract_specification": {"test_contract_specification.py"},
    "settlement": {"test_settlement.py"},
    "margin": {"test_margin.py"},
    "leverage": {"test_leverage.py"},
    "initial_margin": {"test_initial_margin.py"},
    "maintenance_margin": {"test_maintenance_margin.py"},
    "position_side": {"test_position_side_mode.py"},
    "position_mode": {"test_position_side_mode.py"},
    "price_quantity": {"test_price_quantity.py"},
    "funding": {"funding_contract_test.py"},
    "pnl": {"pnl_contract_test.py"},
    "exposure": {"exposure_contract_test.py"},
    "liquidation": {"liquidation_contract_test.py"},
    "liquidation_event": {"liquidation_event_contract_test.py"},
    "accounting": {"accounting_contract_test.py"},
    "settlement_accounting": {"accounting_contract_test.py"},
}


def test_every_futures_contract_has_explicit_test_ownership():
    production = {
        path.stem
        for path in PRODUCTION.glob("*.py")
        if path.name != "__init__.py"
    }
    missing_mapping: list[str] = sorted(production - TEST_OWNERS.keys())
    assert not missing_mapping, (
        "G03 production contract lacks explicit test ownership: "
        f"{missing_mapping}"
    )

    missing_files: list[str] = sorted(
        {
            test_name
            for names in TEST_OWNERS.values()
            for test_name in names
            if not (TESTS / test_name).is_file()
        }
    )
    assert not missing_files, (
        "G03 mapped contract test file is missing: "
        f"{missing_files}"
    )


def test_contract_test_tree_contains_no_explicit_skip_or_xfail_markers():
    offenders = []
    for path in TESTS.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if (
            "pytest.skip(" in text
            or "pytest.mark.skip" in text
            or "pytest.mark.xfail" in text
        ):
            offenders.append(str(path))
    assert not offenders, f"G03 test weakening markers detected: {offenders}"
