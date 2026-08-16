from importlib.metadata import version as metadata_version
import json
from pathlib import Path
import re
from ruamel.yaml import YAML  # type: ignore[import-not-found]
from cffconvert.cli.version import __version__ as cli_version


ROOT = Path(__file__).resolve().parents[1]


def get_version_from_pyproject_toml():
    file_contents = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    regex = re.compile(r'^version = "(?P<version>\S*)"$', re.MULTILINE)
    match = re.search(regex, file_contents)
    assert match is not None
    return match["version"]


EXPECTED_VERSION = get_version_from_pyproject_toml()


def test_citation_cff():
    file_contents = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    actual_version = YAML(typ="safe").load(file_contents)["version"]
    assert actual_version == EXPECTED_VERSION


def test_zenodo_json():
    file_contents = (ROOT / ".zenodo.json").read_text(encoding="utf-8")
    actual_version = json.loads(file_contents)["version"]
    assert actual_version == EXPECTED_VERSION


def test_cli_version_metadata():
    installed_version = metadata_version("cffconvert")
    assert installed_version == EXPECTED_VERSION
    assert cli_version == installed_version


def test_dockerfile_does_not_hard_code_version_label():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "org.opencontainers.image.version" not in dockerfile
