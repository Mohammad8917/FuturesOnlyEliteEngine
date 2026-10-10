"""Static regression guard: the product must remain permanently signal-only."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "tests", "validation"}
FORBIDDEN_CALLS = {
    "create_order", "submit_order", "place_order", "send_order",
    "cancel_order", "replace_order", "amend_order", "modify_order",
    "open_position", "close_position", "transfer_funds", "set_leverage",
}


def _production_python_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.py")
        if not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    )


def test_production_source_has_no_live_order_or_account_mutation_calls() -> None:
    violations: list[str] = []
    for path in _production_python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            violations.append(f"{path.relative_to(ROOT)}: source cannot be audited: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else (
                    node.func.id if isinstance(node.func, ast.Name) else ""
                )
                if name.lower() in FORBIDDEN_CALLS:
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: forbidden call {name}")
    assert not violations, "Signal-only invariant violated:\n" + "\n".join(violations)


def test_product_documents_define_signal_only_without_order_writes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    adr = (ROOT / "docs" / "architecture" / "adr" / "ADR-0006-signal-only-product-scope.md").read_text(encoding="utf-8").lower()
    assert "permanent signal-only" in readme
    assert "must never" in adr
    assert "submit, amend, cancel, or retry a live exchange order" in adr
