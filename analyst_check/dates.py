from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from .models import CheckResult

DateValue = str | date | datetime | pd.Timestamp


def _timestamp(value: DateValue | None) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Data limite inválida: {value!r}") from exc
    if pd.isna(timestamp):
        raise ValueError("A data limite não pode ser nula")
    return timestamp.tz_localize("UTC") if timestamp.tzinfo is None else timestamp.tz_convert("UTC")


def check_date_range(
    df: pd.DataFrame,
    column: str,
    *,
    min_date: DateValue | None = None,
    max_date: DateValue | None = None,
    allow_future: bool = False,
) -> CheckResult:
    if column not in df.columns:
        raise KeyError(f"Coluna ausente: {column}")
    lower, upper = _timestamp(min_date), _timestamp(max_date)
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("min_date deve ser menor ou igual a max_date")

    original = df[column]
    converted = pd.to_datetime(original, errors="coerce", utc=True)
    nulls = original.isna()
    invalid = converted.isna() & ~nulls
    before = converted < lower if lower is not None else pd.Series(False, index=df.index)
    after = converted > upper if upper is not None else pd.Series(False, index=df.index)
    future = converted > pd.Timestamp.now(tz="UTC")
    affected = nulls | invalid | before | after | (future if not allow_future else False)
    valid = converted.dropna()
    count = int(affected.sum())
    return CheckResult(
        "date_range", "warning" if count else "success", not bool(count), count,
        f"{count} registros com datas inválidas ou fora dos limites",
        {
            "column": column,
            "observed_min": valid.min().isoformat() if not valid.empty else None,
            "observed_max": valid.max().isoformat() if not valid.empty else None,
            "nulls": int(nulls.sum()),
            "invalid": int(invalid.sum()),
            "before_min": int(before.sum()),
            "after_max": int(after.sum()),
            "future": int(future.sum()),
            "min_date": lower.isoformat() if lower is not None else None,
            "max_date": upper.isoformat() if upper is not None else None,
        },
    )
