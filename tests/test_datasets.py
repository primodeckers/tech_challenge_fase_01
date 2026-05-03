"""Testes do módulo de dados."""

import numpy as np
import pytest

from churn_prediction.datasets import (
    default_data_path,
    feature_column_types,
    load_churn_telco,
    make_X_y,
)


def test_default_path_points_to_raw_xlsx() -> None:
    p = default_data_path()
    assert p.name == "Telco_customer_churn.xlsx"
    assert "data" in p.parts and "raw" in p.parts


@pytest.mark.skipif(not default_data_path().is_file(), reason="Dataset ausente")
def test_load_and_xy_consistency() -> None:
    df = load_churn_telco()
    X, y = make_X_y(df)
    assert len(X) == len(y)
    assert "Churn Label" not in X.columns
    assert set(np.unique(y)) <= {0, 1}


@pytest.mark.skipif(not default_data_path().is_file(), reason="Dataset ausente")
def test_feature_types_cover_all_columns() -> None:
    df = load_churn_telco()
    X, _ = make_X_y(df)
    num, cat = feature_column_types(X)
    assert set(num) | set(cat) == set(X.columns)
