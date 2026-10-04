from __future__ import annotations

from collections.abc import Iterable, Mapping

import pandas as pd
from pandas.api import types as ptypes

from .models import CheckResult


def _equivalent_dtype(actual: object, expected: str) -> bool:
    try:
        wanted = ptypes.pandas_dtype(expected)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Tipo esperado inválido: {expected!r}") from exc

    if ptypes.is_dtype_equal(actual, wanted):
        return True

    families = (
        ptypes.is_integer_dtype,
        ptypes.is_float_dtype,
        ptypes.is_bool_dtype,
        ptypes.is_datetime64_any_dtype,
        ptypes.is_timedelta64_dtype,
    )
    if any(predicate(actual) and predicate(wanted) for predicate in families):
        return True
    return ptypes.is_string_dtype(actual) and ptypes.is_string_dtype(wanted)


def check_schema(
    df: pd.DataFrame,
    required: Mapping[str, str] | Iterable[str] | None = None,
    *,
    expected_types: Mapping[str, str] | None = None,
    allow_extra: bool = True,
) -> CheckResult:
    if required is None:
        required_names: set[str] = set()
        types: dict[str, str] = {}
    elif isinstance(required, Mapping):
        required_names = set(required)
        types = dict(required)
    elif isinstance(required, str):
        required_names = {required}
        types = {}
    else:
        required_names = set(required)
        types = {}

    types.update(expected_types or {})
    columns = set(df.columns)
    missing = sorted(required_names - columns)
    missing_typed = sorted(set(types) - columns)
    missing = sorted(set(missing) | set(missing_typed))
    unexpected = sorted(columns - (required_names | set(types))) if not allow_extra else []
    duplicate_names = [str(name) for name in df.columns[df.columns.duplicated()].unique()]
    wrong_types = {
        name: {"expected": expected, "actual": str(df[name].dtype)}
        for name, expected in types.items()
        if name in columns and name not in duplicate_names
        and not _equivalent_dtype(df[name].dtype, expected)
    }
    passed = not (missing or unexpected or duplicate_names or wrong_types)
    return CheckResult(
        check="schema",
        status="success" if passed else "error",
        passed=passed,
        rows_affected=0,
        message="Schema válido" if passed else "Schema diferente do esperado",
        details={
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": [str(name) for name in df.columns],
            "dtypes": {str(name): str(dtype) for name, dtype in df.dtypes.items()},
            "memory_bytes": int(df.memory_usage(index=True, deep=True).sum()),
            "missing_columns": missing,
            "unexpected_columns": unexpected,
            "duplicate_columns": duplicate_names,
            "wrong_types": wrong_types,
        },
    )
