"""G03 guard: every production Futures contract boundary has explicit test ownership."""

import ast
from pathlib import Path

PRODUCTION = Path("contracts/futures")
TESTS = Path("tests")

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

FORBIDDEN_TEST_MARKERS = {"skip", "skipif", "xfail", "importorskip"}


def _dotted_name(node: ast.AST) -> str | None:
    """Return a dotted attribute/name path for statically inspectable syntax."""
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _test_weakening_markers(path: Path) -> list[str]:
    """Find common pytest skip/xfail APIs without matching explanatory strings."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return [f"{path}: cannot inspect test source: {exc}"]

    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "pytest":
            for alias in node.names:
                if alias.name in FORBIDDEN_TEST_MARKERS:
                    offenders.append(
                        f"{path}:{node.lineno}: imports pytest.{alias.name}"
                    )
        elif isinstance(node, ast.Attribute):
            dotted = _dotted_name(node)
            if (
                dotted
                and dotted.startswith("pytest.")
                and node.attr in FORBIDDEN_TEST_MARKERS
            ):
                offenders.append(f"{path}:{node.lineno}: references {dotted}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_TEST_MARKERS:
            # Catch direct imports aliased to the same local identifier.
            if any(
                isinstance(parent, ast.ImportFrom)
                and parent.module == "pytest"
                and any(alias.name == node.id for alias in parent.names)
                for parent in ast.walk(tree)
            ):
                offenders.append(f"{path}:{node.lineno}: references pytest.{node.id}")
    return sorted(set(offenders))


def test_every_futures_contract_has_explicit_test_ownership():
    production = {
        path.stem for path in PRODUCTION.glob("*.py") if path.name != "__init__.py"
    }
    missing_mapping = sorted(production - TEST_OWNERS.keys())
    assert not missing_mapping, (
        f"G03 production contract lacks explicit test ownership: {missing_mapping}"
    )

    missing_files = sorted(
        {
            test_name
            for names in TEST_OWNERS.values()
            for test_name in names
            if not (TESTS / "contracts" / test_name).is_file()
        }
    )
    assert not missing_files, (
        f"G03 mapped contract test file is missing: {missing_files}"
    )


def test_all_test_sources_contain_no_pytest_skip_or_xfail_apis():
    offenders = sorted(
        offender
        for path in TESTS.rglob("*.py")
        for offender in _test_weakening_markers(path)
    )
    assert not offenders, (
        "G03 test weakening APIs are forbidden throughout the test tree:\n"
        + "\n".join(offenders)
    )
