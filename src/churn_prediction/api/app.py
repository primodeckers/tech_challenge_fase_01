"""Aplicação FastAPI — carrega o pipeline exportado em `artifacts.export_logistic_artifact`."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import Body, FastAPI, HTTPException

from churn_prediction.config import THRESHOLD_START
from churn_prediction.serving import ChurnPredictor


def resolve_artifact_dir(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    env = os.getenv("CHURN_ARTIFACT_DIR")
    if env:
        return Path(env).resolve()
    return (Path.cwd() / "models" / "churn_api").resolve()


def create_app(*, artifact_dir: Path | None = None) -> FastAPI:
    """`artifact_dir` opcional (útil em testes); senão usa env ou `models/churn_api` na cwd."""

    pred_holder: dict[str, ChurnPredictor | None] = {"p": None}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        root = resolve_artifact_dir(artifact_dir)
        if (root / "pipeline.joblib").is_file():
            pred_holder["p"] = ChurnPredictor.load(root)
        else:
            pred_holder["p"] = None
        yield

    app = FastAPI(
        title="Churn Telco — API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        loaded = pred_holder["p"] is not None
        return {"status": "ok", "model_loaded": loaded}

    @app.post("/predict")
    def predict(
        payload: Annotated[dict[str, Any], Body(...)],
    ) -> dict[str, Any]:
        pred = pred_holder["p"]
        if pred is None:
            raise HTTPException(
                status_code=503,
                detail=("Modelo não carregado. Rode o script export ou defina CHURN_ARTIFACT_DIR."),
            )
        try:
            p_churn = pred.predict_proba_churn(payload)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        churn_flag = p_churn >= THRESHOLD_START
        return {
            "probability_churn": p_churn,
            "threshold": THRESHOLD_START,
            "predicted_churn": churn_flag,
        }

    return app


app = create_app()
