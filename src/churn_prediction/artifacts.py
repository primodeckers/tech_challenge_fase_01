"""Treino rápido e exportação do pipeline logístico para uso na API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

from churn_prediction.baselines import build_preprocessor, pipeline_logistic
from churn_prediction.datasets import default_data_path, load_churn_telco, make_X_y


def export_logistic_artifact(
    artifact_dir: Path,
    *,
    data_path: Path | None = None,
) -> None:
    """Ajusta regressão logística no dataset completo e grava `pipeline.joblib` + `meta.json`."""
    path = data_path or default_data_path()
    df = load_churn_telco(path)
    X, y = make_X_y(df)
    pre = build_preprocessor(X)
    pipe = pipeline_logistic(pre)
    pipe.fit(X, y)

    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    bundle = artifact_dir / "pipeline.joblib"
    meta_path = artifact_dir / "meta.json"

    joblib.dump(pipe, bundle)
    meta: dict[str, Any] = {
        "columns": list(X.columns),
        "dataset_rows": len(X),
        "dataset_file": path.name,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
