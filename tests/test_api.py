"""Testes da API FastAPI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from churn_prediction.api.app import create_app
from churn_prediction.artifacts import export_logistic_artifact

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "Telco_customer_churn.xlsx"


def test_root(tmp_path: Path) -> None:
    app = create_app(artifact_dir=tmp_path)
    with TestClient(app) as client:
        r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "churn_prediction"
    assert body["links"]["health"] == "/health"


def test_health_sem_modelo(tmp_path: Path) -> None:
    app = create_app(artifact_dir=tmp_path)
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is False


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_health_com_modelo(tmp_path: Path) -> None:
    bundle = tmp_path / "api_bundle"
    export_logistic_artifact(bundle, data_path=DATA_FILE)
    app = create_app(artifact_dir=bundle)
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["model_loaded"] is True


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_predict_422_campos_em_falta(tmp_path: Path) -> None:
    bundle = tmp_path / "api_bundle"
    export_logistic_artifact(bundle, data_path=DATA_FILE)
    app = create_app(artifact_dir=bundle)
    with TestClient(app) as client:
        r = client.post("/predict", json={})
    assert r.status_code == 422
    assert "Campos em falta" in r.json()["detail"]


@pytest.mark.skipif(not DATA_FILE.is_file(), reason="Dataset ausente")
def test_predict_200_payload_valido(tmp_path: Path) -> None:
    bundle = tmp_path / "api_bundle"
    export_logistic_artifact(bundle, data_path=DATA_FILE)
    app = create_app(artifact_dir=bundle)

    from churn_prediction.datasets import load_churn_telco, make_X_y

    df = load_churn_telco(DATA_FILE)
    X, _ = make_X_y(df)
    payload = json.loads(X.iloc[[0]].to_json(orient="records"))[0]

    with TestClient(app) as client:
        r = client.post("/predict", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "probability_churn" in body
    assert "threshold" in body
    assert "predicted_churn" in body
    assert 0.0 <= body["probability_churn"] <= 1.0
