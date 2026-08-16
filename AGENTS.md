# AGENTS.md

`cffconvert` — Python CLI and library to validate and convert `CITATION.cff` files (CFF 1.0.1–1.3.0) to APA-like, BibTeX, CodeMeta, EndNote, RIS, schema.org JSON, and Zenodo JSON. Does not convert `references` or `preferred-citation` keys.

## Setup

```shell
uv venv && source .venv/bin/activate
uv pip install --editable .[dev,testing]           # dev tooling + test deps
```

Alternatively, use the Makefile targets:

```shell
make dev-install        # install with dev + testing deps (editable)
make test               # run full test suite (in Docker)
make test-local         # run full test suite on the host (requires dev-install)
make test-version       # run version-consistency checks (in Docker)
make lint               # ruff, pyroma
make precommit          # run all pre-commit hooks
```

Requires Python ≥ 3.10. Source under `src/cffconvert/` (setuptools `find` from `src/`).

**Always run commands inside the Docker sandbox and prefer Makefile targets over raw commands.** Use `make docker-build` to build the production image, `make docker-run ARGS="…"` to execute `cffconvert` inside the container, and `make test` to run the full test suite in Docker (builds a test image with testing dependencies). Use `make test-local` to run tests on the host instead. For lint targets, run `make lint` or `uv pip install --system --editable .[dev,testing]` inside the sandbox — never run `uv run` or `make` targets directly on the host.

## Validation commands

```shell
make test               # full suite in Docker (--maxfail=1, --strict-markers)
make test-local         # full suite on the host (requires dev-install)
make test-version       # version-consistency checks in Docker
make test-version-local # version-consistency checks on the host
make test-marker M=bibtex   # by marker in Docker: apalike|bibtex|codemeta|endnote|ris|schemaorg|zenodo|cli|lib
pytest -m bibtex        # by marker on the host
make lint               # ruff, pyroma
make precommit          # pre-commit run --all-files
```

For changes under `.github/workflows/`, lint every workflow and exercise the changed commands rather than relying only
on the project test suite:

```shell
docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:latest
make docker-build && make docker-run ARGS="--validate"  # validate the root CITATION.cff with current source
```

Run changed CI commands in the relevant container or runner environment so unsupported CLI flags and shell differences
fail before CI.

Pytest markers are registered in `pyproject.toml` — do not introduce unregistered markers. Test fixtures live under `tests/cli/cff_<version>/` and `tests/lib/cff_<version>/`.

## Invariants and constraints

- **Version sync**: the canonical package version is `2026.8`. It must match across `pyproject.toml`, `src/cffconvert/cli/version.py`, `CITATION.cff`, and `.zenodo.json`. The release tag (for the first planned release, `v2026.08`) is separate. Enforced by `tests/test_consistent_versioning.py`.
- **Dockerfile**: multi-stage build with the same pinned Python image in both builder and runtime (uv installed via pip in the builder). Includes a `test` stage with testing dependencies for `make test`. The Dockerfile must not hard-code `org.opencontainers.image.version`; GHCR metadata supplies release image labels.
- **Style**: line length 120, double quotes, single-line imports, force-sorted within sections (`known_first_party = ["cffconvert"]`). Config in `pyproject.toml` (`[tool.ruff]`, `[tool.ruff.lint.isort]`, `[tool.ruff.lint.flake8-quotes]`).
- **YAML parsing**: use `ruamel.yaml` with `typ="safe"`; timestamps must be loaded as strings (see `YAML_TIMESTAMP_TYPE` in `src/cffconvert/lib/constants.py` and each `citation.py`).
- **Schema loading**: JSON schemas live in `src/cffconvert/schemas/<version>/schema.json`, loaded at runtime via `get_package_root()` from `src/cffconvert/root.py`.
- **Validation backends**: `jsonschema` for CFF 1.2.0+, `pykwalify` for 1.0.x–1.1.0.
- **Interim distribution**: install from the Git tag attached to a published GitHub Release. Do not publish this fork to
  PyPI because the `cffconvert` package name is already in use there.
- **Container releases**: publishing a GitHub Release triggers GHCR publication using that release's tag. Keep the
  workflow version-agnostic; do not hard-code a release tag or publish an implicit `latest` tag.

## Change patterns

### Adding a new CFF schema version

1. Create `src/cffconvert/lib/cff_<version>/` with exporter modules.
2. Add `src/cffconvert/schemas/<version>/schema.json`.
3. Register the version in `Citation._implementations` (`src/cffconvert/lib/citation.py`).
4. Add test fixtures under `tests/cli/cff_<version>/` and `tests/lib/cff_<version>/`.
5. Implement all `Contract` methods (`src/cffconvert/lib/contracts/citation.py`).

### Adding a new output format

1. Add the format to `options["outputformat"]` in `src/cffconvert/cli/cli.py` and the `outstr` dict in `src/cffconvert/cli/validate_or_write_output.py`.
2. Implement `as_<format>()` on every `Citation_*` class and the `Contract` ABC.
3. Add test fixtures and a pytest marker in `pyproject.toml`.

## Authoritative references

- `pyproject.toml` — build, dependencies, ruff, pytest config
- `README.dev.md` — developer setup, testing, linting, author-key construction system
- `CONTRIBUTING.md` — contribution workflow
- `CHANGELOG.md` — version history
- `.pre-commit-config.yaml` — pre-commit hook definitions
