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
    assert (
        "- Current gate: finish same-SHA verification after this source-of-truth "
        "synchronization, obtain required independent PR #35 review/authorized merge, "
        "then verify all applicable checks on the exact resulting `main` SHA and "
        "resolve the historical G05 false-green" in state
    )
    assert (
        "- Implementation phase authorized: YES — Phase 1 Domain Contracts only"
        in state
    )
    assert (
        "- Completed phases: Phase 0 — Architecture Baseline / Governance Final Audit"
        in state
    )
    assert (
        "- Active work: synchronize current governance state and validate all applicable "
        "CI on the final candidate SHA; PR #35 remains open and unmerged pending "
        "independent review." in state
    )
    assert (
        "- Blocked work: Phase 2+ production implementation until PR #35 is reviewed/merged"
        in state
    )
    assert (
        "Live gate authority: the current branch HEAD and its GitHub Actions check-runs are authoritative"
        in state
    )

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


def test_g07_phase_applicability_is_explicit_and_fail_closed() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "g07-integration-resilience.yml"
    ).read_text(encoding="utf-8")
    adr = (ARCH / "adr" / "ADR-0001-phase-scoped-gate-applicability.md").read_text(
        encoding="utf-8"
    )
    state = _read("project-state.md")
    assert "- **Status:** APPROVED" in adr
    assert "NOT APPLICABLE (not passed)" in adr
    assert "G07 NOT APPLICABLE" in workflow
    assert "G07 has NOT passed" in workflow
    master_index = _read("ARCHITECTURE-MASTER-INDEX.md")
    roadmap = _read("master-roadmap-and-governance.md")
    change_guard = _read("CHANGE-GUARD.md")
    assert (
        "Phase 1-only/no operational scope means G07 NOT APPLICABLE (not passed)"
        in master_index
    )
    assert (
        "Proposed ADR-0001 records the question for owner review; it is not approved"
        not in master_index
    )
    assert (
        "Until it is approved, gate applicability and merge authorization must not be guessed"
        not in roadmap
    )
    assert "owner reviews/reconfirms the proposal" not in change_guard
    assert "Technical lock status: UNVERIFIED" in state
    assert "independent required review/approval is outstanding" in state
    assert "if: needs.applicability.outputs.operational_scope == 'true'" in workflow
    assert "Phase 1 Domain Contracts only" in state
    assert "Phase 2+ production implementation remains blocked" in state
    assert (
        "Last verified candidate evidence before this synchronization is SHA" in state
    )


def test_g05_coverage_floor_has_independent_fail_closed_guard() -> None:
    workflow = (ROOT / ".github" / "workflows" / "g05-coverage.yml").read_text(
        encoding="utf-8"
    )
    assert "--cov=contracts/futures" in workflow
    assert "--cov-fail-under=98" in workflow

    guard_start = workflow.index(
        "- name: Independently enforce the 98 percent coverage floor"
    )
    upload_start = workflow.index("- name: Upload coverage report", guard_start)
    guard = workflow[guard_start:upload_start]

    assert "if: always()" in guard
    assert 'ET.parse(report).getroot()' in guard
    assert 'root.attrib["lines-covered"]' in guard
    assert 'root.attrib["lines-valid"]' in guard
    assert "lines_valid <= 0" in guard
    assert "if percentage < 98.0:" in guard
    assert "G05 FAIL: official coverage must be >= 98.00%" in guard
    assert "sys.exit(1)" in guard
