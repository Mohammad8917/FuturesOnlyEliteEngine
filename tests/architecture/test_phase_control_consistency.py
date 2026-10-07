from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture"


def _read(name: str) -> str:
    return (ARCH / name).read_text(encoding="utf-8")


def test_phase_control_documents_are_consistent() -> None:
    master_index = _read("ARCHITECTURE-MASTER-INDEX.md")
    roadmap = _read("master-roadmap-and-governance.md")
    state = _read("project-state.md")

    assert (
        "The current project state is Phase 1 — Domain Contracts."
        in master_index
    )
    assert (
        "Phase 0 — Architecture Baseline / Governance Final Audit is CLOSED"
        in master_index
    )
    assert "Phase 1 is authorized." in master_index
    assert "Phase 2+ remains blocked" in master_index

    assert "**Phase 0 status:** CLOSED — Phase 1 Domain Contracts authorized." in roadmap
    assert "Phase 1 Domain Contracts is authorized." in roadmap
    assert "Phase 2+ remains blocked" in roadmap

    assert "- Current phase: Phase 1 — Domain Contracts" in state
    assert "- Current gate: Phase 1 Domain Contracts" in state
    assert (
        "- Implementation phase authorized: YES — Phase 1 Domain Contracts"
        in state
    )
    assert "- Completed phases: Phase 0 — Architecture Baseline / Governance Final Audit" in state
    assert "- Active work: Phase 1 Domain Contracts" in state

    assert "Production implementation remains blocked until the Phase 0 exit criteria" not in master_index
