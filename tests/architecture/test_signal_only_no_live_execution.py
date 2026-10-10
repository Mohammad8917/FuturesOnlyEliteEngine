"""Static regression guard: the product must remain permanently signal-only.

This guard complements review. It cannot prove the absence of arbitrary dynamic
code, generated code, external deployments, or untracked local files.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "tests", "validation"}
FORBIDDEN_NAMES = {
    "createorder", "submitorder", "placeorder", "sendorder",
    "cancelorder", "replaceorder", "amendorder", "modifyorder",
    "openposition", "closeposition", "transferfunds", "setleverage",
    "createorders", "submitorders", "placeorders", "cancelorders",
    "privatepostorder", "privatepostorders", "fapiprivatepostorder",
    "fapiprivatepostorders", "privatefuturespostorder",
}
FORBIDDEN_TEXT = {
    "create_order", "submit_order", "place_order", "send_order",
    "cancel_order", "replace_order", "amend_order", "modify_order",
    "open_position", "close_position", "transfer_funds", "set_leverage",
}
# These SDKs expose live trading/write APIs. Do not add one merely for market data;
# a future read-only integration requires a separately reviewed, constrained port.
FORBIDDEN_EXCHANGE_SDKS = {
    "ccxt", "ccxtpro", "pythonbinance", "binance", "pybit", "bybit",
    "oandapyv20", "ib_insync", "ib_async", "metatrader5", "krakenex",
    "kucoin", "okx", "gate_api", "coinbase-advanced-py",
}
DEPENDENCY_MANIFEST_NAMES = {
    "requirements.txt", "requirements-ci.txt", "pyproject.toml", "setup.py",
    "setup.cfg", "pipfile", "pipfile.lock", "poetry.lock", "uv.lock",
    "environment.yml", "environment.yaml",
}


def _normalized(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _production_python_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.py")
        if not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    )


def test_production_source_has_no_live_order_or_account_mutation_calls() -> None:
    violations: list[str] = []
    for path in _production_python_files():
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            violations.append(f"{path.relative_to(ROOT)}: source cannot be audited: {exc}")
            continue

        aliases: dict[str, str] = {}
        forbidden_sdks = {_normalized(sdk) for sdk in FORBIDDEN_EXCHANGE_SDKS}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = _normalized((node.module or "").split(".")[0])
                if module in forbidden_sdks:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: forbidden exchange SDK import {node.module}"
                    )
                for item in node.names:
                    imported = _normalized(item.name)
                    if imported in FORBIDDEN_NAMES:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: forbidden imported API {item.name}"
                        )
                    aliases[item.asname or item.name] = imported
            elif isinstance(node, ast.Import):
                for item in node.names:
                    module = _normalized(item.name.split(".")[0])
                    if module in forbidden_sdks:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: forbidden exchange SDK import {item.name}"
                        )
                    aliases[item.asname or item.name.split(".")[0]] = _normalized(item.name)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute):
                name = node.func.attr
            elif isinstance(node.func, ast.Name):
                name = node.func.id
                if aliases.get(name, "") in FORBIDDEN_NAMES:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: forbidden aliased API call {name}"
                    )
            else:
                name = ""
            if _normalized(name) in FORBIDDEN_NAMES:
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: forbidden call {name}")
            # Catch common reflective lookups such as getattr(client, "create_order").
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if _normalized(arg.value) in FORBIDDEN_NAMES:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: forbidden API name string {arg.value}"
                        )

        for forbidden in FORBIDDEN_TEXT:
            if forbidden in source.lower():
                violations.append(
                    f"{path.relative_to(ROOT)}: forbidden live-write identifier {forbidden}"
                )

    assert not violations, "Signal-only invariant violated:\n" + "\n".join(sorted(set(violations)))


def test_no_exchange_trading_sdk_is_declared_as_a_dependency() -> None:
    violations: list[str] = []
    def is_manifest(path: Path) -> bool:
        name = path.name.lower()
        return (
            name in DEPENDENCY_MANIFEST_NAMES
            or (name.startswith("requirements") and name.endswith(".txt"))
            or name.startswith("dockerfile")
        )

    manifests = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and is_manifest(path)
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    )
    for path in manifests:
        try:
            source = path.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeError) as exc:
            violations.append(f"{path.relative_to(ROOT)}: dependency manifest unreadable: {exc}")
            continue
        normalized_source = _normalized(source)
        for sdk in FORBIDDEN_EXCHANGE_SDKS:
            if _normalized(sdk) in normalized_source:
                violations.append(
                    f"{path.relative_to(ROOT)}: trading-capable exchange SDK dependency {sdk}"
                )
    assert not violations, "Signal-only dependency invariant violated:\n" + "\n".join(violations)


def test_product_documents_define_signal_only_without_order_writes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    adr = (
        ROOT / "docs" / "architecture" / "adr" /
        "ADR-0006-signal-only-product-scope.md"
    ).read_text(encoding="utf-8").lower()
    assert "permanent signal-only" in readme
    assert "must **never**" in adr
    assert "submit, amend, cancel, or retry a live exchange order" in adr
