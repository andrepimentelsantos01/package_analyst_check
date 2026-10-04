import pandas as pd
import pytest

from analyst_check import reconcile


def test_reconcile_composite_key_and_differences() -> None:
    source = pd.DataFrame({
        "empresa": ["A", "A", "B"],
        "id": [1, 2, 1],
        "valor": [10.0, 20.0, 30.0],
    })
    target = pd.DataFrame({
        "empresa": ["A", "A", "C"],
        "id": [1, 2, 1],
        "valor": [10.0, 25.0, 40.0],
    })

    result = reconcile(source, target, key=["empresa", "id"], value="valor")

    assert result.source_rows == result.target_rows == 3
    assert result.row_difference == 0
    assert result.source_total == 60.0
    assert result.target_total == 75.0
    assert result.absolute_difference == 15.0
    assert result.percentage_difference == 25.0
    assert result.source_only["empresa"].tolist() == ["B"]
    assert result.target_only["empresa"].tolist() == ["C"]
    assert result.value_mismatches["id"].tolist() == [2]


def test_reconcile_rejects_duplicate_keys() -> None:
    source = pd.DataFrame({"id": [1, 1], "valor": [2, 3]})
    target = pd.DataFrame({"id": [1], "valor": [5]})

    with pytest.raises(ValueError, match="chaves duplicadas"):
        reconcile(source, target, key="id", value="valor")
