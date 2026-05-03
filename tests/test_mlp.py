"""Testes da MLP de churn."""

from pathlib import Path

import pytest
import torch
from sklearn.model_selection import train_test_split

from churn_prediction.config import RANDOM_SEED
from churn_prediction.datasets import load_churn_telco, make_X_y
from churn_prediction.mlp import ChurnMLP, train_churn_mlp

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "Telco_customer_churn.xlsx"


def test_mlp_forward_shape() -> None:
    torch.manual_seed(0)
    m = ChurnMLP(n_features=12, hidden_layers=(16, 8), dropout=0.1)
    x = torch.randn(32, 12)
    out = m(x)
    assert out.shape == (32,)


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_train_churn_mlp_short_run() -> None:
    df = load_churn_telco(DATA_FILE)
    X, y = make_X_y(df)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_SEED, stratify=y
    )
    result = train_churn_mlp(
        X_train,
        y_train,
        X_val,
        y_val,
        max_epochs=5,
        patience=2,
        min_epochs=1,
        batch_size=512,
        hidden_layers=(32, 16),
        random_seed=RANDOM_SEED,
    )
    assert "roc_auc" in result.metrics
    assert "average_precision" in result.metrics
    assert result.metrics["epochs_trained"] >= 1
    assert len(result.history["train_loss"]) == int(result.metrics["epochs_trained"])
