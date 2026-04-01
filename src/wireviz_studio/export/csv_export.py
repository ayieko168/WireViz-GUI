"""CSV export helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def export_csv(rows: Iterable[dict], output_path: str) -> None:
    """Write BOM rows to CSV with stable headers from the first row."""
    row_list = list(rows)
    if not row_list:
        Path(output_path).write_text("", encoding="utf-8")
        return

    headers = list(row_list[0].keys())
    with Path(output_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in row_list:
            normalized = {
                key: ", ".join(str(item) for item in value) if isinstance(value, list) else value
                for key, value in row.items()
            }
            writer.writerow(normalized)
