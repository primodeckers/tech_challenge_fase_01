# Tech Challenge — Fase 1 (Produtização de modelos)

Projeto de churn em telecom no ritmo do challenge: primeiro EDA e baselines no sklearn com MLflow, depois uma MLP em PyTorch também registrada no MLflow, e por fim uma API FastAPI que serve o pipeline logístico (mesmo pré-processamento dos notebooks). Documentação extra está em `docs/` — canvas, métricas/limiar e um model card enxuto.

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
| `tests/` | `pytest` |
| `docs/` | Canvas (`ml_canvas.md` / `.html`), métricas (`metricas_e_limiar.md`), model card (`model_card.md`) |
| `pyproject.toml` | Dependências, ruff, pytest |
| `requirements.txt` | Atalho `pip install -r ...` |

## Make (opcional)

```bash
make install-dev
make lint
make lint-fix
make test
```

Sem make: `ruff check src tests`, `pytest`.

## EDA

Com o venv ativo e pacotes instalados, abra `notebooks/01_eda_telco_churn.ipynb` no Jupyter ou no Cursor com kernel `.venv`.

## Baselines e MLflow

Abra `notebooks/02_baselines_mlflow.ipynb` e rode as células. Os *runs* vão para `mlruns/` (não vai para o Git, está no `.gitignore`).

Para ver bonito: na raiz, com venv, `mlflow ui` e abra o link que aparecer (muitas vezes `http://127.0.0.1:5000`).

## MLP (PyTorch)

Abra `notebooks/03_mlp_mlflow.ipynb` e rode as células. O experimento MLflow chama-se `telco_churn_mlp` (compare com `telco_churn_baselines`). Treino em GPU se o PyTorch detectar CUDA; senão usa CPU.

## API (FastAPI)

Gera o artefato do **pipeline logístico** (regressão + pré-processamento igual ao dos notebooks) e sobe o servidor:

```bash
python scripts/export_logistic_artifact.py
uvicorn churn_prediction.api.app:app --reload --host 127.0.0.1 --port 8000
```

`pipeline.joblib` e `meta.json` vão para `models/churn_api/` por padrão (estão no `.gitignore`; cada clone do repo precisa gerar de novo ou copiar).

- **`GET /`** — resumo e *links* (`/health`, `/docs`, etc.).
- **`GET /health`** — `model_loaded` diz se o modelo foi encontrado ao arrancar.
- **`POST /predict`** — corpo JSON com **todas** as colunas de entrada de uma linha de cliente; resposta com `probability_churn`, `threshold` (do `config`) e `predicted_churn`.
- **`GET /docs`** — Swagger UI para experimentar o `POST /predict`.

Outra pasta: variável de ambiente **`CHURN_ARTIFACT_DIR`** a apontar para o diretório que tem `pipeline.joblib` e `meta.json`.

Para testar o `POST /predict`, o corpo precisa ter as mesmas colunas que o Excel (sem `Churn Label`). Um jeito rápido é copiar os valores de uma linha do dataset para um JSON — o Swagger em `/docs` ajuda a montar.

Testes da API: `pytest tests/test_api.py`.

## Dataset

`data/raw/Telco_customer_churn.xlsx` (Telco / IBM, uso acadêmico).

## Licença

Veja o `LICENSE`.
