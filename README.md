# Tech Challenge — Fase 1 (Produtização de modelos)

Churn em telecom: baselines no sklearn, depois MLP em PyTorch, MLflow para não perder os experimentos, e FastAPI no fim — é o desenho do Tech Challenge.

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
| `notebooks/` | EDA (`01_...`) e baselines + MLflow (`02_...`) |
| `tests/` | `pytest` |
| `docs/` | Canvas (`ml_canvas.md` / `.html`), métricas (`metricas_e_limiar.md`), Model Card mais tarde |
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

## Dataset

`data/raw/Telco_customer_churn.xlsx` (Telco / IBM, uso acadêmico).

## Licença

Veja o `LICENSE`.
