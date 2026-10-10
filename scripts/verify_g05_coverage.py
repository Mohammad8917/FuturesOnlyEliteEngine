from __future__ import annotations

import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MINIMUM_COVERAGE_PERCENT = 98.0


def main() -> int:
    report = Path("coverage.xml")
    if not report.is_file():
        print("G05 FAIL: coverage.xml was not produced")
        return 1

    try:
        root = ET.parse(report).getroot()
        if root.tag != "coverage":
            print("G05 FAIL: coverage report root element must be <coverage>")
            return 1

        # Require the structural metadata emitted by coverage.py. A syntactically
        # valid but truncated/root-only XML document is not evidence of coverage.
        required_attributes = (
            "version",
            "timestamp",
            "line-rate",
            "lines-covered",
            "lines-valid",
        )
        missing = [name for name in required_attributes if name not in root.attrib]
        if missing:
            print(
                "G05 FAIL: coverage report is incomplete; missing attributes: "
                f"{', '.join(missing)}"
            )
            return 1

        sources = root.find("sources")
        packages = root.find("packages")
        if sources is None or packages is None:
            print(
                "G05 FAIL: coverage report is incomplete; "
                "<sources> and <packages> are required"
            )
            return 1

        classes = packages.findall(".//class")
        if not classes or any(not item.get("filename", "").strip() for item in classes):
            print(
                "G05 FAIL: coverage report is incomplete; "
                "at least one class with a filename is required"
            )
            return 1

        line_nodes = packages.findall(".//line")
        if not line_nodes:
            print(
                "G05 FAIL: coverage report is incomplete; "
                "class-level executable-line evidence is required"
            )
            return 1

        covered_from_classes = 0
        for line in line_nodes:
            line_number = int(line.attrib["number"])
            hits = int(line.attrib["hits"])
            if line_number <= 0 or hits < 0:
                print(
                    "G05 FAIL: coverage report contains invalid class-level line data"
                )
                return 1
            if hits > 0:
                covered_from_classes += 1

        lines_covered = int(root.attrib["lines-covered"])
        lines_valid = int(root.attrib["lines-valid"])
        reported_rate = float(root.attrib["line-rate"])
        timestamp = int(root.attrib["timestamp"])
    except (ET.ParseError, KeyError, TypeError, ValueError, OverflowError) as exc:
        print(f"G05 FAIL: invalid coverage report: {exc}")
        return 1

    if (
        not root.attrib["version"].strip()
        or timestamp <= 0
        or not math.isfinite(reported_rate)
        or not 0 <= reported_rate <= 1
        or lines_valid <= 0
        or lines_covered < 0
        or lines_covered > lines_valid
    ):
        print("G05 FAIL: coverage report has invalid metadata or line counts")
        return 1

    calculated_rate = lines_covered / lines_valid
    if (
        len(line_nodes) != lines_valid
        or covered_from_classes != lines_covered
        or not math.isclose(reported_rate, calculated_rate, rel_tol=0, abs_tol=0.0001)
    ):
        print(
            "G05 FAIL: coverage report root totals do not match "
            "class-level line evidence"
        )
        return 1

    percentage = calculated_rate * 100
    print(
        f"G05 independently measured exact line coverage: "
        f"{lines_covered}/{lines_valid} = {percentage:.6f}%"
    )
    if percentage < MINIMUM_COVERAGE_PERCENT:
        print("G05 FAIL: official coverage must be >= 98.00%")
        return 1

    print("G05 PASS: coverage is >= 98.00%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
