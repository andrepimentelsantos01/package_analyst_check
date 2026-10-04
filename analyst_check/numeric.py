from __future__ import annotations

import numpy as np
import pandas as pd

from .models import CheckResult


def check_numeric_range(
    df: pd.DataFrame,
    column: str,
    *,
    min_value: float | None = None,
    max_value: float | None = None,
) -> CheckResult:
    if column not in df.columns:
        raise KeyError(f"Coluna ausente: {column}")
    if min_value is not None and max_value is not None and min_value > max_value:
        raise ValueError("min_value deve ser menor ou igual a max_value")

    original = df[column]
    numeric = pd.to_numeric(original, errors="coerce")
    values = pd.Series(numeric.to_numpy(dtype=float, na_value=np.nan), index=df.index)
    nulls = original.isna()
    invalid = numeric.isna() & ~nulls
    infinite = pd.Series(np.isinf(values.to_numpy()), index=df.index)
    finite = pd.Series(np.isfinite(values.to_numpy()), index=df.index)
    below = (values < min_value) & finite if min_value is not None else pd.Series(False, index=df.index)
    above = (values > max_value) & finite if max_value is not None else pd.Series(False, index=df.index)
    affected = nulls | invalid | infinite | below | above
    usable = values[finite]
    count = int(affected.sum())
    stats = {
        "min": float(usable.min()) if not usable.empty else None,
        "max": float(usable.max()) if not usable.empty else None,
        "mean": float(usable.mean()) if not usable.empty else None,
        "median": float(usable.median()) if not usable.empty else None,
        "sum": float(usable.sum()) if not usable.empty else None,
        "std": float(usable.std()) if len(usable) > 1 else None,
    }
    return CheckResult(
        "numeric_range", "warning" if count else "success", not bool(count), count,
        f"{count} registros com valores numéricos inválidos ou fora dos limites",
        {
            "column": column,
            "min_value": min_value,
            "max_value": max_value,
            "below_min": int(below.sum()),
            "above_max": int(above.sum()),
            "negative": int(((values < 0) & finite).sum()),
            "zero": int(((values == 0) & finite).sum()),
            "nulls": int(nulls.sum()),
            "invalid": int(invalid.sum()),
            "infinite": int(infinite.sum()),
            "statistics": stats,
        },
    )
