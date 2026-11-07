"""Unit tests for Provider (T13).

Ports the upstream JUnit tests in java/src/test/.../ProviderTest.java where
they make sense without a full population run, plus hand-computed NPI cases.
The load-and-find JUnit tests that need only a state load are covered by the
ProviderProbe parity test (tests/parity/test_provider.py) instead; the ones
listed in test_provider_skipped_upstream document the rest.
"""

from __future__ import annotations

import pytest

import synthea.world.agents.person as person_module
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.world.agents.person import Person
from synthea.world.agents.provider import Provider, ProviderType
from synthea.world.concepts.health_record import EncounterType
from synthea.world.geography.location import Location
from tests.parity.person_doubles import CoverageRecordDouble, HealthRecordDouble


@pytest.fixture(autouse=True)
def _person_doubles(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow real Person construction while T16/T14 are unmerged (see the
    parity test docstring in tests/parity/test_provider.py)."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)


@pytest.fixture(autouse=True)
def _clear_providers() -> None:
    Provider.clear()


def test_to_npi_check_digit() -> None:
    """Upstream ProviderTest.testNPICreation.

    Hand-check for 123456789: prefix constant 24; digits from the right are
    doubled on even steps (starting with the units digit): contributions
    9*2->8+1, 8, 7*2->4+1, 6, 5*2->0+1, 4, 3*2->6, 2, 1*2->2 sum to 43;
    24 + 43 = 67, so the check digit is 70 - 67 = 3.
    """
    assert Provider.to_npi(123_456_789) == "1234567893"


def test_to_npi_requires_nine_digits() -> None:
    with pytest.raises(ValueError, match="should be exactly 9 digits"):
        Provider.to_npi(99_999_999)
    with pytest.raises(ValueError, match="should be exactly 9 digits"):
        Provider.to_npi(1_000_000_000)


def test_to_provider_npi_from_zero() -> None:
    """toProviderNPI("0") is toNPI(888888888): all digits are 8; five doubled
    steps contribute 7 each (16 -> 6 + 1) and four single steps contribute 8
    each, so the running total is 24 + 35 + 32 = 91 and the check digit is
    100 - 91 = 9."""
    assert Provider.to_provider_npi("0", 123) == "8888888889"


def test_to_provider_npi_unparseable_id_uses_default() -> None:
    # defaultId 0 gives the same value as the explicit "0" case above.
    assert Provider.to_provider_npi("not-a-number", 0) == "8888888889"
    assert Provider.to_provider_npi(None, 0) == "8888888889"  # type: ignore[arg-type]


def test_to_provider_npi_cap() -> None:
    with pytest.raises(ValueError, match=r"Supplied id \(888888889\) is too big, max is 888888888"):
        Provider.to_provider_npi("888888889", 0)


def test_csv_line_to_provider_full_row() -> None:
    row = {
        "id": "42",
        "npi": "1234567893",
        "name": "General Hospital",
        "address": "1 Main St",
        "city": "Boston",
        "state": "MA",
        "zip": "02101",
        "fips_county": "025",
        "phone": "555-0100",
        "ownership": "Private",
        "category": "01",
        "provider_type_code": "00",
        "provider_num": "123456",
        "pin": "PIN123",
        "upin": "UPIN123",
        "region_code": "01",
        "clia_lab_number": "CLIA1",
        "bed_count": "120",
        "lat": "42.36",
        "lon": "-71.06",
        "emergency": "true",
    }
    provider = Provider.csv_line_to_provider(row)
    assert provider.id == "42"
    assert provider.npi == "1234567893"
    assert provider.name == "General Hospital"
    assert provider.bed_count == 120
    assert provider.cms_pin == "PIN123"
    assert provider.cms_upin == "UPIN123"
    # setLocation(lon, lat): x is longitude, y is latitude.
    assert provider.get_x() == -71.06
    assert provider.get_y() == 42.36
    # Only unmapped keys remain in the row for the attributes table.
    assert row == {"emergency": "true"}


def test_csv_line_to_provider_defaults_and_cleanup() -> None:
    row = {
        "name": "",
        "pin": "123456789012345",  # 15 chars > 14 -> dropped
        "upin": "1234567890123",  # 13 chars > 12 -> dropped
        "bed_count": "not-a-number",  # parse failure ignored
        "LAT": "junk",
        "LON": "junk",
    }
    provider = Provider.csv_line_to_provider(row)
    # No id and no npi: npi derives from the current loaded count (0 here,
    # after clear), and the empty name falls back to the id.
    assert provider.npi == "8888888889"
    assert provider.id == provider.npi
    assert provider.name == provider.id
    assert provider.cms_pin is None
    assert provider.cms_upin is None
    assert provider.bed_count is None
    # Unparseable coordinates fall back to (0.0, 0.0).
    assert provider.get_x() == 0.0
    assert provider.get_y() == 0.0


def test_merge_copies_null_fields_and_unions_services() -> None:
    """Upstream ProviderTest.testProviderMerge, without the state load."""
    source = Provider.csv_line_to_provider(
        {"id": "7", "npi": "1234567893", "name": "Merged Hospital", "lat": "1.5", "lon": "2.5"}
    )
    source.services_provided.add(EncounterType.WELLNESS)
    blank = Provider()
    blank.uuid = None  # type: ignore[assignment]
    blank.merge(source)
    assert blank.uuid == source.uuid
    assert blank.name == source.name
    assert blank.services_provided == source.services_provided


def test_merge_utilization_sums_cells() -> None:
    left = Provider()
    left.increment_encounters(EncounterType.WELLNESS, 2020)
    right = Provider()
    right.increment_encounters(EncounterType.WELLNESS, 2020)
    right.increment_labs(2021)
    left.merge(right)
    utilization = left.get_utilization()
    assert utilization[(2020, Provider.ENCOUNTERS)] == 2
    assert utilization[(2020, Provider.ENCOUNTERS + "-wellness")] == 2
    assert utilization[(2021, Provider.LABS)] == 1


def test_increment_encounters_counts_both_keys() -> None:
    provider = Provider()
    provider.increment_encounters(EncounterType.AMBULATORY, 1999)
    utilization = provider.get_utilization()
    assert utilization[(1999, "encounters")] == 1
    assert utilization[(1999, "encounters-ambulatory")] == 1
    provider.add_revenue(10.5)
    provider.add_revenue(0.25)
    assert provider.get_revenue() == 10.75


def test_accepts_veteran_and_ihs() -> None:
    """Upstream ProviderTest.testVaFacilityOnlyAcceptsVeteran, plus IHS."""
    va = Provider()
    va.type = ProviderType.VETERAN
    veteran = Person(0)
    veteran.attributes[Person.VETERAN] = "vietnam"
    non_vet = Person(1)
    assert va.accepts(veteran, 0) is True
    assert va.accepts(non_vet, 0) is False

    ihs = Provider()
    ihs.type = ProviderType.IHS
    native = Person(2)
    native.attributes[Person.RACE] = "native"
    assert ihs.accepts(native, 0) is True
    assert ihs.accepts(non_vet, 0) is False

    untyped = Provider()
    assert untyped.accepts(non_vet, 0) is True


def test_insert_into_provider_map_merges_duplicates() -> None:
    row = {"id": "9", "npi": "1234567893", "name": "Dup Clinic", "lat": "3.0", "lon": "4.0"}
    first = Provider.csv_line_to_provider(dict(row))
    first.services_provided.add(EncounterType.WELLNESS)
    Provider.insert_into_provider_map(first)
    assert Provider.loaded == 1
    second = Provider.csv_line_to_provider(dict(row))
    second.services_provided.add(EncounterType.HOSPICE)
    Provider.insert_into_provider_map(second)
    # Same uuid (npi + name): merged into the first, not re-inserted.
    assert Provider.loaded == 1
    providers = Provider.get_provider_list()
    assert len(providers) == 1
    assert providers[0].services_provided == {EncounterType.WELLNESS, EncounterType.HOSPICE}


def test_load_providers_massachusetts_smoke() -> None:
    """Upstream ProviderTest.testLoadProvidersByStateName /
    testGenerateClinicianByState / testAllFacilitiesHaveAnIdOrNpi, on the
    default test state."""
    location = Location("Massachusetts", None)
    Provider.load_providers(location, DefaultRandomNumberGenerator(1))
    providers = Provider.get_provider_list()
    assert providers
    for provider in providers:
        assert provider.id is not None or provider.npi is not None
    first = providers[0]
    assert first.clinician_map.get("GENERAL PRACTICE")


def test_provider_skipped_upstream() -> None:
    """Upstream ProviderTest cases not ported here, with reasons:

    * testLoadProvidersByAbbreviation / testGenerateClinicianByAbbreviation:
      the "alternative" state in test properties is Utah, loaded the same way
      as the Massachusetts smoke test above.
    * testNearest{Inpatient,Ambulatory,Wellness,Emergency,UrgentCare}In{State,
      City} and testNearestEmergencyInDC (@Ignore upstream): findService over
      a real load is exercised deterministically by the ProviderProbe parity
      test (tests/parity/test_provider.py, ops cases).
    * testAllFiles: walks every providers/*.csv through the 6-arg
      loadProviders; the default files for all loaded states are exercised by
      the parity loads, and walking the resource tree is a Java classpath
      idiom with no Python equivalent in the port.
    """
