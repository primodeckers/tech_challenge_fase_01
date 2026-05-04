"""Aplicação FastAPI — carrega o pipeline exportado em `artifacts.export_logistic_artifact`."""

from __future__ import annotations

import json
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import Body, FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from churn_prediction.config import THRESHOLD_START
from churn_prediction.serving import ChurnPredictor

_LOG = logging.getLogger("churn_prediction.api")


def _ensure_json_logger() -> logging.Logger:
    if _LOG.handlers:
        return _LOG
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(message)s"))
    _LOG.addHandler(h)
    _LOG.setLevel(logging.INFO)
    _LOG.propagate = False
    return _LOG


def resolve_artifact_dir(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    env = os.getenv("CHURN_ARTIFACT_DIR")
    if env:
        return Path(env).resolve()
    return (Path.cwd() / "models" / "churn_api").resolve()


class LatencyLoggingMiddleware(BaseHTTPMiddleware):
    """Regista cada pedido em JSON (uma linha) e devolve latência no header."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        log = _ensure_json_logger()
        t0 = time.perf_counter()
        response = await call_next(request)
        ms = (time.perf_counter() - t0) * 1000
        line = json.dumps(
            {
                "event": "http_request",
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "latency_ms": round(ms, 2),
            },
            ensure_ascii=False,
        )
        log.info(line)
        response.headers["X-Process-Time-Ms"] = str(round(ms, 2))
        return response


def create_app(*, artifact_dir: Path | None = None) -> FastAPI:
    """`artifact_dir` opcional (útil em testes); senão usa env ou `models/churn_api` na cwd."""

    _ensure_json_logger()
    pred_holder: dict[str, ChurnPredictor | None] = {"p": None}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        root = resolve_artifact_dir(artifact_dir)
        loaded = (root / "pipeline.joblib").is_file()
        if loaded:
            pred_holder["p"] = ChurnPredictor.load(root)
        else:
            pred_holder["p"] = None
        _LOG.info(
            json.dumps(
                {
                    "event": "lifespan_startup",
                    "artifact_dir": str(root),
                    "model_loaded": pred_holder["p"] is not None,
                },
                ensure_ascii=False,
            )
        )
        yield

    app = FastAPI(
        title="Churn Telco — API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(LatencyLoggingMiddleware)

    @app.get("/")
    def root() -> dict[str, Any]:
        """Raiz só orienta: as rotas úteis são /health e POST /predict."""
        return {
            "service": "churn_prediction",
            "message": "Use GET /health ou POST /predict. Documentação interativa em /docs.",
            "links": {
                "health": "/health",
                "predict": "POST /predict",
                "docs": "/docs",
                "openapi": "/openapi.json",
            },
        }

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
