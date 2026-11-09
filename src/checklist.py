
"""Load and manage category-specific inspection checklists."""

import json
from pathlib import Path
from typing import Dict, List


DEFAULT_CHECKLIST_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "checklists.json"
)


def load_checklists(
    path: Path = DEFAULT_CHECKLIST_PATH
) -> Dict:
    """Load editable checklists from JSON."""

    with path.open("r", encoding="utf-8") as file:
        checklists = json.load(file)

    if not isinstance(checklists, dict):
        raise ValueError("Checklist data must be a JSON object.")

    return checklists


def get_checklist(
    category: str,
    path: Path = DEFAULT_CHECKLIST_PATH
) -> List[str]:
    """Return five inspection items for a category."""

    checklists = load_checklists(path)

    if category not in checklists:
        raise ValueError(
            f"No checklist exists for category: {category}"
        )

    return checklists[category]["inspection_items"]
