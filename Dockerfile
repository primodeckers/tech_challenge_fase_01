# Imagem para Google Cloud Run (FIAP: deploy opcional em GCP).
# Antes do build: gerar artefactos (pipeline.joblib + meta.json) na pasta models/churn_api.
#
#   python scripts/export_logistic_artifact.py
#   docker build -t churn-api .

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY src/churn_prediction /app/src/churn_prediction

ENV PYTHONPATH=/app/src
ENV CHURN_ARTIFACT_DIR=/app/models/churn_api

# Copia o bundle exportado localmente (não versionado no Git por causa do .joblib).
COPY models/churn_api /app/models/churn_api

ENV PORT=8080
EXPOSE 8080

# Cloud Run define PORT em tempo de execução.
CMD ["sh", "-c", "exec uvicorn churn_prediction.api.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
