from pathlib import Path
import sys

def test_interpreter_matches_project_version_pin():
    project_root = Path(__file__).resolve().parents[1]

    expected_version = (
        project_root / ".python-version"
    ).read_text(encoding="utf-8").strip()

    actual_version = ".".join(map(str, sys.version_info[:3]))

    assert actual_version == expected_version, (
        f"Expected Python {expected_version}, "
        f"but running Python {actual_version}."
    )
