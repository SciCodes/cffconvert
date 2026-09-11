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
def test_writing_multiple_outputs_to_default_files(cffstr):
    expected_apalike = read_sibling_file(__file__, "apalike.txt")
    expected_bibtex = read_sibling_file(__file__, "bibtex.bib")
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["--output", "apalike", "--output", "bibtex"])
        with open("_citation.txt", "rt", encoding="utf-8") as fid:
            actual_apalike = fid.read()
        with open("_citation.bib", "rt", encoding="utf-8") as fid:
            actual_bibtex = fid.read()
    assert result.exit_code == 0
    assert result.output == ""
    assert expected_apalike == actual_apalike
    assert expected_bibtex == actual_bibtex


@pytest.mark.cli
def test_writing_multiple_outputs_to_custom_files(cffstr):
    expected_apalike = read_sibling_file(__file__, "apalike.txt")
    expected_bibtex = read_sibling_file(__file__, "bibtex.bib")
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["-O", "apalike=my-citation.txt", "-O", "bibtex=my-citation.bib"])
        with open("my-citation.txt", "rt", encoding="utf-8") as fid:
            actual_apalike = fid.read()
        with open("my-citation.bib", "rt", encoding="utf-8") as fid:
            actual_bibtex = fid.read()
    assert result.exit_code == 0
    assert result.output == ""
    assert expected_apalike == actual_apalike
    assert expected_bibtex == actual_bibtex


@pytest.mark.cli
@pytest.mark.parametrize(
    "output_specification, error_message",
    [
        ("unsupported", "is not one of"),
        ("bibtex=", "output path cannot be empty"),
    ],
)
def test_rejecting_invalid_output_specification(output_specification, error_message):
    runner = CliRunner()
    result = runner.invoke(cffconvert, ["-O", output_specification])
    assert result.exit_code == 2
    assert error_message in result.output


@pytest.mark.cli
def test_default_cff_output_does_not_overwrite_input(cffstr):
    expected = read_sibling_file(__file__, "CITATION.cff")
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("CITATION.cff", "wt", encoding="utf-8") as fid:
            fid.write(cffstr)
        result = runner.invoke(cffconvert, ["-O", "cff"])
        with open("CITATION.cff", "rt", encoding="utf-8") as fid:
            actual_input = fid.read()
        with open("_citation.cff", "rt", encoding="utf-8") as fid:
            actual_output = fid.read()
    assert result.exit_code == 0
    assert actual_input == cffstr
    assert actual_output == expected


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
