from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture"
CONTRACTS = ROOT / "contracts" / "futures"
TESTS = ROOT / "tests" / "contracts"

SOURCE_OF_TRUTH = (
    "architecture-invariants.md",
    "architecture-contract.md",
    "dependency-rules.md",
    "futures-responsibility-map.md",
    "ARCHITECTURE-MASTER-INDEX.md",
    "master-roadmap-and-governance.md",
    "project-state.md",
    "CHANGE-GUARD.md",
)

PHASE1_BOUNDARIES = (
    (("instrument",), "test_instrument_identity.py"),
    (("contract_specification",), "test_contract_specification.py"),
    (("settlement",), "test_settlement.py"),
    (("margin",), "test_margin.py"),
    (("leverage",), "test_leverage.py"),
    (("initial_margin",), "test_initial_margin.py"),
    (("maintenance_margin",), "test_maintenance_margin.py"),
    (("position_side", "position_mode"), "test_position_side_mode.py"),
    (("price_quantity",), "test_price_quantity.py"),
    (("funding",), "funding_contract_test.py"),
    (("pnl",), "pnl_contract_test.py"),
    (("exposure",), "exposure_contract_test.py"),
    (("liquidation",), "liquidation_contract_test.py"),
    (("liquidation_event",), "liquidation_event_contract_test.py"),
    (("accounting", "settlement_accounting"), "accounting_contract_test.py"),
)


def test_all_source_of_truth_documents_exist() -> None:
    missing = [name for name in SOURCE_OF_TRUTH if not (ARCH / name).is_file()]
    assert not missing, f"Missing Source-of-Truth documents: {missing}"


def test_phase1_has_production_and_test_boundaries() -> None:
    missing: list[str] = []
    for production_names, test_name in PHASE1_BOUNDARIES:
        for production_name in production_names:
            if not (CONTRACTS / f"{production_name}.py").is_file():
                missing.append(f"production:{production_name}.py")
        if not (TESTS / test_name).is_file():
            missing.append(f"test:{test_name}")
    assert not missing, f"Incomplete Phase 1 boundaries: {missing}"


def test_phase1_is_futures_only_and_gates_remain_strict() -> None:
    invariants = (ARCH / "architecture-invariants.md").read_text(encoding="utf-8")
    roadmap = (ARCH / "master-roadmap-and-governance.md").read_text(encoding="utf-8")
    change_guard = (ARCH / "CHANGE-GUARD.md").read_text(encoding="utf-8")

    assert "Operational Spot is forbidden." in invariants
    assert "CRYPTO" in invariants and "FOREX" in invariants and "GOLD" in invariants
    assert "Linear" in invariants and "Inverse" in invariants
    assert "G05" in roadmap and ">= 98%" in roadmap
    assert "G08" in roadmap and ">= 90%" in roadmap
    assert "G05 >= 98% and G08 >= 90%" in change_guard
    assert "weakening thresholds" in change_guard


def test_phase2_plus_remains_blocked_until_phase1_exit() -> None:
    state = (ARCH / "project-state.md").read_text(encoding="utf-8")
    assert "Phase 2+ production implementation remains blocked" in state
    assert "final completeness/evidence audit are CLOSED" in state
    assert "Next authorized action: G02 entry review/announcement." in state
