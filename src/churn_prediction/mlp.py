"""Rede MLP (PyTorch) para classificação binária de churn sobre *features* já transformadas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader, TensorDataset

from churn_prediction.baselines import build_preprocessor
from churn_prediction.config import RANDOM_SEED, THRESHOLD_START


class ChurnMLP(nn.Module):
    """Perceptrão multicamada: logits para `BCEWithLogitsLoss`."""

    def __init__(
        self,
        n_features: int,
        hidden_layers: tuple[int, ...] = (128, 64),
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = n_features
        for h in hidden_layers:
            layers.extend(
                [
                    nn.Linear(prev, h),
                    nn.ReLU(),
                    nn.Dropout(dropout),
                ]
            )
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


@dataclass(frozen=True)
class TrainMLPResult:
    model: ChurnMLP
    preprocessor: ColumnTransformer
    metrics: dict[str, Any]
    history: dict[str, list[float]]


def _set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _numpy_to_loader(
    X: np.ndarray,
    y: np.ndarray,
    *,
    batch_size: int,
    shuffle: bool,
) -> DataLoader:
    xt = torch.from_numpy(X)
    yt = torch.from_numpy(y.astype(np.float32))
    ds = TensorDataset(xt, yt)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=False)


def _evaluate_metrics(
    y_true: np.ndarray,
    prob_pos: np.ndarray,
    *,
    threshold_default: float = 0.5,
    threshold_start: float = THRESHOLD_START,
) -> dict[str, float]:
    y_hat_default = (prob_pos >= threshold_default).astype(np.int64)
    y_hat_thr = (prob_pos >= threshold_start).astype(np.int64)
    return {
        "roc_auc": float(roc_auc_score(y_true, prob_pos)),
        "average_precision": float(average_precision_score(y_true, prob_pos)),
        "f1_default_threshold": float(f1_score(y_true, y_hat_default)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_hat_default)),
        "f1_at_threshold_start": float(f1_score(y_true, y_hat_thr)),
    }


def train_churn_mlp(
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_val: pd.DataFrame,
    y_val: np.ndarray,
    *,
    preprocessor: ColumnTransformer | None = None,
    hidden_layers: tuple[int, ...] = (128, 64),
    dropout: float = 0.2,
    lr: float = 1e-3,
    batch_size: int = 256,
    max_epochs: int = 200,
    patience: int = 20,
    min_epochs: int = 5,
    device: torch.device | None = None,
    random_seed: int = RANDOM_SEED,
) -> TrainMLPResult:
    """Treina a MLP com *early stopping* na PR-AUC de validação.

    O pré-processador (`ColumnTransformer`) é ajustado **só** em `X_train`.
    """
    _set_seed(random_seed)
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

    pre = preprocessor or build_preprocessor(X_train)
    pre.fit(X_train)
    Xt_train = pre.transform(X_train).astype(np.float32)
    Xt_val = pre.transform(X_val).astype(np.float32)

    n_features = Xt_train.shape[1]
    model = ChurnMLP(n_features, hidden_layers=hidden_layers, dropout=dropout).to(device)

    n_pos = float(y_train.sum())
    n_neg = float(len(y_train) - n_pos)
    pos_weight = torch.tensor([n_neg / max(n_pos, 1.0)], device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_loader = _numpy_to_loader(
        Xt_train, y_train, batch_size=batch_size, shuffle=True
    )

    history: dict[str, list[float]] = {
        "train_loss": [],
        "val_avg_precision": [],
        "val_roc_auc": [],
    }

    best_ap = -1.0
    best_state: dict[str, Any] | None = None
    epochs_no_improve = 0
    best_epoch = 0

    for epoch in range(max_epochs):
        model.train()
        epoch_losses: list[float] = []
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            epoch_losses.append(float(loss.detach().cpu()))

        history["train_loss"].append(float(np.mean(epoch_losses)))

        model.eval()
        with torch.no_grad():
            xv = torch.from_numpy(Xt_val).to(device)
            logits_val = model(xv).cpu().numpy()
            prob_val = 1.0 / (1.0 + np.exp(-logits_val))
        mval = _evaluate_metrics(y_val, prob_val)
        history["val_avg_precision"].append(mval["average_precision"])
        history["val_roc_auc"].append(mval["roc_auc"])

        if mval["average_precision"] > best_ap:
            best_ap = mval["average_precision"]
            best_state = {
                k: v.detach().cpu().clone() for k, v in model.state_dict().items()
            }
            best_epoch = epoch + 1
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        if epoch + 1 >= min_epochs and epochs_no_improve >= patience:
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        xv = torch.from_numpy(Xt_val).to(device)
        logits_val = model(xv).cpu().numpy()
        prob_val = 1.0 / (1.0 + np.exp(-logits_val))

    final_metrics = _evaluate_metrics(y_val, prob_val)
    final_metrics["best_epoch"] = float(best_epoch)
    final_metrics["epochs_trained"] = float(epoch + 1)

    return TrainMLPResult(
        model=model.cpu(),
        preprocessor=pre,
        metrics=final_metrics,
        history=history,
    )
