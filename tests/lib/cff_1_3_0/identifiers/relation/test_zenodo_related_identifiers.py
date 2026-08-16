from functools import lru_cache
import os
import pytest
from cffconvert import Citation
from cffconvert.lib.cff_1_3_x.zenodo import ZenodoObject


@lru_cache
def get_cffstr():
    fixture = os.path.join(os.path.dirname(__file__), "CITATION.cff")
    with open(fixture, "rt", encoding="utf-8") as f:
        return f.read()


def get_relation_types():
    return [
        "Cites",
        "Compiles",
        "Continues",
        "Describes",
        "Documents",
        "HasMetadata",
        "HasPart",
        "IsCitedBy",
        "IsCompiledBy",
        "IsContinuedBy",
        "IsDerivedFrom",
        "IsDescribedBy",
        "IsDocumentedBy",
        "IsIdenticalTo",
        "IsMetadataFor",
        "IsNewVersionOf",
        "IsObsoletedBy",
        "IsPartOf",
        "IsPreviousVersionOf",
        "IsPublishedIn",
        "IsReferencedBy",
        "IsRequiredBy",
        "IsReviewedBy",
        "IsSourceOf",
        "IsSupplementedBy",
        "IsSupplementTo",
        "IsVariantFormOf",
        "Obsoletes",
        "References",
        "Requires",
        "Reviews"
    ]


def get_relation_types_skip():
    return [
        "HasVersion",
        "IsVersionOf"
    ]


@pytest.mark.lib
@pytest.mark.zenodo
@pytest.mark.parametrize("expected", get_relation_types())
def test_with_relation(expected):
    cffstr = get_cffstr().replace("IsCompiledBy", expected)
    citation = Citation(cffstr)
    zenodo_object = ZenodoObject(citation.cffobj, initialize_empty=True)
    related_identifiers = zenodo_object.add_related_identifiers().related_identifiers
    assert related_identifiers is not None
    assert isinstance(related_identifiers, list)
    assert len(related_identifiers) > 0
    # pylint: disable=unsubscriptable-object
    assert isinstance(related_identifiers[0], dict)
    # pylint: disable=unsubscriptable-object
    actual = related_identifiers[0].get("relation")
    assert actual[1:] == expected[1:]
    assert actual[0] == expected[0].lower()


@pytest.mark.lib
@pytest.mark.zenodo
@pytest.mark.parametrize("expected", get_relation_types_skip())
def test_with_relation_unmapped(expected):
    cffstr = get_cffstr().replace("IsCompiledBy", expected)
    citation = Citation(cffstr)
    zenodo_object = ZenodoObject(citation.cffobj, initialize_empty=True)
    with pytest.raises(ValueError, match="Zenodo does not support the identifier relation"):
        zenodo_object.add_related_identifiers()


@pytest.mark.lib
@pytest.mark.zenodo
def test_original_form_relation_uses_zenodo_legacy_spelling():
    cffstr = get_cffstr().replace("IsCompiledBy", "IsOriginalFormOf")
    citation = Citation(cffstr)
    zenodo_object = ZenodoObject(citation.cffobj, initialize_empty=True)
    related_identifiers = zenodo_object.add_related_identifiers().related_identifiers
    assert related_identifiers[0]["relation"] == "isOrignialFormOf"


@pytest.mark.lib
@pytest.mark.zenodo
def test_without_relation():
    cffstr = get_cffstr().replace("relation: IsCompiledBy\n    ", "")
    citation = Citation(cffstr)
    zenodo_object = ZenodoObject(citation.cffobj, initialize_empty=True)
    related_identifiers = zenodo_object.add_related_identifiers().related_identifiers
    assert related_identifiers is not None
    assert isinstance(related_identifiers, list)
    assert len(related_identifiers) > 0
    # pylint: disable=unsubscriptable-object
    assert isinstance(related_identifiers[0], dict)
    # pylint: disable=unsubscriptable-object
    relation = related_identifiers[0].get("relation")
    assert relation == "isSupplementedBy"


@pytest.mark.lib
@pytest.mark.zenodo
def test_complete_zenodo_output_matches_fixture():
    citation = Citation(get_cffstr())
    fixture = os.path.join(os.path.dirname(__file__), ".zenodo.json")
    with open(fixture, "rt", encoding="utf-8") as f:
        expected = f.read()
    assert citation.as_zenodo() == expected
