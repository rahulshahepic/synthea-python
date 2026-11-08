"""Java: C19ImmunizationModule.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Protocol, cast

from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.modules.covid.c19_vaccine import C19Vaccine, EUASet
from synthea.modules.covid.c19_vaccine_age_distributions import C19VaccineAgeDistributions
from synthea.modules.covid.late_adopter_model import LateAdopterModel
from synthea.modules.encounter_module import EncounterModule
from synthea.modules.immunizations import Immunizations
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.health_record import Code, EncounterType, HealthRecord

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class C19ImmunizationModule:
    """Java: C19ImmunizationModule."""

    COVID_CODE: ClassVar[str] = "840539006"
    FIRST_POSSIBLE_SHOT_TIME: ClassVar[int] = 1607688000000
    MODERNA_APPROVED: ClassVar[int] = 1608292800000
    JANSSEN_APPROVED: ClassVar[int] = 1614427200000
    EXPAND_AGE_TO_TWELVE: ClassVar[int] = 1620648000000
    LATE_ADOPTION_START_TIME: ClassVar[int] = 1631620800000
    FIRST_ELIGIBLE_AGE: ClassVar[int] = 16
    EXPANDED_ELIGIBLE_AGE: ClassVar[int] = 12
    C19_VACCINE_STATUS: ClassVar[str] = "C19_VACCINE_STATUS"
    C19_VACCINE: ClassVar[str] = "C19_VACCINE"
    C19_SCHEDULED_FIRST_SHOT: ClassVar[str] = "C19_SCHEDULED_FIRST_SHOT"
    C19_SCHEDULED_SECOND_SHOT: ClassVar[str] = "C19_SCHEDULED_SECOND_SHOT"
    C19_LATE_ADOPTER_MODEL: ClassVar[str] = "C19_LATE_ADOPTER_MODEL"
    C19_FULLY_VACCINATED: ClassVar[str] = "C19_FULLY_VACCINATED"
    C19_PERSON_ATTRS_KEY: ClassVar[str] = "covid19"

    def __init__(self) -> None:
        """Java: C19ImmunizationModule#C19ImmunizationModule.

        Java overloads:
        ()
        """
        # Java: constructing a Module subclass triggers Module.loadModules(),
        # which instantiates every core module — including a
        # C19ImmunizationModule — so when the registry has not been loaded
        # yet, initialize() runs once for the registry's instance before
        # this constructor's own initialize() runs. Because
        # C19VaccineAgeDistributions.loadRawDistribution() appends to its
        # static maps, that first construction double-loads the raw
        # distributions (the 12-15 list ends up filtered twice). Reproduced
        # here: if the Python registry has not been loaded, load it and
        # run the registry instance's initialize() first.
        from synthea.engine.module import Module

        if Module.modules is None:
            Module.get_module_suppliers()
            C19VaccineAgeDistributions.initialize()
            C19Vaccine.initialize()
        C19VaccineAgeDistributions.initialize()
        C19Vaccine.initialize()
        self.name: str = "COVID-19 Immunization Module"

    def clone(self) -> Module:
        """Java: C19ImmunizationModule#clone.

        Java overloads:
        ()
        """
        return cast("Module", self)

    @staticmethod
    def currently_has_covid(person: Person) -> bool:
        """Java: C19ImmunizationModule#currentlyHasCOVID.

        Java overloads:
        (Person person)
        """
        record = cast("HealthRecord", person.record)
        return record.condition_active(C19ImmunizationModule.COVID_CODE)

    @staticmethod
    def eligible_for_shot(person: Person, time: int) -> bool:
        """Java: C19ImmunizationModule#eligibleForShot.

        Java overloads:
        (Person person, long time)
        """
        age = person.age_in_years(time)
        return age >= C19ImmunizationModule.FIRST_ELIGIBLE_AGE or (
            time >= C19ImmunizationModule.EXPAND_AGE_TO_TWELVE
            and age >= C19ImmunizationModule.EXPANDED_ELIGIBLE_AGE
        )

    @staticmethod
    def decide_on_shot(person: Person, time: int) -> bool:
        """Java: C19ImmunizationModule#decideOnShot.

        Java overloads:
        (Person person, long time)
        """
        chance_of_getting_shot = C19VaccineAgeDistributions.chance_of_getting_shot(person, time)
        return chance_of_getting_shot >= person.rand()

    @staticmethod
    def select_vaccine(person: Person, time: int) -> EUASet:
        """Java: C19ImmunizationModule#selectVaccine.

        Java overloads:
        (Person person, long time)
        """
        if time < C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME:
            raise ValueError("No vaccines were available at time: " + str(time))
        elif time < C19ImmunizationModule.MODERNA_APPROVED:
            return EUASet.PFIZER
        elif (
            time >= C19ImmunizationModule.MODERNA_APPROVED
            and time <= C19ImmunizationModule.JANSSEN_APPROVED
        ):
            # Randomly select, with equal chance
            if person.rand() < 0.5:
                return EUASet.PFIZER
            else:
                return EUASet.MODERNA
        elif time > C19ImmunizationModule.JANSSEN_APPROVED:
            return C19Vaccine.select_shot(person)
        # Java falls through to `return null`; unreachable because the
        # approval constants are strictly increasing.
        return cast("EUASet", None)

    @staticmethod
    def vaccinate(person: Person, time: int, series: int) -> None:
        """Java: C19ImmunizationModule#vaccinate.

        Java overloads:
        (Person person, long time, int series)
        """
        encounter_code = Code(
            "http://snomed.info/sct",
            "33879002",
            "Administration of vaccine to produce active immunity (procedure)",
        )
        module_name = "COVID-19 Immunization Module"
        if person.has_current_encounter():
            # Do nothing, vaccinate at the current encounter...
            pass
        else:
            EncounterModule.create_encounter(
                person,
                time,
                EncounterType.OUTPATIENT,
                ClinicianSpecialty.GENERAL_PRACTICE,
                encounter_code,
                module_name,
            )
        record = cast("HealthRecord", person.record)
        immunization = record.immunization(time, "COVID19")
        immunization.series = series
        vaccine = C19Vaccine.EUAs[
            cast("EUASet", person.attributes.get(C19ImmunizationModule.C19_VACCINE))
        ]
        imm_code = Code("http://hl7.org/fhir/sid/cvx", vaccine.get_cvx(), vaccine.get_display())
        immunization.codes.append(imm_code)

        immunization_history = cast(
            "JavaHashMap[str, list[int]] | None",
            person.attributes.get(Immunizations.IMMUNIZATIONS),
        )
        if immunization_history is None:
            immunization_history = JavaHashMap()
            person.attributes[Immunizations.IMMUNIZATIONS] = immunization_history
        covid_immunization_history = immunization_history.get(
            C19ImmunizationModule.C19_PERSON_ATTRS_KEY
        )
        if covid_immunization_history is None:
            covid_immunization_history = []
            immunization_history[C19ImmunizationModule.C19_PERSON_ATTRS_KEY] = (
                covid_immunization_history
            )
        covid_immunization_history.append(time)
        record.encounter_end(time + Utilities.convert_time("minutes", 15), EncounterType.OUTPATIENT)
        if person.has_current_encounter() and person.get_current_encounter_module() == module_name:
            person.release_current_encounter(time, module_name)

    def process(self, person: Person, time: int) -> bool:
        """Java: C19ImmunizationModule#process.

        Java overloads:
        (Person person, long time)
        """
        if time < C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME:
            return False

        status = cast(
            "VaccinationStatus | None",
            person.attributes.get(C19ImmunizationModule.C19_VACCINE_STATUS),
        )
        if status is None:
            status = VaccinationStatus.NOT_ELIGIBLE
            person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = status

        if status == VaccinationStatus.NOT_ELIGIBLE:
            if C19ImmunizationModule.eligible_for_shot(person, time):
                if C19ImmunizationModule.decide_on_shot(person, time):
                    person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                        VaccinationStatus.WAITING_FOR_SHOT
                    )
                    shot_date = C19VaccineAgeDistributions.select_shot_time(person, time)
                    if shot_date < time:
                        # TODO: Figure out what to do when the person should receive
                        # their shot in the current time step (Java comment)
                        shot_date = time
                    person.attributes[C19ImmunizationModule.C19_SCHEDULED_FIRST_SHOT] = shot_date
                    person.attributes[C19ImmunizationModule.C19_VACCINE] = (
                        C19ImmunizationModule.select_vaccine(person, shot_date)
                    )
                else:
                    person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                        VaccinationStatus.POTENTIAL_LATE_ADOPTER
                    )
            else:
                person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                    VaccinationStatus.NOT_ELIGIBLE
                )
        elif status == VaccinationStatus.WAITING_FOR_SHOT:
            scheduled_shot_date = cast(
                "int", person.attributes.get(C19ImmunizationModule.C19_SCHEDULED_FIRST_SHOT)
            )
            if scheduled_shot_date <= time:
                if C19ImmunizationModule.currently_has_covid(person):
                    # wait for COVID to resolve before getting shot
                    return False
                C19ImmunizationModule.vaccinate(person, time, 1)
                vaccine_used = C19Vaccine.EUAs[
                    cast("EUASet", person.attributes.get(C19ImmunizationModule.C19_VACCINE))
                ]
                if vaccine_used.is_two_dose():
                    person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                        VaccinationStatus.FIRST_SHOT
                    )
                    person.attributes[C19ImmunizationModule.C19_SCHEDULED_SECOND_SHOT] = (
                        vaccine_used.get_time_between_doses() + time
                    )
                else:
                    person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                        VaccinationStatus.FULLY_VACCINATED
                    )
                    person.attributes[C19ImmunizationModule.C19_FULLY_VACCINATED] = True
        elif status == VaccinationStatus.FIRST_SHOT:
            # Assuming someone doesn't get COVID between first and second shot
            scheduled_second_shot_date = cast(
                "int", person.attributes.get(C19ImmunizationModule.C19_SCHEDULED_SECOND_SHOT)
            )
            if scheduled_second_shot_date <= time:
                C19ImmunizationModule.vaccinate(person, time, 2)
                person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                    VaccinationStatus.FULLY_VACCINATED
                )
                person.attributes[C19ImmunizationModule.C19_FULLY_VACCINATED] = True
        elif status in (
            VaccinationStatus.FULLY_VACCINATED,
            VaccinationStatus.NEVER_GOING_TO_GET_SHOT,
        ):
            # Java: separate FULLY_VACCINATED and NEVER_GOING_TO_GET_SHOT
            # cases, both do nothing.
            pass
        elif status == VaccinationStatus.POTENTIAL_LATE_ADOPTER:
            if time >= C19ImmunizationModule.LATE_ADOPTION_START_TIME:
                model = cast(
                    "LateAdopterModel | None",
                    person.attributes.get(C19ImmunizationModule.C19_LATE_ADOPTER_MODEL),
                )
                if model is None:
                    model = LateAdopterModel(person, time)
                    person.attributes[C19ImmunizationModule.C19_LATE_ADOPTER_MODEL] = model
                will_get_shot = model.will_get_shot(person, time)
                if will_get_shot:
                    person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                        VaccinationStatus.WAITING_FOR_SHOT
                    )
                    shot_date = time + Utilities.convert_time("weeks", 1)
                    person.attributes[C19ImmunizationModule.C19_SCHEDULED_FIRST_SHOT] = shot_date
                    person.attributes[C19ImmunizationModule.C19_VACCINE] = (
                        C19ImmunizationModule.select_vaccine(person, shot_date)
                    )
                elif model.is_not_getting_shot():
                    person.attributes[C19ImmunizationModule.C19_VACCINE_STATUS] = (
                        VaccinationStatus.NEVER_GOING_TO_GET_SHOT
                    )
        else:
            # should never get here
            raise RuntimeError(
                "COVID-19 Immunization entered an unknown state based on"
                "a person's vaccination status"
            )

        return False

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: C19ImmunizationModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError(
            "Java: C19ImmunizationModule#inventoryAttributes — out of scope: "
            "helpers/Attributes.java is not in docs/port_map.toml, so the "
            "Attributes.inventory helper has no owning task in the port"
        )


class VaccinationStatus(StrEnum):
    """Java: VaccinationStatus."""

    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    WAITING_FOR_SHOT = "WAITING_FOR_SHOT"
    POTENTIAL_LATE_ADOPTER = "POTENTIAL_LATE_ADOPTER"
    NEVER_GOING_TO_GET_SHOT = "NEVER_GOING_TO_GET_SHOT"
    FIRST_SHOT = "FIRST_SHOT"
    FULLY_VACCINATED = "FULLY_VACCINATED"


setattr(C19ImmunizationModule, "VaccinationStatus", VaccinationStatus)  # noqa: B010
