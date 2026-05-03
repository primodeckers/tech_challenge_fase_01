"""Pipelines de pré-processamento e baselines Scikit-Learn."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from churn_prediction.config import RANDOM_SEED
from churn_prediction.datasets import feature_column_types


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    num_cols, cat_cols = feature_column_types(X)
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "oh",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric_pipe, num_cols),
            ("cat", categorical_pipe, cat_cols),
        ]
    )


def pipeline_dummy(pre: ColumnTransformer) -> Pipeline:
    return Pipeline(
        [
            ("prep", pre),
            (
                "clf",
                DummyClassifier(strategy="stratified", random_state=RANDOM_SEED),
            ),
        ]
    )


def pipeline_logistic(pre: ColumnTransformer) -> Pipeline:
    return Pipeline(
        [
            ("prep", pre),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )
