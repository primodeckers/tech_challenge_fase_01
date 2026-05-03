# Métricas de negócio e limiar

Antes de insistir nos modelos mais pesados, fechamos **métrica técnica**, **custo FP/FN** e **limiar** para não ficar mudando critério no meio. Os custos aqui são **chute razoável do grupo**, não valores da contabilidade — numa empresa real alguém de finanças traria os valores em dinheiro. Servem para alinhar o limiar e para contar no vídeo STAR.

## Métricas técnicas

Queremos uma métrica principal para comparar *runs* no MLflow sem discutir só “acertou mais vezes”.

**PR-AUC** (*average precision*) fica como principal: há muitos *não churn* na base e a classe que nos interessa é minoria — PR-AUC costuma ser mais honesta que ROC nisto.

Ao lado disso guardamos **F1** na classe churn (dá para falar com o grupo num número só), **ROC-AUC** (todo mundo conhece), e **balanced accuracy** para ver se estamos melhores que adivinhar pela maioria. **Accuracy** sozinha não decide nada aqui.

## Custo FP vs. FN (hipótese)

**FN:** o cliente ia sair, o modelo não avisou — perdemos a chance de segurá-lo.

**FP:** o modelo marcou risco e o cliente ficava — gastamos contato e tempo.

Combinado que o grupo vai usar por ora: **1 FN “pesa” o dobro de 1 FP** (razão 2 : 1). Não são euros; é só para pesar o limiar e desenhar a matriz de confusão no relatório. Se o professor ou o grupo quiserem outra razão, alteramos este arquivo e reavaliamos o limiar.

## Limiar em probabilidade

O *logit* (e mais tarde a MLP) pode dar **probabilidade** de churn. Começamos com **0,35** em vez de 0,5 porque, com FN mais caro que FP, faz sentido puxar mais *recall* na classe positiva e aceitar mais falsos alarmes no início. O valor fino sai depois de olhar validação / curva PR — isto é **ponto de partida**, não “ótimo”.

## MLflow e código

Nos notebooks `02_baselines_mlflow.ipynb` e `03_mlp_mlflow.ipynb` já vão alguns *params* com estes números (`cost_fn_relative`, `cost_fp_relative`, `threshold_start`, etc.) e a métrica **`f1_at_threshold_start`** (F1 na classe churn com probabilidades *out-of-fold* e o limiar `THRESHOLD_START` do `config.py`). O *seed* e os *folds* estão no `src/churn_prediction/config.py` para não ficar com número mágico espalhado.
