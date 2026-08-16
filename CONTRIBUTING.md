# Contributing guidelines

We welcome any kind of contribution to our software, from simple comment or
question to a full fledged [pull
request](https://help.github.com/articles/about-pull-requests/). However, we ask
that you read and follow this organization's [Code of Conduct](https://github.com/citation-file-format/citation-file-format/blob/master/CODE_OF_CONDUCT.md).

A contribution can be one of the following cases:

1. you have a question;
1. you think you may have found a bug (including unexpected behavior);
1. you want to make some kind of change to the code base (e.g. to fix a bug, to add
   a new feature, to update documentation).

The sections below outline the steps in each case.

## You have a question

1. use the search functionality
   [here](https://github.com/citation-file-format/cffconvert/issues) to see if someone already filed the same issue;
2. if your issue search did not yield any relevant results, make a new issue;
3. apply the "Question" label; apply other labels when relevant.

## You think you may have found a bug

1. use the search functionality
   [here](https://github.com/citation-file-format/cffconvert/issues) to see if someone already filed the same issue;
2. if your issue search did not yield any relevant results, make a new issue,
   making sure to provide enough information to the rest of the community to
   understand the cause and context of the problem. Depending on the issue, you may
   want to include:
    - the [SHA
      hashcode](https://help.github.com/articles/autolinked-references-and-urls/#commit-shas)
      of the commit that is causing your problem;
    - some identifying information (name and version number) for dependencies you're
      using;
    - information about the operating system;
3. apply relevant labels to the newly created issue.

## You want to make some kind of change to the code base

1. (**important**) announce your plan to the rest of the community _before you
   start working_. This announcement should be in the form of a (new) issue;
2. (**important**) wait until some kind of consensus is reached about your idea
   being a good idea;
3. if needed, fork the repository to your own Github profile and create your own
   feature branch off of the latest master commit. While working on your feature
   branch, make sure to stay up to date with the master branch by pulling in changes, possibly from the 'upstream' repository (follow the instructions [here](https://help.github.com/articles/configuring-a-remote-for-a-fork/) and [here](https://help.github.com/articles/syncing-a-fork/));
4. make sure the existing tests still work by running `pytest tests/`;
5. add your own tests (if applicable);
6. update or expand the documentation;
7. [push](http://rogerdudler.github.io/git-guide/) your feature branch to (your
   fork of) the ``cffconvert`` repository on GitHub;
8. create the pull request, e.g. following the instructions
   [here](https://help.github.com/articles/creating-a-pull-request/).

In case you feel like you have a valuable contribution to make, but you don't know
how to write or run tests for it, or how to create the documentation: don't
let this discourage you from making the pull request; we can help you! Just go
ahead and submit the pull request, but keep in mind that you might be asked to
append additional commits to your pull request.

## For maintainers

### Development setup

Install with dev and testing dependencies in an editable environment:

```shell
uv venv && source .venv/bin/activate
uv pip install --editable .[dev,testing]
```

Or use the Makefile:

```shell
make dev-install        # install with dev + testing deps (editable)
make test               # run the full test suite (in Docker)
make test-local         # run the full test suite (locally, requires dev-install)
make test-version       # run version-consistency checks (in Docker)
make test-version-local # run version-consistency checks (locally)
make lint               # run isort, ruff, prospector, pyroma
make precommit          # run all pre-commit hooks
```

### Packaging

Build source and wheel distributions, then validate them:

```shell
make clean        # remove stale build artifacts
make build        # build sdist + wheel into dist/
make check-dist   # twine check dist/*
```

### Release preparation

Before publishing, update the version **everywhere** it must be synchronized.
The version is checked for consistency by `tests/test_consistent_versioning.py`
across these files:

1. `pyproject.toml` — `version = "X.Y.Z"`
2. `CITATION.cff` — `version: X.Y.Z`
3. `.zenodo.json` — `"version": "X.Y.Z"`
4. `Dockerfile` — `LABEL org.opencontainers.image.version="X.Y.Z"`
5. `docs/alternative-install-options.md` — `docker build --tag cffconvert:X.Y.Z .`
6. `README.dev.md` — multiple patterns (requires line, docker tag, docker push)

Update the version in all of the above, then run:

```shell
make test-version   # verify version consistency
make release-check  # full local validation gate (clean, lint, test, test-version, build, check-dist)
```

`make release-check` runs the complete local validation gate. It never publishes
anything — it only verifies that the package is ready for release.

### TestPyPI (optional dry run)

To verify the package installs cleanly from a real index before a production
release, publish to TestPyPI:

```shell
make publish-test   # builds, checks, and uploads to TestPyPI
```

This requires a `~/.pypirc` entry for `testpypi` or `TWINE_USERNAME` /
`TWINE_PASSWORD` environment variables pointing at a TestPyPI account.

### Production release procedure

Production releases are published to PyPI **exclusively** via GitHub Releases
and PyPI Trusted Publishing. There is no `make publish` target for production.

**Steps:**

1. Ensure `main` is green (CI passes) and `make release-check` succeeds locally.
2. Update `CHANGELOG.md` with the release notes for the new version.
3. Commit and push all version changes to `main`.
4. Create a **GitHub Release** on the `citation-file-format/cffconvert` repository:
   - Tag name: the version string from `pyproject.toml` (e.g. `3.0.0`).
   - Title: the version string (e.g. `3.0.0`).
   - Description: paste the relevant `CHANGELOG.md` section.
5. Publishing the GitHub Release triggers the
   [`publish-to-pypi`](.github/workflows/publish-to-pypi.yml) workflow:
   - Checks out the exact release tag.
   - Verifies the tag matches `pyproject.toml` version.
   - Builds sdist + wheel.
   - Runs `twine check dist/*`.
   - Uploads to PyPI using **Trusted Publishing** (OIDC, no API tokens).
6. After PyPI publication succeeds, the existing
   [`zenodraft`](.github/workflows/zenodraft.yml) workflow creates a Zenodo
   deposit draft (triggered by the same release event).

### PyPI Trusted Publishing configuration

Trusted Publishing is configured on the PyPI side (no API tokens in GitHub
Secrets). The GitHub Actions workflow uses `pypa/gh-action-pypi-publish@release/v1`
with `permissions: id-token: write` and `environment: pypi`.

**PyPI settings (configured once by a project admin):**

| Setting | Value |
|---------|-------|
| PyPI project | `cffconvert` |
| Owner | `citation-file-format` (or `SciCodes`) |
| Repository | `citation-file-format/cffconvert` |
| Workflow filename | `publish-to-pypi.yml` |
| Environment name | `pypi` |

See the [PyPI Trusted Publishing
docs](https://docs.pypi.org/trusted-publishers/) for setup details.

### Release checklist

- [ ] All version files updated (`pyproject.toml`, `CITATION.cff`, `.zenodo.json`, `Dockerfile`, `docs/alternative-install-options.md`, `README.dev.md`)
- [ ] `CHANGELOG.md` updated with release notes
- [ ] `make test-version` passes (version consistency)
- [ ] `make release-check` passes (full local gate)
- [ ] CI green on `main`
- [ ] GitHub Release created with tag matching `pyproject.toml` version
- [ ] `publish-to-pypi` workflow completed successfully
- [ ] `zenodraft` workflow completed (Zenodo deposit created)
- [ ] PyPI page shows new version: <https://pypi.org/project/cffconvert/>
- [ ] (Optional) Docker image built and pushed to DockerHub

