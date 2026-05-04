# Tech Challenge — Fase 1 (Produtização de modelos)

Churn em telecom: EDA no notebook, baselines e Random Forest no sklearn com MLflow, MLP em PyTorch com runs no mesmo MLflow, API FastAPI a servir o pipeline de regressão logística exportado (o pré-processamento é o mesmo dos notebooks). Em `docs/` ficam o canvas, o doc de métricas e limiar, o model card, o texto de deploy (batch vs pedido) e o rascunho de monitoramento.

## Requisitos

Python **3.11** ou **3.12** costuma ser o mais seguro para o PyTorch. Se você estiver no 3.14 ou acima, veja no site do PyTorch se já há *wheel* para sua máquina. Git para versionar.

## Setup

```bash
cd tech_challenge_fase_01
python -m venv .venv
```

Ativar o venv: no Git Bash `source .venv/Scripts/activate`, no PowerShell `.\.venv\Scripts\Activate.ps1`.

Instalar tudo (projeto + ferramentas de dev):

```bash
pip install -U pip
pip install -e ".[dev]"
```

Ou `pip install -r requirements.txt` — faz o mesmo que o comando de cima com `[dev]`.

**Kernel do Jupyter:** precisa ser o Python dentro do `.venv`. Se aparecer `No module named matplotlib`, quase de certeza o kernel não é o do venv ou você ainda não instalou as dependências nele.

Se o notebook de EDA ficar com outputs enormes, no Jupyter use “Clear all outputs” e salve. Os scripts `scripts/apply_eda_interpretations.py` e `scripts/build_baselines_notebook.py` estão no `.gitignore`: você pode mantê-los só no seu computador como apoio; eles não vão para o remoto.

## Pastas (resumo)

| Pasta | Para quê |
|-------|----------|
| `src/churn_prediction/` | Código do modelo e dados |
| `data/raw/` | Excel `Telco_customer_churn.xlsx` |
| `models/` | Modelos guardados |
| `notebooks/` | EDA (`01_...`), baselines (`02_...`), MLP PyTorch (`03_...`) |
| `mlruns/` | Tracking local do MLflow (criado ao correr os notebooks; não vai para o Git) |
| `tests/` | `pytest` |
| `docs/` | Canvas, métricas/limiar, model card, `deploy_arquitetura.md`, `monitoramento.md` |
| `pyproject.toml` | Dependências, ruff, pytest |
| `requirements.txt` | Atalho `pip install -r ...` |

## Make (opcional)

```bash
make install-dev
make lint
make lint-fix
make test
```

`make run` é o mesmo que `make serve` (sobe o uvicorn da API no `127.0.0.1:8000`).

Sem make: `ruff check src tests`, `pytest`.

## EDA

Com o venv ativo e pacotes instalados, abra `notebooks/01_eda_telco_churn.ipynb` no Jupyter ou no Cursor com kernel `.venv`.

## Baselines

Abra `notebooks/02_baselines_mlflow.ipynb` e rode as células: *Dummy*, regressão logística e **Random Forest** no mesmo pré-processamento, com cinco *folds*. Cada modelo abre um run no MLflow com nome `dummy_stratified`, `logistic_regression`, `random_forest` (a Random Forest demora mais que os outros).

## MLP (PyTorch)

Abra `notebooks/03_mlp_mlflow.ipynb` e rode as células. Treino em GPU se o PyTorch detectar CUDA; senão usa CPU.

## MLflow — onde grava e como abrir a UI

Os notebooks apontam o tracking para **`mlruns/` na raiz deste repositório** (`file:.../tech_challenge_fase_01/mlruns`). Essa pasta é só na tua máquina — está no `.gitignore`, por isso quem clonar o repo precisa de **correr os notebooks outra vez** (ou copiar um `mlruns/` à parte se quiseres preservar os mesmos números noutra máquina).

Experimentos definidos em `src/churn_prediction/config.py`:

| Experimento | Notebook |
|-------------|----------|
| `telco_churn_baselines` | `02_baselines_mlflow.ipynb` |
| `telco_churn_mlp` | `03_mlp_mlflow.ipynb` |

Para ver métricas e parâmetros no browser, na **raiz** do projeto, com o venv ativo:

```bash
cd tech_challenge_fase_01
python -m mlflow ui --backend-store-uri file:./mlruns
```

(`mlflow` pode não estar no PATH; por isso `python -m mlflow`.)

Abre o URL que o comando imprimir (geralmente `http://127.0.0.1:5000`). Escolhe o experimento no menu **Experiments**. Os runs aparecem na vista de **Runs** ou em **Run evaluations**, conforme a versão da UI — **não** uses o separador **Traces** para isto (é outra funcionalidade; sem *tracing* manual fica vazio).

Documentação escrita do projeto (métricas, limiar, model card, deploy, monitoramento) está em `docs/`; vale sincronizar números do MLflow com `docs/model_card.md` quando fechares os runs finais.

## API (FastAPI)

Gera o artefato do **pipeline logístico** (regressão + pré-processamento igual ao dos notebooks) e sobe o servidor:

```bash
python scripts/export_logistic_artifact.py
uvicorn churn_prediction.api.app:app --reload --host 127.0.0.1 --port 8000
# ou, com make: make run
```

`pipeline.joblib` e `meta.json` vão para `models/churn_api/` por padrão (estão no `.gitignore`; cada clone do repo precisa gerar de novo ou copiar).

- **`GET /`** — resumo e *links* (`/health`, `/docs`, etc.).
- **`GET /health`** — `model_loaded` diz se o modelo foi encontrado ao arrancar.
- **`POST /predict`** — corpo JSON com **todas** as colunas de entrada de uma linha de cliente; resposta com `probability_churn`, `threshold` (do `config`) e `predicted_churn`.
- **`GET /docs`** — Swagger UI para experimentar o `POST /predict`.

Os pedidos vão saindo no terminal em JSON (uma linha por pedido, com caminho, método, status e tempo em ms). O header `X-Process-Time-Ms` na resposta diz quanto demorou.

Outra pasta: variável de ambiente **`CHURN_ARTIFACT_DIR`** a apontar para o diretório que tem `pipeline.joblib` e `meta.json`.

Para testar o `POST /predict`, o corpo precisa ter as mesmas colunas que o Excel (sem `Churn Label`). Um jeito rápido é copiar os valores de uma linha do dataset para um JSON — o Swagger em `/docs` ajuda a montar.

Testes da API: `pytest tests/test_api.py`.

## Dataset

`data/raw/Telco_customer_churn.xlsx` (Telco / IBM, uso acadêmico).

## Licença

Veja o `LICENSE`.
