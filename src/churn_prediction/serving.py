"""Carregar artefacto treinado e produzir probabilidade de churn."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline


class ChurnPredictor:
    """Envolve o `Pipeline` sklearn e a ordem das colunas guardada no `meta.json`."""

    def __init__(self, pipeline: Pipeline, columns: list[str]) -> None:
        self.pipeline = pipeline
        self.columns = columns

    @classmethod
    def load(cls, artifact_dir: Path) -> ChurnPredictor:
        artifact_dir = artifact_dir.resolve()
        meta_path = artifact_dir / "meta.json"
        bundle = artifact_dir / "pipeline.joblib"
        if not bundle.is_file():
            raise FileNotFoundError(f"Artefacto em falta: {bundle}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        pipe = joblib.load(bundle)
        return cls(pipe, list(meta["columns"]))

    def predict_proba_churn(self, row: dict[str, Any]) -> float:
        missing = [c for c in self.columns if c not in row]
        if missing:
            raise ValueError(f"Campos em falta: {missing}")
        frame = pd.DataFrame([{c: row[c] for c in self.columns}])
        prob = self.pipeline.predict_proba(frame)[0, 1]
        return float(prob)
