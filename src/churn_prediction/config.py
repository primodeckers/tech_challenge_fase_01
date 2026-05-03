"""Constantes partilhadas (reprodutibilidade e MLflow)."""

RANDOM_SEED: int = 42
N_CV_SPLITS: int = 5
MLFLOW_EXPERIMENT_BASELINES: str = "telco_churn_baselines"
MLFLOW_EXPERIMENT_MLP: str = "telco_churn_mlp"
# Limiar inicial de probabilidade (classe positiva = churn); ver docs/metricas_e_limiar.md
THRESHOLD_START: float = 0.35
