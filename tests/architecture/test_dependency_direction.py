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
