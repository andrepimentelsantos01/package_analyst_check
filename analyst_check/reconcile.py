from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from .models import ReconciliationResult


def reconcile(
    source: pd.DataFrame,
    target: pd.DataFrame,
    key: str | Sequence[str],
    value: str,
) -> ReconciliationResult:
    """Compara totais e valores por chave única entre duas bases."""
    keys = [key] if isinstance(key, str) else list(key)
    if not keys or len(keys) != len(set(keys)) or value in keys:
        raise ValueError("Informe uma chave válida, distinta da coluna de valor")
    for label, frame in (("source", source), ("target", target)):
        if not isinstance(frame, pd.DataFrame):
            raise TypeError(f"{label} deve ser um pandas.DataFrame")
        missing = [name for name in [*keys, value] if name not in frame.columns]
        if missing:
            raise KeyError(f"Colunas ausentes em {label}: {missing}")
        if frame[keys].isna().any().any():
            raise ValueError(f"{label} contém chaves nulas")
        if frame.duplicated(subset=keys).any():
            raise ValueError(f"{label} contém chaves duplicadas")

    source_values = pd.to_numeric(source[value], errors="raise")
    target_values = pd.to_numeric(target[value], errors="raise")
    for label, values in (("source", source_values), ("target", target_values)):
        if np.isinf(values.to_numpy(dtype=float, na_value=np.nan)).any():
            raise ValueError(f"{label} contém valores infinitos em {value}")

    occupied = set(keys) | {value}
    source_name, target_name, indicator_name = "__source_value", "__target_value", "__match"
    while any(name in occupied for name in (source_name, target_name, indicator_name)):
        source_name += "_"
        target_name += "_"
        indicator_name += "_"
    source_output, target_output = "source_value", "target_value"
    while source_output in keys or target_output in keys:
        source_output += "_"
        target_output += "_"
    difference_output = "difference"
    while difference_output in keys or difference_output in (source_output, target_output):
        difference_output += "_"
    left = source[keys].copy()
    left[source_name] = source_values
    right = target[keys].copy()
    right[target_name] = target_values
    merged = left.merge(
        right, on=keys, how="outer", indicator=indicator_name, validate="one_to_one"
    )
    source_only = merged.loc[merged[indicator_name] == "left_only", [*keys, source_name]].rename(
        columns={source_name: value}
    ).reset_index(drop=True)
    target_only = merged.loc[merged[indicator_name] == "right_only", [*keys, target_name]].rename(
        columns={target_name: value}
    ).reset_index(drop=True)

    matched = merged[indicator_name] == "both"
    same = merged[source_name].eq(merged[target_name]).fillna(False)
    both_null = merged[source_name].isna() & merged[target_name].isna()
    value_mismatches = merged.loc[
        matched & ~(same | both_null), [*keys, source_name, target_name]
    ].rename(columns={source_name: source_output, target_name: target_output}).reset_index(drop=True)
    value_mismatches[difference_output] = (
        value_mismatches[source_output] - value_mismatches[target_output]
    )

    source_total = float(source_values.sum())
    target_total = float(target_values.sum())
    absolute_difference = abs(source_total - target_total)
    percentage_difference = (
        absolute_difference / abs(source_total) * 100 if source_total != 0 else
        (0.0 if target_total == 0 else None)
    )
    return ReconciliationResult(
        source_rows=len(source),
        target_rows=len(target),
        row_difference=len(source) - len(target),
        source_total=source_total,
        target_total=target_total,
        absolute_difference=absolute_difference,
        percentage_difference=percentage_difference,
        source_only=source_only,
        target_only=target_only,
        value_mismatches=value_mismatches,
    )
