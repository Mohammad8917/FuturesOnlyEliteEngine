"""G03 guard: every production Futures contract boundary has a dedicated contract test."""
from pathlib import Path


PRODUCTION = Path("contracts/futures")
TESTS = Path("tests/contracts")


def test_every_futures_contract_has_a_dedicated_test_boundary():
    production = {
        path.stem
        for path in PRODUCTION.glob("*.py")
        if path.name != "__init__.py"
    }
    test_stems = {
        path.stem.removesuffix("_contract_test").removesuffix("test_")
        for path in TESTS.glob("*.py")
        if path.name != "__init__.py"
    }
    missing = sorted(production - test_stems)
    assert not missing, f"G03 missing dedicated contract tests: {missing}"


def test_contract_test_tree_contains_no_explicit_skip_or_xfail_markers():
    offenders = []
    for path in TESTS.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "pytest.skip(" in text or "pytest.mark.skip" in text or "pytest.mark.xfail" in text:
            offenders.append(str(path))
    assert not offenders, f"G03 test weakening markers detected: {offenders}"
