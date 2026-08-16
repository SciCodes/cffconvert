# `cffconvert`

[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1162057.svg)](https://doi.org/10.5281/zenodo.1162057)
[![testing](https://github.com/citation-file-format/cffconvert/actions/workflows/testing.yml/badge.svg)](https://github.com/citation-file-format/cffconvert/actions/workflows/testing.yml)
[![linting](https://github.com/citation-file-format/cffconvert/actions/workflows/linting.yml/badge.svg)](https://github.com/citation-file-format/cffconvert/actions/workflows/linting.yml)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=cffconvert&metric=code_smells)](https://sonarcloud.io/dashboard?id=cffconvert)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/1811/badge)](https://bestpractices.coreinfrastructure.org/projects/1811)
[![Research Software Directory](https://img.shields.io/badge/rsd-cffconvert-00a3e3.svg)](https://research-software.nl/software/cffconvert)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu)
[![FAIR checklist badge](https://fairsoftwarechecklist.net/badge.svg)](https://fairsoftwarechecklist.net/v0.2?f=31&a=32113&i=32100&r=113)
[![Docker Pulls](https://img.shields.io/docker/pulls/citationcff/cffconvert)](https://hub.docker.com/r/citationcff/cffconvert)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/citation-file-format/cffconvert/2.0.0)](https://github.com/citation-file-format/cffconvert/compare/2.0.0...HEAD)


Command line program to validate and convert [`CITATION.cff`](https://github.com/citation-file-format/citation-file-format) files.

## Supported input versions of the Citation File Format

| Citation File Format schema version | Link to Zenodo release                                                                                           |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `1.3.0`                             | unreleased                                                                                                       |
| `1.2.0`                             | [![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5171937.svg)](https://doi.org/10.5281/zenodo.5171937) |
| `1.1.0`                             | [![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4813122.svg)](https://doi.org/10.5281/zenodo.4813122) |
| `1.0.3`                             | [![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1222163.svg)](https://doi.org/10.5281/zenodo.1222163) |
| `1.0.2`                             | [![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1120256.svg)](https://doi.org/10.5281/zenodo.1120256) |
| `1.0.1`                             | [![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1117789.svg)](https://doi.org/10.5281/zenodo.1117789) |

## Supported output formats

1. APA-like plaintext
2. BibTeX
3. CodeMeta
4. EndNote
5. RIS
6. schema.org JSON
7. Zenodo JSON

`cffconvert` does not support converting items from `references` or `preferred-citation` keys at the moment.
The `contact` key is currently validation-only. `license-url` is preserved in schema.org and CodeMeta output, but is
validation-only for the other formats. Zenodo output supports one SPDX license per record and raises an error when a
CFF file specifies multiple licenses.

## Installing

Install the official interim source distribution from the Git tag attached to a published GitHub Release.
The first planned concrete example is `v2026.08`.

```shell
python3 -m pip install --user git+https://github.com/scicodes/cffconvert.git@<release-tag>
```
Replace `<release-tag>` with the published GitHub Release tag, for example `v2026.08`.
Untagged `main` is development-only. Do not use PyPI for this fork; the `cffconvert` package name is already in use there.
Ensure that the user space directory `~/.local/bin/` is on the `PATH`.

```shell
which cffconvert
```
should now return the location of the program.

To install a specific branch, tag, or commit:

```shell
python3 -m pip install --user git+https://github.com/scicodes/cffconvert.git@<ref>
```

Replace `<ref>` with a branch name, tag, or commit SHA. For the official interim source distribution, use the published release tag.

For a local development install, clone the repository and install in editable mode:

```shell
git clone https://github.com/scicodes/cffconvert.git
cd cffconvert
python3 -m pip install --user --editable .[dev,testing]
```

See [docs/alternative-install-options.md](docs/alternative-install-options.md) for alternative install options.

## Docker

`cffconvert` will be available on GHCR as `ghcr.io/scicodes/cffconvert:<release-tag>` after the GitHub Release for that tag is published.
For the first planned example release, that tag is `v2026.08`.
Replace `<release-tag>` with the published GitHub Release tag.
Legacy Docker Hub images still exist at https://hub.docker.com/r/citationcff/cffconvert.

Example usage:

```shell
docker run --rm -v "$PWD":/work -w /work ghcr.io/scicodes/cffconvert:<release-tag> --validate
docker run --rm -v "$PWD":/work -w /work ghcr.io/scicodes/cffconvert:<release-tag> --version
docker run --rm -v "$PWD":/work -w /work ghcr.io/scicodes/cffconvert:<release-tag> --help
# etc
```

## `pre-commit` hook

`cffconvert` is also available as a [pre-commit](https://pre-commit.com) hook. Add the following to your
`.pre-commit-config.yaml` file to start validating your CITATION.cff automatically whenever you issue a `git commit`:

```yaml
repos:
  - repo: https://github.com/citation-file-format/cffconvert
    rev: 054bda51dbe278b3e86f27c890e3f3ac877d616c
    hooks:
      - id: validate-cff
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and release procedures.

## Command line interface

See `cffconvert`'s options:

```shell
cffconvert --help
```

Shows:

```shell
Usage: cffconvert [OPTIONS]

  Command line program to validate and convert CITATION.cff files.

Options:
  -i, --infile PATH               Path to the CITATION.cff input file. If this
                                  option is omitted, './CITATION.cff' is used.
  -o, --outfile PATH              Path to the output file.
  -f, --format [apalike|bibtex|cff|codemeta|endnote|ris|schema.org|zenodo]
                                  Output format.
  -u, --url TEXT                  URL to the CITATION.cff input file.
  -h, --help                      Show help and exit.
  --show-trace                    Show error trace.
  --validate                      Validate the CITATION.cff file and exit.
  --version                       Print version and exit.
  --verbose                       Control output verbosity.

  If this program is useful to you, consider giving it a star on GitHub:
  https://github.com/citation-file-format/cffconvert
```

## Example usage

### Validating a local CITATION.cff file

```shell
cffconvert --validate
cffconvert --validate -i CITATION.cff
cffconvert --validate -i ${PWD}/CITATION.cff
cffconvert --validate -i ../some-other-dir/CITATION.cff
```

### Validating a remote CITATION.cff file

```shell
cffconvert --validate --url https://github.com/<org>/<repo>
cffconvert --validate --url https://github.com/<org>/<repo>/commit/<sha>
cffconvert --validate --url https://github.com/<org>/<repo>/tree/<sha>
cffconvert --validate --url https://github.com/<org>/<repo>/tree/<tag>
cffconvert --validate --url https://github.com/<org>/<repo>/tree/<branch>
```


### Converting metadata to other formats

If there is a valid `CITATION.cff` file in the current directory, you can convert to various other formats and 
print the result on standard out with:

```shell
cffconvert -f bibtex
cffconvert -f codemeta
cffconvert -f endnote
cffconvert -f ris
cffconvert -f schema.org
cffconvert -f zenodo
cffconvert -f apalike
```

### Writing to a file

```shell
# with i/o redirection:
cffconvert -f bibtex > bibtex.bib
cffconvert -f zenodo > .zenodo.json
cffconvert -f endnote > ${PWD}/endnote.enw
# etc

# without i/o redirection
cffconvert -f bibtex -o bibtex.bib
cffconvert -f zenodo -o .zenodo.json
cffconvert -f endnote -o ${PWD}/endnote.enw
# etc
```
