# Deploy na Google Cloud Run (GCP)

O PDF do challenge deixa o deploy em nuvem como opcional; usei **GCP** para bater com o enunciado. Abaixo fica o que está no ar e, mais abaixo, o que alguém precisa se quiser repetir o processo noutro projeto.

## O que está publicado (este trabalho)

Serviço **churn-telco-api** na região **europe-west1**:

| O quê | URL |
|--------|-----|
| Raiz | `https://churn-telco-api-169412920601.europe-west1.run.app` |
| Swagger | `https://churn-telco-api-169412920601.europe-west1.run.app/docs` |
| Health | `https://churn-telco-api-169412920601.europe-west1.run.app/health` |

Teste rápido no terminal: `curl -sS "https://churn-telco-api-169412920601.europe-west1.run.app/health"`. Para o `POST /predict`, há um corpo de exemplo em **`examples/predict_sample.json`** (primeira linha do `X` após `make_X_y`, alinhada ao `meta.json`). Exemplo com `curl`:

```bash
curl -sS -X POST "https://churn-telco-api-169412920601.europe-west1.run.app/predict" \
  -H "Content-Type: application/json" \
  -d @examples/predict_sample.json
```

(Em Windows PowerShell podes usar `Get-Content examples/predict_sample.json -Raw | curl ...` ou colar o JSON no Swagger em `/docs`.)

### Validar o deploy

Depois do `gcloud run deploy`, confirma que o modelo carregou e que o `/predict` responde:

```bash
curl -sS "https://churn-telco-api-169412920601.europe-west1.run.app/health"
# Esperado: {"status":"ok","model_loaded":true}

curl -sS -X POST "https://churn-telco-api-169412920601.europe-west1.run.app/predict" \
  -H "Content-Type: application/json" \
  -d @examples/predict_sample.json
# Esperado: JSON com probability_churn, threshold, predicted_churn (HTTP 200)
```

Se `model_loaded` for `false` ou `/predict` devolver **503** *«Modelo não carregado»*, vê a secção **Notas** abaixo (`.gcloudignore`, export e **variável de ambiente no Git Bash**).

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
     --set-env-vars "CHURN_ARTIFACT_DIR=/app/models/churn_api"
   ```

   **Windows (Git Bash):** sem aspas, o MSYS transforma `/app/...` em `C:\Program Files\Git\app\...` e o serviço fica com `CHURN_ARTIFACT_DIR` errado → `/health` com `model_loaded: false` e 503 no `/predict`. Use aspas como acima, `MSYS_NO_PATHCONV=1`, ou corre o mesmo comando no **cmd.exe** / PowerShell.

   O `--source .` manda o código para o Cloud Build, monta a imagem e publica. No fim o CLI mostra o URL HTTPS novo.

   Se `europe-west1` não der na conta, tenta `--region us-central1` ([lista de regiões](https://cloud.google.com/run/docs/locations)).

## Notas e resolução de problemas

- **Cold start:** depois de estar parado, o primeiro pedido pode levar alguns segundos.
- **`pipeline.joblib`** não vai para o Git (`.gitignore`); cada deploy usa os ficheiros que estiverem na máquina quando corres o comando (após `export_logistic_artifact`).
- **503 *«Modelo não carregado»* ou `/health` com `model_loaded: false` — causas frequentes:**
  1. **`CHURN_ARTIFACT_DIR` errado no Cloud Run** (típico no **Git Bash** sem aspas: `/app/...` vira `C:\Program Files\Git\app\...`). Corrige com `--set-env-vars "CHURN_ARTIFACT_DIR=/app/models/churn_api"` ou redeploy a partir do **cmd.exe** / PowerShell.
  2. **`.joblib` ausente na imagem:** o `gcloud run deploy --source` respeita o `.gitignore` e **não** envia `*.joblib` a menos que exista **`.gcloudignore`** na raiz com `#!include:.gitignore` e `!models/churn_api/pipeline.joblib`. Sem isso, o *build* pode concluir mas o modelo não está em `/app/models/churn_api` dentro do container.
  3. **Export em falta:** corre `python scripts/export_logistic_artifact.py` antes do deploy para existir `models/churn_api/pipeline.joblib` localmente.
- **Memória:** comecei com `1Gi`; se o *container* reiniciar ao carregar o modelo, sobe para `--memory 2Gi`.
