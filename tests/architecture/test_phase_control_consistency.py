from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture"


def _read(name: str) -> str:
    return (ARCH / name).read_text(encoding="utf-8")


def test_phase_control_documents_are_consistent() -> None:
    master_index = _read("ARCHITECTURE-MASTER-INDEX.md")
    roadmap = _read("master-roadmap-and-governance.md")
    state = _read("project-state.md")
    invariants = _read("architecture-invariants.md")
    contract = _read("architecture-contract.md")
    responsibility = _read("futures-responsibility-map.md")
    dependencies = _read("dependency-rules.md")
    change_guard = _read("CHANGE-GUARD.md")

    assert "The current project state is Phase 1 — Domain Contracts." in master_index
    assert (
        "Phase 0 — Architecture Baseline / Governance Final Audit is CLOSED"
        in master_index
    )
    assert "Phase 1 is authorized." in master_index
    assert "Phase 2+ remains blocked" in master_index

    assert (
        "**Phase 0 status:** CLOSED — Phase 1 Domain Contracts authorized." in roadmap
    )
    assert "Phase 1 Domain Contracts is authorized." in roadmap
    assert "Phase 2+ remains blocked" in roadmap

    assert "- Current phase: Phase 1 — Domain Contracts" in state
    assert "- Current gate: same-SHA closure snapshot verification and PR #35 review/merge" in state
    assert (
        "- Implementation phase authorized: YES — Phase 1 Domain Contracts only"
        in state
    )
    assert (
        "- Completed phases: Phase 0 — Architecture Baseline / Governance Final Audit"
        in state
    )
    assert "- Active work: verify all applicable gates on the closure snapshot SHA" in state
    assert "- Blocked work: Phase 2+ production implementation until the closure snapshot passes" in state
    assert "No all-gates same-SHA pass is claimed for the closure snapshot commit yet." in state

    assert (
        "Production implementation remains blocked until the Phase 0 exit criteria"
        not in master_index
    )

    authoritative_markers = (
        "Futures-only",
        "CRYPTO",
        "FOREX",
        "GOLD",
        "Linear",
        "Inverse",
    )
    for marker in authoritative_markers:
        assert marker in invariants
        assert marker in contract
        assert marker in responsibility
        assert marker in master_index

    assert "Operational Spot is forbidden." in invariants
    assert "Operational Spot is forbidden." in invariants
    assert "Operational Spot is forbidden." in master_index
    assert "Spot" in contract
    assert "Spot" in responsibility
    assert "Spot" in dependencies

    assert "Phase 1 — Domain Contracts" in master_index
    phase1_contract_requirements = (
        "instrument identity",
        "contract family",
        "Linear/Inverse",
        "multiplier",
        "settlement asset",
        "margin asset",
        "leverage",
        "position side",
        "position mode",
        "precision",
        "funding",
        "realized PnL",
        "unrealized PnL",
        "exposure",
        "liquidation",
        "Futures accounting",
        "failure semantics",
    )
    for requirement in phase1_contract_requirements:
        assert requirement in master_index
        assert requirement in roadmap
        assert requirement in responsibility
        assert requirement in contract

    assert (
        "No Phase 2+ implementation may be used to conceal an incomplete Phase 1 contract."
        in master_index
    )
    assert (
        "No production implementation should precede a clearly owned contract."
        in contract
    )
    assert "Phase 1 Domain Contracts" in roadmap
    assert "Phase 1 — Domain Contracts" in state

    assert "architecture-change governance process" in invariants
    assert "ADR" in master_index
    assert "ADR" in change_guard

    assert "G01" in invariants
    assert "G05" in invariants
    assert "G08" in invariants
    assert "G01" in contract
    assert "G05" in contract
    assert "G08" in contract
    assert "G01 -> G02 -> G03 -> G04 -> G05 -> G06 -> G07 -> G08" in roadmap
    assert "G01–G08" in change_guard

    assert "not technically locked" in change_guard
    assert "not the architectural contract" in state
