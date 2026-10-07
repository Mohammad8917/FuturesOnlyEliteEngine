"""FILE: tests/architecture/test_dependency_direction.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the architecture dependency validator enforces the frozen dependency direction.
LAYER: tests
OWNS: Architecture dependency validator regression coverage for dependency direction and cycle detection.
DOES_NOT_OWN: production architecture policy, runtime orchestration, provider behavior
DEPENDENCIES: validation
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_architecture_dependency_validator_passes_current_tree() -> None:
    result = subprocess.run(
        [sys.executable, "validation/architecture_dependency_validator.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_rejects_domain_infrastructure_import(tmp_path: Path) -> None:
    (tmp_path / "domain").mkdir()
    (tmp_path / "infrastructure").mkdir()
    (tmp_path / "domain" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "infrastructure" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "domain" / "model.py").write_text(
        "from infrastructure.client import Client\n",
        encoding="utf-8",
    )
    (tmp_path / "infrastructure" / "client.py").write_text("", encoding="utf-8")

    from validation.architecture_dependency_validator import validate

    errors = validate(tmp_path)
    assert any("domain -> infrastructure" in error for error in errors)


def test_validator_rejects_futures_false_switch(tmp_path: Path) -> None:
    (tmp_path / "application").mkdir()
    (tmp_path / "application" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "application" / "provider.py").write_text(
        "def route(provider, futures=False):\n    return provider\n",
        encoding="utf-8",
    )

    from validation.architecture_dependency_validator import validate

    errors = validate(tmp_path)
    assert any("futures=False" in error for error in errors)


def test_validator_rejects_spot_symbol_in_domain(tmp_path: Path) -> None:
    (tmp_path / "domain").mkdir()
    (tmp_path / "domain" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "domain" / "instrument.py").write_text(
        "SpotInstrument = object\n",
        encoding="utf-8",
    )

    from validation.architecture_dependency_validator import validate

    errors = validate(tmp_path)
    assert any("Spot symbol/reference" in error for error in errors)
