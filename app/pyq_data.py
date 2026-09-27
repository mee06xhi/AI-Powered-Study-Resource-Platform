"""
Shared PYQ-data loading logic. Pulled out of main.py so both the
/analyze-pyq endpoint and the agent's analyze_pyq tool can use the same
loading logic without importing from each other.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_pyq_text() -> tuple[str, list[str]]:
    """
    Load the raw text of every available previous-year question paper.
    Preference order: year*.txt files, else sample.txt.
    Returns (combined_text, filenames_used).
    """
    year_files = sorted(PROJECT_ROOT.glob("year*.txt"))
    if year_files:
        texts = [f.read_text(encoding="utf-8") for f in year_files]
        return "\n\n".join(texts), [f.name for f in year_files]

    sample = PROJECT_ROOT / "sample.txt"
    if sample.exists():
        return sample.read_text(encoding="utf-8"), [sample.name]

    return "", []