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
    """Find pytest skip/xfail APIs, including common import and module aliases."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return [f"{path}: cannot inspect test source: {exc}"]

    offenders: list[str] = []
    pytest_aliases = {"pytest"}
    mark_aliases = {"pytest.mark"}
    imported_marker_aliases: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pytest":
                    pytest_aliases.add(alias.asname or "pytest")
        elif isinstance(node, ast.ImportFrom) and node.module == "pytest":
            for alias in node.names:
                local_name = alias.asname or alias.name
                if alias.name in FORBIDDEN_TEST_MARKERS:
                    offenders.append(
                        f"{path}:{node.lineno}: imports pytest.{alias.name}"
                    )
                    imported_marker_aliases.add(local_name)
                elif alias.name == "mark":
                    mark_aliases.add(local_name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            dotted = _dotted_name(node)
            if dotted is None:
                continue
            root = dotted.split(".", maxsplit=1)[0]
            is_pytest_module_api = (
                root in pytest_aliases and node.attr in FORBIDDEN_TEST_MARKERS
            )
            is_pytest_mark_api = (
                root in mark_aliases and node.attr in FORBIDDEN_TEST_MARKERS
            )
            if is_pytest_module_api or is_pytest_mark_api:
                offenders.append(f"{path}:{node.lineno}: references {dotted}")
        elif isinstance(node, ast.Name) and node.id in imported_marker_aliases:
            offenders.append(
                f"{path}:{node.lineno}: references imported pytest marker "
                f"alias {node.id}"
            )
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            # Also catch getattr(pytest_alias, "skip") and
            # getattr(pytest_mark_alias, "skipif") style indirection.
            if node.func.id == "getattr" and len(node.args) >= 2:
                target = node.args[0]
                marker = node.args[1]
                target_path = _dotted_name(target)
                is_pytest_marker_target = (
                    isinstance(target, ast.Name)
                    and target.id in pytest_aliases | mark_aliases
                ) or (
                    target_path is not None
                    and (
                        target_path in mark_aliases
                        or target_path in pytest_aliases
                        or (
                            target_path.split(".", maxsplit=1)[0] in pytest_aliases
                            and target_path.split(".", maxsplit=1)[1:] == ["mark"]
                        )
                    )
                )
                if (
                    is_pytest_marker_target
                    and isinstance(marker, ast.Constant)
                    and marker.value in FORBIDDEN_TEST_MARKERS
                ):
                    offenders.append(
                        f"{path}:{node.lineno}: dynamically accesses pytest "
                        f"marker {marker.value}"
                    )
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


def test_dynamic_getattr_cannot_hide_pytest_weakening_markers(tmp_path: Path):
    source = tmp_path / "test_dynamic_marker.py"
    source.write_text(
        "import pytest as pt\ngetattr(pt.mark, 'skip')\ngetattr(pt, 'xfail')\n",
        encoding="utf-8",
    )

    offenders = _test_weakening_markers(source)

    assert len(offenders) == 2
    assert any("marker skip" in offender for offender in offenders)
    assert any("marker xfail" in offender for offender in offenders)
