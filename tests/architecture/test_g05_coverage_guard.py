from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "scripts" / "verify_g05_coverage.py"


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
        '<coverage lines-covered="1174" lines-valid="1200" />',
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "97.833333%" in result.stdout
    assert "G05 FAIL: official coverage must be >= 98.00%" in result.stdout


def test_g05_guard_accepts_exactly_98_percent(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        '<coverage lines-covered="98" lines-valid="100" />',
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode == 0
    assert "G05 PASS: coverage is >= 98.00%" in result.stdout


def test_g05_guard_fails_closed_when_report_is_missing(tmp_path: Path) -> None:
    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "G05 FAIL: coverage.xml was not produced" in result.stdout


def test_g05_guard_fails_closed_on_invalid_line_counts(tmp_path: Path) -> None:
    (tmp_path / "coverage.xml").write_text(
        '<coverage lines-covered="101" lines-valid="100" />',
        encoding="utf-8",
    )

    result = _run_guard(tmp_path)

    assert result.returncode != 0
    assert "G05 FAIL: coverage report has invalid line counts" in result.stdout


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
