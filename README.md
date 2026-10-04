# Analyst Check

Analyst Check é um pacote Python para validações comuns no trabalho de análise de dados.

A ideia é evitar repetir verificações de nulos, duplicidades, schemas, datas, valores e reconciliações em cada projeto. Os resultados são objetos Python; nenhuma validação imprime dados automaticamente.

## Instalação

Requer Python 3.11 ou superior.

```powershell
pip install .
```

Para usar a demonstração diretamente na pasta do projeto:

```powershell
pip install -r requirements.txt
```

## Exemplo rápido

```python
import pandas as pd
from analyst_check import DataCheck, inspect_dataframe

df = pd.DataFrame({
    "id": [1, 2, 2],
    "data": ["2025-01-01", "2025-01-02", None],
    "valor": [100.0, -20.0, None],
})

check = DataCheck(df)
check.schema(required={"id": "int64", "valor": "float64"})
check.nulls()
check.duplicates()
check.unique_key("id")
check.date_range("data", min_date="2025-01-01")
check.numeric_range("valor", min_value=0)

print(check.summary())
resultado = check.summary(as_dict=True)
check.to_json("resultado.json")
check.to_csv("resultado.csv")

basico = inspect_dataframe(df)
```

Cada método retorna um `CheckResult` com `check`, `status`, `passed`, `rows_affected`, `message` e `details`. `inspect_dataframe` executa schema, nulos, duplicidades e qualidade básica e retorna um resumo em dicionário. `summary()` reúne somente as verificações já chamadas no objeto.

## Validações

- `schema`: linhas, colunas, tipos, memória aproximada, colunas obrigatórias e extras opcionais. Tipos equivalentes da mesma família são aceitos.
- `nulls` e `duplicates`: contagens e percentuais.
- `quality`: colunas vazias ou constantes e valores infinitos em colunas numéricas.
- `unique_key`: chave simples ou composta. Conta ocorrências repetidas após a primeira.
- `date_range`: extremos observados, nulos, datas inválidas, futuras e fora dos limites. Datas futuras são sinalizadas por padrão; use `allow_future=True` quando fizerem parte da base.
- `numeric_range`: limites, negativos, zeros, nulos, infinitos e estatísticas dos valores finitos.
- `allowed_values`: valores fora da lista e suas frequências.
- `expect`: `greater_than`, `greater_or_equal`, `less_than`, `less_or_equal`, `equal`, `not_equal`, `in`, `not_null` e `unique`.

Nulos são contados como falhas nas regras de data, valor numérico e expectativas de comparação. `status` pode ser `success`, `warning` ou `error`. Erros de schema recebem `error`; dados fora das regras recebem `warning`. Colunas inexistentes e argumentos inválidos geram exceções Python.

## Reconciliação

```python
from analyst_check import reconcile

resultado = reconcile(
    source=df_origem,
    target=df_destino,
    key=["empresa", "id_transacao"],
    value="valor",
)

print(resultado.source_total, resultado.target_total)
print(resultado.source_only)
print(resultado.target_only)
print(resultado.value_mismatches)
```

O resultado traz contagens, totais, diferenças e três DataFrames para análise posterior. A diferença percentual usa o valor absoluto do total da origem como base; quando esse total é zero, retorna `0.0` se o destino também for zero e `None` caso contrário. As chaves precisam ser únicas e não nulas em cada base para evitar associações ambíguas.

## Execução local

Na raiz do projeto, no PowerShell:

```powershell
.\start --local
```

O comando usa o Python do ambiente atual e mostra uma pequena base com problemas intencionais. Não instala dependências.

## Estrutura

```text
analyst_check/    pacote e API pública
examples/         demonstração local
tests/            testes unitários
pyproject.toml    metadados e configuração de build
setup.py          entrada mínima de compatibilidade
start.cmd         execução local no Windows
```

## Gerar o pacote depois

Quando quiser gerar uma wheel e um source distribution:

```powershell
pip install build
python -m build
```

Os arquivos serão criados em `dist/`. Nada é publicado automaticamente.

## Licença

MIT. Veja [LICENSE](LICENSE).
