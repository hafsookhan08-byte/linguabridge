"""
Very simple progress tracker. Saves scores to a local JSON file so
past attempts persist across a session and across app restarts on
the same deployment.
"""

import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "progress.json")


def _load():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def _save(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)


def add_record(section: str, band_score: float, details: str = ""):
    """Save one practice attempt: which section, what band score, when."""
    records = _load()
    records.append({
        "section": section,
        "band_score": band_score,
        "details": details,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    _save(records)


def get_records():
    return _load()
