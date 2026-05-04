# Deploy na Google Cloud Run (GCP)

O PDF do challenge deixa o deploy em nuvem como opcional; usei **GCP** para bater com o enunciado. Abaixo fica o que está no ar e, mais abaixo, o que alguém precisa se quiser repetir o processo noutro projeto.

## O que está publicado (este trabalho)

Serviço **churn-telco-api** na região **europe-west1**:

| O quê | URL |
|--------|-----|
| Raiz | `https://churn-telco-api-169412920601.europe-west1.run.app` |
| Swagger | `https://churn-telco-api-169412920601.europe-west1.run.app/docs` |
| Health | `https://churn-telco-api-169412920601.europe-west1.run.app/health` |

Teste rápido no terminal: `curl -sS "https://churn-telco-api-169412920601.europe-west1.run.app/health"`. O `POST /predict` funciona como no ambiente local; o corpo continua a ser uma linha de *features* alinhada ao `meta.json` do export.

## O que a Google exige

Conta com **faturação** ligada ao projeto (mesmo a usar *free tier*, o Cloud Run costuma bloquear sem *billing*). Instalei o [`gcloud` CLI](https://cloud.google.com/sdk/docs/install) e ativei as APIs `run`, `artifactregistry` e `cloudbuild` depois de associar o cartão.

## Se fores fazer o teu deploy outra vez

1. Com o Excel em `data/raw/`, na raiz do repositório:

   ```bash
   python scripts/export_logistic_artifact.py
   ```

   Isto gera `models/churn_api/pipeline.joblib` e `meta.json`. O `Dockerfile` copia essa pasta; sem o `.joblib` o build rebenta.

2. Na mesma pasta onde está o `Dockerfile`:

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

   O `--source .` manda o código para o Cloud Build, monta a imagem e publica. No fim o CLI mostra o URL HTTPS novo.

   Se `europe-west1` não der na conta, tenta `--region us-central1` ([lista de regiões](https://cloud.google.com/run/docs/locations)).

## Notas

- **Cold start:** depois de estar parado, o primeiro pedido pode levar alguns segundos.
- **`pipeline.joblib`** não vai para o Git (`.gitignore`); cada deploy usa os ficheiros que estiverem na máquina quando corres o comando.
- Memória: comecei com `1Gi`; se o *container* reiniciar ao carregar o modelo, sobe para `--memory 2Gi`.
