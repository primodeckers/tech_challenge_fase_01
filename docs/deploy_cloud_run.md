# Deploy na Google Cloud Run (GCP)

Alinha ao PDF do Tech Challenge: **deploy opcional em nuvem** com **endpoint público** (bónus), usando **GCP**.

## Pré-requisitos

1. Conta Google com **faturação ativa** no projeto (Cloud Run tem *free tier*, mas a GCP costuma pedir cartão para criar o projeto).
2. [`gcloud` CLI](https://cloud.google.com/sdk/docs/install) instalado.
3. Neste repositório, com o Excel em `data/raw/`, gerar o artefacto **antes** do build Docker:

   ```bash
   cd tech_challenge_fase_01
   python scripts/export_logistic_artifact.py
   ```

   Isto cria `models/churn_api/pipeline.joblib` e `meta.json`. Sem isto, o `docker build` falha no `COPY models/churn_api`.

## Deploy direto a partir do código (recomendado)

Na raiz do projeto (`tech_challenge_fase_01`), com `Dockerfile` presente:

```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID

gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud run deploy churn-telco-api \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars CHURN_ARTIFACT_DIR=/app/models/churn_api
```

O comando `--source .` envia o contexto para o **Cloud Build**, constrói a imagem com o `Dockerfile` e faz o deploy. No fim, o CLI imprime a **URL HTTPS** do serviço — é essa que podes entregar como “deploy em nuvem”.

Se a região `europe-west1` não estiver disponível na conta, troca por `us-central1` ou outra [região Cloud Run](https://cloud.google.com/run/docs/locations).

## Testar

```bash
curl -sS "URL_DO_SERVICO/health"
```

Para `/predict`, usa o mesmo corpo JSON que no Swagger local (`/docs`).

## Notas

- **Cold start:** o primeiro pedido após inatividade pode demorar alguns segundes no *tier* gratuito.
- **Memória:** se o *container* reiniciar ou falhar ao carregar o `pipeline.joblib`, aumenta para `--memory 2Gi`.
- **Segredo:** não commits `pipeline.joblib` no Git (`.gitignore`); o build usa sempre os ficheiros **na tua máquina** no momento do deploy.
