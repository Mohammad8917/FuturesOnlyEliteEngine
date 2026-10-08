from pathlib import Path


WORKFLOW = Path(".github/workflows/g01-dependency-architecture.yml")


def test_g01_ci_has_strict_reproducibility_and_execution_controls() -> None:
    content = WORKFLOW.read_text(encoding="utf-8")
    lock = Path("requirements-ci.txt").read_text(encoding="utf-8")

    required_fragments = (
        'workflow_dispatch:',
        "concurrency:",
        "cancel-in-progress: true",
        "permissions:",
        "contents: read",
        "timeout-minutes: 15",
        "runs-on: ubuntu-24.04",
        'python-version: "3.13"',
        'cache: "pip"',
        "--disable-pip-version-check",
        "--no-input",
        "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683",
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
    )

    for fragment in required_fragments:
        assert fragment in content

    assert lock.strip().splitlines()[-1] == "pytest==8.4.2"

    assert "continue-on-error: true" not in content
    assert "continue-on-error: false" not in content
    assert "--ignore" not in content
    assert "xfail" not in content.lower()
