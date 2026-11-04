"""Java API skeleton: Exporter.java."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.generator import Generator
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry as ClaimClaimEntry
    from synthea.world.concepts.health_record import Entry as HealthRecordEntry
    from synthea.world.concepts.health_record import HealthRecord

    class CodeMapper(Protocol):
        """Java boundary type: CodeMapper; external to the mapped Python port."""

    class Mapping(Protocol):
        """Java boundary type: Mapping; external to the mapped Python port."""

    class Pair(Protocol):
        """Java boundary type: Pair; external to the mapped Python port."""

    class PatientExporter(Protocol):
        """Java boundary type: PatientExporter; external to the mapped Python port."""

    class PostCompletionExporter(Protocol):
        """Java boundary type: PostCompletionExporter; external to the mapped Python port."""

    class PrintWriter(Protocol):
        """Java boundary type: PrintWriter; external to the mapped Python port."""


class Exporter:
    """Java: Exporter; pending T25."""

    deferredExports: ClassVar[list[Pair]]  # Java initialization deferred to T25.
    fileWriters: ClassVar[dict[Path, PrintWriter]] = {}
    FILE_BUFFER_SIZE: ClassVar[int] = 4194304
    patientExporters: ClassVar[list[PatientExporter]]  # Java initialization deferred to T25.
    postCompletionExporters: ClassVar[
        list[PostCompletionExporter]
    ]  # Java initialization deferred to T25.
    codeMappers: ClassVar[dict[str, CodeMapper]]  # Java initialization deferred to T25.

    def __init__(self) -> None:
        """Java: Exporter#Exporter.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Exporter#Exporter — pending T25")

    @staticmethod
    def load_custom_exporters() -> None:
        """Java: Exporter#loadCustomExporters.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Exporter#loadCustomExporters — pending T25")

    @staticmethod
    def load_code_mappers() -> None:
        """Java: Exporter#loadCodeMappers.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Exporter#loadCodeMappers — pending T25")

    @staticmethod
    def get_code_mapper(code_system: str) -> CodeMapper:
        """Java: Exporter#getCodeMapper.

        Java overloads:
        (String codeSystem)
        """
        raise NotImplementedError("Java: Exporter#getCodeMapper — pending T25")

    @staticmethod
    def get_code_mappers() -> dict[str, CodeMapper]:
        """Java: Exporter#getCodeMappers.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Exporter#getCodeMappers — pending T25")

    @staticmethod
    def export(
        person: Person, stop_time: int, options: ExporterRuntimeOptions | None = None
    ) -> bool | None:
        """Java: Exporter#export.

        Java overloads:
        (Person person, long stopTime, ExporterRuntimeOptions options)
        (Person person, long stopTime)
        """
        raise NotImplementedError("Java: Exporter#export — pending T25")

    @staticmethod
    def export_record(
        person: Person, file_tag: str, stop_time: int, options: ExporterRuntimeOptions
    ) -> bool:
        """Java: Exporter#exportRecord.

        Java overloads:
        (Person person, String fileTag, long stopTime, ExporterRuntimeOptions options)
        """
        raise NotImplementedError("Java: Exporter#exportRecord — pending T25")

    @staticmethod
    def write_new_file(file: Path, contents: str) -> None:
        """Java: Exporter#writeNewFile.

        Java overloads:
        (Path file, String contents)
        """
        raise NotImplementedError("Java: Exporter#writeNewFile — pending T25")

    @staticmethod
    def overwrite_file(file: Path, contents: str) -> None:
        """Java: Exporter#overwriteFile.

        Java overloads:
        (Path file, String contents)
        """
        raise NotImplementedError("Java: Exporter#overwriteFile — pending T25")

    @staticmethod
    def append_to_file(file: Path, contents: str) -> None:
        """Java: Exporter#appendToFile.

        Java overloads:
        (Path file, String contents)
        """
        raise NotImplementedError("Java: Exporter#appendToFile — pending T25")

    @staticmethod
    def close_open_files() -> None:
        """Java: Exporter#closeOpenFiles.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Exporter#closeOpenFiles — pending T25")

    @staticmethod
    def run_post_completion_exports(
        generator: Generator, options: ExporterRuntimeOptions | None = None
    ) -> None:
        """Java: Exporter#runPostCompletionExports.

        Java overloads:
        (Generator generator)
        (Generator generator, ExporterRuntimeOptions options)
        """
        raise NotImplementedError("Java: Exporter#runPostCompletionExports — pending T25")

    @staticmethod
    def filter_for_export(
        original_or_record: Person | HealthRecord, years_to_keep: int, end_time: int
    ) -> Person | HealthRecord:
        """Java: Exporter#filterForExport.

        Java overloads:
        (Person original, int yearsToKeep, long endTime)
        (HealthRecord record, int yearsToKeep, long endTime)
        """
        raise NotImplementedError("Java: Exporter#filterForExport — pending T25")

    @staticmethod
    def filter_entries[E](
        entries: list[E],
        claim_items: list[ClaimClaimEntry],
        cutoff_date: int,
        end_time: int,
        keep_function: Callable[[E], bool],
    ) -> None:
        """Java: Exporter#filterEntries.

        Java overloads:
        (List entries, List claimItems, long cutoffDate, long endTime, Predicate
        keepFunction)
        """
        raise NotImplementedError("Java: Exporter#filterEntries — pending T25")

    @staticmethod
    def entry_within_time_range(e: HealthRecordEntry, cutoff_date: int, end_time: int) -> bool:
        """Java: Exporter#entryWithinTimeRange.

        Java overloads:
        (HealthRecord.Entry e, long cutoffDate, long endTime)
        """
        raise NotImplementedError("Java: Exporter#entryWithinTimeRange — pending T25")

    @staticmethod
    def filter_after_death(person: Person) -> None:
        """Java: Exporter#filterAfterDeath.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: Exporter#filterAfterDeath — pending T25")

    @staticmethod
    def get_output_folder(folder_name: str, person: Person) -> Path:
        """Java: Exporter#getOutputFolder.

        Java overloads:
        (String folderName, Person person)
        """
        raise NotImplementedError("Java: Exporter#getOutputFolder — pending T25")

    @staticmethod
    def filename(person: Person, tag: str, extension: str) -> str:
        """Java: Exporter#filename.

        Java overloads:
        (Person person, String tag, String extension)
        """
        raise NotImplementedError("Java: Exporter#filename — pending T25")


class SupportedFhirVersion(StrEnum):
    """Java: SupportedFhirVersion; pending T25."""

    DSTU2 = "DSTU2"
    STU3 = "STU3"
    R4 = "R4"


class ExporterRuntimeOptions:
    """Java: ExporterRuntimeOptions; pending T25."""

    def __init__(self, init: ExporterRuntimeOptions | None = None) -> None:
        """Java: ExporterRuntimeOptions#ExporterRuntimeOptions.

        Java overloads:
        ()
        (ExporterRuntimeOptions init)
        """
        self.years_of_history: int
        self.defer_exports: bool
        self.terminology_service: bool
        self.record_queue: list[str]
        self.fhir_version: SupportedFhirVersion
        self.flexporter_mappings: list[Mapping]
        raise NotImplementedError(
            "Java: ExporterRuntimeOptions#ExporterRuntimeOptions — pending T25"
        )

    def enable_queue(self, version: SupportedFhirVersion) -> None:
        """Java: ExporterRuntimeOptions#enableQueue.

        Java overloads:
        (SupportedFhirVersion version)
        """
        raise NotImplementedError("Java: ExporterRuntimeOptions#enableQueue — pending T25")

    def queued_fhir_version(self) -> SupportedFhirVersion:
        """Java: ExporterRuntimeOptions#queuedFhirVersion.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExporterRuntimeOptions#queuedFhirVersion — pending T25")

    def is_queue_enabled(self) -> bool:
        """Java: ExporterRuntimeOptions#isQueueEnabled.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExporterRuntimeOptions#isQueueEnabled — pending T25")

    def get_next_record(self) -> str:
        """Java: ExporterRuntimeOptions#getNextRecord.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExporterRuntimeOptions#getNextRecord — pending T25")

    def is_record_queue_empty(self) -> bool:
        """Java: ExporterRuntimeOptions#isRecordQueueEmpty.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExporterRuntimeOptions#isRecordQueueEmpty — pending T25")

    def add_flexporter_mapping(self, mapping: Mapping) -> None:
        """Java: ExporterRuntimeOptions#addFlexporterMapping.

        Java overloads:
        (Mapping mapping)
        """
        raise NotImplementedError("Java: ExporterRuntimeOptions#addFlexporterMapping — pending T25")


setattr(Exporter, "SupportedFhirVersion", SupportedFhirVersion)  # noqa: B010
setattr(Exporter, "ExporterRuntimeOptions", ExporterRuntimeOptions)  # noqa: B010
