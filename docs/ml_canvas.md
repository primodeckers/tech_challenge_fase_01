# ML Canvas — churn Telco (Tech Challenge, Fase 1)

Este documento segue as **caixas** do [Machine Learning Canvas](https://www.ownml.co/machine-learning-canvas) (Louis Dorard / OWNML). Os títulos em inglês copiam o *template*; o texto descreve este projeto. Se no relatório pedirem referência bibliográfica: *Machine Learning Canvas*, Louis Dorard (OWNML), [ownml.co](https://www.ownml.co/).

Trabalho em cima do `data/raw/Telco_customer_churn.xlsx` e do `notebooks/01_eda_telco_churn.ipynb`. Se o Excel mudar, vale rever as porcentagens e as notas de qualidade.

Versão em **quadro** na mesma pasta: `ml_canvas.html` (abre no navegador). Quem alterar um ficheiro deve alinhar o par (md ou html) para não ficarem versões diferentes.

---

## End-user — *quem usa o sistema preditivo / quem é afetado*

Direção e dono de produto querem menos churn sem estourar o orçamento de campanhas. Marketing e CRM querem listas priorizadas e mensagens que não chateiem quem não ia sair. Operações e *call center* precisam de filas realistas — não dá para tratar sete mil pessoas na mesma semana. Neste exercício, o trabalho de dados cobre *pipeline*, MLflow e API. Jurídico só faria falta em produção com dados reais; aqui é exercício com dataset público.

---

## Value proposition — *o que fazemos pelos usuários*

A operadora perde clientes por cancelamento. Retenção costuma ser mais barata que aquisição, por isso o valor do sistema é **priorizar** quem tem mais probabilidade de sair, para concentrar contatos ou ofertas onde o retorno compensa, em vez de ir à sorte na base toda.

O modelo deve produzir **risco de churn** (probabilidade ou classe) para alimentar CRM ou filas de *call center*, com revisão humana nos casos limítrofes (regra de negócio a fechar).

O Excel não traz insatisfação subjetiva, falhas de rede ou mudança de cidade — o modelo trabalha com o que há.

---

## Data sources — *de onde vêm os dados*

- Arquivo **`data/raw/Telco_customer_churn.xlsx`** no repositório (IBM-style Telco churn, uso acadêmico).
- Em uma operadora real entrariam bases internas de *billing*, CRM e possivelmente APIs de terceiros; não é o cenário deste challenge.

---

## Problem — *especificação do “motor” de predição*

**Pergunta que o modelo responde:** este cliente tende a cancelar nos próximos tempos (no sentido captado pelo rótulo histórico `Churn Label`)?

**Entrada (*input*):** linha de cliente com variáveis tabulares (serviços, contrato, cobranças, *tenure*, etc.), no *schema* fechado depois do *pipeline* (o que fica de fora, o que é numérico, o que vai a *one-hot*).

**Saídas possíveis:** probabilidade de churn ou etiqueta *Yes* / *No* conforme um **limiar** ligado ao custo FP/FN (ver *Performance evaluation*).

**Tipo de problema:** classificação binária supervisionada.

***Baseline* simples (alternativa ao ML):** regras manuais do tipo “contrato *month-to-month* e *tenure* baixo → risco alto”, ou previsão constante (*Dummy*); no código há `DummyClassifier` e regressão logística antes da MLP.

---

## Data preparation — *como obtemos dados de treino e que *features* usamos*

Ordem de grandeza: **~7k linhas**, **30+ colunas** — volume modesto, mas dá para treinar e comparar modelos sem drama. Alvo: `Churn Label` (*Yes* / *No*); no EDA a classe *Yes* rondava **cerca de um quarto** da base (desequilibrada, mas não raríssima). Vale medir de novo depois de tratar as linhas em que `Total Charges` não convertia para número (poucas, mas não zero).

**Features:** serviços, contrato, encargos, *tenure*, composição do agregado, etc. **Cuidado com *leakage*:** `Churn Score`, `CLTV`, `Churn Reason` cheiram a informação *post hoc* — por omissão **não entram** como *input* até haver confirmação do *timing* em documentação de negócio.

---

## Performance evaluation — *como medimos sucesso*

Valores fechados (razão FP/FN, limiar de partida, tabela de métricas): **`docs/metricas_e_limiar.md`**. Aqui fica o resumo em linguagem de negócio.

**Métricas de negócio (*bottom-line*, a quantificar):** custo de **falso negativo** (perdemos a retenção) vs. **falso positivo** (contato inútil, desgaste). Sem contabilidade fina no enunciado, uso **razões** FP:FN plausíveis (ex.: “1 FN custa o dobro de 1 FP”) e documento no *Model Card*. *Accuracy* sozinha não conta — com muitos *No* na base dá para parecer bom sem aprender.

**Métricas de precisão da predição:** ROC-AUC para comparar entre si; **PR-AUC** e **F1** na classe *Yes* porque a classe positiva é minoria; Brier só se a probabilidade for usada para cortes finos.

**Avaliação *offline*:** validação cruzada **estratificada**, *seed* fixo, mesma lógica para baselines e para a MLP mais tarde — senão misturam-se *laranjas com maçãs*.

**Em produção (rascunho para o relatório):** taxa de churn entre clientes marcados como alto risco, estabilidade das distribuições de *features* (*drift*), volume de predições falhadas — isto encaixa no plano de `docs/monitoramento.md`.

---

## Using predictions — *integração: quando e como usamos as predições*

**Quando predizemos e quantas vezes:** batch diário (lista para campanha) ou sob pedido; no challenge a entrega inclui **FastAPI**, por isso o desenho principal é **sob pedido**; o README documenta batch como alternativa em produção.

**Restrição de tempo:** *p95* do `POST /predict` na ordem de **meio segundo** com *payload* típico em máquina modesta; *cold start* documentado se for relevante.

**Como usamos predições e confiança:** filas por *score* decrescente; limiar ajustável quando o custo FP/FN mudar.

**Se não houver predição a tempo:** fila de *fallback* (regra simples ou “não priorizar”) — pode detalhar-se no desenho da API se necessário.

---

## Learning models — *quando criamos/atualizamos modelos*

**Quando treinar ou refrescar:** após janelas de dados fechadas (ex. mensalidade do mês anterior) ou quando o *drift* passar um limiar — neste trabalho foquei numa versão entregável e deixo o *retrain* automático como evolução futura.

**Restrição de tempo de treino:** aceitável em minutos neste volume; MLP com GPU opcional.

**Critério para “subir” modelo:** melhoria clara em PR-AUC ou F1 no *Yes* em relação ao *baseline* logístico, sem degradação grave na tabela de confusão ao limiar escolhido; tudo registrado no MLflow com *commit* Git e referência ao arquivo de dados.

---

## Riscos e limitações (extra)

Base histórica pode não representar novos produtos ou regiões. Quem atende o telefone vai querer saber **por que** o cliente apareceu como risco — um *score* sozinho não responde a isso; mais tarde pode ser preciso ver importância de variáveis (há quem use SHAP) ou regras simples por canal, se o negócio pedir. Os dados do exercício trazem identificadores e endereço; num cenário real entraria legislação de proteção de dados (LGPD / GDPR) e minimização de dados.

---

## Próximos passos

Estão feitos: doc de custo FP/FN e limiar (`metricas_e_limiar.md`), baselines com *Dummy*, logística e Random Forest no `02_baselines_mlflow.ipynb`, MLP no `03_mlp_mlflow.ipynb`, export da logística, API com rotas úteis e testes; model card, deploy (incluindo o desenho em `deploy_arquitetura.md` e a API pública no Cloud Run, ver `deploy_cloud_run.md`) e monitoramento em `docs/`. Falta sobretudo **gravar o vídeo STAR**.
