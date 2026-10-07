"""FuturesOnlyEliteEngine architecture dependency validator.

This validator enforces the authoritative dependency direction defined by:
- docs/architecture/dependency-rules.md
- docs/architecture/futures-responsibility-map.md
- docs/architecture/ARCHITECTURE-MASTER-INDEX.md

It intentionally validates only architecture that actually exists in the target
repository. Absence of a future production layer is not converted into a
synthetic violation; Phase/implementation completeness is governed separately.
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = ROOT

# Canonical architectural layers. Multiple filesystem spellings are accepted
# only as aliases for the same authoritative responsibility.
LAYER_ALIASES: dict[str, tuple[str, ...]] = {
    "domain": ("domain", "domain/futures"),
    "contracts": ("contracts", "contracts/futures"),
    "application": ("application", "application/futures"),
    "risk": ("risk",),
    "execution": ("execution",),
    "infrastructure": ("infrastructure",),
    "market_data": ("market", "market_data", "data"),
    "analysis": ("analysis", "strategy"),
    "configuration": ("configuration", "config", "security"),
    "observability": ("observability", "notification", "notifications"),
}

# Dependency policy from dependency-rules.md. A layer may depend on itself,
# standard-library modules, and the explicitly listed architectural layers.
ALLOWED: dict[str, set[str]] = {
    "domain": {"contracts"},
    "contracts": {"domain"},
    "application": {"domain", "contracts", "market_data", "risk", "execution"},
    "risk": {"domain", "contracts", "configuration"},
    "execution": {"contracts", "domain", "risk", "infrastructure", "configuration"},
    "infrastructure": {
        "application",
        "contracts",
        "domain",
        "market_data",
        "execution",
        "configuration",
        "observability",
    },
    "market_data": {"contracts", "domain", "infrastructure", "configuration"},
    "analysis": {"domain", "contracts", "market_data", "application"},
    "configuration": set(),
    "observability": {"contracts", "execution"},
}

FORBIDDEN_IMPORT_PREFIXES: dict[str, tuple[str, ...]] = {
    "domain": (
        "requests",
        "httpx",
        "aiohttp",
        "sqlalchemy",
        "psycopg",
        "redis",
        "boto3",
        "kafka",
        "pika",
        "dotenv",
        "fastapi",
        "flask",
    ),
    "risk": ("requests", "httpx", "aiohttp", "ccxt", "binance"),
    "analysis": ("requests", "httpx", "aiohttp", "ccxt", "binance"),
    "observability": ("ccxt", "binance"),
}

TEST_DIR = ROOT / "tests"


def _module_name(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    return ".".join(relative.parts)


def _layer_for(path: Path) -> str | None:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return None

    parts = relative.parts
    if not parts:
        return None
    first = parts[0]

    for layer, aliases in LAYER_ALIASES.items():
        if first in {alias.split("/")[0] for alias in aliases}:
            return layer
    return None


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def _import_root(name: str) -> str:
    return name.split(".", 1)[0]


def _layer_from_import(import_name: str) -> str | None:
    root = _import_root(import_name)
    for layer, aliases in LAYER_ALIASES.items():
        if root in {alias.split("/")[0] for alias in aliases}:
            return layer
    return None


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                found.append(node.module)
    return found


def validate() -> list[str]:
    errors: list[str] = []
    graph: dict[str, set[str]] = defaultdict(set)
    python_files = _iter_python_files()

    for path in python_files:
        layer = _layer_for(path)
        if layer is None:
            continue

        module = _module_name(path)
        try:
            imported = _imports(path)
        except (OSError, SyntaxError) as exc:
            errors.append(f"{module}: cannot parse source: {exc}")
            continue

        for import_name in imported:
            imported_layer = _layer_from_import(import_name)
            if imported_layer is not None and imported_layer != layer:
                graph[layer].add(imported_layer)
                if imported_layer not in ALLOWED.get(layer, set()):
                    errors.append(
                        f"{module}: forbidden architectural dependency "
                        f"{layer} -> {imported_layer} via {import_name}"
                    )

            if any(
                import_name == prefix or import_name.startswith(prefix + ".")
                for prefix in FORBIDDEN_IMPORT_PREFIXES.get(layer, ())
            ):
                errors.append(
                    f"{module}: forbidden infrastructure/transport import "
                    f"{import_name} in {layer}"
                )

            # Domain must never depend on infrastructure by package path,
            # regardless of how infrastructure is named below it.
            if layer == "domain" and (
                import_name.startswith("infrastructure.")
                or import_name.startswith("exchange.")
                or import_name.startswith("exchanges.")
            ):
                errors.append(
                    f"{module}: domain imports infrastructure/exchange module "
                    f"{import_name}"
                )

        if layer == "risk":
            for import_name in imported:
                if any(
                    token in import_name.lower()
                    for token in ("order", "exchange", "execution")
                ) and _layer_from_import(import_name) in {"execution", "infrastructure"}:
                    errors.append(
                        f"{module}: risk must not depend on order/exchange execution "
                        f"authority: {import_name}"
                    )

        if layer == "analysis":
            for import_name in imported:
                if _layer_from_import(import_name) == "execution":
                    errors.append(
                        f"{module}: analysis/strategy must not depend on execution: "
                        f"{import_name}"
                    )

    # Detect architectural cycles among discovered layers.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycle = " -> ".join(stack + [node])
            errors.append(f"architectural dependency cycle: {cycle}")
            return
        if node in visited:
            return
        visiting.add(node)
        for child in sorted(graph.get(node, ())):
            visit(child, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for layer in sorted(graph):
        visit(layer, [])

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("ARCHITECTURE DEPENDENCY: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ARCHITECTURE DEPENDENCY: PASS")
    print("Validated all discovered architectural Python dependencies.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
