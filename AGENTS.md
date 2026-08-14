# AGENTS.md

`cffconvert` — Python CLI and library to validate and convert `CITATION.cff` files (CFF 1.0.1–1.3.0) to APA-like, BibTeX, CodeMeta, EndNote, RIS, schema.org JSON, and Zenodo JSON. Does not convert `references` or `preferred-citation` keys.

## Setup

```shell
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install --editable .[dev,testing]           # dev tooling + test deps
```

Requires Python ≥ 3.8. Source under `src/cffconvert/` (setuptools `find` from `src/`).

## Validation commands

```shell
pytest tests/                              # full suite (--maxfail=1, --strict-markers)
pytest -m bibtex                           # by marker: apalike|bibtex|codemeta|endnote|ris|schemaorg|zenodo|cli|lib
pytest tests/test_consistent_versioning.py # version-sync checks (run after any version bump)
isort --check-only --diff src/cffconvert tests/
ruff check src/cffconvert
prospector --profile-path .prospector.yml
pyroma .
pre-commit run --all-files
```

Pytest markers are registered in `pyproject.toml` — do not introduce unregistered markers. Test fixtures live under `tests/cli/cff_<version>/` and `tests/lib/cff_<version>/`.

## Invariants and constraints

- **Version sync**: the version string must match across `pyproject.toml`, `CITATION.cff`, `.zenodo.json`, and `Dockerfile`. Enforced by `tests/test_consistent_versioning.py`.
- **Style**: line length 120, double quotes, single-line imports, force-sorted within sections (`known_first_party = ["cffconvert"]`). Config in `pyproject.toml` (`[tool.isort]`, `[tool.ruff]`, `[tool.ruff.flake8-quotes]`).
- **YAML parsing**: use `ruamel.yaml` with `typ="safe"`; timestamps must be loaded as strings (see `YAML_TIMESTAMP_TYPE` in `src/cffconvert/lib/constants.py` and each `citation.py`).
- **Schema loading**: JSON schemas live in `src/cffconvert/schemas/<version>/schema.json`, loaded at runtime via `get_package_root()` from `src/cffconvert/root.py`.
- **Validation backends**: `jsonschema` for CFF 1.2.0+, `pykwalify` for 1.0.x–1.1.0.
- **Prospector**: ignores `src/cffconvert/gcloud/gcloud.py` (see `.prospector.yml`).

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

- `pyproject.toml` — build, dependencies, isort, ruff, pytest config
- `README.dev.md` — developer setup, testing, linting, author-key construction system
- `CONTRIBUTING.md` — contribution workflow
- `CHANGELOG.md` — version history
- `.pre-commit-config.yaml` — pre-commit hook definitions
