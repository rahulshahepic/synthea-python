"""Java JUnit: ClinicianSpecialtyTest, TelemedicineConfigTest; T11 edge contracts."""

import math
from unittest.mock import Mock

import pytest

from synthea.helpers.simple_yml import SimpleYML
from synthea.world.concepts.biometrics_config import BiometricsConfig
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.names import Names
from synthea.world.concepts.race_and_ethnicity import RaceAndEthnicity
from synthea.world.concepts.telemedicine_config import (
    EnumeratedDistribution,
    TelemedicineConfig,
    TelemedicineProbabilities,
)
from synthea.world.concepts.vital_sign import VitalSign


def test_specialties_map() -> None:
    """Java: ClinicianSpecialtyTest#testSpecialtiesMap."""
    specialties = ClinicianSpecialty.get_specialties()
    assert specialties
    assert all(len(ClinicianSpecialty.get_cms_provider_specialty_code(s)) == 2 for s in specialties)
    assert ClinicianSpecialty.get_cms_provider_specialty_code("unknown") == "01"
    specialties.clear()
    assert ClinicianSpecialty.get_specialties()


def test_telemedicine_from_json() -> None:
    """Java: TelemedicineConfigTest#testFromJSON."""
    config = TelemedicineConfig.from_json()
    distribution = config.get_pre_telemed_typical_emergency()
    assert distribution is not None
    assert dict(distribution.get_pmf())[TelemedicineConfig.EMERGENCY] == 0.25


def test_vital_sign_display_lookup_and_enum_name_fallback() -> None:
    for sign in VitalSign:
        assert VitalSign.from_string(sign.to_string().swapcase()) is sign
        assert VitalSign.from_string(sign.name) is sign
        assert str(sign) == sign.to_string()
    with pytest.raises(KeyError):
        VitalSign.from_string("not a vital")
    # The enum fallback is case-sensitive, unlike display-name matching.
    with pytest.raises(KeyError):
        VitalSign.from_string("systolic_blood_pressure")


def test_biometrics_types_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        BiometricsConfig, "biometrics", SimpleYML("a: [1, 2]\nb: [1, 2.5]\nc: [true]\n")
    )
    assert BiometricsConfig.ints("a") == [1, 2]
    assert BiometricsConfig.doubles("b") == [1.0, 2.5]
    for path in ("b", "c", "missing"):
        with pytest.raises(TypeError):
            BiometricsConfig.ints(path)
    with pytest.raises(TypeError):
        BiometricsConfig.doubles("c")
    assert BiometricsConfig.get("missing") is None
    fallback = object()
    assert BiometricsConfig.get("missing", fallback) is fallback


def test_immutable_race_maps() -> None:
    for mapping in (
        RaceAndEthnicity.create_cdc_race_lookup(),
        RaceAndEthnicity.create_cdc_ethnicity_lookup(),
        RaceAndEthnicity.create_cdc_ethnicity_display_lookup(),
    ):
        assert len(mapping) == 7
        with pytest.raises(TypeError):
            mapping["new"] = "invalid"


@pytest.mark.parametrize(
    "weights", [[], [("a", 0.0)], [("a", -1.0)], [("a", math.inf)], [("a", math.nan)]]
)
def test_distribution_rejects_invalid_probabilities(weights: list[tuple[str, float]]) -> None:
    with pytest.raises(ValueError):
        EnumeratedDistribution(weights)


def test_distribution_reseed_and_pmf_copy() -> None:
    probabilities = TelemedicineProbabilities({"ambulatory": 2.0, "emergency": 1.0})
    distribution = probabilities.to_enumerated_distribution()
    assert distribution.get_pmf() == [("ambulatory", 2.0 / 3), ("emergency", 1.0 / 3)]
    with pytest.raises(RuntimeError, match="reseed first"):
        distribution.sample()
    distribution.reseed_random_generator(42)
    first = [distribution.sample() for _ in range(100)]
    distribution.get_pmf().clear()
    distribution.reseed_random_generator(42)
    assert first == [distribution.sample() for _ in range(100)]
    assert probabilities.telemedicine == 0.0


def test_names_loaded_resource_and_hash_contract() -> None:
    assert Names.load_names().get("english.M") == Names.names.get("english.M")
    assert Names.add_hash("") == "0"


def test_distribution_exact_boundary_matches_commons_math_binary_search() -> None:
    """Math3.6.1 binarySearch returns equality index; strict check falls back last."""
    distribution = EnumeratedDistribution([(value, 0.25) for value in "abcd"])
    distribution._random = Mock(next_double=Mock(return_value=0.25))
    assert distribution.sample() == "d"
