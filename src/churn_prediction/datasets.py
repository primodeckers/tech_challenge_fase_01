"""Carregamento e preparação do dataset Telco churn para modelação tabular."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Colunas que não entram no X por decisão de modelagem (IDs, alvo, *leakage* provável).
DROP_FOR_MODELING: list[str] = [
    "CustomerID",
    "Churn Label",
    "Churn Reason",
    "Churn Score",
    "CLTV",
    "Churn Value",
    "Lat Long",
]


def default_data_path(root: Path | None = None) -> Path:
    """Caminho para o Excel em `data/raw/` relativamente à raiz do repositório."""
    if root is None:
        root = Path(__file__).resolve().parents[2]
    return root / "data" / "raw" / "Telco_customer_churn.xlsx"


def load_churn_telco(path: Path | None = None) -> pd.DataFrame:
    """Lê o Excel e trata `Total Charges` numérico; remove linhas sem total válido."""
    path = path or default_data_path()
    df = pd.read_excel(path)
    df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")
    df = df.dropna(subset=["Total Charges"]).reset_index(drop=True)
    return df


def make_X_y(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """Constrói matriz de *features* e vetor alvo binário (1 = churn)."""
    if "Churn Label" not in df.columns:
        raise KeyError("Esperada coluna 'Churn Label' no DataFrame.")
    y = (df["Churn Label"] == "Yes").astype(np.int64).values
    to_drop = [c for c in DROP_FOR_MODELING if c in df.columns]
    X = df.drop(columns=to_drop).copy()
    return X, y


def feature_column_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Separa nomes de colunas numéricas vs. não numéricas para o `ColumnTransformer`."""
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]
    return num_cols, cat_cols
