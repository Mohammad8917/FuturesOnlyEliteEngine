"""FILE: tests/architecture/test_forbidden_imports.py
KIT: Futures-Only Elite Architecture Compliance
RESPONSIBILITY: Verify dependency-policy allowed and forbidden layer edges cannot contradict each other.
LAYER: tests
OWNS: Architecture dependency-policy consistency regression coverage.
DOES_NOT_OWN: production architecture policy, runtime orchestration, exchange behavior
DEPENDENCIES: validation.architecture_dependency_validator
PYTHON: 3.13
"""

from __future__ import annotations

from validation.architecture_dependency_validator import ALLOWED, FORBIDDEN_IMPORTS


def test_allowed_and_forbidden_edges_are_disjoint() -> None:
    for layer, forbidden in FORBIDDEN_IMPORTS.items():
        assert forbidden.isdisjoint(ALLOWED.get(layer, set())), layer
