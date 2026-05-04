"""Smoke test dos pipelines de baseline."""

from pathlib import Path

import pytest
from sklearn.model_selection import train_test_split

from churn_prediction.baselines import (
    build_preprocessor,
    pipeline_dummy,
    pipeline_random_forest,
)
from churn_prediction.config import RANDOM_SEED, THRESHOLD_START
from churn_prediction.datasets import load_churn_telco, make_X_y

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "Telco_customer_churn.xlsx"


def test_threshold_start_in_open_unit_interval() -> None:
    assert 0.0 < THRESHOLD_START < 1.0


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_dummy_pipeline_fits() -> None:
    df = load_churn_telco()
    X, y = make_X_y(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_SEED, stratify=y
    )
    pre = build_preprocessor(X_train)
    pipe = pipeline_dummy(pre)
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    assert len(preds) == len(y_test)


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_random_forest_pipeline_fits_small_sample() -> None:
    df = load_churn_telco(DATA_FILE).iloc[:600]
    X, y = make_X_y(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_SEED, stratify=y
    )
    pre = build_preprocessor(X_train)
    pipe = pipeline_random_forest(pre)
    pipe.fit(X_train, y_train)
    assert len(pipe.predict(X_test)) == len(y_test)
