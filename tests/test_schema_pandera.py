"""Schema Pandera alinhado às colunas de `make_X_y` (entrada do modelo / API)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pandera.errors
import pytest

from churn_prediction.datasets import load_churn_telco, make_X_y
from churn_prediction.schemas import feature_row_schema

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "Telco_customer_churn.xlsx"


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_feature_row_schema_accepts_model_columns() -> None:
    df = load_churn_telco(DATA_FILE)
    X, _ = make_X_y(df)
    row = json.loads(X.iloc[[0]].to_json(orient="records"))[0]
    schema = feature_row_schema(list(X.columns))
    frame = pd.DataFrame([row])
    schema.validate(frame)


def test_feature_row_schema_strict_rejects_extra_column() -> None:
    schema = feature_row_schema(["a", "b"])
    bad = pd.DataFrame([{"a": 1, "b": 2, "extra": 3}])
    with pytest.raises(pandera.errors.SchemaErrors):
        schema.validate(bad)
