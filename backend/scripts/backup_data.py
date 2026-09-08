"""Create a timestamped backup of the local database and Excel register."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "backups"
DATABASE = ROOT / "pib_assessment.db"
EXCEL = ROOT / "data" / "assessments.xlsx"


def main() -> None:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_DIR / stamp
    destination.mkdir(parents=True, exist_ok=True)

    copied = 0
    for source in (DATABASE, EXCEL):
        if source.exists():
            shutil.copy2(source, destination / source.name)
            copied += 1

    if copied == 0:
        raise SystemExit("No database or Excel data found to back up.")
    print(f"Created {copied} backup file(s) in {destination}")


if __name__ == "__main__":
    main()
