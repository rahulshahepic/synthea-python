"""Java API skeleton: ExportHelper.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.components import Attachment, SampledData
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Observation

    class FastDateFormat(Protocol):
        """Java boundary type: FastDateFormat; external to the mapped Python port."""


class ExportHelper:
    """Java: ExportHelper; pending T25."""

    DATE_FORMAT: ClassVar[FastDateFormat]  # Java initialization deferred to T25.
    ISO_DATE_FORMAT: ClassVar[FastDateFormat]  # Java initialization deferred to T25.
    SNOMED_URI: ClassVar[str] = "http://snomed.info/sct"
    LOINC_URI: ClassVar[str] = "http://loinc.org"
    RXNORM_URI: ClassVar[str] = "http://www.nlm.nih.gov/research/umls/rxnorm"
    CVX_URI: ClassVar[str] = "http://hl7.org/fhir/sid/cvx"
    DICOM_DCM_URI: ClassVar[str] = (
        "http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_29.html"
    )
    CDT_URI: ClassVar[str] = "http://www.ada.org/cdt"
    ICD9_URI: ClassVar[str] = "http://hl7.org/fhir/sid/icd-9-cm"
    ICD10_URI: ClassVar[str] = "http://hl7.org/fhir/sid/icd-10"
    ICD10_CM_URI: ClassVar[str] = "http://hl7.org/fhir/sid/icd-10-cm"
    CPT_URI: ClassVar[str] = "http://www.ama-assn.org/go/cpt"
    UNDUPLICATED_FHIR_RESOURCES: ClassVar[list[str]] = ["Location", "Organization", "Practitioner"]

    def __init__(self) -> None:
        """Java: ExportHelper#ExportHelper.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExportHelper#ExportHelper — pending T25")

    @staticmethod
    def get_observation_value(observation: Observation, code: str | None = None) -> str:
        """Java: ExportHelper#getObservationValue.

        Java overloads:
        (Observation observation)
        (Observation observation, String code)
        """
        raise NotImplementedError("Java: ExportHelper#getObservationValue — pending T25")

    @staticmethod
    def sampled_data_to_value_string(sampled_data: SampledData) -> str:
        """Java: ExportHelper#sampledDataToValueString.

        Java overloads:
        (SampledData sampledData)
        """
        raise NotImplementedError("Java: ExportHelper#sampledDataToValueString — pending T25")

    @staticmethod
    def attachment_to_value_string(attachment: Attachment) -> str:
        """Java: ExportHelper#attachmentToValueString.

        Java overloads:
        (Attachment attachment)
        """
        raise NotImplementedError("Java: ExportHelper#attachmentToValueString — pending T25")

    @staticmethod
    def get_observation_type(observation: Observation) -> str:
        """Java: ExportHelper#getObservationType.

        Java overloads:
        (Observation observation)
        """
        raise NotImplementedError("Java: ExportHelper#getObservationType — pending T25")

    @staticmethod
    def iso() -> FastDateFormat:
        """Java: ExportHelper#iso.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExportHelper#iso — pending T25")

    @staticmethod
    def date_from_timestamp(time: int) -> str:
        """Java: ExportHelper#dateFromTimestamp.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: ExportHelper#dateFromTimestamp — pending T25")

    @staticmethod
    def iso8601_timestamp(time: int) -> str:
        """Java: ExportHelper#iso8601Timestamp.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: ExportHelper#iso8601Timestamp — pending T25")

    @staticmethod
    def next_friday(time: int) -> int:
        """Java: ExportHelper#nextFriday.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: ExportHelper#nextFriday — pending T25")

    @staticmethod
    def get_system_uri(system: str) -> str:
        """Java: ExportHelper#getSystemURI.

        Java overloads:
        (String system)
        """
        raise NotImplementedError("Java: ExportHelper#getSystemURI — pending T25")

    @staticmethod
    def get_system_from_uri(uri: str) -> str:
        """Java: ExportHelper#getSystemFromURI.

        Java overloads:
        (String uri)
        """
        raise NotImplementedError("Java: ExportHelper#getSystemFromURI — pending T25")

    @staticmethod
    def build_fhir_search_url(resource_type: str, identifier: str) -> str:
        """Java: ExportHelper#buildFhirSearchUrl.

        Java overloads:
        (String resourceType, String identifier)
        """
        raise NotImplementedError("Java: ExportHelper#buildFhirSearchUrl — pending T25")

    @staticmethod
    def build_fhir_npi_search_url(clinician: Clinician) -> str:
        """Java: ExportHelper#buildFhirNpiSearchUrl.

        Java overloads:
        (Clinician clinician)
        """
        raise NotImplementedError("Java: ExportHelper#buildFhirNpiSearchUrl — pending T25")

    @staticmethod
    def build_uuid(person_or_person_seed: Person | int, timestamp: int, key: str) -> str:
        """Java: ExportHelper#buildUUID.

        Java overloads:
        (Person person, long timestamp, String key)
        (long personSeed, long timestamp, String key)
        """
        raise NotImplementedError("Java: ExportHelper#buildUUID — pending T25")
