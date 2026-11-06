"""Exact T11 component parity: Person_double supplies only the real T01 RNG."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.simple_yml import SimpleYML
from synthea.helpers.utilities import Utilities
from synthea.javacompat.fmt import double_to_string
from synthea.world.concepts.biometrics_config import BiometricsConfig
from synthea.world.concepts.bmi import BMI
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.names import Names
from synthea.world.concepts.race_and_ethnicity import RaceAndEthnicity
from synthea.world.concepts.telemedicine_config import (
    TelemedicineConfig,
    TelemedicineProbabilities,
)
from synthea.world.concepts.vital_sign import VitalSign


class Person_double(DefaultRandomNumberGenerator):  # noqa: N801
    """Only real T01 RNG plumbing; Person construction otherwise reaches T16 stub."""


def _biometrics() -> dict[str, object]:
    """Traverse the actual resource and exercise every public config lookup overload."""
    output: dict[str, object] = {}

    def walk(mapping: dict[str, object], prefix: str) -> None:
        for key in mapping:
            path = prefix + key
            value = BiometricsConfig.get(path)
            output[path] = value
            if isinstance(value, dict):
                walk(value, path + ".")
            if isinstance(value, list):
                if all(type(item) in (float, int) for item in value):
                    output[path + "#doubles"] = BiometricsConfig.doubles(path)
                if all(type(item) is int for item in value):
                    output[path + "#ints"] = BiometricsConfig.ints(path)

    raw = SimpleYML(Utilities.read_resource("biometrics.yml")).internal_map
    assert raw is not None
    walk(raw, "")
    output["missing"] = BiometricsConfig.get("absent")
    output["default"] = BiometricsConfig.get("absent", "fallback")
    return output


@pytest.mark.parity
def test_concepts_component_parity(golden, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every T11 public method, seven seeds; >=1000 names per gender/language."""
    directory: Path = golden("ConceptsProbe")
    for append in (False, True):
        monkeypatch.setattr(Names, "append_numbers_to_names", append)
        for line in (directory / f"concepts-{str(append).lower()}.jsonl").read_text().splitlines():
            expected = json.loads(line)
            seed = int(expected["seed"])
            actual: dict[str, object] = {"seed": str(seed), "append": append}
            combos: list[object] = []
            for language in ("english", "spanish", "SPANISH", "french", "ſpanish", None):
                for gender in ("M", "F"):
                    person = Person_double(seed)
                    draws = [
                        [
                            Names.fake_first_name(gender, language, person),
                            Names.fake_last_name(language, person),
                        ]
                        for _ in range(1000)
                    ]
                    combos.append([language, gender, draws, str(person.rand_long())])
            actual["names"] = combos
            person = Person_double(seed)
            actual["addresses"] = [Names.fake_address(i % 2 == 0, person) for i in range(1000)]
            actual["addressNext"] = str(person.rand_long())
            actual["hashes"] = [[name, Names.add_hash(name)] for name, _ in expected["hashes"]]
            actual["race"] = [list(pair) for pair in RaceAndEthnicity.LOOK_UP_CDC_RACE.items()]
            actual["ethnicityCode"] = [
                list(pair) for pair in RaceAndEthnicity.LOOK_UP_CDC_ETHNICITY_CODE.items()
            ]
            actual["ethnicityDisplay"] = [
                list(pair) for pair in RaceAndEthnicity.LOOK_UP_CDC_ETHNICITY_DISPLAY.items()
            ]
            actual["specialties"] = [
                [specialty, ClinicianSpecialty.get_cms_provider_specialty_code(specialty)]
                for specialty in [*ClinicianSpecialty.get_specialties(), "unrecognized"]
            ]
            actual["vitals"] = [
                [
                    sign.name,
                    sign.to_string(),
                    VitalSign.from_string(sign.to_string()).name,
                    VitalSign.from_string(sign.to_string().lower()).name,
                    VitalSign.from_string(sign.name).name,
                ]
                for sign in VitalSign
            ]
            actual["unicodeVital"] = VitalSign.from_string("Weİght").name
            actual["biometrics"] = _biometrics()
            bmis: list[object] = []
            for i, row in enumerate(expected["bmi"]):
                if i < 200:
                    height = person.rand(1.0, 300.0)
                    weight = person.rand(0.0, 1000.0)
                else:
                    height, weight = float(row[0]), float(row[1])
                bmis.append(
                    [
                        double_to_string(height),
                        double_to_string(weight),
                        double_to_string(BMI.calculate(height, weight)),
                        double_to_string(BMI.weight_for_height_and_bmi(height, weight)),
                    ]
                )
            actual["bmi"] = bmis
            config = TelemedicineConfig.from_json()
            actual["telemedicineStart"] = str(config.get_telemedicine_start_time())
            actual["insurance"] = config.get_high_emergency_use_insurance_names()
            distributions: list[object] = []
            for distribution in [
                config.get_pre_telemed_high_emergency(),
                config.get_pre_telemed_typical_emergency(),
                config.get_telemed_high_emergency(),
                config.get_telemed_typical_emergency(),
                TelemedicineProbabilities(
                    {"ambulatory": 2.0, "emergency": 1.0}
                ).to_enumerated_distribution(),
                TelemedicineProbabilities(
                    {"ambulatory": 0.0, "emergency": 1.0, "telemedicine": 3.0}
                ).to_enumerated_distribution(),
            ]:
                assert distribution is not None
                pmf = [
                    [value, double_to_string(probability)]
                    for value, probability in distribution.get_pmf()
                ]
                distribution.reseed_random_generator(seed)
                distributions.append([pmf, [distribution.sample() for _ in range(1000)]])
            actual["distributions"] = distributions
            assert actual == expected
