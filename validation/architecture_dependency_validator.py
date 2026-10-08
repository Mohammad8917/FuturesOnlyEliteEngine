"""Strict FuturesOnlyEliteEngine architecture dependency validator."""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYER_ALIASES = {
    "domain": {"domain"},
    "contracts": {"contracts"},
    "application": {"application"},
    "risk": {"risk"},
    "execution": {"execution"},
    "infrastructure": {"infrastructure"},
    "market_data": {"market", "market_data", "data"},
    "analysis": {"analysis", "strategy"},
    "configuration": {"configuration", "config", "security"},
    "observability": {"observability", "notification", "notifications"},
}

ALLOWED = {
    "domain": {"contracts"},
    "contracts": set(),
    "application": {"domain", "contracts"},
    "risk": {"domain", "contracts"},
    "execution": {"contracts", "domain", "risk", "infrastructure"},
    "infrastructure": {
        "application", "contracts", "domain", "market_data", "execution",
        "configuration", "observability",
    },
    "market_data": {"contracts", "domain", "infrastructure"},
    "analysis": {"domain", "contracts", "market_data", "application"},
    "configuration": set(),
    "observability": {"contracts"},
}

FORBIDDEN_IMPORTS = {
    "domain": {
        "requests", "httpx", "aiohttp", "sqlalchemy", "psycopg", "redis",
        "boto3", "kafka", "pika", "dotenv", "fastapi", "flask", "ccxt", "binance",
    },
    "contracts": {
        "requests", "httpx", "aiohttp", "sqlalchemy", "psycopg", "redis",
        "boto3", "kafka", "pika", "dotenv", "fastapi", "flask", "ccxt", "binance",
    },
    "application": {
        "requests", "httpx", "aiohttp", "sqlalchemy", "psycopg", "redis",
        "boto3", "kafka", "pika", "dotenv", "fastapi", "flask", "ccxt", "binance",
    },
    "risk": {
        "requests", "httpx", "aiohttp", "sqlalchemy", "psycopg", "redis",
        "boto3", "kafka", "pika", "dotenv", "fastapi", "flask", "ccxt", "binance",
    },
    "analysis": {
        "requests", "httpx", "aiohttp", "sqlalchemy", "psycopg", "redis",
        "boto3", "kafka", "pika", "dotenv", "fastapi", "flask", "ccxt", "binance",
    },
}

SPOT_TOKENS = {"spot", "spotmarket", "spotorder", "spotprovider"}
ORDER_CALLS = {
    "create_order", "submit_order", "place_order", "send_order",
    "cancel_order", "replace_order",
}
HTTP_CALLS = {"request", "get", "post", "put", "patch", "delete"}
HTTP_RECEIVER_NAMES = {"client", "session", "http", "transport"}
NON_EXECUTION_ORDER_LAYERS = {
    "domain", "contracts", "application", "risk", "analysis", "market_data",
}
NON_IO_LAYERS = {"domain", "risk", "analysis"}
EXCLUDED = {".git", ".venv", "venv", "__pycache__"}


def _layer_for(path: Path, root: Path) -> str | None:
    try:
        first = path.relative_to(root).parts[0]
    except (ValueError, IndexError):
        return None
    for layer, aliases in LAYER_ALIASES.items():
        if first in aliases:
            return layer
    return None


def _files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.py")
        if not any(part in EXCLUDED for part in p.parts)
    )


def _module(path: Path, root: Path) -> str:
    return ".".join(path.relative_to(root).with_suffix("").parts)


def _resolve_relative(path: Path, root: Path, level: int, module: str) -> Path | None:
    base = path.relative_to(root).parent
    if level:
        for _ in range(level - 1):
            base = base.parent
    target = root / base / Path(*module.split(".")) if module else root / base
    candidate = target.with_suffix(".py")
    if candidate.is_file():
        return candidate
    init = target / "__init__.py"
    return init if init.is_file() else None


def _import_layer(path: Path, root: Path, module: str, level: int) -> str | None:
    if level:
        target = _resolve_relative(path, root, level, module)
        return _layer_for(target, root) if target else None
    root_name = module.split(".", 1)[0]
    for layer, aliases in LAYER_ALIASES.items():
        if root_name in aliases:
            return layer
    return None


def _imports(tree: ast.AST) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend((a.name, 0) for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.append((node.module or "", node.level))
    return result


def _forbidden_root(module: str, roots: set[str]) -> bool:
    return module.split(".", 1)[0].lower() in roots


def _spot(value: str) -> bool:
    normalized = value.lower().replace("_", "").replace("-", "")
    return normalized in SPOT_TOKENS or normalized.startswith("spot")


def _is_stdlib_import(module: str) -> bool:
    return module.split(".", 1)[0] in sys.stdlib_module_names


def _call_receiver_name(node: ast.Attribute) -> str | None:
    receiver = node.value
    if isinstance(receiver, ast.Name):
        return receiver.id.lower()
    if isinstance(receiver, ast.Attribute):
        return receiver.attr.lower()
    return None


def validate(root: Path = ROOT) -> list[str]:
    errors: set[str] = set()
    graph: dict[str, set[str]] = defaultdict(set)

    for path in _files(root):
        layer = _layer_for(path, root)
        if layer is None:
            continue
        module_name = _module(path, root)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            errors.add(f"{module_name}: cannot parse source: {exc}")
            continue

        for imported, level in _imports(tree):
            target_layer = _import_layer(path, root, imported, level)

            if level and _resolve_relative(path, root, level, imported) is None:
                errors.add(
                    f"{module_name}: unresolved relative import: "
                    f"{'.' * level}{imported}"
                )

            if target_layer is not None and target_layer != layer:
                graph[layer].add(target_layer)
                if target_layer not in ALLOWED[layer]:
                    errors.add(
                        f"{module_name}: forbidden dependency "
                        f"{layer} -> {target_layer} via {imported or 'relative import'}"
                    )

            if level == 0 and _forbidden_root(imported, FORBIDDEN_IMPORTS.get(layer, set())):
                errors.add(f"{module_name}: forbidden external dependency: {imported}")

            if layer in {"domain", "contracts"} and level == 0 and not _is_stdlib_import(imported):
                root_name = imported.split(".", 1)[0]
                known_internal = any(root_name in aliases for aliases in LAYER_ALIASES.values())
                if not known_internal:
                    errors.add(
                        f"{module_name}: non-stdlib external dependency in {layer}: {imported}"
                    )

            if layer in LAYER_ALIASES and _spot(imported):
                errors.add(f"{module_name}: forbidden Spot dependency: {imported}")

            if layer == "domain" and imported.lower().startswith(
                ("infrastructure.", "exchange.", "exchanges.")
            ):
                errors.add(f"{module_name}: domain imports exchange infrastructure: {imported}")

            if layer == "risk" and any(
                token in imported.lower()
                for token in ("execution", "exchange", "order", "ccxt", "binance")
            ):
                errors.add(f"{module_name}: risk imports execution/order authority: {imported}")

            if layer == "analysis" and target_layer == "execution":
                errors.add(f"{module_name}: analysis imports execution: {imported}")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if _spot(node.name):
                    errors.add(f"{module_name}: forbidden Spot symbol/reference: {node.name}")

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    positional = list(node.args.posonlyargs) + list(node.args.args)
                    defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
                    for argument, default in zip(positional, defaults):
                        if (
                            argument.arg == "futures"
                            and isinstance(default, ast.Constant)
                            and default.value is False
                        ):
                            errors.add(f"{module_name}: forbidden futures=False switch")
                    for keyword_arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                        if (
                            argument.arg == "futures"
                            and isinstance(default, ast.Constant)
                            and default.value is False
                        ):
                            errors.add(f"{module_name}: forbidden futures=False switch")

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ORDER_CALLS and layer in NON_EXECUTION_ORDER_LAYERS:
                        errors.add(
                            f"{module_name}: forbidden order call in {layer}: {node.func.attr}"
                        )
                    if (
                        node.func.attr in HTTP_CALLS
                        and layer in NON_IO_LAYERS
                        and _call_receiver_name(node.func) in HTTP_RECEIVER_NAMES
                    ):
                        errors.add(
                            f"{module_name}: forbidden HTTP call in {layer}: {node.func.attr}"
                        )
                for keyword in node.keywords:
                    if keyword.arg == "futures" and isinstance(keyword.value, ast.Constant):
                        if keyword.value.value is False:
                            errors.add(f"{module_name}: forbidden futures=False switch")

            if isinstance(node, ast.Name) and _spot(node.id):
                errors.add(f"{module_name}: forbidden Spot symbol/reference: {node.id}")
            if isinstance(node, ast.Attribute) and _spot(node.attr):
                errors.add(f"{module_name}: forbidden Spot symbol/reference: {node.attr}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(layer: str, stack: list[str]) -> None:
        if layer in visiting:
            errors.add(f"architectural dependency cycle: {' -> '.join(stack + [layer])}")
            return
        if layer in visited:
            return
        visiting.add(layer)
        for child in sorted(graph[layer]):
            visit(child, stack + [layer])
        visiting.remove(layer)
        visited.add(layer)

    for layer in sorted(graph):
        visit(layer, [])

    return sorted(errors)


def main() -> int:
    errors = validate()
    if errors:
        print("ARCHITECTURE DEPENDENCY: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("ARCHITECTURE DEPENDENCY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
