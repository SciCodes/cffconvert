from importlib.metadata import version as metadata_version
from click.testing import CliRunner
import pytest
from cffconvert.cli.cli import cli as cffconvert


@pytest.mark.cli
def test_printing_of_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cffconvert, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"{metadata_version('cffconvert')}\n"
