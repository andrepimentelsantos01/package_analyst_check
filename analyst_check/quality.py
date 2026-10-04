from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from .models import CheckResult


def check_nulls(df: pd.DataFrame) -> CheckResult:
    counts = df.isna().sum()
    affected = int(df.isna().any(axis=1).sum())
    details = {
        "total_nulls": int(counts.sum()),
        "by_column": {
            str(name): {
                "count": int(count),
                "percentage": float(count / len(df) * 100) if len(df) else 0.0,
            }
            for name, count in counts.items()
        },
        "empty_columns": [str(name) for name in df.columns[df.isna().all()]],
    }
    return CheckResult(
        "nulls", "warning" if affected else "success", not bool(affected), affected,
        f"{affected} registros com valores nulos", details,
    )


def check_duplicates(df: pd.DataFrame) -> CheckResult:
    count = int(df.duplicated().sum())
    return CheckResult(
        "duplicates", "warning" if count else "success", not bool(count), count,
        f"{count} registros duplicados encontrados",
        {"percentage": float(count / len(df) * 100) if len(df) else 0.0},
    )


def check_quality(df: pd.DataFrame) -> CheckResult:
    empty = [str(name) for name in df.columns[df.isna().all()]]
    constant = [
        str(name) for position, name in enumerate(df.columns)
        if df.iloc[:, position].nunique(dropna=True) == 1
    ]
    infinite: dict[str, int] = {}
    affected = pd.Series(False, index=df.index)
    for position, name in enumerate(df.columns):
        column = df.iloc[:, position]
        if is_numeric_dtype(column.dtype):
            mask = pd.Series(np.isinf(column.to_numpy(dtype=float, na_value=np.nan)), index=df.index)
            infinite[str(name)] = int(mask.sum())
            affected |= mask
    has_issues = bool(empty or constant or affected.any())
    return CheckResult(
        "quality", "warning" if has_issues else "success", not has_issues,
        int(affected.sum()),
        "Colunas vazias, constantes ou valores infinitos encontrados" if has_issues else "Qualidade básica sem ocorrências",
        {"empty_columns": empty, "constant_columns": constant, "infinite_by_column": infinite},
    )


def check_unique_key(df: pd.DataFrame, key: str | Sequence[str]) -> CheckResult:
    keys = [key] if isinstance(key, str) else list(key)
    if not keys or len(keys) != len(set(keys)):
        raise ValueError("Informe uma chave válida sem colunas repetidas")
    missing = [name for name in keys if name not in df.columns]
    if missing:
        raise KeyError(f"Colunas de chave ausentes: {missing}")
    count = int(df.duplicated(subset=keys).sum())
    return CheckResult(
        "unique_key", "warning" if count else "success", not bool(count), count,
        f"{count} chaves duplicadas encontradas",
        {"columns": keys, "percentage": float(count / len(df) * 100) if len(df) else 0.0},
    )
