"""Java API skeleton for csv_exporter.py.
Java: org.mitre.synthea.export.CSVExporter.
"""

from __future__ import annotations

from enum import StrEnum


class CSVExporter:
    """Java: CSVExporter; pending T26."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: CSVExporter constructor; pending T26."""
        raise NotImplementedError("Java: CSVExporter — pending T26")

    def get_instance(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#getInstance."""
        raise NotImplementedError("Java: getInstance — pending T26")

    def export_organizations_and_providers(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportOrganizationsAndProviders."""
        raise NotImplementedError("Java: exportOrganizationsAndProviders — pending T26")

    def export_payers(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPayers."""
        raise NotImplementedError("Java: exportPayers — pending T26")

    def export_payer_transitions(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPayerTransitions."""
        raise NotImplementedError("Java: exportPayerTransitions — pending T26")

    def export_patient_expenses(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPatientExpenses."""
        raise NotImplementedError("Java: exportPatientExpenses — pending T26")

    def export(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#export."""
        raise NotImplementedError("Java: export — pending T26")

    def export_patient(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPatient."""
        raise NotImplementedError("Java: exportPatient — pending T26")

    def export_encounter(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportEncounter."""
        raise NotImplementedError("Java: exportEncounter — pending T26")

    def export_condition(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportCondition."""
        raise NotImplementedError("Java: exportCondition — pending T26")

    def export_allergy(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportAllergy."""
        raise NotImplementedError("Java: exportAllergy — pending T26")

    def export_quality_of_life_observations(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportQualityOfLifeObservations."""
        raise NotImplementedError("Java: exportQualityOfLifeObservations — pending T26")

    def export_observation(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportObservation."""
        raise NotImplementedError("Java: exportObservation — pending T26")

    def export_procedure(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportProcedure."""
        raise NotImplementedError("Java: exportProcedure — pending T26")

    def export_medication(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportMedication."""
        raise NotImplementedError("Java: exportMedication — pending T26")

    def export_immunization(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportImmunization."""
        raise NotImplementedError("Java: exportImmunization — pending T26")

    def export_care_plan(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportCarePlan."""
        raise NotImplementedError("Java: exportCarePlan — pending T26")

    def export_imaging_study(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportImagingStudy."""
        raise NotImplementedError("Java: exportImagingStudy — pending T26")

    def export_device(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportDevice."""
        raise NotImplementedError("Java: exportDevice — pending T26")

    def export_supply(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportSupply."""
        raise NotImplementedError("Java: exportSupply — pending T26")

    def export_organization(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportOrganization."""
        raise NotImplementedError("Java: exportOrganization — pending T26")

    def export_provider(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportProvider."""
        raise NotImplementedError("Java: exportProvider — pending T26")

    def export_payer(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPayer."""
        raise NotImplementedError("Java: exportPayer — pending T26")

    def export_payer_transition(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPayerTransition."""
        raise NotImplementedError("Java: exportPayerTransition — pending T26")

    def export_patient_expense(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportPatientExpense."""
        raise NotImplementedError("Java: exportPatientExpense — pending T26")

    def claim_department_code(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#claimDepartmentCode."""
        raise NotImplementedError("Java: claimDepartmentCode — pending T26")

    def export_claim(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#exportClaim."""
        raise NotImplementedError("Java: exportClaim — pending T26")

    def simulate_claim_process(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#simulateClaimProcess."""
        raise NotImplementedError("Java: simulateClaimProcess — pending T26")

    def set_amount(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#setAmount."""
        raise NotImplementedError("Java: setAmount — pending T26")

    def to_string(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#toString."""
        raise NotImplementedError("Java: toString — pending T26")

    def clean(self, *args: object, **kwargs: object) -> object:
        """Java: CSVExporter#clean."""
        raise NotImplementedError("Java: clean — pending T26")


class SingletonHolder:
    """Java: SingletonHolder; pending T26."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: SingletonHolder constructor; pending T26."""
        raise NotImplementedError("Java: SingletonHolder — pending T26")


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

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ClaimTransaction constructor; pending T26."""
        raise NotImplementedError("Java: ClaimTransaction — pending T26")
