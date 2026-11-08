"""Java: EncounterModuleTest, DeathModuleTest and ImmunizationsTest."""

from __future__ import annotations

import pytest

from synthea.modules.death_module import DeathModule
from synthea.modules.encounter_module import EncounterModule
from synthea.modules.immunizations import Immunizations
from synthea.world.agents.person import Person
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.health_record import Code, EncounterType, Medication
from tests.parity.test_encounter import date, participants
from tests.parity.test_encounter import encounter_config as encounter_config
from tests.parity.test_encounter import module_constructor_double as module_constructor_double


@pytest.mark.parametrize(
    "severity,kind",
    [
        (0, EncounterType.WELLNESS),
        (501, EncounterType.EMERGENCY),
        (351, EncounterType.URGENTCARE),
        (301, EncounterType.OUTPATIENT),
    ],
)
def test_encounter_has_clinician_and_provider(
    encounter_config: None, module_constructor_double: None, severity: int, kind: EncounterType
) -> None:
    """Java: four EncounterModuleTest clinician/provider tests with isolated patient state."""
    p, org, clinicians, birth, _ = participants(0)
    module = EncounterModule()
    module.process(p, birth)
    time = birth
    if severity:
        module.end_encounter_module_encounters(p, birth + 3600000)
        time += 604800000
        p.set_symptom("Test", "Test", "Test", time, severity, False)
        module.process(p, time)
    assert p.record is not None
    encounter = p.record.encounters[-1]
    assert encounter.type == kind.to_string()
    assert encounter.provider is org
    assert encounter.clinician in clinicians
    count, draws = len(p.record.encounters), p.get_count()
    module.process(p, time)
    assert len(p.record.encounters) == count
    assert p.get_count() == draws
    assert (
        EncounterModule.create_encounter(
            p, time, kind, ClinicianSpecialty.GENERAL_PRACTICE, None, "Other"
        )
        is None
    )
    assert module.clone() is module


@pytest.mark.parametrize("severity", [300, 350, 500])
def test_encounter_strict_symptom_thresholds(
    encounter_config: None, module_constructor_double: None, severity: int
) -> None:
    """Java: process uses > rather than >= at every symptom threshold."""
    p, _, _, birth, _ = participants(0)
    module = EncounterModule()
    module.process(p, birth)
    module.end_encounter_module_encounters(p, birth + 3600000)
    p.set_symptom("Test", "Test", "Test", birth + 604800000, severity, False)
    module.process(p, birth + 604800000)
    assert p.record is not None
    if severity == 300:
        assert len(p.record.encounters) == 1
    else:
        expected = EncounterType.OUTPATIENT if severity == 350 else EncounterType.URGENTCARE
        assert p.record.encounters[-1].type == expected.to_string()


@pytest.mark.parametrize(
    "months,interval_months",
    [
        (0, 1),
        (1, 1),
        (2, 2),
        (5, 2),
        (6, 3),
        (17, 3),
        (18, 6),
        (47, 6),
        (48, 12),
        (19 * 12, 12),
        (20 * 12, 36),
        (39 * 12, 36),
        (40 * 12, 24),
        (49 * 12, 24),
        (50 * 12, 12),
        (90 * 12, 12),
    ],
)
def test_encounter_recommended_intervals(
    encounter_config: None, module_constructor_double: None, months: int, interval_months: int
) -> None:
    """Java: recommendedTimeBetweenWellnessVisits age boundaries and chronic-medication cap."""
    from synthea.helpers.utilities import Utilities

    p, _, _, birth, _ = participants(0)
    time = date(1950 + months // 12, 1 + months % 12)
    module = EncounterModule()
    expected = (
        Utilities.convert_time("years", interval_months // 12)
        if interval_months >= 12
        else Utilities.convert_time("months", interval_months)
    )
    assert module.recommended_time_between_wellness_visits(p, time) == expected
    assert p.record is not None
    med = p.record.new_entry(lambda: Medication(birth, "chronic"))
    p.chronic_medications["chronic"] = med
    assert module.recommended_time_between_wellness_visits(p, time) == min(
        expected, Utilities.convert_time("years", 1)
    )


def test_encounter_does_not_close_another_modules_visit(
    encounter_config: None, module_constructor_double: None
) -> None:
    """Java: endEncounterModuleEncounters only ends reservations owned by EncounterModule."""
    p, _, _, birth, _ = participants(0)
    encounter = EncounterModule.create_encounter(
        p,
        birth,
        EncounterType.WELLNESS,
        ClinicianSpecialty.GENERAL_PRACTICE,
        EncounterModule.GENERAL_EXAM,
        "Other",
    )
    p.attributes[EncounterModule.ACTIVE_WELLNESS_ENCOUNTER] = True
    EncounterModule().end_encounter_module_encounters(p, birth + 3600000)
    assert p.get_current_encounter_module() == "Other"
    assert encounter.ended is False


def test_death_certificate(encounter_config: None) -> None:
    """Java: DeathModuleTest#testDeathCertificate, using real clinical objects."""
    p, _, _, birth, _ = participants(0)
    time = birth + 31536000000
    cause = Code("SNOMED-CT", "12345", "Some disease")
    p.record_death(time, cause)
    DeathModule.process(p, time)
    assert p.record is not None
    encounter = p.record.encounters[0]
    assert encounter.type == EncounterType.WELLNESS.to_string()
    assert encounter.start == time
    assert encounter.codes[0].code == "308646001"
    assert encounter.codes[0].display == "Death Certification"
    report = encounter.reports[0]
    assert report.type == "69409-1" and report.start == time
    assert report.codes[0].code == "69409-1"
    assert report.codes[0].display == "U.S. standard certificate of death - 2003 revision"
    observation = report.observations[0]
    assert observation.type == "69453-9" and observation.start == time
    assert observation.value is cause
    assert observation.codes[0].code == "69453-9"
    assert observation.codes[0].display == "Cause of Death [US Standard Certificate of Death]"
    assert observation.category == "exam"
    assert encounter.ended
    assert p.get_current_encounter_module() == "DeathModule"
    # The lock prevents ordinary future encounters; Java does not deduplicate certification.
    DeathModule.process(p, time)
    assert len(p.record.encounters) == 2


@pytest.mark.parametrize("dead", [False, True])
def test_death_no_certificate_without_death_and_cause(encounter_config: None, dead: bool) -> None:
    """Java: DeathModule#process requires both death and a known cause."""
    p, _, _, birth, _ = participants(0)
    if dead:
        p.record_death(birth + 1, None)
    else:
        p.attributes[Person.CAUSE_OF_DEATH] = Code("s", "c", "cause")
    DeathModule.process(p, birth + 1)
    assert p.record is not None and not p.record.encounters


@pytest.mark.parametrize("code,expected", [("52", 2), (None, 1), ("unknown", 1)])
def test_immunizations_maximum_doses(code: str | None, expected: int) -> None:
    """Java: ImmunizationsTest#testMaximumDoses / testMaximumDosesNothing."""
    assert Immunizations.get_maximum_doses(code) == expected


@pytest.mark.parametrize("months,expected", [(53, 1), (54, -1)])
def test_immunizations_four_year_window(months: int, expected: int) -> None:
    """Java: immunizationDue excludes recommendations that are at least 48 months old."""
    p = Person(0)
    p.attributes[Person.BIRTHDATE] = date(2000)
    assert (
        Immunizations.immunization_due("hepb", p, date(2000 + months // 12, 1 + months % 12), {})
        == expected
    )


def test_immunizations_historical_availability_and_history_side_effect() -> None:
    """Java: immunizationDue adds history even when the vaccine is not yet available."""
    p = Person(0)
    p.attributes[Person.BIRTHDATE] = date(1980)
    history: dict[str, list[int]] = {}
    assert Immunizations.immunization_due("hepb", p, date(1980), history) == -1
    assert history == {"hepb": []}
    assert Immunizations.immunization_due("hepb", p, date(1981), history) == 1
    history["hepb"] = [date(1981)] * 3
    assert Immunizations.immunization_due("hepb", p, date(1981), history) == -1


def test_encounter_cardiology_uses_first_loaded_provider(encounter_config: None) -> None:
    """Java: createEncounter uses the first provider for cardiology and specialty fallback."""
    from synthea.world.agents.provider import Provider

    p, org, clinicians, birth, _ = participants(0)
    preferred = Provider()
    preferred.uuid = "preferred-other"
    p.set_provider(EncounterType.OUTPATIENT, preferred)
    encounter = EncounterModule.create_encounter(
        p,
        birth,
        EncounterType.OUTPATIENT,
        ClinicianSpecialty.CARDIOLOGY,
        EncounterModule.ENCOUNTER_CHECKUP,
        "Cardiac",
    )
    assert encounter.provider is org
    assert encounter.clinician in clinicians


def test_encounter_wellness_code_at_eighteenth_birthday(encounter_config: None) -> None:
    """Java: getWellnessVisitCode changes exactly at the eighteenth birthday."""
    p, _, _, _, _ = participants(0)
    assert (
        EncounterModule.get_wellness_visit_code(p, date(1967, 12, 31))
        is EncounterModule.WELL_CHILD_VISIT
    )
    assert EncounterModule.get_wellness_visit_code(p, date(1968)) is EncounterModule.GENERAL_EXAM
