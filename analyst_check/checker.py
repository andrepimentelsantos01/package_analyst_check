from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .dates import check_date_range
from .expectations import check_allowed_values, check_expect
from .models import CheckResult
from .numeric import check_numeric_range
from .quality import check_duplicates, check_nulls, check_quality, check_unique_key
from .report import write_csv, write_json
from .schema import check_schema


class DataCheck:
    def __init__(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("DataCheck requer um pandas.DataFrame")
        self.df = df
        self.results: list[CheckResult] = []

    def _record(self, result: CheckResult) -> CheckResult:
        self.results.append(result)
        return result

    def schema(
        self,
        required: Mapping[str, str] | Iterable[str] | None = None,
        *,
        expected_types: Mapping[str, str] | None = None,
        allow_extra: bool = True,
    ) -> CheckResult:
        return self._record(check_schema(self.df, required, expected_types=expected_types, allow_extra=allow_extra))

    def nulls(self) -> CheckResult:
        return self._record(check_nulls(self.df))

    def duplicates(self) -> CheckResult:
        return self._record(check_duplicates(self.df))

    def quality(self) -> CheckResult:
        return self._record(check_quality(self.df))

    def unique_key(self, key: str | Sequence[str]) -> CheckResult:
        return self._record(check_unique_key(self.df, key))

    def date_range(
        self,
        column: str,
        *,
        min_date: str | date | datetime | pd.Timestamp | None = None,
        max_date: str | date | datetime | pd.Timestamp | None = None,
        allow_future: bool = False,
    ) -> CheckResult:
        return self._record(check_date_range(
            self.df, column, min_date=min_date, max_date=max_date, allow_future=allow_future
        ))

    def numeric_range(
        self, column: str, *, min_value: float | None = None, max_value: float | None = None
    ) -> CheckResult:
        return self._record(check_numeric_range(
            self.df, column, min_value=min_value, max_value=max_value
        ))

    def allowed_values(self, column: str, allowed: Iterable[Any]) -> CheckResult:
        return self._record(check_allowed_values(self.df, column, allowed))

    def expect(self, column: str, rule: str, value: Any = None) -> CheckResult:
        return self._record(check_expect(self.df, column, rule, value))

    def summary(self, *, as_dict: bool = False) -> str | dict[str, Any]:
        statuses = {result.status for result in self.results}
        overall = "error" if "error" in statuses else "warning" if "warning" in statuses else "success"
        summary = {
            "name": "Analyst Check",
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "overall_status": overall,
            "checks": [result.as_dict() for result in self.results],
        }
        if as_dict:
            return summary
        lines = [
            "ANALYST CHECK", "-" * 32,
            f"Registros: {summary['rows']}",
            f"Colunas:   {summary['columns']}", "",
        ]
        lines.extend(
            f"{result.check}: {result.status.upper()} — {result.message}"
            for result in self.results
        )
        lines.extend(["", f"Status geral: {overall.upper()}"])
        return "\n".join(lines)

    def to_json(self, path: str | Path) -> Path:
        return write_json(path, self.summary(as_dict=True))

    def to_csv(self, path: str | Path) -> Path:
        return write_csv(path, [result.as_dict() for result in self.results])


def inspect_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    check = DataCheck(df)
    check.schema()
    check.nulls()
    check.duplicates()
    check.quality()
    return check.summary(as_dict=True)
