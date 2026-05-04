# Métricas de negócio e limiar

Antes de insistir nos modelos mais pesados, alinhei **métrica técnica**, **custo FP/FN** e **limiar** para não mudar critério no meio do trabalho. Os custos aqui são **hipótese razoável**, não valores da contabilidade — numa empresa real alguém de finanças traria os valores em dinheiro. Servem para fixar o limiar e para contar no vídeo STAR.

## Métricas técnicas

Escolhi uma métrica principal para comparar *runs* no MLflow sem ficar só na conversa de “acertou mais vezes”.

**PR-AUC** (*average precision*) é a principal: há muitos *não churn* na base e a classe que nos interessa é minoria — neste desenho a PR-AUC diz mais sobre o que precisamos que a ROC sozinha.

Ao lado disso registo **F1** na classe churn (um número só para comparar modelos), **ROC-AUC** (referência comum), e **balanced accuracy** para ver se estamos melhores que adivinhar pela maioria. **Accuracy** sozinha não decide nada aqui.

## Custo FP vs. FN (hipótese)

**FN:** o cliente ia sair, o modelo não avisou — perdemos a chance de segurá-lo.

**FP:** o modelo marcou risco e o cliente ficava — gastamos contato e tempo.

Hipótese que uso por ora: **1 FN “pesa” o dobro de 1 FP** (razão 2 : 1). Não são euros; é só para pesar o limiar e desenhar a matriz de confusão no relatório. Se o avaliador pedir outra razão, altero este ficheiro e reavalio o limiar.

## Limiar em probabilidade

O *logit* (e mais tarde a MLP) pode dar **probabilidade** de churn. Comecei com **0,35** em vez de 0,5 porque, com FN mais caro que FP, convém puxar mais *recall* na classe positiva e aceitar mais falsos alarmes no início. O valor fino sai depois de olhar validação / curva PR — isto é **ponto de partida**, não “ótimo”.

## MLflow e código

Nos notebooks `02_baselines_mlflow.ipynb` e `03_mlp_mlflow.ipynb` já vão alguns *params* com estes números (`cost_fn_relative`, `cost_fp_relative`, `threshold_start`, etc.) e a métrica **`f1_at_threshold_start`** (F1 na classe churn com probabilidades *out-of-fold* e o limiar `THRESHOLD_START` do `config.py`). O *seed* e os *folds* estão no `src/churn_prediction/config.py` para não ficar com número mágico espalhado.

A API (`POST /predict`) usa o mesmo limiar para montar `predicted_churn`: lê `THRESHOLD_START` do código quando o servidor sobe (não está no `meta.json`). Mudou o limiar no `config.py`? Sobe o `uvicorn` outra vez para pegar o valor novo.
