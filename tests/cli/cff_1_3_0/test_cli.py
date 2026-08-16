import json
from click.testing import CliRunner
import pytest
from cffconvert.cli.cli import cli as cffconvert
from tests.cli.helpers import get_formats
from tests.cli.helpers import read_sibling_file


@pytest.fixture(scope="module")
def cffstr():
    return read_sibling_file(__file__, "CITATION.cff")


@pytest.mark.cli
def test_local_cff_file_does_not_exist():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cffconvert, ["-f", "bibtex"])
    assert isinstance(result.exception, FileNotFoundError)
    assert result.exit_code == 1
    assert "No such file or directory" in str(result.exception)


@pytest.mark.cli
def test_printing_of_help():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cffconvert, ["--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")


@pytest.mark.cli
@pytest.mark.parametrize("fmt, fname", get_formats())
def test_printing_on_stdout(fmt, fname, cffstr):
    expected = read_sibling_file(__file__, fname)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["-f", fmt])
    assert result.exit_code == 0
    actual = result.output
    assert expected == actual


@pytest.mark.cli
def test_raising_error_on_unsupported_format(cffstr):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["-f", "unsupported_97491"])
    assert result.exit_code == 2
    assert "Error: Invalid value for '-f'" in str(result.output)


@pytest.mark.cli
def test_without_arguments():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cffconvert, [])
    assert result.exit_code == 1
    assert isinstance(result.exception, FileNotFoundError)
    assert result.exception.strerror == "No such file or directory"


@pytest.mark.cli
@pytest.mark.parametrize("fmt, fname", get_formats())
def test_writing_to_file(fmt, fname, cffstr):
    expected = read_sibling_file(__file__, fname)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["-f", fmt, "-o", fname])
        with open(fname, "rt", encoding="utf-8") as fid:
            actual = fid.read()
    assert result.exit_code == 0
    assert expected == actual


@pytest.mark.cli
def test_cff_1_3_metadata_end_to_end():
    cffstr = """authors:
  - name: Test organization
    ror: https://ror.org/04bwf3e34
cff-version: 1.3.0
contributors:
  - given-names: Ada
    family-names: Lovelace
license-url: https://example.org/license
message: Cite this work
title: Test title
"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["-f", "schema.org"])
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert output["author"][0]["@id"] == "https://ror.org/04bwf3e34"
    assert output["contributor"][0]["familyName"] == "Lovelace"
    assert output["license"] == "https://example.org/license"
