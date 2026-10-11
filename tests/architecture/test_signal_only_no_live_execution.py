"""Static regression guard: the product must remain permanently signal-only.

This guard complements review. It cannot prove the absence of arbitrary dynamic
code, generated code, external deployments, or untracked local files.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "tests"}
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
        and path.relative_to(ROOT).as_posix() != "validation/architecture_dependency_validator.py"
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
            # Catch reflective lookups in positional/keyword arguments and
            # string-key dispatch such as client["create_order"](...).
            for arg in [*node.args, *(kw.value for kw in node.keywords)]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if _normalized(arg.value) in FORBIDDEN_NAMES:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: forbidden API name string {arg.value}"
                        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                value = node.slice.value
                if isinstance(value, str) and _normalized(value) in FORBIDDEN_NAMES:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: forbidden string-key API dispatch {value}"
                    )
        # Catch common REST order-write routes even when code uses a generic
        # HTTP client instead of a named exchange SDK method.
        for pattern in FORBIDDEN_RUNTIME_PATTERNS:
            for match in pattern.finditer(source):
                line = source.count("\n", 0, match.start()) + 1
                violations.append(
                    f"{path.relative_to(ROOT)}:{line}: forbidden live-write/API pattern {match.group(0)}"
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



# Text-based runtime/deployment surfaces are checked separately from Python AST.
# Keep documentation and tests out of this scan: they describe the forbidden
# APIs and must be able to assert that those APIs are forbidden.
TEXT_RUNTIME_SUFFIXES = {
    ".sh", ".bash", ".ps1", ".bat", ".cmd", ".yml", ".yaml", ".json",
    ".toml", ".ini", ".cfg", ".conf", ".service", ".properties", ".xml", ".py",
    ".tf", ".hcl", ".psm1", ".env", ".js", ".mjs", ".cjs", ".ts",
    ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".cs", ".php", ".rb",
    ".lua", ".sql", ".ipynb",
}
TEXT_RUNTIME_FILENAMES = {
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "compose.yml", "compose.yaml", ".dockerignore", "makefile", "procfile",
    "taskfile",
}
TEXT_RUNTIME_EXCLUDED_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "tests", "docs", "dist", "build", "node_modules",
}
FORBIDDEN_RUNTIME_PATTERNS = (
    re.compile(r"\b(?:create|submit|place|send|cancel|replace|amend|modify)_orders?\b", re.I),
    re.compile(r"\b(?:create|submit|place|send|cancel|replace|amend|modify)(?:Live)?Orders?\b", re.I),
    re.compile(r"\b(?:open|close|liquidate)_positions?\b", re.I),
    re.compile(r"\b(?:open|close|liquidate)(?:Real)?Positions?\b", re.I),
    re.compile(r"\b(?:transfer|withdraw|deposit)_funds?\b", re.I),
    re.compile(r"\b(?:transfer|withdraw|deposit)Funds?\b", re.I),
    re.compile(r"\bset_leverage\b|\bchange_leverage\b", re.I),
    re.compile(r"\b(?:set|change)Leverage\b", re.I),
    re.compile(r"/(?:fapi|dapi)/v\d+/order(?:s)?(?:\b|/)", re.I),
    re.compile(r"/api/v\d+/(?:orders?|positions?)(?:\b|/)", re.I),
    re.compile(r"/v\d+/(?:orders?|positions?)(?:/|\b|\?)", re.I),
    re.compile(r"/(?:private/)?orders?/(?:create|submit|place|cancel|replace|amend|modify)(?:/|\b|\?)", re.I),
)
FORBIDDEN_RUNTIME_SDK_TOKENS = tuple(
    re.compile(r"(?<![a-z0-9])" + re.escape(sdk) + r"(?![a-z0-9])", re.I)
    for sdk in FORBIDDEN_EXCHANGE_SDKS
)


def _text_runtime_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part.lower() in TEXT_RUNTIME_EXCLUDED_PARTS for part in relative.parts):
            continue
        # This single file is an architecture policy validator whose purpose is
        # to contain forbidden API names as deny-list data, not runtime code.
        if relative.as_posix() == "validation/architecture_dependency_validator.py":
            continue
        lower_name = path.name.lower()
        is_env_file = lower_name == ".env" or lower_name.startswith(".env.") or lower_name.startswith(".env-")
        if path.suffix.lower() in TEXT_RUNTIME_SUFFIXES or lower_name in TEXT_RUNTIME_FILENAMES or is_env_file:
            files.append(path)
            continue
        # Also inspect extensionless text files and executable/shebang scripts;
        # these can otherwise evade suffix-based discovery.
        if path.suffix == "" or path.stat().st_mode & 0o111:
            try:
                with path.open("rb") as stream:
                    header = stream.read(512)
            except OSError:
                files.append(path)  # unreadable candidates fail closed below
                continue
            if header.startswith(b"#!") or (0 not in header and header.strip()):
                try:
                    header.decode("utf-8")
                except UnicodeDecodeError:
                    if path.stat().st_mode & 0o111:
                        files.append(path)  # executable but non-text: fail closed
                    continue
                files.append(path)
    return sorted(files)


def test_runtime_scripts_and_deployment_configuration_have_no_live_write_paths() -> None:
    violations: list[str] = []
    for path in _text_runtime_files():
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            violations.append(f"{path.relative_to(ROOT)}: runtime/config file cannot be audited: {exc}")
            continue
        for pattern in FORBIDDEN_RUNTIME_PATTERNS:
            for match in pattern.finditer(source):
                line = source.count("\n", 0, match.start()) + 1
                violations.append(
                    f"{path.relative_to(ROOT)}:{line}: forbidden live-write/API pattern {match.group(0)}"
                )
        for pattern in FORBIDDEN_RUNTIME_SDK_TOKENS:
            if pattern.search(source):
                violations.append(
                    f"{path.relative_to(ROOT)}: forbidden trading-capable exchange SDK token"
                )
    assert not violations, "Signal-only runtime/config invariant violated:\n" + "\n".join(sorted(set(violations)))

def test_product_documents_define_signal_only_without_order_writes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    adr = (
        ROOT / "docs" / "architecture" / "adr" /
        "ADR-0006-signal-only-product-scope.md"
    ).read_text(encoding="utf-8").lower()
    assert "permanent signal-only" in readme
    assert "must **never**" in adr
    assert "submit, amend, cancel, or retry a live exchange order" in adr


def test_guard_patterns_cover_common_live_write_bypass_spellings() -> None:
    samples = {
        "snake_case method": "client.create_order(symbol, quantity)",
        "camel_case method": "client.createOrder(symbol, quantity)",
        "generic exchange REST endpoint": 'client.request("POST", "/fapi/v1/order")',
        "versioned order route": 'client.request("POST", "/v5/order/create")',
        "generic orders route": 'requests.post("/api/v1/orders", json=payload)',
        "camel_case fund transfer": "client.transferFunds(destination, amount)",
        "camel_case leverage mutation": "client.setLeverage(symbol, leverage)",
    }
    for label, sample in samples.items():
        assert any(pattern.search(sample) for pattern in FORBIDDEN_RUNTIME_PATTERNS), (
            f"Signal-only guard missed {label}: {sample}"
        )
