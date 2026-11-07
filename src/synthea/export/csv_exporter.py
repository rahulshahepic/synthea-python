"""Java: org.mitre.synthea.export.CSVExporter; CSV rows in Java export order."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from decimal import ROUND_DOWN, Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.export.csv_constants import CSVConstants
from synthea.export.csv_file_manager import CSVFileManager
from synthea.export.export_helper import ExportHelper
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat.fmt import format as java_format
from synthea.javacompat.numbers import double_to_string, idiv, to_int64
from synthea.world.agents.clinician import Clinician
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.agents.provider import Provider
from synthea.world.concepts.claim import Claim
from synthea.world.concepts.health_record import (
    Allergy,
    CarePlan,
    Code,
    Device,
    Encounter,
    EncounterType,
    Entry,
    ImagingStudy,
    Immunization,
    Medication,
    Observation,
    Procedure,
    ReactionSeverity,
    Supply,
)

if TYPE_CHECKING:
    from synthea.world.agents.payer import Payer
    from synthea.world.concepts.claim import ClaimEntry
    from synthea.world.concepts.healthinsurance.plan_record import PlanRecord

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def _text(value: object) -> str:
    """Java: StringBuilder#append(Object), including null and double spelling."""
    if value is None:
        return "null"
    if isinstance(value, float):
        return double_to_string(value)
    return str(value)


def _money(value: Decimal | None) -> str:
    """Java: String.format(Locale.US, "%.2f", BigDecimal)."""
    return java_format("%.2f", value) if value is not None else ""


def _optional(value: object) -> str:
    """Java: append a nullable field only when it is non-null."""
    return "" if value is None else _text(value)


def _date(value: int) -> str:
    """Java: ExportHelper#dateFromTimestamp."""
    return ExportHelper.date_from_timestamp(value)


def _iso(value: int) -> str:
    """Java: ExportHelper#iso8601Timestamp."""
    return ExportHelper.iso8601_timestamp(value)


class CSVExporter:
    """Java: org.mitre.synthea.export.CSVExporter."""

    NEWLINE: ClassVar[str] = "\n"

    def __init__(self) -> None:
        """Java: CSVExporter#CSVExporter."""
        self.init()

    def init(self) -> None:
        """Java: CSVExporter#init."""
        self.file_manager = CSVFileManager()
        self.transaction_id = 0

    @staticmethod
    def get_instance() -> CSVExporter:
        """Java: CSVExporter#getInstance (lazy singleton)."""
        if SingletonHolder.instance is None:
            SingletonHolder.instance = CSVExporter()
        return SingletonHolder.instance

    def _row(self, key: str, values: list[object]) -> None:
        """Java: StringBuilder append sequence and CSVFileManager#writeResourceLine."""
        self.file_manager.write_resource_line(
            ",".join(_text(v) for v in values) + self.NEWLINE, key
        )

    def export_organizations_and_providers(self) -> None:
        """Java: CSVExporter#exportOrganizationsAndProviders."""
        for org in Provider.get_provider_list():
            total = sum(
                v for (_, key), v in org.get_utilization().items() if key == Provider.ENCOUNTERS
            )
            if total > 0:
                self.export_organization(org, total)
                for clinicians in org.clinician_map.values():
                    for clinician in clinicians:
                        self.export_provider(clinician, org.get_resource_id())
            self.file_manager.flush_writer(CSVConstants.ORGANIZATION_KEY)
            self.file_manager.flush_writer(CSVConstants.PROVIDER_KEY)

    def export_payers(self) -> None:
        """Java: CSVExporter#exportPayers."""
        for payer in PayerManager.get_all_payers():
            self.export_payer(payer)
            self.file_manager.flush_writer(CSVConstants.PAYER_KEY)
        self.export_payer(PayerManager.get_no_insurance_plan().get_payer())
        self.file_manager.flush_writer(CSVConstants.PAYER_KEY)

    def export_payer_transitions(self, person: Person, stop_time: int) -> None:
        """Java: CSVExporter#exportPayerTransitions; includes all past member IDs."""
        for plan in sorted(person.coverage.get_plan_history(), key=lambda p: p.get_start_time()):
            if plan.get_start_time() <= stop_time:
                self.export_payer_transition(person, plan)
        self.file_manager.flush_writer(CSVConstants.PAYER_TRANSITION_KEY)

    def export_patient_expenses(self, person: Person, cut_off_time: int, stop_time: int) -> None:
        """Java: CSVExporter#exportPatientExpenses."""
        for plan in sorted(person.coverage.get_plan_history(), key=lambda p: p.get_start_time()):
            if plan.get_start_time() <= stop_time and plan.get_stop_time() >= cut_off_time:
                self.export_patient_expense(person, plan)
        self.file_manager.flush_writer(CSVConstants.PATIENT_EXPENSE_KEY)

    def export(self, person: Person, time: int) -> None:
        """Java: CSVExporter#export."""
        assert person.record is not None
        person_id = self.export_patient(person, time)
        for encounter in person.record.encounters:
            encounter_id = self.export_encounter(person_id, encounter)
            payer_id = encounter.claim.get_payer().uuid
            self.export_claim(person, encounter.claim, encounter, encounter_id, time)
            for condition in encounter.conditions:
                if Config.get("generate.terminology_service_url"):
                    raise NotImplementedError("Terminology service is out of scope")
                self.export_condition(person_id, encounter_id, condition)
            for allergy in encounter.allergies:
                self.export_allergy(person_id, encounter_id, allergy)
            for observation in encounter.observations:
                self.export_observation(person_id, encounter_id, observation)
            for procedure in encounter.procedures:
                self.export_procedure(person_id, encounter_id, procedure)
            for medication in encounter.medications:
                self.export_medication(person_id, encounter_id, payer_id, medication, time)
                self.export_claim(person, medication.claim, encounter, encounter_id, time)
            for immunization in encounter.immunizations:
                self.export_immunization(person_id, encounter_id, immunization)
            for care_plan in encounter.careplans:
                self.export_care_plan(person_id, encounter_id, care_plan)
            for study in encounter.imaging_studies:
                self.export_imaging_study(person_id, encounter_id, study)
            for device in encounter.devices:
                self.export_device(person_id, encounter_id, device)
            for supply in encounter.supplies:
                self.export_supply(person_id, encounter_id, encounter, supply)
        years = Config.get_as_integer("exporter.years_of_history")
        cut_off = datetime(1900, 1, 1, tzinfo=UTC)
        if years > 0:
            now = datetime.now(UTC)  # Java: Calendar.getInstance(), export metadata only
            cut_off = now.replace(year=now.year - years, month=1, day=1)
        CSVExporter.get_instance().export_payer_transitions(person, time)
        CSVExporter.get_instance().export_patient_expenses(
            person, int(cut_off.timestamp() * 1000), time
        )
        if Config.get_as_boolean("exporter.csv.include_quality_of_life_observations", True):
            self.export_quality_of_life_observations(person_id, person, cut_off)
        for key in (
            CSVConstants.PATIENT_KEY,
            CSVConstants.ENCOUNTER_KEY,
            CSVConstants.CONDITION_KEY,
            CSVConstants.ALLERGY_KEY,
            CSVConstants.MEDICATION_KEY,
            CSVConstants.CAREPLAN_KEY,
            CSVConstants.OBSERVATION_KEY,
            CSVConstants.PROCEDURE_KEY,
            CSVConstants.IMMUNIZATION_KEY,
            CSVConstants.IMAGING_STUDY_KEY,
            CSVConstants.DEVICE_KEY,
            CSVConstants.SUPPLY_KEY,
            CSVConstants.CLAIM_KEY,
            CSVConstants.CLAIM_TRANSACTION_KEY,
            CSVConstants.PATIENT_EXPENSE_KEY,
        ):
            self.file_manager.flush_writer(key)

    def export_patient(self, person: Person, time: int) -> str:
        """Java: CSVExporter#exportPatient."""
        person_id = cast(str, person.attributes[Person.ID])
        if "exported_to_csv" in person.attributes:
            return person_id
        person.attributes["exported_to_csv"] = person_id
        fields: list[object] = [
            person_id,
            _date(cast(int, person.attributes[Person.BIRTHDATE])),
            "" if person.alive(time) else _date(cast(int, person.attributes[Person.DEATHDATE])),
        ]
        for attribute in (
            Person.IDENTIFIER_SSN,
            Person.IDENTIFIER_DRIVERS,
            Person.IDENTIFIER_PASSPORT,
            Person.NAME_PREFIX,
            Person.FIRST_NAME,
            Person.MIDDLE_NAME,
            Person.LAST_NAME,
            Person.NAME_SUFFIX,
            Person.MAIDEN_NAME,
            Person.MARITAL_STATUS,
            Person.RACE,
            Person.ETHNICITY,
            Person.GENDER,
            Person.BIRTHPLACE,
            Person.ADDRESS,
            Person.CITY,
            Person.STATE,
            Person.COUNTY,
            Person.FIPS,
            Person.ZIP,
        ):
            fields.append(self.clean(cast(str | None, person.attributes.get(attribute, ""))))
        fields.extend(
            [
                person.get_y(),
                person.get_x(),
                person.coverage.get_total_out_of_pocket_expenses(),
                person.coverage.get_total_coverage(),
                person.attributes.get(Person.INCOME),
            ]
        )
        self._row(CSVConstants.PATIENT_KEY, fields)
        return person_id

    def export_encounter(self, person_id: str, encounter: Encounter) -> str:
        """Java: CSVExporter#exportEncounter."""
        coding = encounter.codes[0]
        encounter_id = str(encounter.uuid)
        payer = encounter.claim.get_payer()
        reason = encounter.reason
        self._row(
            CSVConstants.ENCOUNTER_KEY,
            [
                encounter_id,
                _iso(encounter.start),
                _iso(encounter.stop) if encounter.stop else "",
                person_id,
                encounter.provider.get_resource_id() if encounter.provider else "",
                encounter.clinician.get_resource_id() if encounter.clinician else "",
                payer.get_resource_id() if payer else "",
                encounter.type.lower() if encounter.type else "",
                coding.code,
                self.clean(coding.display),
                _money(encounter.get_cost()),
                _money(encounter.claim.get_total_claim_cost()),
                _money(encounter.claim.get_total_covered_cost()),
                reason.code if reason else "",
                self.clean(reason.display) if reason else "",
            ],
        )
        return encounter_id

    def export_condition(self, person_id: str, encounter_id: str, condition: Entry) -> None:
        """Java: CSVExporter#exportCondition."""
        code = condition.codes[0]
        self._row(
            CSVConstants.CONDITION_KEY,
            [
                _date(condition.start),
                _date(condition.stop) if condition.stop else "",
                person_id,
                encounter_id,
                code.system,
                code.code,
                self.clean(code.display),
            ],
        )

    def export_allergy(self, person_id: str, encounter_id: str, allergy: Allergy) -> None:
        """Java: CSVExporter#exportAllergy; stable severity ordering before truncation."""
        code = allergy.codes[0]
        fields: list[object] = [
            _date(allergy.start),
            _date(allergy.stop) if allergy.stop else "",
            person_id,
            encounter_id,
            code.code,
            ExportHelper.get_system_from_uri(code.system),
            self.clean(code.display),
            _optional(allergy.allergy_type),
            _optional(allergy.category),
        ]
        reactions = list(allergy.reactions.items()) if allergy.reactions is not None else []
        if len(reactions) > 1:
            reactions.sort(key=lambda item: list(ReactionSeverity).index(item[1]))
        for reaction, severity in reactions[:2]:
            fields.extend([reaction.code, self.clean(reaction.display), severity])
        fields.extend([""] * (6 - min(2, len(reactions)) * 3))
        self._row(CSVConstants.ALLERGY_KEY, fields)

    def export_quality_of_life_observations(
        self, person_id: str, person: Person, cut_off: datetime
    ) -> None:
        """Java: CSVExporter#exportQualityOfLifeObservations; Calendar YEAR is lenient."""
        assert person.record is not None
        now = datetime.now(UTC)
        birthday = _EPOCH + timedelta(milliseconds=cast(int, person.attributes[Person.BIRTHDATE]))
        for score in ("QALY", "DALY", "QOLS"):
            scores = cast(dict[int, float], person.attributes[score])
            for year, value in scores.items():
                birthday = birthday.replace(year=year, day=1) + timedelta(days=birthday.day - 1)
                if cut_off < birthday < now:
                    obs = person.record.new_entry(
                        lambda birthday=birthday, score=score, value=value: Observation(
                            int(birthday.timestamp() * 1000), score, value
                        )
                    )
                    obs.unit = "{score}" if score == "QOLS" else "a"
                    obs.codes.append(Code("GBD", score, score))
                    self.export_observation(person_id, "", obs)

    def export_observation(
        self, person_id: str, encounter_id: str, observation: Observation
    ) -> None:
        """Java: CSVExporter#exportObservation."""
        if observation.value is None:
            for child in observation.observations or []:
                self.export_observation(person_id, encounter_id, child)
            return
        code = observation.codes[0]
        self._row(
            CSVConstants.OBSERVATION_KEY,
            [
                _iso(observation.start),
                person_id,
                encounter_id,
                _optional(observation.category),
                code.code,
                self.clean(code.display),
                self.clean(ExportHelper.get_observation_value(observation)),
                self.clean(observation.unit),
                ExportHelper.get_observation_type(observation),
            ],
        )

    def export_procedure(self, person_id: str, encounter_id: str, procedure: Procedure) -> None:
        """Java: CSVExporter#exportProcedure."""
        code = procedure.codes[0]
        reason = procedure.reasons[0] if procedure.reasons else None
        self._row(
            CSVConstants.PROCEDURE_KEY,
            [
                _iso(procedure.start),
                _iso(procedure.stop) if procedure.stop else "",
                person_id,
                encounter_id,
                code.system,
                code.code,
                self.clean(code.display),
                _money(procedure.get_cost()),
                reason.code if reason else "",
                self.clean(reason.display) if reason else "",
            ],
        )

    def export_medication(
        self,
        person_id: str,
        encounter_id: str,
        payer_id: str,
        medication: Medication,
        stop_time: int,
    ) -> None:
        """Java: CSVExporter#exportMedication; refills are used directly as dispenses."""
        code = medication.codes[0]
        cost = medication.get_cost()
        duration = (medication.stop or stop_time) - medication.start
        details = medication.prescription_details
        if details is not None and "refills" in details:
            dispenses = int(cast(int, details["refills"]))
        elif details is not None and "duration" in details:
            spec = cast(dict[str, object], details["duration"])
            dispenses = idiv(
                duration,
                Utilities.convert_time(cast(str, spec["unit"]), cast(int, spec["quantity"])),
            )
        else:
            dispenses = idiv(duration, Utilities.convert_time("months", 1))
        dispenses = max(1, dispenses)
        total = (cost * dispenses).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        reason = medication.reasons[0] if medication.reasons else None
        self._row(
            CSVConstants.MEDICATION_KEY,
            [
                _iso(medication.start),
                _iso(medication.stop) if medication.stop else "",
                person_id,
                payer_id,
                encounter_id,
                code.code,
                self.clean(code.display),
                _money(cost),
                _money(medication.claim.get_total_covered_cost()),
                dispenses,
                _money(total),
                reason.code if reason else "",
                self.clean(reason.display) if reason else "",
            ],
        )

    def export_immunization(self, person_id: str, encounter_id: str, immunization: Entry) -> None:
        """Java: CSVExporter#exportImmunization."""
        code = immunization.codes[0]
        self._row(
            CSVConstants.IMMUNIZATION_KEY,
            [
                _iso(immunization.start),
                person_id,
                encounter_id,
                code.code,
                self.clean(code.display),
                _money(immunization.get_cost()),
            ],
        )

    def export_care_plan(self, person_id: str, encounter_id: str, care_plan: CarePlan) -> str:
        """Java: CSVExporter#exportCarePlan; display is intentionally uncleaned."""
        code = care_plan.codes[0]
        reason = care_plan.reasons[0] if care_plan.reasons else None
        self._row(
            CSVConstants.CAREPLAN_KEY,
            [
                care_plan.uuid,
                _date(care_plan.start),
                _date(care_plan.stop) if care_plan.stop else "",
                person_id,
                encounter_id,
                code.code,
                code.display,
                reason.code if reason else "",
                self.clean(reason.display) if reason else "",
            ],
        )
        return str(care_plan.uuid)

    def export_imaging_study(
        self, person_id: str, encounter_id: str, imaging_study: ImagingStudy
    ) -> str:
        """Java: CSVExporter#exportImagingStudy; one write for all series/instances."""
        rows = []
        for series in imaging_study.series:
            assert series.instances is not None
            assert series.body_site is not None and series.modality is not None
            for instance in series.instances:
                assert instance.sop_class is not None
                rows.append(
                    ",".join(
                        _text(v)
                        for v in [
                            imaging_study.uuid,
                            _iso(imaging_study.start),
                            person_id,
                            encounter_id,
                            series.dicom_uid,
                            series.body_site.code,
                            series.body_site.display,
                            series.modality.code,
                            series.modality.display,
                            instance.dicom_uid,
                            instance.sop_class.code,
                            instance.sop_class.display,
                            imaging_study.codes[0].code,
                        ]
                    )
                    + self.NEWLINE
                )
        self.file_manager.write_resource_line("".join(rows), CSVConstants.IMAGING_STUDY_KEY)
        return str(imaging_study.uuid)

    def export_device(self, person_id: str, encounter_id: str, device: Device) -> None:
        """Java: CSVExporter#exportDevice."""
        code = device.codes[0]
        self._row(
            CSVConstants.DEVICE_KEY,
            [
                _iso(device.start),
                _iso(device.stop) if device.stop else "",
                person_id,
                encounter_id,
                code.code,
                self.clean(code.display),
                device.udi,
            ],
        )

    def export_supply(
        self, person_id: str, encounter_id: str, encounter: Encounter, supply: Supply
    ) -> None:
        """Java: CSVExporter#exportSupply."""
        code = supply.codes[0]
        self._row(
            CSVConstants.SUPPLY_KEY,
            [
                _date(supply.start),
                person_id,
                encounter_id,
                code.code,
                self.clean(code.display),
                supply.quantity,
            ],
        )

    def export_organization(self, org: Provider, utilization: int) -> None:
        """Java: CSVExporter#exportOrganization."""
        self._row(
            CSVConstants.ORGANIZATION_KEY,
            [
                org.get_resource_id(),
                self.clean(org.name),
                self.clean(org.address),
                org.city,
                org.state,
                org.zip,
                org.get_y(),
                org.get_x(),
                org.phone,
                org.get_revenue(),
                utilization,
                self.clean(org.npi),
            ],
        )

    def export_provider(self, provider: Clinician, org_id: str) -> None:
        """Java: CSVExporter#exportProvider."""
        fields: list[object] = [provider.get_resource_id(), org_id]
        for key in (
            Clinician.NAME,
            Clinician.GENDER,
            Clinician.SPECIALTY,
            Clinician.ADDRESS,
            Clinician.CITY,
            Clinician.STATE,
            Clinician.ZIP,
        ):
            fields.append(self.clean(cast(str | None, provider.attributes.get(key, ""))))
        fields.extend(
            [
                provider.get_y(),
                provider.get_x(),
                provider.get_encounter_count(),
                provider.get_procedure_count(),
                self.clean(provider.npi),
            ]
        )
        self._row(CSVConstants.PROVIDER_KEY, fields)

    def export_payer(self, payer: Payer) -> None:
        """Java: CSVExporter#exportPayer."""
        fields: list[object] = [payer.get_resource_id(), payer.get_name(), payer.get_ownership()]
        for key in ("address", "city", "state_headquartered", "zip", "phone"):
            fields.append(self.clean(cast(str | None, payer.get_attributes().get(key, ""))))
        fields.extend(
            [
                _money(payer.get_amount_covered()),
                _money(payer.get_amount_uncovered()),
                _money(payer.get_revenue()),
                payer.get_encounters_covered_count(),
                payer.get_encounters_uncovered_count(),
                payer.get_medications_covered_count(),
                payer.get_medications_uncovered_count(),
                payer.get_procedures_covered_count(),
                payer.get_procedures_uncovered_count(),
                payer.get_immunizations_covered_count(),
                payer.get_immunizations_uncovered_count(),
                payer.get_unique_customers(),
                payer.get_qols_average(),
                payer.get_num_years_covered() * 12,
            ]
        )
        self._row(CSVConstants.PAYER_KEY, fields)

    def export_payer_transition(self, person: Person, plan_record: PlanRecord) -> None:
        """Java: CSVExporter#exportPayerTransition."""
        secondary = plan_record.get_secondary_plan()
        self._row(
            CSVConstants.PAYER_TRANSITION_KEY,
            [
                person.attributes.get(Person.ID),
                _optional(plan_record.id),
                _iso(plan_record.get_start_time()),
                _iso(plan_record.get_stop_time()) if plan_record.get_stop_time() else "",
                plan_record.get_plan().get_payer().get_resource_id(),
                secondary.get_payer().get_resource_id()
                if secondary.get_payer() and not secondary.is_no_insurance()
                else "",
                _optional(plan_record.ownership),
                _optional(plan_record.owner_name),
            ],
        )

    def export_patient_expense(self, person: Person, plan_record: PlanRecord) -> None:
        """Java: CSVExporter#exportPatientExpense; expenses are cast to double."""
        self._row(
            CSVConstants.PATIENT_EXPENSE_KEY,
            [
                person.attributes.get(Person.ID),
                _iso(plan_record.get_start_time()),
                plan_record.get_plan().get_payer().get_resource_id(),
                float(plan_record.get_out_of_pocket_expenses()),
                float(plan_record.get_insurance_expenses()),
                float(plan_record.get_covered_expenses()),
            ],
        )

    def claim_department_code(self, encounter: Encounter, patient: Person) -> str:
        """Java: CSVExporter#claimDepartmentCode."""
        if encounter.type is None:
            return "99"
        kind = EncounterType.from_string(encounter.type)
        if kind == EncounterType.WELLNESS:
            return "10" if patient.age_in_years(encounter.start) < 18 else "20"
        return str(list(EncounterType).index(kind))

    def export_claim(
        self, person: Person, claim: Claim, encounter: Encounter, encounter_id: str, time: int
    ) -> None:
        """Java: CSVExporter#exportClaim."""
        institutional = encounter.provider.institutional if encounter.provider else True
        clinician = encounter.clinician.get_resource_id() if encounter.clinician else ""
        secondary = claim.get_secondary_payer()
        has_secondary = secondary is not None and not secondary.is_no_insurance()
        dept = self.claim_department_code(encounter, claim.person)
        diagnoses: list[str | None] = []
        if encounter.reason:
            diagnoses.append(encounter.reason.code)
        for item in encounter.conditions:
            if len(diagnoses) == 8:
                break
            diagnoses.append(item.codes[0].code)
        if not diagnoses:
            diagnoses.append(encounter.codes[0].code)
        diagnoses.extend([None] * (8 - len(diagnoses)))
        assert claim.person.record is not None
        onset = encounter.start
        for code in diagnoses:
            if code is not None:
                found = claim.person.record.present_onset(code)
                if found is not None and found < onset:
                    onset = found
        fields: list[object] = [
            claim.uuid,
            claim.person.attributes.get(Person.ID),
            clinician,
            ""
            if encounter.claim.get_payer() is None or encounter.claim.get_payer().is_no_insurance()
            else claim.get_payer().get_resource_id(),
            secondary.get_resource_id() if has_secondary else "",
            dept,
            dept,
            *[_optional(code) for code in diagnoses],
            "",
            encounter_id,
            _iso(onset),
            _iso(encounter.start),
            clinician,
        ]
        if time > encounter.stop:
            status, covered, patient, billed = "CLOSED", "0", "0", _iso(encounter.stop)
        else:
            status = "BILLED"
            covered = _money(encounter.claim.get_total_covered_cost())
            patient = _money(claim.get_total_claim_cost() - claim.get_total_covered_cost())
            billed = _iso(encounter.start)
        fields.extend(
            [
                status,
                status if has_secondary else "",
                status,
                covered,
                covered if has_secondary else "",
                patient,
                billed,
                billed if has_secondary else "",
                billed,
                "2" if institutional else "1",
                ("2" if institutional else "1") if has_secondary else "0",
            ]
        )
        self._row(CSVConstants.CLAIM_KEY, fields)
        self.simulate_claim_process(
            person,
            claim,
            str(claim.uuid),
            encounter,
            encounter_id,
            claim.main_entry,
            diagnoses,
            dept,
            True,
        )
        for entry in claim.items:
            if isinstance(entry.entry, (Procedure, Immunization, Medication)):
                self.simulate_claim_process(
                    person,
                    claim,
                    str(claim.uuid),
                    encounter,
                    encounter_id,
                    entry,
                    diagnoses,
                    dept,
                    False,
                )

    def _next_transaction(self) -> int:
        """Java: AtomicLong#getAndIncrement, including signed overflow."""
        current = self.transaction_id
        self.transaction_id = to_int64(current + 1)
        return current

    def simulate_claim_process(
        self,
        person: Person,
        claim: Claim,
        claim_id: str,
        encounter: Encounter,
        encounter_id: str,
        claim_entry: ClaimEntry,
        diagnosis_codes: list[str | None],
        department_id: str,
        main_entry: bool,
    ) -> None:
        """Java: CSVExporter#simulateClaimProcess; preserve unused charge ID increments."""
        charge_id = self._next_transaction()

        def new() -> ClaimTransaction:
            """Java: repeated ClaimTransaction construction with common fields."""
            t = ClaimTransaction(
                encounter, encounter_id, claim, claim_id, charge_id, claim_entry, person
            )
            t.department_id = department_id
            t.diagnosis_codes = diagnosis_codes
            return t

        def write(t: ClaimTransaction) -> None:
            """Java: CSVFileManager#writeResourceLine for this transaction."""
            self.file_manager.write_resource_line(t.to_string(), CSVConstants.CLAIM_TRANSACTION_KEY)

        t = new()
        t.type = ClaimTransactionType.CHARGE
        t.set_amount(claim_entry.cost)
        t.transfer_type = "p" if claim.get_payer().is_no_insurance() else "1"
        write(t)
        charge_id = self._next_transaction()
        remainder = claim_entry.cost
        if main_entry and claim_entry.copay_paid_by_patient > Claim.ZERO_CENTS:
            remainder = max(Claim.ZERO_CENTS, remainder - claim_entry.copay_paid_by_patient)
            t = new()
            t.type, t.method = ClaimTransactionType.PAYMENT, PaymentMethod.COPAY
            t.payment, t.unpaid = claim_entry.copay_paid_by_patient, remainder
            write(t)
            charge_id = self._next_transaction()
        if claim_entry.adjustment > Claim.ZERO_CENTS:
            remainder = max(Claim.ZERO_CENTS, remainder - claim_entry.adjustment)
            t = new()
            t.type, t.method = ClaimTransactionType.ADJUSTMENT, PaymentMethod.SYSTEM
            t.adjustment, t.unpaid = claim_entry.adjustment, remainder
            write(t)
            charge_id = self._next_transaction()
        payer_amount = claim_entry.paid_by_payer + claim_entry.coinsurance_paid_by_payer
        if payer_amount > Claim.ZERO_CENTS:
            remainder -= payer_amount
            t = new()
            t.type, t.method = ClaimTransactionType.PAYMENT, PaymentMethod.ECHECK
            t.payment, t.unpaid = payer_amount, remainder
            write(t)
            charge_id = self._next_transaction()
        secondary_amount = claim_entry.paid_by_secondary_payer
        if secondary_amount > Claim.ZERO_CENTS:
            t = new()
            t.type = ClaimTransactionType.TRANSFEROUT
            t.amount = t.unpaid = remainder
            write(t)
            transfer_out = charge_id
            charge_id = self._next_transaction()
            t = new()
            t.type = ClaimTransactionType.TRANSFERIN
            t.transfer_type, t.transfer_id = "2", transfer_out
            t.amount = t.unpaid = remainder
            write(t)
            charge_id = self._next_transaction()
            remainder -= secondary_amount
            t = new()
            t.type, t.method = ClaimTransactionType.PAYMENT, PaymentMethod.ECHECK
            t.payment, t.unpaid = secondary_amount, remainder
            write(t)
            charge_id = self._next_transaction()
        if remainder > Claim.ZERO_CENTS:
            if not claim.get_payer().is_no_insurance():
                t = new()
                t.type = ClaimTransactionType.TRANSFEROUT
                t.amount = t.unpaid = remainder
                write(t)
                transfer_out = charge_id
                charge_id = self._next_transaction()
                t = new()
                t.type = ClaimTransactionType.TRANSFERIN
                t.transfer_type, t.transfer_id = "p", transfer_out
                t.amount = t.unpaid = remainder
                write(t)
                charge_id = self._next_transaction()
            t = new()
            t.type = ClaimTransactionType.PAYMENT
            t.method = (PaymentMethod.CASH, PaymentMethod.CHECK, PaymentMethod.CC)[charge_id % 3]
            t.payment, t.unpaid = remainder, Claim.ZERO_CENTS
            write(t)
            charge_id = self._next_transaction()

    @staticmethod
    def clean(src: str | None) -> str:
        """Java: CSVExporter#clean; String.trim removes only U+0000 through U+0020."""
        return (
            ""
            if src is None
            else re.sub(r"\r\n|\r|\n|,", " ", src).strip("".join(chr(i) for i in range(33)))
        )


class SingletonHolder:
    """Java: CSVExporter.SingletonHolder, initialized on first access."""

    instance: ClassVar[CSVExporter | None] = None

    def __init__(self) -> None:
        """Java: SingletonHolder#SingletonHolder (implicit constructor)."""


class ClaimTransactionType(StrEnum):
    """Java: CSVExporter.ClaimTransactionType."""

    CHARGE = "CHARGE"
    PAYMENT = "PAYMENT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFERIN = "TRANSFERIN"
    TRANSFEROUT = "TRANSFEROUT"


class PaymentMethod(StrEnum):
    """Java: CSVExporter.PaymentMethod."""

    CASH = "CASH"
    CHECK = "CHECK"
    COPAY = "COPAY"
    SYSTEM = "SYSTEM"
    CC = "CC"
    ECHECK = "ECHECK"


class ClaimTransaction:
    """Java: CSVExporter.ClaimTransaction."""

    def __init__(
        self,
        encounter: Encounter,
        encounter_id: str,
        claim: Claim,
        claim_id: str,
        charge_id: int,
        claim_entry: ClaimEntry,
        person: Person,
    ) -> None:
        """Java: ClaimTransaction#ClaimTransaction."""
        self.id = ExportHelper.build_uuid(
            person, encounter.start, f"ClaimTransaction for Claim {claim_id} {charge_id}"
        )
        self.encounter_id, self.claim_id, self.charge_id = encounter_id, claim_id, charge_id
        self.transfer_id = 0
        self.transfer_type: str | None = None
        self.patient_id = cast(str, claim.person.attributes.get(Person.ID))
        self.member_id: str | None = claim.get_plan_record_member_id()
        self.type: ClaimTransactionType
        self.amount = Claim.ZERO_CENTS
        self.units: int | None = 1
        self.unit_amount: Decimal | None = Claim.ZERO_CENTS
        self.payment: Decimal | None = Claim.ZERO_CENTS
        self.adjustment: Decimal | None = Claim.ZERO_CENTS
        self.unpaid: Decimal | None = Claim.ZERO_CENTS
        self.method: PaymentMethod | None = None
        self.start, self.stop = claim_entry.entry.start, claim_entry.entry.stop
        self.organization_id = encounter.provider.get_resource_id() if encounter.provider else None
        self.clinician_id = encounter.clinician.get_resource_id() if encounter.clinician else None
        self.department_id: str | None = None
        self.procedure_code = CSVExporter.clean(claim_entry.entry.codes[0].code)
        self.procedure_display = CSVExporter.clean(claim_entry.entry.codes[0].display)
        self.diagnosis_codes: list[str | None] = []
        self.notes: str | None = None

    def set_amount(self, amount: Decimal) -> None:
        """Java: ClaimTransaction#setAmount."""
        self.amount = self.unit_amount = amount

    def to_string(self) -> str:
        """Java: ClaimTransaction#toString; unset TODATE stays empty."""
        charge = self.type == ClaimTransactionType.CHARGE
        transfer_in = self.type == ClaimTransactionType.TRANSFERIN
        transfer_out = self.type == ClaimTransactionType.TRANSFEROUT
        fields: list[object] = [
            self.id,
            self.claim_id,
            self.charge_id,
            self.patient_id,
            self.type,
            _money(self.amount) if charge or transfer_in else "",
            self.method
            if self.type in (ClaimTransactionType.PAYMENT, ClaimTransactionType.ADJUSTMENT)
            else "",
            _iso(self.start),
            _iso(self.stop) if self.stop else "",
            self.organization_id,
            self.procedure_code,
            "",
            "",
            *[str(i + 1) if self.diagnosis_codes[i] else "" for i in range(4)],
            _optional(self.units),
            self.department_id,
            CSVExporter.clean(self.procedure_display),
            _money(self.unit_amount),
            self.transfer_id if transfer_in else "",
            self.transfer_type if charge or transfer_in else "",
            _money(self.payment),
            _money(self.adjustment),
            _money(self.amount) if transfer_in or transfer_out else "",
            _money(self.unpaid),
            self.encounter_id,
            "",
            _optional(self.member_id),
            "1",
            self.clinician_id,
            self.clinician_id,
        ]
        return ",".join(_text(v) for v in fields) + CSVExporter.NEWLINE


setattr(CSVExporter, "SingletonHolder", SingletonHolder)  # noqa: B010
setattr(CSVExporter, "ClaimTransactionType", ClaimTransactionType)  # noqa: B010
setattr(CSVExporter, "PaymentMethod", PaymentMethod)  # noqa: B010
setattr(CSVExporter, "ClaimTransaction", ClaimTransaction)  # noqa: B010
