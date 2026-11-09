
"""Save and retrieve local inspection history."""

import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_HISTORY_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "inspection_history.json"
)


def load_history(
    path: Path = DEFAULT_HISTORY_PATH
) -> List[Dict[str, Any]]:
    """Load saved inspection records."""

    with path.open("r", encoding="utf-8") as file:
        history = json.load(file)

    if not isinstance(history, list):
        raise ValueError("Inspection history must be a JSON array.")

    return history


def save_inspection(
    record: Dict[str, Any],
    path: Path = DEFAULT_HISTORY_PATH
) -> None:
    """Append an inspection record."""

    history = load_history(path)
    history.append(record)

    path.write_text(
        json.dumps(history, indent=2),
        encoding="utf-8"
    )
