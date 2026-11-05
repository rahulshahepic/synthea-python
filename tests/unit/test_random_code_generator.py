"""Java: RandomCodeGeneratorTest; offline ports use its original fixture resources."""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest

from synthea.helpers.random_code_generator import RandomCodeGenerator
from synthea.resources import resource_path
from synthea.world.concepts.health_record import Code

URI = "http://snomed.info/sct?fhir_vs=ecl%2F%3C%3C131148009"


@pytest.fixture(autouse=True)
def clear_cache() -> Iterator[None]:
    cache, selected, base = (
        dict(RandomCodeGenerator.codeListCache),
        list(RandomCodeGenerator.selectedCodes),
        RandomCodeGenerator.expandBaseUrl,
    )
    RandomCodeGenerator.codeListCache.clear()
    RandomCodeGenerator.selectedCodes.clear()
    yield
    RandomCodeGenerator.codeListCache.clear()
    RandomCodeGenerator.codeListCache.update(cache)
    RandomCodeGenerator.selectedCodes[:] = selected
    RandomCodeGenerator.expandBaseUrl = base


def fixture(name: str) -> dict[str, object]:
    # Upstream tests use src/test/resources; no copying or altering the Java fixture.
    root = resource_path("").parents[1]
    path = root / "test/resources/wiremock/RandomCodeGeneratorTest/__files" / name
    return json.loads(path.read_text())


def test_get_code() -> None:
    """Java: RandomCodeGeneratorTest#getCode (offline load of the same response)."""
    RandomCodeGenerator.load_value_set(URI, fixture("codes.json"))
    selected = RandomCodeGenerator.get_code(
        URI, 1234, Code("SNOMED-CT", "38341003", "Hypertension")
    )
    assert selected is not None
    assert (selected.system, selected.code, selected.display) == (
        "http://snomed.info/sct",
        "312858004",
        "Neonatal tracheobronchial haemorrhage",
    )


@pytest.mark.parametrize(
    "name,message",
    [
        ("noExpansion.ValueSet.json", "ValueSet does not contain compose or expansion"),
        ("noTotal.ValueSet.json", "No total element in ValueSet expand result"),
        ("noContains.ValueSet.json", "ValueSet expansion does not contain any codes"),
    ],
)
def test_invalid_expansions(name: str, message: str) -> None:
    """Java: throwsWhenNoExpansion/throwsWhenNoTotal/throwsWhenNoContains."""
    with pytest.raises(RuntimeError, match=message):
        RandomCodeGenerator.load_value_set(URI, fixture(name))


def test_missing_code_elements() -> None:
    """Java: RandomCodeGeneratorTest#throwsWhenMissingCodeElements."""
    RandomCodeGenerator.load_value_set(URI, fixture("missingCodeElements.ValueSet.json"))
    with pytest.raises(RuntimeError, match="does not contain system, code and display"):
        RandomCodeGenerator.get_code(URI, 1234, None)
    assert RandomCodeGenerator.selectedCodes == []


def test_invalid_value_set_url() -> None:
    """Java: RandomCodeGeneratorTest#invalidValueSetUrlTest."""
    fallback = Code("SNOMED-CT", "38341003", "Hypertension")
    assert RandomCodeGenerator.get_code("", 1234, fallback) is fallback
    assert RandomCodeGenerator.get_code("", 1234) is None
    assert not RandomCodeGenerator.code_in_value_set(fallback, "")
    assert RandomCodeGenerator.selectedCodes == []


def test_cache_identity_and_overloads() -> None:
    value = Code("s", "c", "display")
    RandomCodeGenerator.codeListCache[URI] = [value]
    assert RandomCodeGenerator.get_code(URI, 42) is value
    assert RandomCodeGenerator.selectedCodes == []
    assert RandomCodeGenerator.get_code(URI, 42, None) is value
    assert RandomCodeGenerator.selectedCodes == [value]
    assert RandomCodeGenerator.code_in_value_set(Code("s", "c", "different"), URI)
    assert not RandomCodeGenerator.code_in_value_set(Code("s", "other", "different"), URI)
    RandomCodeGenerator.load_value_set(URI, {})  # existing cache is never replaced or revalidated
    assert RandomCodeGenerator.codeListCache[URI] == [value]


def test_compose_order_url_fallback_and_validation() -> None:
    vs = {
        "url": URI,
        "compose": {
            "include": [
                {
                    "system": "s1",
                    "concept": [{"code": "b", "display": "B"}, {"code": "a", "display": "A"}],
                },
                {"system": "s2", "concept": [{"code": "c", "display": "C"}]},
            ]
        },
    }
    RandomCodeGenerator.load_value_set(None, vs)
    assert [c.code for c in RandomCodeGenerator.codeListCache[URI]] == ["b", "a", "c"]
    RandomCodeGenerator.load_value_set(None, {})
    with pytest.raises(RuntimeError, match="does not contain any codes defined within compose"):
        RandomCodeGenerator.load_value_set(
            "http://example.org/empty", {"compose": {"include": [{"system": "s"}]}}
        )
    RandomCodeGenerator.validate_code(
        Code(" ", " ", " ")
    )  # StringUtils.isAnyEmpty doesn't reject whitespace
    with pytest.raises(ValueError):
        RandomCodeGenerator.codeListCache["http://example.org/zero"] = []
        RandomCodeGenerator.get_code("http://example.org/zero", 1)


def test_network_expansion_is_explicitly_excluded() -> None:
    RandomCodeGenerator.set_base_url("http://example.org/terminology")
    assert (
        RandomCodeGenerator.expandBaseUrl == "http://example.org/terminology/ValueSet/$expand?url="
    )
    with pytest.raises(NotImplementedError, match="out of scope"):
        RandomCodeGenerator.get_code("http://example.org/uncached", 42)
