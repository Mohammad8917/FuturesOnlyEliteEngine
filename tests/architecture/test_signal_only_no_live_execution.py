"""Static regression guard: the product must remain permanently signal-only.

This guard is intentionally conservative and complements review; it is not a
proof against arbitrary reflection, generated code, or external deployments.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Validation contains the architecture-audit tool itself, not product runtime.
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
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for item in node.names:
                    imported = _normalized(item.name)
                    if imported in FORBIDDEN_NAMES:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: forbidden imported API {item.name}"
                        )
                    aliases[item.asname or item.name] = imported
            elif isinstance(node, ast.Import):
                for item in node.names:
                    aliases[item.asname or item.name.split(".")[0]] = _normalized(item.name)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    name = node.func.id
                    imported_name = aliases.get(name, "")
                    if imported_name in FORBIDDEN_NAMES:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: forbidden aliased API call {name}"
                        )
                else:
                    name = ""
                if _normalized(name) in FORBIDDEN_NAMES:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: forbidden call {name}"
                    )
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


def test_product_documents_define_signal_only_without_order_writes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    adr = (
        ROOT / "docs" / "architecture" / "adr" /
        "ADR-0006-signal-only-product-scope.md"
    ).read_text(encoding="utf-8").lower()
    assert "permanent signal-only" in readme
    assert "must never" in adr
    assert "submit, amend, cancel, or retry a live exchange order" in adr
