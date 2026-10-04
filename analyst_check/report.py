from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def write_json(path: str | Path, summary: dict[str, Any]) -> Path:
    target = Path(path)
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
    return target


def write_csv(path: str | Path, checks: list[dict[str, Any]]) -> Path:
    target = Path(path)
    with target.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(
            output, fieldnames=["check", "status", "passed", "rows_affected", "message", "details"]
        )
        writer.writeheader()
        for check in checks:
            writer.writerow({
                **check,
                "details": json.dumps(check["details"], ensure_ascii=False, default=_json_default),
            })
    return target
