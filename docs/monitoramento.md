# Monitoramento — rascunho

Texto para depois de existir tráfego real. Hoje o modelo só corre na máquina de cada um; mesmo assim deixamos isto escrito porque o guia pedia métricas, alertas e um roteiro de resposta.

**Infra:** estabilidade do `/health`, contagem de 5xx no `/predict`, latência em p50 e p95. O middleware já escreve `latency_ms` em JSON no stdout; num datacenter isso ia para uma ferramenta tipo Prometheus ou Grafana, não para o terminal local de desenvolvimento.

**Modelo:** evolução da fração de `predicted_churn=True` ao longo dos dias; salto brusco pode ser mudança de população nos dados ou bug a montante. Quando existir rótulo com atraso (ex.: churn observado ao fim de um mês), comparar taxa de churn entre o grupo “alto risco” e o resto. Pedidos rejeitados por schema deviam aparecer contados para alguém notar.

**Alertas (números por acordo com o negócio):** p95 de latência acima do limite combinado; health a dizer que o modelo não carregou; subida forte de 422 — muitas vezes é sistema de origem a mudar coluna ou formato.

**Quando a coisa falha:** 503 → export correu? `CHURN_ARTIFACT_DIR` correto (no deploy Windows/Git Bash ver **docs/deploy_cloud_run.md**)? `.gcloudignore` a incluir `pipeline.joblib` no *upload*? Chuva de 422 → comparar payload com `meta.json`. Probabilidades que não batem com o que o negócio espera → notebook com amostra recente; se a PR-AUC despenhar face ao que tinham no treino, planejar novo treino e novo export.
