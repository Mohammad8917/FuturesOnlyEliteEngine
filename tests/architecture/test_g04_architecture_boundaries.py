"""G04 regression coverage for enforced architecture/dependency boundaries."""

from __future__ import annotations

from pathlib import Path

from validation.architecture_dependency_validator import validate


def _pkg(root: Path, name: str) -> None:
    path = root / name
    path.mkdir(parents=True, exist_ok=True)
    (path / "__init__.py").write_text("", encoding="utf-8")


def _source(root: Path, layer: str, name: str, source: str) -> None:
    _pkg(root, layer)
    (root / layer / name).write_text(source, encoding="utf-8")


def test_current_tree_passes_g04_validator() -> None:
    assert validate() == []


def test_rejects_forbidden_layer_edge(tmp_path: Path) -> None:
    _source(
        tmp_path,
        "application",
        "service.py",
        "from infrastructure.client import Client\n",
    )
    _source(tmp_path, "infrastructure", "client.py", "")
    errors = validate(tmp_path)
    assert any("application -> infrastructure" in error for error in errors)


def test_rejects_unresolved_relative_import(tmp_path: Path) -> None:
    _source(tmp_path, "domain", "model.py", "from .missing import Contract\n")
    errors = validate(tmp_path)
    assert any("unresolved relative import" in error for error in errors)


def test_rejects_non_stdlib_external_dependency_in_contracts(tmp_path: Path) -> None:
    _source(tmp_path, "contracts", "model.py", "import requests\n")
    errors = validate(tmp_path)
    assert any("forbidden external dependency" in error for error in errors)


def test_rejects_spot_reference_in_every_operational_layer(tmp_path: Path) -> None:
    for layer in (
        "domain",
        "contracts",
        "application",
        "risk",
        "execution",
        "infrastructure",
        "market_data",
        "analysis",
        "configuration",
        "observability",
    ):
        _source(tmp_path, layer, "model.py", "class SpotProvider: pass\n")
    errors = validate(tmp_path)
    assert sum("forbidden Spot symbol/reference" in error for error in errors) >= 10


def test_rejects_order_call_outside_execution(tmp_path: Path) -> None:
    _source(
        tmp_path,
        "risk",
        "policy.py",
        "def reject(client):\n    return client.submit_order()\n",
    )
    errors = validate(tmp_path)
    assert any("forbidden order call in risk" in error for error in errors)


def test_allows_order_call_inside_execution(tmp_path: Path) -> None:
    _source(
        tmp_path,
        "execution",
        "gateway.py",
        "def submit(client):\n    return client.submit_order()\n",
    )
    assert validate(tmp_path) == []


def test_rejects_http_call_in_domain_and_risk(tmp_path: Path) -> None:
    _source(
        tmp_path,
        "domain",
        "pricing.py",
        "def load(client):\n    return client.get('/price')\n",
    )
    _source(
        tmp_path,
        "risk",
        "policy.py",
        "def load(client):\n    return client.get('/risk')\n",
    )
    errors = validate(tmp_path)
    assert any("forbidden HTTP call in domain" in error for error in errors)
    assert any("forbidden HTTP call in risk" in error for error in errors)


def test_rejects_layer_cycle(tmp_path: Path) -> None:
    _source(
        tmp_path, "application", "service.py", "from analysis.signal import Signal\n"
    )
    _source(
        tmp_path, "analysis", "signal.py", "from application.service import Service\n"
    )
    errors = validate(tmp_path)
    assert any("architectural dependency cycle" in error for error in errors)
