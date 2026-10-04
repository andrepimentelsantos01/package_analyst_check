from __future__ import annotations

import pandas as pd

from analyst_check import DataCheck, reconcile


def main() -> None:
    df = pd.DataFrame({
        "id": [1, 2, 2, 4],
        "data": ["2025-01-10", "2025-02-15", "2025-02-15", None],
        "valor": [100.0, 200.0, -50.0, None],
        "status": ["PAGO", "PAGO", "INVALIDO", "PENDENTE"],
    })
    check = DataCheck(df)
    check.schema(required={"id": "int64", "valor": "float64"})
    check.nulls()
    check.duplicates()
    check.quality()
    check.unique_key("id")
    check.date_range("data", min_date="2025-01-01")
    check.numeric_range("valor", min_value=0)
    check.allowed_values("status", ["PAGO", "PENDENTE", "CANCELADO"])
    check.expect("valor", "greater_or_equal", 0)
    print(check.summary())

    target = pd.DataFrame({"id": [1, 2, 3], "valor": [100.0, 180.0, 30.0]})
    source = df.loc[[0, 1, 3], ["id", "valor"]]
    comparison = reconcile(source, target, key="id", value="valor")
    print("\nReconciliação")
    print(f"Somente na origem: {len(comparison.source_only)}")
    print(f"Somente no destino: {len(comparison.target_only)}")
    print(f"Valores diferentes: {len(comparison.value_mismatches)}")


if __name__ == "__main__":
    main()
