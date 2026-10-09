from __future__ import annotations

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
        lines_covered = int(root.attrib["lines-covered"])
        lines_valid = int(root.attrib["lines-valid"])
    except (ET.ParseError, KeyError, ValueError) as exc:
        print(f"G05 FAIL: invalid coverage report: {exc}")
        return 1

    if lines_valid <= 0 or lines_covered < 0 or lines_covered > lines_valid:
        print("G05 FAIL: coverage report has invalid line counts")
        return 1

    percentage = (lines_covered / lines_valid) * 100
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
