.PHONY: install install-dev lint lint-fix test export-model serve run

install:
	python -m pip install -U pip
	python -m pip install -e .

install-dev:
	python -m pip install -U pip
	python -m pip install -e ".[dev]"

lint:
	ruff check src tests
	ruff format --check src tests

lint-fix:
	ruff check --fix src tests
	ruff format src tests

test:
	pytest

export-model:
	python scripts/export_logistic_artifact.py

serve:
	uvicorn churn_prediction.api.app:app --reload --host 127.0.0.1 --port 8000

run: serve
