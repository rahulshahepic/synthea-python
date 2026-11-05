"""Java API skeleton: HealthRecord.java."""

from __future__ import annotations

import builtins
from decimal import Decimal
from enum import StrEnum
from typing import IO, TYPE_CHECKING, ClassVar
from uuid import UUID

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.claim import Claim


class HealthRecord:
    """Java: HealthRecord; pending T08."""

    ENCOUNTERS: ClassVar[str] = "encounters"
    PROCEDURES: ClassVar[str] = "procedures"
    MEDICATIONS: ClassVar[str] = "medications"
    IMMUNIZATIONS: ClassVar[str] = "immunizations"

    def __init__(self, person: Person) -> None:
        """Java: HealthRecord#HealthRecord.

        Java overloads:
        (Person person)
        """
        self.person: Person
        self.provider: Provider
        self.encounters: list[Encounter]
        self.present: dict[str, Entry]
        self.death: int
        self.demographics_at_record_creation: dict[str, object]
        raise NotImplementedError("Java: HealthRecord#HealthRecord — pending T08")

    def provider_count(self) -> int:
        """Java: HealthRecord#providerCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: HealthRecord#providerCount — pending T08")

    def text_summary(self) -> str:
        """Java: HealthRecord#textSummary.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: HealthRecord#textSummary — pending T08")

    def current_encounter(self, time: int) -> Encounter:
        """Java: HealthRecord#currentEncounter.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: HealthRecord#currentEncounter — pending T08")

    def time_since_last_wellness_encounter(self, time: int) -> int:
        """Java: HealthRecord#timeSinceLastWellnessEncounter.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: HealthRecord#timeSinceLastWellnessEncounter — pending T08")

    def last_wellness_encounter(self) -> Encounter:
        """Java: HealthRecord#lastWellnessEncounter.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: HealthRecord#lastWellnessEncounter — pending T08")

    def observation(self, time: int, type: str, value: object) -> Observation:
        """Java: HealthRecord#observation.

        Java overloads:
        (long time, String type, Object value)
        """
        raise NotImplementedError("Java: HealthRecord#observation — pending T08")

    def multi_observation(self, time: int, type: str, number_of_observations: int) -> Observation:
        """Java: HealthRecord#multiObservation.

        Java overloads:
        (long time, String type, int numberOfObservations)
        """
        raise NotImplementedError("Java: HealthRecord#multiObservation — pending T08")

    def get_latest_observation(self, type: str) -> Observation:
        """Java: HealthRecord#getLatestObservation.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: HealthRecord#getLatestObservation — pending T08")

    def condition_start(self, time: int, primary_code: str) -> Entry:
        """Java: HealthRecord#conditionStart.

        Java overloads:
        (long time, String primaryCode)
        """
        raise NotImplementedError("Java: HealthRecord#conditionStart — pending T08")

    def condition_end(self, time: int, primary_code: str) -> None:
        """Java: HealthRecord#conditionEnd.

        Java overloads:
        (long time, String primaryCode)
        """
        raise NotImplementedError("Java: HealthRecord#conditionEnd — pending T08")

    def condition_end_by_state(self, time: int, state_name: str) -> None:
        """Java: HealthRecord#conditionEndByState.

        Java overloads:
        (long time, String stateName)
        """
        raise NotImplementedError("Java: HealthRecord#conditionEndByState — pending T08")

    def condition_active(self, type: str) -> bool:
        """Java: HealthRecord#conditionActive.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: HealthRecord#conditionActive — pending T08")

    def present_onset(self, code: str) -> int:
        """Java: HealthRecord#presentOnset.

        Java overloads:
        (String code)
        """
        raise NotImplementedError("Java: HealthRecord#presentOnset — pending T08")

    def allergy_start(self, time: int, primary_code: str) -> Allergy:
        """Java: HealthRecord#allergyStart.

        Java overloads:
        (long time, String primaryCode)
        """
        raise NotImplementedError("Java: HealthRecord#allergyStart — pending T08")

    def allergy_end(self, time: int, primary_code: str) -> None:
        """Java: HealthRecord#allergyEnd.

        Java overloads:
        (long time, String primaryCode)
        """
        raise NotImplementedError("Java: HealthRecord#allergyEnd — pending T08")

    def allergy_end_by_state(self, time: int, state_name: str) -> None:
        """Java: HealthRecord#allergyEndByState.

        Java overloads:
        (long time, String stateName)
        """
        raise NotImplementedError("Java: HealthRecord#allergyEndByState — pending T08")

    def allergy_active(self, type: str) -> bool:
        """Java: HealthRecord#allergyActive.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: HealthRecord#allergyActive — pending T08")

    def procedure(self, time: int, type: str) -> Procedure:
        """Java: HealthRecord#procedure.

        Java overloads:
        (long time, String type)
        """
        raise NotImplementedError("Java: HealthRecord#procedure — pending T08")

    def device_implant(self, time: int, type: str) -> Device:
        """Java: HealthRecord#deviceImplant.

        Java overloads:
        (long time, String type)
        """
        raise NotImplementedError("Java: HealthRecord#deviceImplant — pending T08")

    def device_remove(self, time: int, type: str) -> None:
        """Java: HealthRecord#deviceRemove.

        Java overloads:
        (long time, String type)
        """
        raise NotImplementedError("Java: HealthRecord#deviceRemove — pending T08")

    def device_remove_by_state(self, time: int, state_name: str) -> None:
        """Java: HealthRecord#deviceRemoveByState.

        Java overloads:
        (long time, String stateName)
        """
        raise NotImplementedError("Java: HealthRecord#deviceRemoveByState — pending T08")

    def use_supply(self, time: int, code: Code, quantity: int) -> Supply:
        """Java: HealthRecord#useSupply.

        Java overloads:
        (long time, Code code, int quantity)
        """
        raise NotImplementedError("Java: HealthRecord#useSupply — pending T08")

    def report(self, time: int, type: str, number_of_observations: int) -> Report:
        """Java: HealthRecord#report.

        Java overloads:
        (long time, String type, int numberOfObservations)
        """
        raise NotImplementedError("Java: HealthRecord#report — pending T08")

    def encounter_start(self, time: int, type: EncounterType) -> Encounter:
        """Java: HealthRecord#encounterStart.

        Java overloads:
        (long time, EncounterType type)
        """
        raise NotImplementedError("Java: HealthRecord#encounterStart — pending T08")

    def encounter_end(self, time: int, type: EncounterType) -> None:
        """Java: HealthRecord#encounterEnd.

        Java overloads:
        (long time, EncounterType type)
        """
        raise NotImplementedError("Java: HealthRecord#encounterEnd — pending T08")

    def last_encounter_time(self) -> int:
        """Java: HealthRecord#lastEncounterTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: HealthRecord#lastEncounterTime — pending T08")

    def immunization(self, time: int, type: str) -> Immunization:
        """Java: HealthRecord#immunization.

        Java overloads:
        (long time, String type)
        """
        raise NotImplementedError("Java: HealthRecord#immunization — pending T08")

    def medication_start(self, time: int, type: str, chronic: bool) -> Medication:
        """Java: HealthRecord#medicationStart.

        Java overloads:
        (long time, String type, boolean chronic)
        """
        raise NotImplementedError("Java: HealthRecord#medicationStart — pending T08")

    def medication_administration(self, time: int, type: str) -> Medication:
        """Java: HealthRecord#medicationAdministration.

        Java overloads:
        (long time, String type)
        """
        raise NotImplementedError("Java: HealthRecord#medicationAdministration — pending T08")

    def medication_end(self, time: int, type: str, reason: Code) -> None:
        """Java: HealthRecord#medicationEnd.

        Java overloads:
        (long time, String type, Code reason)
        """
        raise NotImplementedError("Java: HealthRecord#medicationEnd — pending T08")

    def medication_end_by_state(self, time: int, state_name: str, reason: Code) -> None:
        """Java: HealthRecord#medicationEndByState.

        Java overloads:
        (long time, String stateName, Code reason)
        """
        raise NotImplementedError("Java: HealthRecord#medicationEndByState — pending T08")

    def chronic_medication_end(self, type: str) -> None:
        """Java: HealthRecord#chronicMedicationEnd.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: HealthRecord#chronicMedicationEnd — pending T08")

    def medication_active(self, type: str) -> bool:
        """Java: HealthRecord#medicationActive.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: HealthRecord#medicationActive — pending T08")

    def careplan_start(self, time: int, type: str) -> CarePlan:
        """Java: HealthRecord#careplanStart.

        Java overloads:
        (long time, String type)
        """
        raise NotImplementedError("Java: HealthRecord#careplanStart — pending T08")

    def careplan_end(self, time: int, type: str, reason: Code) -> None:
        """Java: HealthRecord#careplanEnd.

        Java overloads:
        (long time, String type, Code reason)
        """
        raise NotImplementedError("Java: HealthRecord#careplanEnd — pending T08")

    def careplan_end_by_state(self, time: int, state_name: str, reason: Code) -> None:
        """Java: HealthRecord#careplanEndByState.

        Java overloads:
        (long time, String stateName, Code reason)
        """
        raise NotImplementedError("Java: HealthRecord#careplanEndByState — pending T08")

    def careplan_active(self, type: str) -> bool:
        """Java: HealthRecord#careplanActive.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: HealthRecord#careplanActive — pending T08")

    def imaging_study(self, time: int, type: str, series: list[Series]) -> ImagingStudy:
        """Java: HealthRecord#imagingStudy.

        Java overloads:
        (long time, String type, List series)
        """
        raise NotImplementedError("Java: HealthRecord#imagingStudy — pending T08")

    def assign_imaging_study_dicom_uids(self, time: int, study: ImagingStudy) -> None:
        """Java: HealthRecord#assignImagingStudyDicomUids.

        Java overloads:
        (long time, ImagingStudy study)
        """
        raise NotImplementedError("Java: HealthRecord#assignImagingStudyDicomUids — pending T08")


class Code:
    """Java: Code; pending T08."""

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
        self.system: str
        self.code: str
        self.display: str
        self.version: str | None
        self.value_set: str | None
        raise NotImplementedError("Java: Code#Code — pending T08")

    def hash_code(self) -> int:
        """Java: Code#hashCode.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Code#hashCode — pending T08")

    def equals(self, obj: object) -> bool:
        """Java: Code#equals.

        Java overloads:
        (Object obj)
        """
        raise NotImplementedError("Java: Code#equals — pending T08")

    def to_string(self) -> str:
        """Java: Code#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Code#toString — pending T08")

    @staticmethod
    def from_json(json_codes: list[object]) -> list[Code]:
        """Java: Code#fromJson.

        Java overloads:
        (JsonArray jsonCodes)
        """
        raise NotImplementedError("Java: Code#fromJson — pending T08")

    def compare_to(self, other: Code) -> int:
        """Java: Code#compareTo.

        Java overloads:
        (Code other)
        """
        raise NotImplementedError("Java: Code#compareTo — pending T08")


class Entry:
    """Java: Entry; pending T08."""

    def __init__(self, start: int, type: str) -> None:
        """Java: Entry#Entry.

        Java overloads:
        (long start, String type)
        """
        self.record: HealthRecord
        self.uuid: UUID
        self.full_url: str
        self.name: str
        self.start: int
        self.stop: int
        self.type: str
        self.codes: list[Code]
        self.cost: Decimal
        self.note: str
        raise NotImplementedError("Java: Entry#Entry — pending T08")

    def determine_cost(self) -> None:
        """Java: Entry#determineCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Entry#determineCost — pending T08")

    def get_cost(self) -> Decimal:
        """Java: Entry#getCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Entry#getCost — pending T08")

    def contains_code(self, code: str, system: str) -> bool:
        """Java: Entry#containsCode.

        Java overloads:
        (String code, String system)
        """
        raise NotImplementedError("Java: Entry#containsCode — pending T08")

    def merge_code_list(self, other_codes: list[Code]) -> None:
        """Java: Entry#mergeCodeList.

        Java overloads:
        (List otherCodes)
        """
        raise NotImplementedError("Java: Entry#mergeCodeList — pending T08")

    def to_string(self) -> str:
        """Java: Entry#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Entry#toString — pending T08")


class EntryWithReasons(Entry):
    """Java: EntryWithReasons; pending T08."""

    def __init__(self, time: int, type: str) -> None:
        """Java: EntryWithReasons#EntryWithReasons.

        Java overloads:
        (long time, String type)
        """
        self.reasons: list[Code]
        raise NotImplementedError("Java: EntryWithReasons#EntryWithReasons — pending T08")

    def merge_reason_list(self, other_codes: list[Code]) -> None:
        """Java: EntryWithReasons#mergeReasonList.

        Java overloads:
        (List otherCodes)
        """
        raise NotImplementedError("Java: EntryWithReasons#mergeReasonList — pending T08")

    def contains_reason(self, code: str, system: str) -> bool:
        """Java: EntryWithReasons#containsReason.

        Java overloads:
        (String code, String system)
        """
        raise NotImplementedError("Java: EntryWithReasons#containsReason — pending T08")


class Observation(Entry):
    """Java: Observation; pending T08."""

    def __init__(self, time: int, type: str, value: object) -> None:
        """Java: Observation#Observation.

        Java overloads:
        (long time, String type, Object value)
        """
        self.value: object
        self.category: str
        self.unit: str
        self.observations: list[Observation]
        self.report: Report
        raise NotImplementedError("Java: Observation#Observation — pending T08")


class Report(Entry):
    """Java: Report; pending T08."""

    def __init__(self, time: int, type: str, observations: list[Observation]) -> None:
        """Java: Report#Report.

        Java overloads:
        (long time, String type, List observations)
        """
        self.observations: list[Observation]
        raise NotImplementedError("Java: Report#Report — pending T08")


class Medication(EntryWithReasons):
    """Java: Medication; pending T08."""

    def __init__(self, time: int, type: str) -> None:
        """Java: Medication#Medication.

        Java overloads:
        (long time, String type)
        """
        self.stop_reason: Code
        self.prescription_details: dict[str, object]
        self.claim: Claim
        self.administration: bool
        self.chronic: bool
        raise NotImplementedError("Java: Medication#Medication — pending T08")

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: Medication#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java: Medication#writeObject — pending T08")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: Medication#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java: Medication#readObject — pending T08")

    def get_quantity(self) -> int:
        """Java: Medication#getQuantity.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Medication#getQuantity — pending T08")


class Immunization(Entry):
    """Java: Immunization; pending T08."""

    def __init__(self, start: int, type: str) -> None:
        """Java: Immunization#Immunization.

        Java overloads:
        (long start, String type)
        """
        self.series: int
        raise NotImplementedError("Java: Immunization#Immunization — pending T08")


class Procedure(EntryWithReasons):
    """Java: Procedure; pending T08."""

    def __init__(self, time: int, type: str) -> None:
        """Java: Procedure#Procedure.

        Java overloads:
        (long time, String type)
        """
        self.provider: Provider
        self.clinician: Clinician
        raise NotImplementedError("Java: Procedure#Procedure — pending T08")


class CarePlan(EntryWithReasons):
    """Java: CarePlan; pending T08."""

    def __init__(self, time: int, type: str) -> None:
        """Java: CarePlan#CarePlan.

        Java overloads:
        (long time, String type)
        """
        self.activities: builtins.set[Code]
        self.goals: builtins.set[dict[str, object]]
        self.stop_reason: Code
        raise NotImplementedError("Java: CarePlan#CarePlan — pending T08")

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: CarePlan#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java: CarePlan#writeObject — pending T08")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: CarePlan#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java: CarePlan#readObject — pending T08")


class ImagingStudy(Entry):
    """Java: ImagingStudy; pending T08."""

    def __init__(self, person: Person, time: int, type: str) -> None:
        """Java: ImagingStudy#ImagingStudy.

        Java overloads:
        (Person person, long time, String type)
        """
        self.dicom_uid: str
        self.series: list[Series]
        raise NotImplementedError("Java: ImagingStudy#ImagingStudy — pending T08")


class Series:
    """Java: Series; pending T08."""

    def __init__(self) -> None:
        """Java: Series#Series.

        Java overloads:
        ()
        """
        self.dicom_uid: str
        self.body_site: Code
        self.modality: Code
        self.instances: list[Instance]
        self.min_number_instances: int
        self.max_number_instances: int
        raise NotImplementedError("Java: Series#Series — pending T08")

    def clone(self) -> Series:
        """Java: Series#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Series#clone — pending T08")


class Instance:
    """Java: Instance; pending T08."""

    def __init__(self) -> None:
        """Java: Instance#Instance.

        Java overloads:
        ()
        """
        self.dicom_uid: str
        self.title: str
        self.sop_class: Code
        raise NotImplementedError("Java: Instance#Instance — pending T08")

    def clone(self) -> Instance:
        """Java: Instance#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Instance#clone — pending T08")


class Device(Entry):
    """Java: Device; pending T08."""

    def __init__(self, start: int, type: str) -> None:
        """Java: Device#Device.

        Java overloads:
        (long start, String type)
        """
        self.manufacturer: str
        self.model: str
        self.udi: str
        self.manufacture_time: int
        self.expiration_time: int
        self.device_identifier: str
        self.lot_number: str
        self.serial_number: str
        raise NotImplementedError("Java: Device#Device — pending T08")

    def generate_udi(self, random: RandomNumberGenerator) -> None:
        """Java: Device#generateUDI.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Device#generateUDI — pending T08")

    def udi_date(self, time: int) -> str:
        """Java: Device#udiDate.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Device#udiDate — pending T08")

    def trim_long(self, value: int, length: int) -> str:
        """Java: Device#trimLong.

        Java overloads:
        (Long value, int length)
        """
        raise NotImplementedError("Java: Device#trimLong — pending T08")


class Supply(Entry):
    """Java: Supply; pending T08."""

    def __init__(self, start: int, type: str) -> None:
        """Java: Supply#Supply.

        Java overloads:
        (long start, String type)
        """
        self.quantity: int
        raise NotImplementedError("Java: Supply#Supply — pending T08")


class EncounterType(StrEnum):
    """Java: EncounterType; pending T08."""

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
    def from_string(value: str) -> EncounterType:
        """Java: EncounterType#fromString.

        Java overloads:
        (String value)
        """
        raise NotImplementedError("Java: EncounterType#fromString — pending T08")

    def code(self) -> str:
        """Java: EncounterType#code.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: EncounterType#code — pending T08")

    def to_string(self) -> str:
        """Java: EncounterType#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: EncounterType#toString — pending T08")


class Encounter(Entry):
    """Java: Encounter; pending T08."""

    def __init__(self, time: int, type: str) -> None:
        """Java: Encounter#Encounter.

        Java overloads:
        (long time, String type)
        """
        self.observations: list[Observation]
        self.reports: list[Report]
        self.conditions: list[Entry]
        self.allergies: list[Allergy]
        self.procedures: list[Procedure]
        self.immunizations: list[Immunization]
        self.medications: list[Medication]
        self.careplans: list[CarePlan]
        self.imaging_studies: list[ImagingStudy]
        self.devices: list[Device]
        self.supplies: list[Supply]
        self.claim: Claim
        self.reason: Code
        self.discharge: Code
        self.provider: Provider
        self.clinician: Clinician
        self.ended: bool
        self.ended_time: int
        self.chronic_meds_renewed: bool
        self.clinical_note: str
        raise NotImplementedError("Java: Encounter#Encounter — pending T08")

    def add_observation(
        self, time: int, type: str, value: object, display: str | None = None
    ) -> Observation:
        """Java: Encounter#addObservation.

        Java overloads:
        (long time, String type, Object value)
        (long time, String type, Object value, String display)
        """
        raise NotImplementedError("Java: Encounter#addObservation — pending T08")

    def find_observation(self, code: str) -> Observation:
        """Java: Encounter#findObservation.

        Java overloads:
        (String code)
        """
        raise NotImplementedError("Java: Encounter#findObservation — pending T08")

    def previous_encounter(self) -> Encounter:
        """Java: Encounter#previousEncounter.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Encounter#previousEncounter — pending T08")

    def end(self, time: int) -> None:
        """Java: Encounter#end.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Encounter#end — pending T08")


class ReactionSeverity(StrEnum):
    """Java: ReactionSeverity; pending T08."""

    SEVERE = "SEVERE"
    MODERATE = "MODERATE"
    MILD = "MILD"


class Allergy(Entry):
    """Java: Allergy; pending T08."""

    def __init__(self, start: int, type: str) -> None:
        """Java: Allergy#Allergy.

        Java overloads:
        (long start, String type)
        """
        self.allergy_type: str
        self.category: str
        self.reactions: dict[Code, ReactionSeverity]
        raise NotImplementedError("Java: Allergy#Allergy — pending T08")


# Java enum constructor arguments (data; behavior remains pending).
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
