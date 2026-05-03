"""Exporta pipeline logístico para a pasta usada pela API (`pipeline.joblib` + `meta.json`).

Uso (na raiz do repo, com venv):
    python scripts/export_logistic_artifact.py
    python scripts/export_logistic_artifact.py --artifact-dir models/churn_api
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta regressão logística para a API.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("models/churn_api"),
        help="Pasta de saída (default: models/churn_api)",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="Excel Telco (default: data/raw/Telco_customer_churn.xlsx)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    import sys

    sys.path.insert(0, str(root / "src"))

    from churn_prediction.artifacts import export_logistic_artifact

    export_logistic_artifact(args.artifact_dir, data_path=args.data)
    print("Artefacto escrito em:", args.artifact_dir.resolve())


if __name__ == "__main__":
    main()
