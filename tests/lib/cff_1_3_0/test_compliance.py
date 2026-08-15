import json
import pytest
from jsonschema.exceptions import ValidationError
from cffconvert import Citation


BASE_CFF = """authors:
  - name: Test author
cff-version: 1.3.0
message: Cite this work
title: Test title
"""


def make_citation(extra=""):
    return Citation(BASE_CFF + extra)


@pytest.mark.lib
def test_ror_rejects_pipe_characters():
    citation = Citation(BASE_CFF.replace("name: Test author", "name: Test organization\n    ror: https://ror.org/0||||||||"))
    with pytest.raises(ValidationError):
        citation.validate()


@pytest.mark.lib
@pytest.mark.schemaorg
@pytest.mark.codemeta
@pytest.mark.parametrize("output_format", ["schemaorg", "codemeta"])
def test_ror_is_preserved_as_jsonld_id(output_format):
    citation = Citation(BASE_CFF.replace(
        "name: Test author",
        "name: Test organization\n    ror: https://ror.org/04bwf3e34"
    ))
    citation.validate()
    output = json.loads(getattr(citation, f"as_{output_format}")())
    assert output["author"][0]["@id"] == "https://ror.org/04bwf3e34"


@pytest.mark.lib
@pytest.mark.schemaorg
def test_ror_and_orcid_are_both_preserved():
    citation = Citation(BASE_CFF.replace(
        "name: Test author",
        "name: Test organization\n"
        "    orcid: https://orcid.org/0000-0002-1825-0097\n"
        "    ror: https://ror.org/04bwf3e34"
    ))
    citation.validate()
    author = json.loads(citation.as_schemaorg())["author"][0]
    assert author["@id"] == "https://ror.org/04bwf3e34"
    assert author["identifier"] == "https://orcid.org/0000-0002-1825-0097"


@pytest.mark.lib
@pytest.mark.zenodo
def test_email_only_contributor_is_omitted_from_zenodo():
    citation = make_citation("contributors:\n  - email: contributor@example.org\n")
    citation.validate()
    assert "contributors" not in json.loads(citation.as_zenodo())


@pytest.mark.lib
@pytest.mark.zenodo
def test_orcid_only_contributor_is_omitted_from_zenodo():
    citation = make_citation("contributors:\n  - orcid: https://orcid.org/0000-0002-1825-0097\n")
    citation.validate()
    assert "contributors" not in json.loads(citation.as_zenodo())


@pytest.mark.lib
@pytest.mark.zenodo
def test_orcid_only_creator_has_clear_zenodo_error():
    citation = Citation(BASE_CFF.replace("name: Test author", "orcid: https://orcid.org/0000-0002-1825-0097"))
    citation.validate()
    with pytest.raises(ValueError, match="Zenodo requires every creator to have a name"):
        citation.as_zenodo()


@pytest.mark.lib
@pytest.mark.zenodo
def test_multiple_licenses_have_clear_zenodo_error():
    citation = make_citation("license:\n  - MIT\n  - Apache-2.0\n")
    citation.validate()
    with pytest.raises(ValueError, match="Zenodo supports only one license"):
        citation.as_zenodo()


@pytest.mark.lib
@pytest.mark.zenodo
def test_single_item_license_list_is_supported_by_zenodo():
    citation = make_citation("license:\n  - MIT\n")
    citation.validate()
    assert json.loads(citation.as_zenodo())["license"] == {"id": "MIT"}


@pytest.mark.lib
@pytest.mark.schemaorg
@pytest.mark.codemeta
@pytest.mark.parametrize("output_format", ["schemaorg", "codemeta"])
def test_multiple_licenses_are_preserved_as_urls(output_format):
    citation = make_citation("license:\n  - MIT\n  - Apache-2.0\n")
    citation.validate()
    output = json.loads(getattr(citation, f"as_{output_format}")())
    assert output["license"] == [
        "https://spdx.org/licenses/MIT",
        "https://spdx.org/licenses/Apache-2.0"
    ]


@pytest.mark.lib
@pytest.mark.schemaorg
@pytest.mark.codemeta
@pytest.mark.parametrize("output_format", ["schemaorg", "codemeta"])
def test_license_url_is_preserved(output_format):
    citation = make_citation("license-url: https://example.org/license\n")
    citation.validate()
    output = json.loads(getattr(citation, f"as_{output_format}")())
    assert output["license"] == "https://example.org/license"


@pytest.mark.lib
@pytest.mark.schemaorg
def test_spdx_license_and_license_url_are_both_preserved():
    citation = make_citation("license: MIT\nlicense-url: https://example.org/license\n")
    citation.validate()
    assert json.loads(citation.as_schemaorg())["license"] == [
        "https://spdx.org/licenses/MIT",
        "https://example.org/license"
    ]


@pytest.mark.lib
@pytest.mark.zenodo
def test_new_spdx_license_is_supported():
    citation = make_citation("license: Linux-man-pages-copyleft\n")
    citation.validate()
    assert json.loads(citation.as_zenodo())["license"] == {"id": "Linux-man-pages-copyleft"}


@pytest.mark.lib
@pytest.mark.zenodo
def test_swh_identifier_is_preserved():
    identifier = "swh:1:rev:309cf2674ee7a0749978cf8265ab91a60aea0f7d"
    citation = make_citation("identifiers:\n  - type: swh\n    value: " + identifier + "\n")
    citation.validate()
    assert json.loads(citation.as_zenodo())["related_identifiers"] == [{
        "identifier": identifier,
        "relation": "isSupplementedBy",
        "scheme": "swh"
    }]


@pytest.mark.lib
@pytest.mark.codemeta
def test_codemeta_contributor_is_preserved():
    citation = make_citation("contributors:\n  - given-names: Ada\n    family-names: Lovelace\n")
    citation.validate()
    assert json.loads(citation.as_codemeta())["contributor"] == [{
        "@type": "Person",
        "familyName": "Lovelace",
        "givenName": "Ada"
    }]
