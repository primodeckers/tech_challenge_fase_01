# Model card — churn Telco (Fase 1)

Resumo do que entra na API e do que fica só nos notebooks. Atualizem os números de métrica aqui quando fecharem o relatório.

## Para que serve

Estimar probabilidade de churn por cliente (sim/não no sentido do rótulo histórico `Churn Label` do Excel IBM Telco). A ideia é priorizar quem merece contato de retenção, não substituir decisão humana em caso limítrofe.

## Dados de treino

- Arquivo: `data/raw/Telco_customer_churn.xlsx` (7032 linhas no recorte que usamos; meta exportada também guarda `dataset_rows` para conferência).
- Variáveis: demo, serviços, contrato, cobrança (*Monthly Charges*, *Total Charges*), *tenure*, etc. — mesmas colunas que a API espera no JSON (sem o rótulo).

## O que a API carrega

- **Modelo servido:** pipeline sklearn com pré-processamento (incluindo *one-hot* e tratamento de tipos) + **regressão logística**. Exportado por `scripts/export_logistic_artifact.py` para `models/churn_api/` (`pipeline.joblib`, `meta.json`). O `.joblib` não vai para o Git por política do repo — cada ambiente gera de novo ou copia.
- **Não é a MLP:** o treino PyTorch está em `03_mlp_mlflow.ipynb` / `src/churn_prediction/mlp.py` para comparar no MLflow; a API foi amarrada à logística por simplicidade de *deploy* e reprodutibilidade no challenge.

## Métricas e limiar

- Comparativos principais nos notebooks: PR-AUC, F1 na classe churn, ROC-AUC, etc. — ver MLflow e `docs/metricas_e_limiar.md`.
- **Limiar de decisão** para classe binária na API: `THRESHOLD_START` em `src/churn_prediction/config.py` (hoje 0,35), alinhado à discussão de custo FP/FN do grupo. A resposta do `POST /predict` inclui `probability_churn`, `threshold` e `predicted_churn`.

## Limitações óbvias

- Dataset público e antigo; não reflete necessariamente a base real de uma operadora hoje.
- Campos como satisfação ou qualidade de rede não existem no Excel — o modelo só vê o que está na planilha.
- **Governança:** não há monitoramento de *drift* nem retreino automático neste entregável.

## Contato / reprodutibilidade

- *Seeds* e folds: `config.py`. Experimentos: pastas `mlruns/` (local, gitignored). Para quem avalia o projeto: notebooks numerados na pasta `notebooks/` e testes em `tests/`.
