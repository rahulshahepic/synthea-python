"""Java: org.mitre.synthea.world.concepts.HealthRecord, including its nested entry types."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Iterator, MutableSet
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import IO, TYPE_CHECKING, ClassVar, cast
from uuid import UUID

from synthea.helpers.utilities import Utilities
from synthea.javacompat.bigdecimal import (
    RoundingMode,
    divide_exact,
    long_value,
    multiply,
    set_scale,
    value_of,
)
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.hashing import java_hash_code, string_compare_to
from synthea.javacompat.numbers import to_int32, to_int64

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.claim import Claim


_MISSING = object()


class OrderedSet[T](MutableSet[T]):
    """Java: LinkedHashSet, retaining insertion order and structural JSON equality.

    Goals are Gson JsonObjects (unhashable Python dicts); linear lookup preserves
    their equality semantics without replacing them with JSON text or salted hashes.
    """

    def __init__(self, values: Iterable[T] = ()) -> None:
        """Java: LinkedHashSet constructors."""
        self._values: list[T] = []
        for value in values:
            self.add(value)

    def __contains__(self, value: object) -> bool:
        """Java: LinkedHashSet#contains."""
        return value in self._values

    def __iter__(self) -> Iterator[T]:
        """Java: LinkedHashSet#iterator."""
        return iter(self._values)

    def __len__(self) -> int:
        """Java: LinkedHashSet#size."""
        return len(self._values)

    def add(self, value: T) -> None:
        """Java: LinkedHashSet#add."""
        if value not in self:
            self._values.append(value)

    def discard(self, value: T) -> None:
        """Java: LinkedHashSet#remove."""
        if value in self:
            self._values.remove(value)


class HealthRecord:
    """Java: HealthRecord."""

    ENCOUNTERS: ClassVar[str] = "encounters"
    PROCEDURES: ClassVar[str] = "procedures"
    MEDICATIONS: ClassVar[str] = "medications"
    IMMUNIZATIONS: ClassVar[str] = "immunizations"

    def __init__(self, person: Person) -> None:
        """Java: HealthRecord#HealthRecord.

        Java overloads:
        (Person person)
        """
        self.person: Person = person
        self.provider: Provider | None = None
        self.encounters: list[Encounter] = []
        self.present: JavaHashMap[str, Entry] = JavaHashMap()
        self.death: int | None = None
        self.demographics_at_record_creation: JavaHashMap[str, object] | None = None
        if person.attributes.get(person.HOUSEHOLD) is not None:
            self.demographics_at_record_creation = JavaHashMap(person.attributes)

    def provider_count(self) -> int:
        """Java: HealthRecord#providerCount.

        Java overloads:
        ()
        """
        return len({enc.provider.uuid for enc in self.encounters if enc.provider is not None})

    def text_summary(self) -> str:
        """Java: HealthRecord#textSummary.

        Java overloads:
        ()
        """
        areas = (
            ("Encounters", None),
            ("Observations", "observations"),
            ("Reports", "reports"),
            ("Conditions", "conditions"),
            ("Allergies", "allergies"),
            ("Procedures", "procedures"),
            ("Immunizations", "immunizations"),
            ("Medications", "medications"),
            ("Care Plans", "careplans"),
            ("Imaging Studies", "imaging_studies"),
        )
        lines = []
        for label, attr in areas:
            count = (
                len(self.encounters)
                if attr is None
                else sum(len(getattr(e, attr)) for e in self.encounters)
            )
            lines.append(f"{label + ':':17}{count}\n")
        return "".join(lines)

    def current_encounter(self, time: int) -> Encounter:
        """Java: HealthRecord#currentEncounter.

        Java overloads:
        (long time)
        """
        from synthea.modules.encounter_module import EncounterModule
        from synthea.world.concepts.clinician_specialty import ClinicianSpecialty

        encounter: Encounter | None = None
        if not self.encounters:
            encounter = EncounterModule.create_encounter(
                self.person,
                time,
                EncounterType.WELLNESS,
                ClinicianSpecialty.GENERAL_PRACTICE,
                EncounterModule.WELL_CHILD_VISIT,
                EncounterModule.NAME,
            )
            encounter.name = "First Wellness"
        for encounter in reversed(self.encounters):
            if encounter.start <= time:
                return encounter
        assert encounter is not None
        return encounter

    def time_since_last_wellness_encounter(self, time: int) -> int:
        """Java: HealthRecord#timeSinceLastWellnessEncounter.

        Java overloads:
        (long time)
        """
        encounter = self.last_wellness_encounter()
        return to_int64(time - encounter.start) if encounter is not None else (1 << 63) - 1

    def last_wellness_encounter(self) -> Encounter | None:
        """Java: HealthRecord#lastWellnessEncounter.

        Java overloads:
        ()
        """
        return next(
            (e for e in reversed(self.encounters) if e.type == EncounterType.WELLNESS.to_string()),
            None,
        )

    def observation(self, time: int, type: str, value: object) -> Observation:
        """Java: HealthRecord#observation.

        Java overloads:
        (long time, String type, Object value)
        """
        return self.current_encounter(time).add_observation(time, type, value)

    def multi_observation(self, time: int, type: str, number_of_observations: int) -> Observation:
        """Java: HealthRecord#multiObservation.

        Java overloads:
        (long time, String type, int numberOfObservations)
        """
        observation = Observation(time, type, None, record=self)
        encounter = self.current_encounter(time)
        count = number_of_observations
        if len(encounter.observations) >= number_of_observations:
            while count > 0:
                observation.observations.append(encounter.observations.pop())
                count -= 1
        encounter.observations.append(observation)
        return observation

    def get_latest_observation(self, type: str) -> Observation | None:
        """Java: HealthRecord#getLatestObservation.

        Java overloads:
        (String type)
        """
        for encounter in reversed(self.encounters):
            obs = encounter.find_observation(type)
            if obs is not None:
                return obs
        return None

    def condition_start(self, time: int, primary_code: str) -> Entry:
        """Java: HealthRecord#conditionStart.

        Java overloads:
        (long time, String primaryCode)
        """
        if primary_code not in self.present:
            condition = Entry(time, primary_code, record=self)
            encounter = self.current_encounter(time)
            encounter.conditions.append(condition)
            encounter.claim.add_line_item(condition)
            self.present[primary_code] = condition
        return self.present[primary_code]

    def condition_end(self, time: int, primary_code: str) -> None:
        """Java: HealthRecord#conditionEnd.

        Java overloads:
        (long time, String primaryCode)
        """
        if primary_code in self.present:
            self.present[primary_code].stop = time
            del self.present[primary_code]

    def condition_end_by_state(self, time: int, state_name: str) -> None:
        """Java: HealthRecord#conditionEndByState.

        Java overloads:
        (long time, String stateName)
        """
        condition = next(
            (e for e in self.present.values() if e.name is not None and e.name == state_name), None
        )
        if condition is not None:
            condition.stop = time
            self.present.remove(condition.type)

    def condition_active(self, type: str) -> bool:
        """Java: HealthRecord#conditionActive.

        Java overloads:
        (String type)
        """
        return type in self.present and self.present[type].stop == 0

    def present_onset(self, code: str) -> int | None:
        """Java: HealthRecord#presentOnset.

        Java overloads:
        (String code)
        """
        return self.present[code].start if code in self.present else None

    def allergy_start(self, time: int, primary_code: str) -> Allergy:
        """Java: HealthRecord#allergyStart.

        Java overloads:
        (long time, String primaryCode)
        """
        if primary_code not in self.present:
            allergy = Allergy(time, primary_code, record=self)
            self.current_encounter(time).allergies.append(allergy)
            self.present[primary_code] = allergy
        return cast(Allergy, self.present[primary_code])

    def allergy_end(self, time: int, primary_code: str) -> None:
        """Java: HealthRecord#allergyEnd.

        Java overloads:
        (long time, String primaryCode)
        """
        if primary_code in self.present:
            self.present[primary_code].stop = time
            del self.present[primary_code]

    def allergy_end_by_state(self, time: int, state_name: str) -> None:
        """Java: HealthRecord#allergyEndByState.

        Java overloads:
        (long time, String stateName)
        """
        allergy = next(
            (e for e in self.present.values() if e.name is not None and e.name == state_name), None
        )
        if allergy is not None:
            allergy.stop = time
            self.present.remove(allergy.type)

    def allergy_active(self, type: str) -> bool:
        """Java: HealthRecord#allergyActive.

        Java overloads:
        (String type)
        """
        return self.condition_active(type)

    def procedure(self, time: int, type: str) -> Procedure:
        """Java: HealthRecord#procedure.

        Java overloads:
        (long time, String type)
        """
        procedure = Procedure(time, type, record=self)
        encounter = self.current_encounter(time)
        encounter.procedures.append(procedure)
        encounter.claim.add_line_item(procedure)
        self.present[type] = procedure
        return procedure

    def device_implant(self, time: int, type: str) -> Device:
        """Java: HealthRecord#deviceImplant.

        Java overloads:
        (long time, String type)
        """
        device = Device(time, type, record=self)
        device.generate_udi(cast("RandomNumberGenerator", self.person))
        encounter = self.current_encounter(time)
        encounter.devices.append(device)
        encounter.claim.add_line_item(device)
        self.present[type] = device
        return device

    def device_remove(self, time: int, type: str) -> None:
        """Java: HealthRecord#deviceRemove.

        Java overloads:
        (long time, String type)
        """
        if type in self.present:
            self.present[type].stop = time
            del self.present[type]

    def device_remove_by_state(self, time: int, state_name: str) -> None:
        """Java: HealthRecord#deviceRemoveByState.

        Java overloads:
        (long time, String stateName)
        """
        device = next(
            (e for e in self.present.values() if e.name is not None and e.name == state_name), None
        )
        if device is not None:
            device.stop = time
            self.present.remove(device.type)

    def use_supply(self, time: int, code: Code, quantity: int) -> Supply:
        """Java: HealthRecord#useSupply.

        Java overloads:
        (long time, Code code, int quantity)
        """
        encounter = self.current_encounter(time)
        supply = Supply(time, code.display, record=self)
        supply.codes.append(code)
        supply.quantity = quantity
        encounter.supplies.append(supply)
        encounter.claim.add_line_item(supply)
        return supply

    def report(self, time: int, type: str, number_of_observations: int) -> Report:
        """Java: HealthRecord#report.

        Java overloads:
        (long time, String type, int numberOfObservations)
        """
        encounter = self.current_encounter(time)
        if len(encounter.observations) > number_of_observations:
            start = len(encounter.observations) - number_of_observations
            if start > len(encounter.observations):
                raise IndexError("Java IndexOutOfBoundsException")
            observations = encounter.observations[start:]
        else:
            observations = list(encounter.observations)
        report = Report(time, type, observations, record=self)
        encounter.reports.append(report)
        encounter.claim.add_line_item(report)
        for obs in observations:
            obs.report = report
        return report

    def encounter_start(self, time: int, type: EncounterType) -> Encounter:
        """Java: HealthRecord#encounterStart.

        Java overloads:
        (long time, EncounterType type)
        """
        encounter = Encounter(time, type.to_string(), record=self)
        self.encounters.append(encounter)
        return encounter

    def encounter_end(self, time: int, type: EncounterType) -> None:
        """Java: HealthRecord#encounterEnd.

        Java overloads:
        (long time, EncounterType type)
        """
        for encounter in reversed(self.encounters):
            encounter_type = EncounterType.from_string(encounter.type)
            if encounter_type == type and not encounter.ended:
                encounter.end(time)
                encounter.determine_cost()
                encounter.claim.assign_costs()
                return

    def last_encounter_time(self) -> int:
        """Java: HealthRecord#lastEncounterTime.

        Java overloads:
        ()
        """
        return max((e.stop for e in self.encounters), default=-(1 << 63))

    def immunization(self, time: int, type: str) -> Immunization:
        """Java: HealthRecord#immunization.

        Java overloads:
        (long time, String type)
        """
        immunization = Immunization(time, type, record=self)
        encounter = self.current_encounter(time)
        encounter.immunizations.append(immunization)
        encounter.claim.add_line_item(immunization)
        return immunization

    def medication_start(self, time: int, type: str, chronic: bool) -> Medication:
        """Java: HealthRecord#medicationStart.

        Java overloads:
        (long time, String type, boolean chronic)
        """
        if type not in self.present:
            medication = Medication(time, type, record=self)
            medication.chronic = chronic
            self.current_encounter(time).medications.append(medication)
            self.present[type] = medication
        else:
            medication = cast(Medication, self.present[type])
        if chronic:
            self.person.chronic_medications[type] = medication
        return medication

    def medication_administration(self, time: int, type: str) -> Medication:
        """Java: HealthRecord#medicationAdministration.

        Java overloads:
        (long time, String type)
        """
        medication = Medication(time, type, record=self)
        medication.stop = time
        medication.administration = True
        self.current_encounter(time).medications.append(medication)
        return medication

    def medication_end(self, time: int, type: str, reason: Code) -> None:
        """Java: HealthRecord#medicationEnd.

        Java overloads:
        (long time, String type, Code reason)
        """
        if type in self.present:
            medication = cast(Medication, self.present[type])
            medication.stop = time
            medication.stop_reason = reason
            self.chronic_medication_end(type)
            del self.present[type]

    def medication_end_by_state(self, time: int, state_name: str, reason: Code) -> None:
        """Java: HealthRecord#medicationEndByState.

        Java overloads:
        (long time, String stateName, Code reason)
        """
        medication = next(
            (e for e in self.present.values() if e.name is not None and e.name == state_name), None
        )
        if medication is not None:
            cast(Medication, medication).stop = time
            cast(Medication, medication).stop_reason = reason
            self.chronic_medication_end(medication.type)
            self.present.remove(medication.type)

    def chronic_medication_end(self, type: str) -> None:
        """Java: HealthRecord#chronicMedicationEnd.

        Java overloads:
        (String type)
        """
        self.person.chronic_medications.pop(type, None)

    def medication_active(self, type: str) -> bool:
        """Java: HealthRecord#medicationActive.

        Java overloads:
        (String type)
        """
        return type in self.present and self.present[type].stop == 0

    def careplan_start(self, time: int, type: str) -> CarePlan:
        """Java: HealthRecord#careplanStart.

        Java overloads:
        (long time, String type)
        """
        if type not in self.present:
            careplan = CarePlan(time, type, record=self)
            self.current_encounter(time).careplans.append(careplan)
            self.present[type] = careplan
        else:
            careplan = cast(CarePlan, self.present[type])
        return careplan

    def careplan_end(self, time: int, type: str, reason: Code) -> None:
        """Java: HealthRecord#careplanEnd.

        Java overloads:
        (long time, String type, Code reason)
        """
        if type in self.present:
            careplan = cast(CarePlan, self.present[type])
            careplan.stop = time
            careplan.stop_reason = reason
            del self.present[type]

    def careplan_end_by_state(self, time: int, state_name: str, reason: Code) -> None:
        """Java: HealthRecord#careplanEndByState.

        Java overloads:
        (long time, String stateName, Code reason)
        """
        careplan = next(
            (e for e in self.present.values() if e.name is not None and e.name == state_name), None
        )
        if careplan is not None:
            cast(CarePlan, careplan).stop = time
            cast(CarePlan, careplan).stop_reason = reason
            self.present.remove(careplan.type)

    def careplan_active(self, type: str) -> bool:
        """Java: HealthRecord#careplanActive.

        Java overloads:
        (String type)
        """
        return type in self.present and self.present[type].stop == 0

    def imaging_study(self, time: int, type: str, series: list[Series]) -> ImagingStudy:
        """Java: HealthRecord#imagingStudy.

        Java overloads:
        (long time, String type, List series)
        """
        study = ImagingStudy(self.person, time, type, record=self)
        study.series = series
        self.assign_imaging_study_dicom_uids(time, study)
        self.current_encounter(time).imaging_studies.append(study)
        return study

    def assign_imaging_study_dicom_uids(self, time: int, study: ImagingStudy) -> None:
        """Java: HealthRecord#assignImagingStudyDicomUids.

        Java overloads:
        (long time, ImagingStudy study)
        """
        for series_no, series in enumerate(study.series, 1):
            series.dicom_uid = Utilities.random_dicom_uid(
                cast("RandomNumberGenerator", self.person), time, series_no, 0
            )
            assert series.instances is not None
            for instance_no, instance in enumerate(series.instances, 1):
                instance.dicom_uid = Utilities.random_dicom_uid(
                    cast("RandomNumberGenerator", self.person), time, series_no, instance_no
                )


class Code:
    """Java: Code."""

    def __init__(
        self,
        system_or_definition: str | dict[str, object],
        code: str | None = None,
        display: str | None = None,
    ) -> None:
        """Java: Code#Code.

        Java overloads:
        (String system, String code, String display)
        (JsonObject definition)
        """
        if isinstance(system_or_definition, dict):
            self.system: str = cast(str, system_or_definition["system"])
            self.code: str = cast(str, system_or_definition["code"])
            self.display: str = cast(str, system_or_definition["display"])
        else:
            self.system = system_or_definition
            self.code = cast(str, code)
            self.display = cast(str, display)
        self.version: str | None = None
        self.value_set: str | None = None

    def hash_code(self) -> int:
        """Java: Code#hashCode.

        Java overloads:
        ()
        """
        return to_int32(
            67 * to_int32(67 * 7 + java_hash_code(self.system)) + java_hash_code(self.code)
        )

    def equals(self, obj: object) -> bool:
        """Java: Code#equals.

        Java overloads:
        (Object obj)
        """
        return type(self) is type(obj) and self.code == obj.code and self.system == obj.system

    def to_string(self) -> str:
        """Java: Code#toString.

        Java overloads:
        ()
        """
        values = (self.system, self.code, self.display, self.version, self.value_set)
        return "system={}, code={}, display={}, version={}, valueSet={}".format(
            *("null" if v is None else v for v in values)
        )

    @staticmethod
    def from_json(json_codes: list[object]) -> list[Code]:
        """Java: Code#fromJson.

        Java overloads:
        (JsonArray jsonCodes)
        """
        return [Code(cast(dict[str, object], item)) for item in json_codes]

    def compare_to(self, other: Code) -> int:
        """Java: Code#compareTo.

        Java overloads:
        (Code other)
        """
        compare = string_compare_to(self.system, other.system)
        return compare if compare != 0 else string_compare_to(self.code, other.code)

    def __eq__(self, other: object) -> bool:
        """Java: HealthRecord.Code#equals."""
        return self.equals(other)

    def __hash__(self) -> int:
        """Java: HealthRecord.Code#hashCode."""
        return self.hash_code()

    def java_hash_code(self) -> int:
        """Java: HealthRecord.Code#hashCode; javacompat collection boundary."""
        return self.hash_code()

    def java_compare_to(self, other: object) -> int:
        """Java: HealthRecord.Code#compareTo; javacompat collection boundary."""
        return self.compare_to(cast(Code, other))

    def __str__(self) -> str:
        """Java: HealthRecord.Code#toString."""
        return self.to_string()


class Entry:
    """Java: Entry."""

    def __init__(self, start: int, type: str, *, record: HealthRecord) -> None:
        """Java: Entry#Entry.

        Java overloads:
        (long start, String type)
        """
        self.record: HealthRecord = record
        self.uuid: UUID | str = record.person.rand_uuid()
        self.full_url: str | None = None
        self.name: str | None = None
        self.start: int = start
        self.stop: int = 0
        self.type: str = type
        self.codes: list[Code] = []
        self.cost: Decimal | None = None
        self.note: str | None = None

    def determine_cost(self) -> None:
        """Java: Entry#determineCost.

        Java overloads:
        ()
        """
        from synthea.world.concepts.costs import Costs

        self.cost = set_scale(
            value_of(Costs.determine_cost_of_entry(self, self.record.person)), 2, RoundingMode.DOWN
        )

    def get_cost(self) -> Decimal:
        """Java: Entry#getCost.

        Java overloads:
        ()
        """
        if self.cost is None:
            self.determine_cost()
        assert self.cost is not None
        return self.cost

    def contains_code(self, code: str, system: str) -> bool:
        """Java: Entry#containsCode.

        Java overloads:
        (String code, String system)
        """
        return any(c.code == code and c.system == system for c in self.codes)

    def merge_code_list(self, other_codes: list[Code]) -> None:
        """Java: Entry#mergeCodeList.

        Java overloads:
        (List otherCodes)
        """
        for other in other_codes:
            if not self.contains_code(other.code, other.system):
                self.codes.append(other)

    def to_string(self) -> str:
        """Java: Entry#toString.

        Java overloads:
        ()
        """
        seconds, millis = divmod(self.start, 1000)
        dt = datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds)
        text = dt.strftime("%Y-%m-%dT%H:%M:%S")
        if millis:
            text += f".{millis:03}"
        return f"{text}Z {self.type}"


class EntryWithReasons(Entry):
    """Java: EntryWithReasons."""

    def __init__(self, time: int, type: str, *, record: HealthRecord) -> None:
        """Java: EntryWithReasons#EntryWithReasons.

        Java overloads:
        (long time, String type)
        """
        super().__init__(time, type, record=record)
        self.reasons: list[Code] = []

    def merge_reason_list(self, other_codes: list[Code]) -> None:
        """Java: EntryWithReasons#mergeReasonList.

        Java overloads:
        (List otherCodes)
        """
        for other in other_codes:
            if not self.contains_reason(other.code, other.system):
                self.codes.append(other)

    def contains_reason(self, code: str, system: str) -> bool:
        """Java: EntryWithReasons#containsReason.

        Java overloads:
        (String code, String system)
        """
        return any(c.code == code and c.system == system for c in self.reasons)


class Observation(Entry):
    """Java: Observation."""

    def __init__(self, time: int, type: str, value: object, *, record: HealthRecord) -> None:
        """Java: Observation#Observation.

        Java overloads:
        (long time, String type, Object value)
        """
        super().__init__(time, type, record=record)
        self.value: object = value
        self.category: str | None = None
        self.unit: str | None = None
        self.observations: list[Observation] = []
        self.report: Report | None = None


class Report(Entry):
    """Java: Report."""

    def __init__(
        self, time: int, type: str, observations: list[Observation], *, record: HealthRecord
    ) -> None:
        """Java: Report#Report.

        Java overloads:
        (long time, String type, List observations)
        """
        super().__init__(time, type, record=record)
        self.observations: list[Observation] = observations


class Medication(EntryWithReasons):
    """Java: Medication."""

    def __init__(self, time: int, type: str, *, record: HealthRecord) -> None:
        """Java: Medication#Medication.

        Java overloads:
        (long time, String type)
        """
        from synthea.world.concepts.claim import Claim

        super().__init__(time, type, record=record)
        self.stop_reason: Code | None = None
        self.prescription_details: dict[str, object] | None = None
        self.administration: bool = False
        self.chronic: bool = False
        self.claim: Claim = Claim(self, record.person)

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: Medication#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError(
            "Java: Medication#write_object snapshot serialization out of scope"
        )

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: Medication#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError(
            "Java: Medication#read_object snapshot serialization out of scope"
        )

    def get_quantity(self) -> int:
        """Java: Medication#getQuantity.

        Java overloads:
        ()
        """
        if self.prescription_details is None:
            return 1 if self.administration else 30
        amount = frequency = period = duration = Decimal(1)
        period_uom, duration_uom = "days", "months"
        if "dosage" in self.prescription_details:
            dosage = cast(dict[str, object], self.prescription_details["dosage"])
            amount = Decimal(str(dosage["amount"]))
            frequency = Decimal(str(dosage["frequency"]))
            period = Decimal(str(dosage["period"]))
            period_uom = cast(str, dosage["unit"])
        if "duration" in self.prescription_details:
            drtn = cast(dict[str, object], self.prescription_details["duration"])
            duration = Decimal(str(drtn["quantity"]))
            duration_uom = cast(str, drtn["unit"])
        period = Decimal(Utilities.convert_time(period_uom, long_value(period)))
        duration = Decimal(Utilities.convert_time(duration_uom, long_value(duration)))
        return long_value(multiply(multiply(amount, frequency), divide_exact(duration, period)))


class Immunization(Entry):
    """Java: Immunization."""

    def __init__(self, start: int, type: str, *, record: HealthRecord) -> None:
        """Java: Immunization#Immunization.

        Java overloads:
        (long start, String type)
        """
        super().__init__(start, type, record=record)
        self.series: int = -1


class Procedure(EntryWithReasons):
    """Java: Procedure."""

    def __init__(self, time: int, type: str, *, record: HealthRecord) -> None:
        """Java: Procedure#Procedure.

        Java overloads:
        (long time, String type)
        """
        super().__init__(time, type, record=record)
        self.stop = to_int64(self.start + 15 * 60_000)
        self.provider: Provider | None = None
        self.clinician: Clinician | None = None


class CarePlan(EntryWithReasons):
    """Java: CarePlan."""

    def __init__(self, time: int, type: str, *, record: HealthRecord) -> None:
        """Java: CarePlan#CarePlan.

        Java overloads:
        (long time, String type)
        """
        super().__init__(time, type, record=record)
        self.activities: OrderedSet[Code] = OrderedSet()
        self.goals: OrderedSet[dict[str, object]] = OrderedSet()
        self.stop_reason: Code | None = None

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: CarePlan#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java: CarePlan#write_object snapshot serialization out of scope")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: CarePlan#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java: CarePlan#read_object snapshot serialization out of scope")


class ImagingStudy(Entry):
    """Java: ImagingStudy."""

    def __init__(self, person: Person, time: int, type: str, *, record: HealthRecord) -> None:
        """Java: ImagingStudy#ImagingStudy.

        Java overloads:
        (Person person, long time, String type)
        """
        super().__init__(time, type, record=record)
        self.dicom_uid: str = Utilities.random_dicom_uid(
            cast("RandomNumberGenerator", person), time, 0, 0
        )
        self.series: list[Series] = []


class Series:
    """Java: Series."""

    def __init__(self) -> None:
        """Java: Series#Series.

        Java overloads:
        ()
        """
        self.dicom_uid: str | None = None
        self.body_site: Code | None = None
        self.modality: Code | None = None
        self.instances: list[Instance] | None = None
        self.min_number_instances: int = 0
        self.max_number_instances: int = 0

    def clone(self) -> Series:
        """Java: Series#clone.

        Java overloads:
        ()
        """
        return copy.copy(self)


class Instance:
    """Java: Instance."""

    def __init__(self) -> None:
        """Java: Instance#Instance.

        Java overloads:
        ()
        """
        self.dicom_uid: str | None = None
        self.title: str | None = None
        self.sop_class: Code | None = None

    def clone(self) -> Instance:
        """Java: Instance#clone.

        Java overloads:
        ()
        """
        return copy.copy(self)


class Device(Entry):
    """Java: Device."""

    def __init__(self, start: int, type: str, *, record: HealthRecord) -> None:
        """Java: Device#Device.

        Java overloads:
        (long start, String type)
        """
        super().__init__(start, type, record=record)
        self.manufacturer: str | None = None
        self.model: str | None = None
        self.udi: str | None = None
        self.manufacture_time: int = 0
        self.expiration_time: int = 0
        self.device_identifier: str | None = None
        self.lot_number: str | None = None
        self.serial_number: str | None = None

    def generate_udi(self, random: RandomNumberGenerator) -> None:
        """Java: Device#generateUDI.

        Java overloads:
        (RandomNumberGenerator random)
        """
        self.device_identifier = self.trim_long(random.rand_long(), 14)
        self.manufacture_time = to_int64(self.start - Utilities.convert_time("weeks", 3))
        self.expiration_time = to_int64(self.start + Utilities.convert_time("years", 25))
        lot = random.rand_long()
        self.lot_number = self.trim_long(lot, int(cast(float, random.rand(4, 20))))
        serial = random.rand_long()
        self.serial_number = self.trim_long(serial, int(cast(float, random.rand(4, 20))))
        self.udi = (
            f"(01){self.device_identifier}(11){self.udi_date(self.manufacture_time)}"
            f"(17){self.udi_date(self.expiration_time)}(10){self.lot_number}(21){self.serial_number}"
        )

    def udi_date(self, time: int) -> str:
        """Java: Device#udiDate.

        Java overloads:
        (long time)
        """
        dt = datetime(1970, 1, 1, tzinfo=UTC) + timedelta(milliseconds=time)
        # Java default en_US calendar uses Sunday-start weeks and one minimal day.
        week_year = (dt + timedelta(days=6 - (dt.weekday() + 1) % 7)).year
        return f"{week_year % 100:02}{dt.month:02}{dt.day:02}"

    def trim_long(self, value: int, length: int) -> str:
        """Java: Device#trimLong.

        Java overloads:
        (Long value, int length)
        """
        return str(value).removeprefix("-")[:length]


class Supply(Entry):
    """Java: Supply."""

    def __init__(self, start: int, type: str, *, record: HealthRecord) -> None:
        """Java: Supply#Supply.

        Java overloads:
        (long start, String type)
        """
        super().__init__(start, type, record=record)
        self.quantity: int = 0


class EncounterType(StrEnum):
    """Java: EncounterType."""

    WELLNESS = "WELLNESS"
    AMBULATORY = "AMBULATORY"
    OUTPATIENT = "OUTPATIENT"
    INPATIENT = "INPATIENT"
    EMERGENCY = "EMERGENCY"
    URGENTCARE = "URGENTCARE"
    HOSPICE = "HOSPICE"
    HOME = "HOME"
    SNF = "SNF"
    VIRTUAL = "VIRTUAL"

    @staticmethod
    def from_string(value: str | None) -> EncounterType:
        """Java: EncounterType#fromString.

        Java overloads:
        (String value)
        """
        if value is None:
            return EncounterType.AMBULATORY
        if value == "super":
            return EncounterType.INPATIENT
        return EncounterType[value.upper()]

    def code(self) -> str:
        """Java: EncounterType#code.

        Java overloads:
        ()
        """
        return cast(str, ENUM_CONSTRUCTOR_ARGUMENTS["EncounterType"][self.name][0])

    def to_string(self) -> str:
        """Java: EncounterType#toString.

        Java overloads:
        ()
        """
        return self.name.lower()


class Encounter(Entry):
    """Java: Encounter."""

    def __init__(self, time: int, type: str, *, record: HealthRecord) -> None:
        """Java: Encounter#Encounter.

        Java overloads:
        (long time, String type)
        """
        from synthea.world.concepts.claim import Claim

        super().__init__(time, type, record=record)
        if type.lower() == "emergency":
            minutes = 60
        elif type.lower() in ("inpatient", "hospice", "snf"):
            minutes = 1440
        else:
            minutes = 15
        self.stop = to_int64(self.start + minutes * 60_000)
        self.ended: bool = False
        self.ended_time: int = 0
        self.chronic_meds_renewed: bool = False
        self.observations: list[Observation] = []
        self.reports: list[Report] = []
        self.conditions: list[Entry] = []
        self.allergies: list[Allergy] = []
        self.procedures: list[Procedure] = []
        self.immunizations: list[Immunization] = []
        self.medications: list[Medication] = []
        self.careplans: list[CarePlan] = []
        self.imaging_studies: list[ImagingStudy] = []
        self.devices: list[Device] = []
        self.supplies: list[Supply] = []
        self.reason: Code | None = None
        self.discharge: Code | None = None
        self.provider: Provider | None = None
        self.clinician: Clinician | None = None
        self.clinical_note: str | None = None
        self.claim: Claim = Claim(self, record.person)

    def add_observation(
        self, time: int, type: str, value: object, display: str | object | None = _MISSING
    ) -> Observation:
        """Java: Encounter#addObservation.

        Java overloads:
        (long time, String type, Object value)
        (long time, String type, Object value, String display)
        """
        observation = Observation(time, type, value, record=self.record)
        self.observations.append(observation)
        if display is not _MISSING:
            observation.codes.append(Code("LOINC", type, cast(str, display)))
        return observation

    def find_observation(self, code: str) -> Observation | None:
        """Java: Encounter#findObservation.

        Java overloads:
        (String code)
        """
        return next((o for o in self.observations if o.type == code), None)

    def previous_encounter(self) -> Encounter | None:
        """Java: Encounter#previousEncounter.

        Java overloads:
        ()
        """
        if len(self.record.encounters) < 2:
            return None
        index = self.record.encounters.index(self) if self in self.record.encounters else -1
        if index == 0:
            return None
        if index < 0:
            raise IndexError("Java IndexOutOfBoundsException")
        return self.record.encounters[index - 1]

    def end(self, time: int) -> None:
        """Java: Encounter#end.

        Java overloads:
        (long time)
        """
        if not self.ended:
            end_time = self.stop
            for entries in (
                self.observations,
                self.reports,
                self.procedures,
                self.immunizations,
                self.imaging_studies,
                self.supplies,
            ):
                for entry in entries:
                    if entry.stop != 0:
                        end_time = max(end_time, entry.stop)
            self.stop = time if self.stop == 0 or end_time == 0 else max(end_time, time)
            self.ended = True
            self.ended_time = time


class ReactionSeverity(StrEnum):
    """Java: ReactionSeverity."""

    SEVERE = "SEVERE"
    MODERATE = "MODERATE"
    MILD = "MILD"

    @property
    def code(self) -> str:
        """Java: HealthRecord.ReactionSeverity#code."""
        return cast(str, ENUM_CONSTRUCTOR_ARGUMENTS["ReactionSeverity"][self.name][0])

    @property
    def display(self) -> str:
        """Java: HealthRecord.ReactionSeverity#display."""
        return cast(str, ENUM_CONSTRUCTOR_ARGUMENTS["ReactionSeverity"][self.name][1])


class Allergy(Entry):
    """Java: Allergy."""

    def __init__(self, start: int, type: str, *, record: HealthRecord) -> None:
        """Java: Allergy#Allergy.

        Java overloads:
        (long start, String type)
        """
        super().__init__(start, type, record=record)
        self.allergy_type: str | None = None
        self.category: str | None = None
        self.reactions: JavaHashMap[Code, ReactionSeverity] | None = None


# Java enum constructor arguments.
ENUM_CONSTRUCTOR_ARGUMENTS: dict[str, dict[str, tuple[object, ...]]] = {
    "EncounterType": {
        "WELLNESS": ("AMB",),
        "AMBULATORY": ("AMB",),
        "OUTPATIENT": ("AMB",),
        "INPATIENT": ("IMP",),
        "EMERGENCY": ("EMER",),
        "URGENTCARE": ("AMB",),
        "HOSPICE": ("HH",),
        "HOME": ("HH",),
        "SNF": ("IMP",),
        "VIRTUAL": ("VR",),
    },
    "ReactionSeverity": {
        "SEVERE": (
            "24484000",
            "Severe",
        ),
        "MODERATE": (
            "6736007",
            "Moderate",
        ),
        "MILD": (
            "255604002",
            "Mild",
        ),
    },
}

setattr(HealthRecord, "Code", Code)  # noqa: B010
setattr(HealthRecord, "Entry", Entry)  # noqa: B010
setattr(HealthRecord, "EntryWithReasons", EntryWithReasons)  # noqa: B010
setattr(HealthRecord, "Observation", Observation)  # noqa: B010
setattr(HealthRecord, "Report", Report)  # noqa: B010
setattr(HealthRecord, "Medication", Medication)  # noqa: B010
setattr(HealthRecord, "Immunization", Immunization)  # noqa: B010
setattr(HealthRecord, "Procedure", Procedure)  # noqa: B010
setattr(HealthRecord, "CarePlan", CarePlan)  # noqa: B010
setattr(HealthRecord, "ImagingStudy", ImagingStudy)  # noqa: B010
setattr(HealthRecord, "Device", Device)  # noqa: B010
setattr(HealthRecord, "Supply", Supply)  # noqa: B010
setattr(HealthRecord, "EncounterType", EncounterType)  # noqa: B010
setattr(HealthRecord, "Encounter", Encounter)  # noqa: B010
setattr(HealthRecord, "ReactionSeverity", ReactionSeverity)  # noqa: B010
setattr(HealthRecord, "Allergy", Allergy)  # noqa: B010
setattr(ImagingStudy, "Series", Series)  # noqa: B010
setattr(ImagingStudy, "Instance", Instance)  # noqa: B010
