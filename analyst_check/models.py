from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

Status = Literal["success", "warning", "error"]


@dataclass(frozen=True)
class CheckResult:
    check: str
    status: Status
    passed: bool
    rows_affected: int
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "status": self.status,
            "passed": self.passed,
            "rows_affected": self.rows_affected,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class ReconciliationResult:
    source_rows: int
    target_rows: int
    row_difference: int
    source_total: float
    target_total: float
    absolute_difference: float
    percentage_difference: float | None
    source_only: pd.DataFrame
    target_only: pd.DataFrame
    value_mismatches: pd.DataFrame

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_rows": self.source_rows,
            "target_rows": self.target_rows,
            "row_difference": self.row_difference,
            "source_total": self.source_total,
            "target_total": self.target_total,
            "absolute_difference": self.absolute_difference,
            "percentage_difference": self.percentage_difference,
            "source_only": self.source_only.to_dict(orient="records"),
            "target_only": self.target_only.to_dict(orient="records"),
            "value_mismatches": self.value_mismatches.to_dict(orient="records"),
        }
