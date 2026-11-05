"""Java API skeleton: CSVExporter.java."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.export.csv_file_manager import CSVFileManager
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.claim import Claim
    from synthea.world.concepts.claim import ClaimEntry as ClaimClaimEntry
    from synthea.world.concepts.health_record import Allergy as HealthRecordAllergy
    from synthea.world.concepts.health_record import (
        CarePlan,
        Device,
        Encounter,
        Entry,
        ImagingStudy,
        Medication,
        Observation,
        Procedure,
        Supply,
    )
    from synthea.world.concepts.healthinsurance.plan_record import PlanRecord

    class AtomicLong(Protocol):
        """Java boundary type: AtomicLong; external to the mapped Python port."""

    class Calendar(Protocol):
        """Java boundary type: Calendar; external to the mapped Python port."""


class CSVExporter:
    """Java: CSVExporter; pending T26."""

    NEWLINE: ClassVar[str] = "\n"

    def __init__(self) -> None:
        """Java: CSVExporter#CSVExporter.

        Java overloads:
        ()
        """
        self.file_manager: CSVFileManager
        self.transaction_id: AtomicLong
        raise NotImplementedError("Java: CSVExporter#CSVExporter — pending T26")

    def init(self) -> None:
        """Java: CSVExporter#init.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVExporter#init — pending T26")

    @staticmethod
    def get_instance() -> CSVExporter:
        """Java: CSVExporter#getInstance.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVExporter#getInstance — pending T26")

    def export_organizations_and_providers(self) -> None:
        """Java: CSVExporter#exportOrganizationsAndProviders.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVExporter#exportOrganizationsAndProviders — pending T26")

    def export_payers(self) -> None:
        """Java: CSVExporter#exportPayers.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVExporter#exportPayers — pending T26")

    def export_payer_transitions(self, person: Person, stop_time: int) -> None:
        """Java: CSVExporter#exportPayerTransitions.

        Java overloads:
        (Person person, long stopTime)
        """
        raise NotImplementedError("Java: CSVExporter#exportPayerTransitions — pending T26")

    def export_patient_expenses(self, person: Person, cut_off_time: int, stop_time: int) -> None:
        """Java: CSVExporter#exportPatientExpenses.

        Java overloads:
        (Person person, long cutOffTime, long stopTime)
        """
        raise NotImplementedError("Java: CSVExporter#exportPatientExpenses — pending T26")

    def export(self, person: Person, time: int) -> None:
        """Java: CSVExporter#export.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CSVExporter#export — pending T26")

    def export_patient(self, person: Person, time: int) -> str:
        """Java: CSVExporter#exportPatient.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CSVExporter#exportPatient — pending T26")

    def export_encounter(self, person_id: str, encounter: Encounter) -> str:
        """Java: CSVExporter#exportEncounter.

        Java overloads:
        (String personID, Encounter encounter)
        """
        raise NotImplementedError("Java: CSVExporter#exportEncounter — pending T26")

    def export_condition(self, person_id: str, encounter_id: str, condition: Entry) -> None:
        """Java: CSVExporter#exportCondition.

        Java overloads:
        (String personID, String encounterID, Entry condition)
        """
        raise NotImplementedError("Java: CSVExporter#exportCondition — pending T26")

    def export_allergy(
        self, person_id: str, encounter_id: str, allergy: HealthRecordAllergy
    ) -> None:
        """Java: CSVExporter#exportAllergy.

        Java overloads:
        (String personID, String encounterID, HealthRecord.Allergy allergy)
        """
        raise NotImplementedError("Java: CSVExporter#exportAllergy — pending T26")

    def export_quality_of_life_observations(
        self, person_id: str, person: Person, cut_off: Calendar
    ) -> None:
        """Java: CSVExporter#exportQualityOfLifeObservations.

        Java overloads:
        (String personID, Person person, Calendar cutOff)
        """
        raise NotImplementedError("Java: CSVExporter#exportQualityOfLifeObservations — pending T26")

    def export_observation(
        self, person_id: str, encounter_id: str, observation: Observation
    ) -> None:
        """Java: CSVExporter#exportObservation.

        Java overloads:
        (String personID, String encounterID, Observation observation)
        """
        raise NotImplementedError("Java: CSVExporter#exportObservation — pending T26")

    def export_procedure(self, person_id: str, encounter_id: str, procedure: Procedure) -> None:
        """Java: CSVExporter#exportProcedure.

        Java overloads:
        (String personID, String encounterID, Procedure procedure)
        """
        raise NotImplementedError("Java: CSVExporter#exportProcedure — pending T26")

    def export_medication(
        self,
        person_id: str,
        encounter_id: str,
        payer_id: str,
        medication: Medication,
        stop_time: int,
    ) -> None:
        """Java: CSVExporter#exportMedication.

        Java overloads:
        (String personID, String encounterID, String payerID, Medication medication,
        long
        stopTime)
        """
        raise NotImplementedError("Java: CSVExporter#exportMedication — pending T26")

    def export_immunization(self, person_id: str, encounter_id: str, immunization: Entry) -> None:
        """Java: CSVExporter#exportImmunization.

        Java overloads:
        (String personID, String encounterID, Entry immunization)
        """
        raise NotImplementedError("Java: CSVExporter#exportImmunization — pending T26")

    def export_care_plan(self, person_id: str, encounter_id: str, care_plan: CarePlan) -> str:
        """Java: CSVExporter#exportCarePlan.

        Java overloads:
        (String personID, String encounterID, CarePlan carePlan)
        """
        raise NotImplementedError("Java: CSVExporter#exportCarePlan — pending T26")

    def export_imaging_study(
        self, person_id: str, encounter_id: str, imaging_study: ImagingStudy
    ) -> str:
        """Java: CSVExporter#exportImagingStudy.

        Java overloads:
        (String personID, String encounterID, ImagingStudy imagingStudy)
        """
        raise NotImplementedError("Java: CSVExporter#exportImagingStudy — pending T26")

    def export_device(self, person_id: str, encounter_id: str, device: Device) -> None:
        """Java: CSVExporter#exportDevice.

        Java overloads:
        (String personID, String encounterID, Device device)
        """
        raise NotImplementedError("Java: CSVExporter#exportDevice — pending T26")

    def export_supply(
        self, person_id: str, encounter_id: str, encounter: Encounter, supply: Supply
    ) -> None:
        """Java: CSVExporter#exportSupply.

        Java overloads:
        (String personID, String encounterID, Encounter encounter, Supply supply)
        """
        raise NotImplementedError("Java: CSVExporter#exportSupply — pending T26")

    def export_organization(self, org: Provider, utilization: int) -> None:
        """Java: CSVExporter#exportOrganization.

        Java overloads:
        (Provider org, int utilization)
        """
        raise NotImplementedError("Java: CSVExporter#exportOrganization — pending T26")

    def export_provider(self, provider: Clinician, org_id: str) -> None:
        """Java: CSVExporter#exportProvider.

        Java overloads:
        (Clinician provider, String orgId)
        """
        raise NotImplementedError("Java: CSVExporter#exportProvider — pending T26")

    def export_payer(self, payer: Payer) -> None:
        """Java: CSVExporter#exportPayer.

        Java overloads:
        (Payer payer)
        """
        raise NotImplementedError("Java: CSVExporter#exportPayer — pending T26")

    def export_payer_transition(self, person: Person, plan_record: PlanRecord) -> None:
        """Java: CSVExporter#exportPayerTransition.

        Java overloads:
        (Person person, PlanRecord planRecord)
        """
        raise NotImplementedError("Java: CSVExporter#exportPayerTransition — pending T26")

    def export_patient_expense(self, person: Person, plan_record: PlanRecord) -> None:
        """Java: CSVExporter#exportPatientExpense.

        Java overloads:
        (Person person, PlanRecord planRecord)
        """
        raise NotImplementedError("Java: CSVExporter#exportPatientExpense — pending T26")

    def claim_department_code(self, encounter: Encounter, patient: Person) -> str:
        """Java: CSVExporter#claimDepartmentCode.

        Java overloads:
        (Encounter encounter, Person patient)
        """
        raise NotImplementedError("Java: CSVExporter#claimDepartmentCode — pending T26")

    def export_claim(
        self, person: Person, claim: Claim, encounter: Encounter, encounter_id: str, time: int
    ) -> None:
        """Java: CSVExporter#exportClaim.

        Java overloads:
        (Person person, Claim claim, Encounter encounter, String encounterID, long time)
        """
        raise NotImplementedError("Java: CSVExporter#exportClaim — pending T26")

    def simulate_claim_process(
        self,
        person: Person,
        claim: Claim,
        claim_id: str,
        encounter: Encounter,
        encounter_id: str,
        claim_entry: ClaimClaimEntry,
        diagnosis_codes: list[str],
        department_id: str,
        main_entry: bool,
    ) -> None:
        """Java: CSVExporter#simulateClaimProcess.

        Java overloads:
        (Person person, Claim claim, String claimId, Encounter encounter, String
        encounterId,
        Claim.ClaimEntry claimEntry, String diagnosisCodes, String departmentId, boolean
        mainEntry)
        """
        raise NotImplementedError("Java: CSVExporter#simulateClaimProcess — pending T26")

    @staticmethod
    def clean(src: str) -> str:
        """Java: CSVExporter#clean.

        Java overloads:
        (String src)
        """
        raise NotImplementedError("Java: CSVExporter#clean — pending T26")


class SingletonHolder:
    """Java: SingletonHolder; pending T26."""

    instance: ClassVar[CSVExporter]  # Java initialization deferred to T26.

    def __init__(self) -> None:
        """Java: SingletonHolder#SingletonHolder.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SingletonHolder#SingletonHolder — pending T26")


class ClaimTransactionType(StrEnum):
    """Java: ClaimTransactionType; pending T26."""

    CHARGE = "CHARGE"
    PAYMENT = "PAYMENT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFERIN = "TRANSFERIN"
    TRANSFEROUT = "TRANSFEROUT"


class PaymentMethod(StrEnum):
    """Java: PaymentMethod; pending T26."""

    CASH = "CASH"
    CHECK = "CHECK"
    COPAY = "COPAY"
    SYSTEM = "SYSTEM"
    CC = "CC"
    ECHECK = "ECHECK"


class ClaimTransaction:
    """Java: ClaimTransaction; pending T26."""

    def __init__(
        self,
        encounter: Encounter,
        encounter_id: str,
        claim: Claim,
        claim_id: str,
        charge_id: int,
        claim_entry: ClaimClaimEntry,
        person: Person,
    ) -> None:
        """Java: ClaimTransaction#ClaimTransaction.

        Java overloads:
        (Encounter encounter, String encounterId, Claim claim, String claimId, long
        chargeId,
        Claim.ClaimEntry claimEntry, Person person)
        """
        self.id: str
        self.encounter_id: str
        self.claim_id: str
        self.charge_id: int
        self.transfer_id: int
        self.transfer_type: str
        self.patient_id: str
        self.member_id: str
        self.type: ClaimTransactionType
        self.amount: Decimal
        self.units: int
        self.unit_amount: Decimal
        self.payment: Decimal
        self.adjustment: Decimal
        self.unpaid: Decimal
        self.method: PaymentMethod
        self.start: int
        self.stop: int
        self.organization_id: str
        self.department_id: str
        self.clinician_id: str
        self.procedure_code: str
        self.procedure_display: str
        self.diagnosis_codes: list[str]
        self.notes: str
        raise NotImplementedError("Java: ClaimTransaction#ClaimTransaction — pending T26")

    def set_amount(self, amount: Decimal) -> None:
        """Java: ClaimTransaction#setAmount.

        Java overloads:
        (BigDecimal amount)
        """
        raise NotImplementedError("Java: ClaimTransaction#setAmount — pending T26")

    def to_string(self) -> str:
        """Java: ClaimTransaction#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimTransaction#toString — pending T26")


setattr(CSVExporter, "SingletonHolder", SingletonHolder)  # noqa: B010
setattr(CSVExporter, "ClaimTransactionType", ClaimTransactionType)  # noqa: B010
setattr(CSVExporter, "PaymentMethod", PaymentMethod)  # noqa: B010
setattr(CSVExporter, "ClaimTransaction", ClaimTransaction)  # noqa: B010
