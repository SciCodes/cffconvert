# Makefile for cffconvert repository maintenance
# Usage: make <target>

.PHONY: install dev-install test test-version test-marker lint precommit clean \
        build check-dist release-check publish-test help \
        docker-build docker-run

# Default Python interpreter (use venv python if available, else system python3)
PYTHON := $(shell command -v python3 2>/dev/null || echo python3)

# uv executable (use uv if available, fall back to python3 -m uv)
UV := $(shell command -v uv 2>/dev/null || echo "python3 -m uv")

## Install runtime dependencies only
install:
	$(UV) pip install .

## Install with dev and testing dependencies (editable)
dev-install:
	$(UV) pip install --editable .[dev,testing]

## Run the full test suite
test:
	pytest tests/

## Run version-consistency tests only
test-version:
	pytest tests/test_consistent_versioning.py

## Run tests for a specific marker (e.g. make test-marker M=bibtex)
test-marker:
	pytest -m $(M)

## Run all linters (isort, ruff, prospector, pyroma)
lint:
	isort --check-only --diff src/cffconvert tests/
	ruff check src/cffconvert
	prospector --profile-path .prospector.yml
	pyroma .

## Run pre-commit hooks on all files
precommit:
	pre-commit run --all-files

## Clean build artifacts and caches
clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

## Build the Docker image
docker-build:
	docker build -t cffconvert .

## Run cffconvert in Docker (pass args via ARGS, e.g. make docker-run ARGS="--validate")
docker-run:
	docker run --rm -v $(PWD):/app cffconvert $(ARGS)

## Build sdist and wheel distributions into dist/
build: clean
	$(PYTHON) -m build

## Check distributions with twine
check-dist:
	$(PYTHON) -m twine check dist/*

## Run the full local release validation gate (never publishes)
release-check: clean lint test test-version build check-dist

## Publish to TestPyPI (optional, requires TestPyPI credentials in ~/.pypirc)
publish-test: check-dist
	$(PYTHON) -m twine upload --repository testpypi dist/*

## Show available targets
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //'
