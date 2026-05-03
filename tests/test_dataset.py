"""Testes de arquivo e schema mínimo do dataset bruto (Telco churn)."""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "raw" / "Telco_customer_churn.xlsx"


def test_raw_dataset_file_exists() -> None:
    assert DATA_PATH.is_file(), f"Esperado arquivo em {DATA_PATH}"


def test_raw_dataset_loads_and_meets_challenge_size() -> None:
    df = pd.read_excel(DATA_PATH)
    assert len(df) >= 5000, "Guia sugere dataset com pelo menos 5000 registos"
    assert df.shape[1] >= 10, "Guia sugere pelo menos 10 features"


def test_raw_dataset_has_churn_columns() -> None:
    df = pd.read_excel(DATA_PATH, nrows=1)
    cols = set(df.columns.astype(str))
    assert "Churn Label" in cols or "Churn Value" in cols, (
        "Colunas de churn esperadas (Churn Label / Churn Value) não encontradas"
    )
