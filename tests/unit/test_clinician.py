"""Unit tests for Clinician (T13). No upstream ClinicianTest exists; these
cover the constructor's NPI/UUID behaviour and counter semantics directly
from Clinician.java."""

from __future__ import annotations

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.world.agents.clinician import Clinician
from synthea.world.agents.person import Point2DDouble
from synthea.world.agents.provider import Provider


def _organization(npi: str = "1234567893") -> Provider:
    provider = Provider()
    provider.npi = npi
    return provider


def test_to_clinician_npi() -> None:
    """toClinicianNPI(0) is Provider.toNPI(999999999): all digits are 9; five
    doubled steps contribute 9 each (18 -> 8 + 1) and four single steps
    contribute 9 each, totalling 24 + 45 + 36 = 105, so the check digit is
    110 - 105 = 5."""
    assert Clinician.to_clinician_npi(0) == "9999999995"


def test_to_clinician_npi_cap() -> None:
    with pytest.raises(
        ValueError, match=r"Supplied id \(1000000000\) is too big, max is 999999999"
    ):
        Clinician.to_clinician_npi(1_000_000_000)


def test_constructor_deterministic_uuid_and_fields() -> None:
    org = _organization()
    first = Clinician(42, DefaultRandomNumberGenerator(7), 11, org)
    second = Clinician(42, DefaultRandomNumberGenerator(7), 11, org)
    other = Clinician(42, DefaultRandomNumberGenerator(7), 12, org)
    assert first.uuid == second.uuid
    assert first.uuid != other.uuid
    assert first.identifier == 11
    assert first.npi == Clinician.to_clinician_npi(11)
    assert first.get_resource_id() == first.uuid
    assert first.get_organization() is org
    # Java: populationSeed is declared but never set by the constructor.
    assert first.population_seed == 0
    assert first.get_encounter_count() == 0
    assert first.get_procedure_count() == 0


def test_constructor_null_organization_uses_identifier_in_uuid_base() -> None:
    with_org = Clinician(1, DefaultRandomNumberGenerator(3), 5, _organization("5"))
    without_org = Clinician(1, DefaultRandomNumberGenerator(3), 5, None)  # type: ignore[arg-type]
    # organization == null -> the base string uses the identifier in place of
    # organization.npi ("5" here), so the UUIDs coincide.
    assert with_org.uuid == without_org.uuid
    assert without_org.get_organization() is None


def test_increment_returns_pre_increment_count() -> None:
    """Java: encounters++ / procedures++ return the value before increment."""
    clinician = Clinician(0, DefaultRandomNumberGenerator(0), 0, _organization())
    assert clinician.increment_encounters() == 0
    assert clinician.increment_encounters() == 1
    assert clinician.get_encounter_count() == 2
    assert clinician.increment_procedures() == 0
    assert clinician.get_procedure_count() == 1


def test_fullname_and_services() -> None:
    clinician = Clinician(0, DefaultRandomNumberGenerator(0), 0, _organization())
    # Java string concatenation renders missing attributes as "null".
    assert clinician.get_fullname() == "null null"
    clinician.attributes[Clinician.NAME_PREFIX] = "Dr."
    clinician.attributes[Clinician.NAME] = "Jane Doe"
    assert clinician.get_fullname() == "Dr. Jane Doe"
    assert clinician.has_service(Clinician.WELLNESS) is False
    clinician.services_provided.append(Clinician.WELLNESS)
    assert clinician.has_service(Clinician.WELLNESS) is True
    assert clinician.get_attributes() is clinician.attributes


def test_lon_lat_from_coordinate_attribute() -> None:
    clinician = Clinician(0, DefaultRandomNumberGenerator(0), 0, _organization())
    clinician.attributes["coordinate"] = Point2DDouble(-71.0, 42.5)
    assert clinician.get_lon_lat().get_x() == -71.0
    assert clinician.get_x() == -71.0
    assert clinician.get_y() == 42.5
