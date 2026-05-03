.PHONY: install install-dev lint lint-fix test

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
