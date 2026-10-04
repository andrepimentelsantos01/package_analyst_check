from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from .models import CheckResult


def check_allowed_values(df: pd.DataFrame, column: str, allowed: Iterable[Any]) -> CheckResult:
    if column not in df.columns:
        raise KeyError(f"Coluna ausente: {column}")
    allowed_list = list(allowed)
    unexpected = df.loc[~df[column].isin(allowed_list), column]
    counts = unexpected.value_counts(dropna=False)
    count = len(unexpected)
    return CheckResult(
        "allowed_values", "warning" if count else "success", not bool(count), count,
        f"{count} registros com valores não permitidos em {column}",
        {
            "column": column,
            "allowed": [str(item) for item in allowed_list],
            "unexpected": [
                {"value": str(value), "count": int(frequency)}
                for value, frequency in counts.items()
            ],
        },
    )


def check_expect(df: pd.DataFrame, column: str, rule: str, value: Any = None) -> CheckResult:
    if column not in df.columns:
        raise KeyError(f"Coluna ausente: {column}")
    series = df[column]
    comparisons = {
        "greater_than": lambda: series > value,
        "greater_or_equal": lambda: series >= value,
        "less_than": lambda: series < value,
        "less_or_equal": lambda: series <= value,
        "equal": lambda: series == value,
        "not_equal": lambda: series != value,
        "in": lambda: series.isin(value),
        "not_null": lambda: series.notna(),
        "unique": lambda: ~series.duplicated(),
    }
    if rule not in comparisons:
        raise ValueError(f"Regra não suportada: {rule}")
    if rule not in {"not_null", "unique"} and value is None:
        raise ValueError(f"A regra {rule} requer value")
    if rule == "in" and (isinstance(value, (str, bytes)) or not isinstance(value, Iterable)):
        raise ValueError("A regra 'in' requer uma coleção de valores")
    matched = comparisons[rule]().fillna(False)
    if rule not in {"not_null", "unique"}:
        matched &= series.notna()
    count = int((~matched).sum())
    return CheckResult(
        "expect", "warning" if count else "success", not bool(count), count,
        f"{count} registros não atenderam à regra {rule} em {column}",
        {"column": column, "rule": rule, "value": value if isinstance(value, (str, int, float, bool, type(None))) else str(value)},
    )
