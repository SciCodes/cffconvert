# Makefile for cffconvert repository maintenance
# Usage: make <target>

.PHONY: install dev-install test test-version test-marker \
        test-local test-version-local test-marker-local \
        lint precommit clean \
        build release-check help \
        docker-build docker-run docker-smoke docker-test-build

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

## Build the test Docker image (includes testing dependencies)
docker-test-build:
	docker build --target test -t cffconvert-test .

## Run the full test suite in Docker
test: docker-test-build
	docker run --rm cffconvert-test

## Run version-consistency tests in Docker
test-version: docker-test-build
	docker run --rm cffconvert-test pytest tests/test_consistent_versioning.py

## Run tests for a specific marker in Docker (e.g. make test-marker M=bibtex)
test-marker: docker-test-build
	docker run --rm cffconvert-test pytest -m $(M)

## Run the full test suite locally (requires dev-install)
test-local:
	pytest tests/

## Run version-consistency tests locally
test-version-local:
	pytest tests/test_consistent_versioning.py

## Run tests for a specific marker locally (e.g. make test-marker-local M=bibtex)
test-marker-local:
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

## Clean build artifacts, caches, and bytecode
clean:
	rm -rf build/ dist/ .eggs/ *.egg-info src/*.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

## Build the production Docker image
docker-build:
	docker build -t cffconvert .

## Run cffconvert in the production Docker image (pass args via ARGS)
## Mounts the host directory at /work to keep the venv at /app intact
docker-run:
	docker run --rm -v $(PWD):/work -w /work cffconvert $(ARGS)

## Build and smoke-test the production Docker image (print version)
docker-smoke: docker-build
	docker run --rm -v $(PWD):/work -w /work cffconvert --version

## Build sdist and wheel distributions into dist/
build: clean
	$(PYTHON) -m build

## Run the full local release validation gate (never publishes)
release-check: clean lint test test-version build

## Show available targets
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //'
