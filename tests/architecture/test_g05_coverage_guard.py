from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "scripts" / "verify_g05_coverage.py"


def _coverage_xml(
    lines_covered: int = 98,
    lines_valid: int = 100,
    *,
    include_packages: bool = True,
    include_class: bool = True,
) -> str:
    class_xml = (
        '<class name="contract.py" filename="contracts/futures/contract.py" '
        'line-rate="0.98" branch-rate="0" complexity="0"><methods />'
        '<lines><line number="1" hits="1" /></lines></class>'
        if include_class
        else ""
    )
    packages_xml = (
        f'<packages><package name="contracts.futures" line-rate="0.98" '
        f'branch-rate="0" complexity="0"><classes>{class_xml}</classes>'
        f'</package></packages>'
        if include_packages
        else ""
    )
    line_rate = lines_covered / lines_valid if lines_valid else 0
    return (
        f'<coverage version="7.6.1" timestamp="1791500000" '
        f'lines-covered="{lines_covered}" lines-valid="{lines_valid}" '
        f'line-rate="{line_rate}" branches-covered="0" branches-valid="0" '
        f'branch-rate="0"><sources><source>.</source></sources>'
        f"{packages_xml}</coverage>"
    )


def _run_guard(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GUARD)],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )


def test_g05_guard_rejects_historical_97_83_percent_false_green(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        _coverage_xml(lines_covered=1174, lines_valid=1200),
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "97.833333%" in result.stdout
    assert "G05 FAIL: official coverage must be >= 98.00%" in result.stdout


def test_g05_guard_accepts_exactly_98_percent(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(_coverage_xml(), encoding="utf-8")

    result = _run_guard(tmp_path)

    assert result.returncode == 0
    assert "G05 PASS: coverage is >= 98.00%" in result.stdout


def test_g05_guard_fails_closed_when_report_is_missing(tmp_path: Path) -> None:
    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "G05 FAIL: coverage.xml was not produced" in result.stdout


def test_g05_guard_fails_closed_on_invalid_line_counts(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        _coverage_xml(lines_covered=101, lines_valid=100),
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert (
        "G05 FAIL: coverage report has invalid metadata or line counts"
        in result.stdout
    )


def test_g05_guard_fails_closed_when_root_is_not_coverage(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        '<not-coverage lines-covered="100" lines-valid="100" />',
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "G05 FAIL: coverage report root element must be <coverage>" in result.stdout


def test_g05_guard_fails_closed_on_malformed_xml(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        '<coverage lines-covered="100" lines-valid="100"',
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "G05 FAIL: invalid coverage report:" in result.stdout


def test_g05_guard_fails_closed_on_truncated_root_only_xml(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        '<coverage version="7.6.1" timestamp="1791500000" '
        'lines-covered="100" lines-valid="100" line-rate="1" />',
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert (
        "G05 FAIL: coverage report is incomplete; "
        "<sources> and <packages> are required"
        in result.stdout
    )


def test_g05_guard_fails_closed_when_package_has_no_class_evidence(
    tmp_path: Path,
) -> None:
    (tmp_path / "coverage.xml").write_text(
        _coverage_xml(include_class=False),
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert (
        "G05 FAIL: coverage report is incomplete; "
        "at least one class with a filename is required"
        in result.stdout
    )
