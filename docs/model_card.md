# Model card — churn Telco

Quem avaliar o repo sem mergulhar no código deve conseguir ler isto em cinco minutos. As tabelas em **Performance** vêm dos *runs* no MLflow na máquina onde se treinou (regenera-se ao voltar a correr os notebooks).

## O que é isto

Pipeline sklearn: o mesmo pré-processamento dos notebooks + regressão logística, gerado com `scripts/export_logistic_artifact.py`. Dados: `Telco_customer_churn.xlsx` (`Telco_customer_churn`, o IBM Telco que aparece em quase todo o curso); depois de limpar `Total Charges` inválido ficam ~7032 linhas. Alvo: `Churn Label` == `Yes`.

A MLP em PyTorch está no `03_mlp_mlflow.ipynb` e em `src/churn_prediction/mlp.py`, com runs no MLflow. A API não usa a MLP: exportamos a logística porque é leve, rápida de servir e fácil de defender oralmente.

## Uso pretendido

Probabilidade de churn para ordenar filas de retenção. Caso dúbio, assume-se revisão humana ou regra de negócio — o modelo não manda fechar contrato.

## Performance

**Baselines** — `02_baselines_mlflow.ipynb`, CV estratificada 5 *folds*, mesmos dados e pré-processamento. No MLflow as métricas `*_mean` são a média dos *folds*; **PR-AUC** é o `average_precision_mean`. **F1 @ 0,35** é `f1_at_threshold_start` (probabilidades *out-of-fold*, limiar do `config`).

| Modelo | PR-AUC | ROC-AUC | F1 (corte 0,5) | Balanced acc. | F1 @ 0,35 |
|--------|--------|---------|----------------|---------------|-----------|
| Dummy (estratificado) | 0,260 | 0,484 | 0,243 | 0,484 | 0,243 |
| Regressão logística | 0,654 | 0,850 | 0,601 | 0,726 | 0,636 |
| Random Forest | 0,664 | 0,854 | 0,642 | 0,770 | 0,616 |

Nestes dados a Random Forest ganha PR-AUC e *balanced accuracy* face à logística; o F1 no **0,35** continua mais alto na logística (0,636 vs 0,616), o que já esperávamos — o corte de negócio não favorece sempre o mesmo modelo que o melhor PR-AUC bruto.

**MLP (PyTorch)** — `03_mlp_mlflow.ipynb`, conjunto de validação com *early stopping*, run MLflow `mlp_dropout02` (nome pode mudar se renomearem o run):

| Métrica | Valor |
|---------|-------|
| PR-AUC | 0,622 |
| ROC-AUC | 0,837 |
| F1 (corte default do modelo) | 0,608 |
| F1 @ 0,35 (`THRESHOLD_START`) | 0,592 |
| Balanced accuracy | 0,746 |

**API em produção (exercício):** só a **regressão logística** exportada — não é automaticamente o modelo com melhor PR-AUC da tabela; foi escolha de simplicidade e tempo.

---

*Última extração dos artefactos em `mlruns/` local; não estão no Git.*

## Dados

As 26 colunas de entrada batem com o `meta.json` do export (lista do que se tirou antes do `X` em `DROP_FOR_MODELING` no `datasets.py`, por causa de ID, alvo e colunas que cheiram a *leakage*). Baselines: CV estratificada. MLP: split treino/validação com early stopping, como no notebook.

## Onde o modelo engana ou fica cego

Planilha pública e antiga: não representa a carteira de uma operadora real hoje. Não existe coluna de satisfação, reclamação ou qualidade de serviço — só o que o Excel tem. Contrato *month-to-month* e tenure curto sobressaem porque são sinais fortes no arquivo, não porque o negócio diga que são a única causa de churn. `Country` / `State` / `City` são categorias de um mercado específico; noutro país o modelo não “transporta”.

Churn é minoria: accuracy alta diz pouco. Por isso no outro doc ficou PR-AUC e F1 na classe positiva. Não abri análise de desempenho por `Gender` nem por outros subgrupos demográficos; num produto com exposição pública isso exigiria alinhamento com jurídico/compliance — ficou fora do âmbito deste trabalho.

## Falhas operacionais que já antecipamos

Sem `pipeline.joblib` no path certo, `/predict` responde 503. JSON incompleto ou coluna a mais: 422; há teste Pandera em `tests/` só sobre o conjunto de nomes de colunas. Categorias novas caem em `handle_unknown="ignore"` no *one-hot*: o pedido não estoura em erro, mas a probabilidade pode ficar estranha se quem alimenta a API mudar o *schema* sem avisar. Valores absurdos (ex. charge negativa) o sklearn pode engolir — só há defesa se alguém olhar para distribuições de entrada de vez em quando.

## Limiar

`THRESHOLD_START` em `config.py` (0,35 por omissão), no mesmo espírito que `metricas_e_limiar.md`: na nossa brincadeira de custos, FN custa mais que FP, daí o corte abaixo de 0,5. Cada resposta traz `probability_churn`, `threshold` e `predicted_churn` para ninguém precisar adivinhar o corte.

## Reprodutibilidade

Seeds e folds no `config.py`. `mlruns/` e `.joblib` não entram no Git; clone novo gera artefatos de novo ou copia-os à parte (README descreve).
