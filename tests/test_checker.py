import numpy as np
import pandas as pd
import pytest

from analyst_check import DataCheck, inspect_dataframe


def test_nulls_duplicates_and_summary() -> None:
    df = pd.DataFrame({"id": [1, 1, 2], "valor": [10.0, 10.0, None]})
    check = DataCheck(df)

    assert check.nulls().rows_affected == 1
    assert check.duplicates().rows_affected == 1
    summary = check.summary(as_dict=True)
    assert summary["overall_status"] == "warning"
    assert len(summary["checks"]) == 2


def test_schema_accepts_nullable_integer_and_detects_missing_or_extra() -> None:
    df = pd.DataFrame({"id": pd.Series([1, None], dtype="Int64"), "extra": [1, 2]})
    check = DataCheck(df)

    valid = check.schema(required={"id": "int64"})
    invalid = check.schema(required={"id": "int64", "data": "datetime64[ns]"}, allow_extra=False)
    assert valid.passed
    assert invalid.status == "error"
    assert invalid.details["missing_columns"] == ["data"]
    assert invalid.details["unexpected_columns"] == ["extra"]


def test_unique_key_supports_composite_keys() -> None:
    df = pd.DataFrame({"empresa": ["A", "A", "B"], "id": [1, 1, 1]})
    result = DataCheck(df).unique_key(["empresa", "id"])

    assert result.rows_affected == 1
    assert result.details["percentage"] == pytest.approx(100 / 3)


def test_numeric_range_reports_limits_and_statistics() -> None:
    df = pd.DataFrame({"valor": [-2.0, 0.0, 5.0, np.inf, np.nan]})
    result = DataCheck(df).numeric_range("valor", min_value=0, max_value=4)

    assert result.rows_affected == 4
    assert result.details["below_min"] == 1
    assert result.details["above_max"] == 1
    assert result.details["infinite"] == 1
    assert result.details["statistics"]["sum"] == 3.0


def test_date_range_counts_null_invalid_and_outside_limits() -> None:
    df = pd.DataFrame({"data": ["2025-01-01", "2024-12-31", "invalida", None]})
    result = DataCheck(df).date_range(
        "data", min_date="2025-01-01", max_date="2025-12-31", allow_future=True
    )

    assert result.rows_affected == 3
    assert result.details["before_min"] == 1
    assert result.details["invalid"] == 1
    assert result.details["nulls"] == 1


def test_allowed_values_and_expectations() -> None:
    df = pd.DataFrame({"status": ["PAGO", "ERRO", "ERRO"], "valor": [1, 0, None]})
    check = DataCheck(df)

    allowed = check.allowed_values("status", ["PAGO", "PENDENTE"])
    expected = check.expect("valor", "greater_than", 0)
    membership = check.expect("status", "in", ["PAGO"])
    assert allowed.rows_affected == 2
    assert allowed.details["unexpected"] == [{"value": "ERRO", "count": 2}]
    assert expected.rows_affected == 2
    assert membership.rows_affected == 2


def test_inspect_dataframe_runs_basic_checks() -> None:
    df = pd.DataFrame({"id": [1, 1], "valor": [np.inf, np.inf]})
    summary = inspect_dataframe(df)

    assert [item["check"] for item in summary["checks"]] == [
        "schema", "nulls", "duplicates", "quality"
    ]
    assert summary["overall_status"] == "warning"
