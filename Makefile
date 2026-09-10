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

## Run all linters (ruff, pyroma)
lint:
	ruff check src/cffconvert tests
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
## The image workdir is /work; the host directory is mounted at /work
docker-run:
	docker run --rm -v $(PWD):/work cffconvert $(ARGS)

## Build and smoke-test the production Docker image
## Covers: --version; read-only /work stdout conversion; arbitrary-UID
## writable /work -o conversion; and a mount over /app cannot hide the
## absolute entrypoint. Uses a temp dir with trap cleanup; leaves no
## generated output in the repo.
docker-smoke: docker-build
	@set -eu; \
	TMP="$$(mktemp -d)"; \
	trap 'rm -rf "$$TMP"' EXIT INT TERM; \
	chmod 755 "$$TMP"; \
	cp CITATION.cff "$$TMP/CITATION.cff"; \
	chmod 644 "$$TMP/CITATION.cff"; \
	mkdir "$$TMP/output"; \
	chmod 777 "$$TMP/output"; \
	echo "smoke: --version"; \
	docker run --rm cffconvert --version; \
	echo "smoke: read-only /work stdout conversion"; \
	docker run --rm -v "$$TMP":/work:ro cffconvert -f bibtex | grep -q "@misc{"; \
	echo "smoke: arbitrary UID writable /work -o conversion"; \
	docker run --rm --user 4242 -v "$$TMP":/input:ro -v "$$TMP/output":/work cffconvert -i /input/CITATION.cff -o /work/out.bib -f bibtex; \
	test -s "$$TMP/output/out.bib"; \
	echo "smoke: /app mount cannot hide the executable"; \
	echo decoy > "$$TMP/cffconvert"; \
	docker run --rm -v "$$TMP":/app cffconvert --version; \
	echo "smoke: OK"

## Build sdist and wheel distributions into dist/
build: clean
	$(PYTHON) -m build

## Run the full local release validation gate (never publishes)
release-check: clean lint test test-version build

## Show available targets
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //'
