"""Java: org.mitre.synthea.export.Exporter."""

from __future__ import annotations

import sys
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, ClassVar, Protocol, TextIO, cast

from synthea.export.csv_exporter import CSVExporter
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import (
    Encounter,
    Entry,
    HealthRecord,
    Observation,
    Report,
)

if TYPE_CHECKING:
    from synthea.engine.generator import Generator
    from synthea.world.concepts.claim import ClaimEntry as ClaimClaimEntry

    class CodeMapper(Protocol):
        """Java boundary type: CodeMapper; external to the mapped Python port."""

    class Mapping(Protocol):
        """Java boundary type: Mapping; external to the mapped Python port."""

    class PatientExporter(Protocol):
        """Java boundary type: PatientExporter; external to the mapped Python port."""

        def export(self, person: Person, stop_time: int, options: ExporterRuntimeOptions) -> None:
            """Java: PatientExporter#export(Person, long, ExporterRuntimeOptions)."""
            ...

    class PostCompletionExporter(Protocol):
        """Java boundary type: PostCompletionExporter; external to the mapped Python port."""

        def export(self, generator: Generator, options: ExporterRuntimeOptions) -> None:
            """Java: PostCompletionExporter#export(Generator, ExporterRuntimeOptions)."""
            ...


# Exporter flags whose exporters are part of this CSV-only port's scope decisions
# (issue #25): FHIR, hospital, practitioner and metadata exporters are ignored
# with a one-time warning; every other non-CSV exporter raises if enabled.
_IGNORED_FLAGS = (
    "exporter.fhir_stu3.export",
    "exporter.fhir_dstu2.export",
    "exporter.fhir.export",
    "exporter.fhir.bulk_data",
    "exporter.metadata.export",
)
_OUT_OF_SCOPE_FLAGS = (
    "exporter.ccda.export",
    "exporter.json.export",
    "exporter.bfd.export",
    "exporter.cpcds.export",
    "exporter.text.export",
    "exporter.text.per_encounter_export",
    "exporter.symptoms.csv.export",
    "exporter.symptoms.text.export",
    "exporter.cdw.export",
    "exporter.clinical_note.export",
)


class Exporter:
    """Java: org.mitre.synthea.export.Exporter."""

    deferred_exports: ClassVar[list[tuple[Person, int]]] = []
    file_writers: ClassVar[dict[Path, TextIO]] = {}
    FILE_BUFFER_SIZE: ClassVar[int] = 4194304
    patient_exporters: ClassVar[list[PatientExporter] | None] = None
    post_completion_exporters: ClassVar[list[PostCompletionExporter] | None] = None
    code_mappers: ClassVar[dict[str, CodeMapper] | None] = None
    _warned_ignored: ClassVar[set[str]] = set()

    def __init__(self) -> None:
        """Java: Exporter#Exporter (abstract class; never instantiated)."""
        raise TypeError("Java: Exporter is abstract")

    @staticmethod
    def _warn_ignored(flag: str) -> None:
        """One-time warning for a default-on exporter this port does not run."""
        if flag not in Exporter._warned_ignored:
            Exporter._warned_ignored.add(flag)
            print(
                f"WARNING: {flag} is enabled, but that exporter is not part of the "
                "CSV-only port and is being ignored. (The CLI defaults it to false.)",
                file=sys.stderr,
            )

    @staticmethod
    def _raise_out_of_scope(flag: str) -> None:
        message = f"{flag} exporter is out of scope for the CSV-only port"
        raise NotImplementedError(message)

    @staticmethod
    def load_custom_exporters() -> None:
        """Java: Exporter#loadCustomExporters."""
        if Config.get_as_boolean("exporter.enable_custom_exporters", False):
            # Java loads PatientExporter/PostCompletionExporter implementations
            # from the classpath via ServiceLoader; there is no classpath here.
            raise NotImplementedError("custom exporters (ServiceLoader) are out of scope")
        # Disabled: Java leaves the (null) lists untouched.

    @staticmethod
    def load_code_mappers() -> None:
        """Java: Exporter#loadCodeMappers."""
        code_system_properties = sorted(
            key for key in Config.all_property_names() if key.startswith("exporter.code_map")
        )
        if code_system_properties:
            # CodeMapper belongs to the BFD/RIF exporter, which is out of scope.
            raise NotImplementedError("exporter.code_map code mappers are out of scope")
        # Java builds an empty TreeMap when nothing is configured.
        Exporter.code_mappers = {}

    @staticmethod
    def get_code_mapper(code_system: str) -> CodeMapper | None:
        """Java: Exporter#getCodeMapper(String)."""
        return Exporter.get_code_mappers().get(code_system)

    @staticmethod
    def get_code_mappers() -> dict[str, CodeMapper]:
        """Java: Exporter#getCodeMappers."""
        if Exporter.code_mappers is None:
            return {}
        return Exporter.code_mappers

    @staticmethod
    def export(
        person: Person, stop_time: int, options: ExporterRuntimeOptions | None = None
    ) -> bool | None:
        """Java: Exporter#export.

        Java overloads:
        (Person person, long stopTime, ExporterRuntimeOptions options)
        (Person person, long stopTime)
        """
        if options is None:
            Exporter.export(person, stop_time, ExporterRuntimeOptions())
            return None
        was_exported = False
        if options.defer_exports:
            was_exported = True
            Exporter.deferred_exports.append((person, stop_time))
        else:
            if options.years_of_history > 0:
                person = cast(
                    Person,
                    Exporter.filter_for_export(person, options.years_of_history, stop_time),
                )
            if not person.alive(stop_time):
                Exporter.filter_after_death(person)
            if person.has_multiple_records:
                records = person.records
                if records is None:
                    raise TypeError("Java NullPointerException: person.records is null")
                for i, key in enumerate(list(records.keys())):
                    person.record = records.get(key)
                    if person.attributes.get(Person.ENTITY) is not None:
                        # Fixed records / identity are out of scope
                        # (PORTING_GUIDE section 8), as in Person#getProvider.
                        raise NotImplementedError(
                            "identity.Entity seed/variant selection is out of scope"
                        )
                    exported = Exporter.export_record(person, str(i), stop_time, options)
                    was_exported = was_exported or exported
            else:
                was_exported = Exporter.export_record(person, "", stop_time, options)
        return was_exported

    @staticmethod
    def export_record(
        person: Person, file_tag: str, stop_time: int, options: ExporterRuntimeOptions
    ) -> bool:
        """Java: Exporter#exportRecord(Person, String, long, ExporterRuntimeOptions)."""
        was_exported = True
        if options.terminology_service:
            # The terminology server is out of scope (PORTING_GUIDE section 8).
            raise NotImplementedError("terminology service ValueSet resolution is out of scope")

        for flag in _IGNORED_FLAGS[:3]:
            if Config.get_as_boolean(flag):
                Exporter._warn_ignored(flag)
        for flag in _OUT_OF_SCOPE_FLAGS[:2]:
            if Config.get_as_boolean(flag):
                Exporter._raise_out_of_scope(flag)
        if Config.get_as_boolean("exporter.csv.export"):
            try:
                CSVExporter.get_instance().export(person, stop_time)
            except OSError as e:
                print(f"IOException in CSV export: {e}", file=sys.stderr)
        for flag in _OUT_OF_SCOPE_FLAGS[2:]:
            if Config.get_as_boolean(flag):
                Exporter._raise_out_of_scope(flag)

        if Config.get_as_boolean("exporter.custom.export", True) and Exporter.patient_exporters:
            for patient_exporter in Exporter.patient_exporters:
                patient_exporter.export(person, stop_time, options)

        if options.is_queue_enabled():
            # The queue carries FHIR JSON, which is out of scope for this port.
            raise NotImplementedError("queued FHIR export is out of scope")
        return was_exported

    @staticmethod
    def write_new_file(file: Path, contents: str) -> None:
        """Java: Exporter#writeNewFile(Path, String).

        Files.write with CREATE_NEW writes the contents plus a line separator,
        and fails (caught, printed) if the file already exists.
        """
        try:
            with open(file, "x", encoding="utf-8", newline="") as f:
                f.write(contents + "\n")
        except OSError as e:
            print(f"IOException in writeNewFile: {e}", file=sys.stderr)

    @staticmethod
    def overwrite_file(file: Path, contents: str) -> None:
        """Java: Exporter#overwriteFile(Path, String)."""
        try:
            with open(file, "w", encoding="utf-8", newline="") as f:
                f.write(contents + "\n")
        except OSError as e:
            print(f"IOException in overwriteFile: {e}", file=sys.stderr)

    @staticmethod
    def append_to_file(file: Path, contents: str) -> None:
        """Java: Exporter#appendToFile(Path, String)."""
        writer = Exporter.file_writers.get(file)
        if writer is None:
            try:
                writer = open(file, "a", encoding="utf-8", newline="")  # noqa: SIM115
            except OSError as e:
                print(f"IOException in appendToFile: {e}", file=sys.stderr)
                raise TypeError("Java NullPointerException: writer is null") from e
            Exporter.file_writers[file] = writer
        writer.write(contents + "\n")

    @staticmethod
    def close_open_files() -> None:
        """Java: Exporter#closeOpenFiles."""
        for writer in Exporter.file_writers.values():
            writer.close()
        Exporter.file_writers.clear()

    @staticmethod
    def run_post_completion_exports(
        generator: Generator, options: ExporterRuntimeOptions | None = None
    ) -> None:
        """Java: Exporter#runPostCompletionExports.

        Java overloads:
        (Generator generator)
        (Generator generator, ExporterRuntimeOptions options)
        """
        if options is None:
            Exporter.run_post_completion_exports(generator, ExporterRuntimeOptions())
            return

        if options.defer_exports:
            non_deferred_options = ExporterRuntimeOptions(options)
            non_deferred_options.defer_exports = False
            for entry_person, entry_stop in Exporter.deferred_exports:
                Exporter.export(entry_person, entry_stop, non_deferred_options)
            Exporter.deferred_exports.clear()

        # Hospital/practitioner/FHIR-group exporters: ignored with a warning.
        Exporter._warn_ignored("exporter.fhir.export")

        if Config.get_as_boolean("exporter.bfd.export"):
            Exporter._raise_out_of_scope("exporter.bfd.export")

        if Config.get_as_boolean("exporter.cdw.export"):
            Exporter._raise_out_of_scope("exporter.cdw.export")

        if Config.get_as_boolean("exporter.csv.export"):
            try:
                CSVExporter.get_instance().export_organizations_and_providers()
                CSVExporter.get_instance().export_payers()
            except OSError as e:
                print(f"IOException in CSV post-completion export: {e}", file=sys.stderr)

        if Config.get_as_boolean("exporter.metadata.export", False):
            Exporter._warn_ignored("exporter.metadata.export")

        if Config.get_as_boolean("generate.track_detailed_transition_metrics", False):
            # No TransitionMetrics module exists in the port yet.
            raise NotImplementedError("TransitionMetrics export is out of scope")

        if Config.get_as_boolean("exporter.fhir.bulk_data"):
            Exporter._warn_ignored("exporter.fhir.bulk_data")

        if (
            Config.get_as_boolean("exporter.custom.export", True)
            and Exporter.post_completion_exporters
        ):
            for post_completion_exporter in Exporter.post_completion_exporters:
                post_completion_exporter.export(generator, options)

        Exporter.close_open_files()

    @staticmethod
    def filter_for_export(
        original_or_record: Person | HealthRecord, years_to_keep: int, end_time: int
    ) -> Person | HealthRecord:
        """Java: Exporter#filterForExport.

        Java overloads:
        (Person original, int yearsToKeep, long endTime)
        (HealthRecord record, int yearsToKeep, long endTime)
        """
        if isinstance(original_or_record, HealthRecord):
            return Exporter._filter_record_for_export(original_or_record, years_to_keep, end_time)
        # TODO: clone the patient so that we export only the last _ years
        # but the rest still exists, just in case
        filtered = original_or_record
        if filtered.has_multiple_records:
            records = filtered.records
            if records is None:
                raise TypeError("Java NullPointerException: filtered.records is null")
            for key in list(records.keys()):
                record = records.get(key)
                if record is None:
                    raise TypeError("Java NullPointerException: record is null")
                Exporter._filter_record_for_export(record, years_to_keep, end_time)
        else:
            record = filtered.record
            if record is None:
                raise TypeError("Java NullPointerException: filtered.record is null")
            filtered.record = Exporter._filter_record_for_export(record, years_to_keep, end_time)
        return filtered

    @staticmethod
    def _filter_record_for_export(
        record: HealthRecord, years_to_keep: int, end_time: int
    ) -> HealthRecord:
        """Java: Exporter#filterForExport(HealthRecord, int, long)."""
        from synthea.modules.death_module import DeathModule

        cutoff_date = end_time - Utilities.convert_time("years", years_to_keep)

        def not_future_dated(e: Entry) -> bool:
            return e.start <= end_time

        def entry_is_active(e: Entry) -> bool:
            return e.stop == 0 or e.stop > cutoff_date

        for encounter in record.encounters:
            claim_items = encounter.claim.items
            # keep a condition if it was active at any point since the cutoff date
            Exporter.filter_entries(
                encounter.conditions, claim_items, cutoff_date, end_time, entry_is_active
            )
            # allergies are essentially the same as conditions
            Exporter.filter_entries(
                encounter.allergies, claim_items, cutoff_date, end_time, entry_is_active
            )

            # some of the "future death" logic could potentially add a future-dated
            # death certificate
            def is_cause_of_death(o: Observation) -> bool:
                return DeathModule.CAUSE_OF_DEATH_CODE.code == o.type

            # keep cause of death unless it's future dated
            Exporter.filter_entries(
                encounter.observations,
                claim_items,
                cutoff_date,
                end_time,
                lambda o: is_cause_of_death(o) and not_future_dated(o),
            )

            # keep all death certificates, unless they are future-dated
            def is_death_certificate(r: Report) -> bool:
                return DeathModule.DEATH_CERTIFICATE.code == r.type

            Exporter.filter_entries(
                encounter.reports,
                claim_items,
                cutoff_date,
                end_time,
                lambda r: is_death_certificate(r) and not_future_dated(r),
            )
            Exporter.filter_entries(encounter.procedures, claim_items, cutoff_date, end_time, None)
            # keep medications if still active, regardless of start date
            Exporter.filter_entries(
                encounter.medications, claim_items, cutoff_date, end_time, entry_is_active
            )
            Exporter.filter_entries(
                encounter.immunizations, claim_items, cutoff_date, end_time, None
            )
            # keep careplans if they are still active, regardless of start date
            Exporter.filter_entries(
                encounter.careplans, claim_items, cutoff_date, end_time, entry_is_active
            )

        # if ANY of these are not empty, the encounter is not empty
        def encounter_not_empty(e: Encounter) -> bool:
            return (
                bool(e.conditions)
                or bool(e.allergies)
                or bool(e.observations)
                or bool(e.reports)
                or bool(e.procedures)
                or bool(e.medications)
                or bool(e.immunizations)
                or bool(e.careplans)
            )

        def is_death_certification(e: Encounter) -> bool:
            return bool(e.codes) and e.codes[0] == DeathModule.DEATH_CERTIFICATION

        # finally filter out any empty encounters
        Exporter.filter_entries(
            record.encounters,
            [],
            cutoff_date,
            end_time,
            lambda e: encounter_not_empty(e) or (is_death_certification(e) and not_future_dated(e)),
        )
        return record

    @staticmethod
    def filter_entries[E: Entry](
        entries: list[E],
        claim_items: list[ClaimClaimEntry],
        cutoff_date: int,
        end_time: int,
        keep_function: Callable[[E], bool] | None,
    ) -> None:
        """Java: Exporter#filterEntries(List, List, long, long, Predicate)."""
        kept: list[E] = []
        for entry in entries:
            # if the entry is not within the keep time range,
            # and the special keep function (if provided) doesn't say keep it
            # remove it from the list
            if not Exporter.entry_within_time_range(entry, cutoff_date, end_time) and (
                keep_function is None or not keep_function(entry)
            ):
                # compare with identity because we only care if it's the actual same object
                claim_items[:] = [ci for ci in claim_items if ci.entry is not entry]
            else:
                kept.append(entry)
        entries[:] = kept

    @staticmethod
    def entry_within_time_range(e: Entry, cutoff_date: int, end_time: int) -> bool:
        """Java: Exporter#entryWithinTimeRange(Entry, long, long)."""
        if e.start > cutoff_date and e.start <= end_time:
            return True  # trivial case, when we're within the last __ years

        # if the entry has a stop time, check if the effective date range
        # overlapped the last __ years
        if e.stop != 0 and e.stop > cutoff_date:
            if e.stop > end_time:
                # If any entries have an end date in the future but are within the
                # cutoffDate, remove the end date but keep the entry (since it's
                # still active).
                e.stop = 0
            return True

        return False

    @staticmethod
    def filter_after_death(person: Person) -> None:
        """Java: Exporter#filterAfterDeath(Person)."""
        from synthea.modules.death_module import DeathModule

        death_time = person.attributes.get(Person.DEATHDATE)
        if death_time is None:
            raise TypeError("Java NullPointerException: Person.DEATHDATE attribute is null")
        if not isinstance(death_time, int):
            raise TypeError("Java ClassCastException: Person.DEATHDATE attribute is not a Long")
        if person.has_multiple_records:
            records = person.records
            if records is None:
                raise TypeError("Java NullPointerException: person.records is null")
            record_list = list(records.values())
        else:
            record = person.record
            if record is None:
                raise TypeError("Java NullPointerException: person.record is null")
            record_list = [record]
        for record in record_list:
            record.encounters[:] = [
                encounter
                for encounter in record.encounters
                if not (
                    encounter.start > death_time
                    and DeathModule.DEATH_CERTIFICATION not in encounter.codes
                )
            ]

    @staticmethod
    def get_output_folder(folder_name: str, person: Person | None) -> Path:
        """Java: Exporter#getOutputFolder(String, Person)."""
        folders = [folder_name]

        if person is not None and Config.get_as_boolean("exporter.subfolders_by_id_substring"):
            person_id = person.attributes.get(Person.ID)
            if not isinstance(person_id, str):
                raise TypeError("Java ClassCastException: Person.ID attribute is not a String")
            folders.append(person_id[0:2])
            folders.append(person_id[0:3])

        base_directory = Config.get("exporter.baseDirectory")
        if base_directory is None:
            raise TypeError("Java NullPointerException: exporter.baseDirectory is not set")
        folder = Path(base_directory, *folders)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def filename(person: Person, tag: str, extension: str) -> str:
        """Java: Exporter#filename(Person, String, String)."""
        if Config.get_as_boolean("exporter.use_uuid_filenames"):
            return str(person.attributes.get(Person.ID)) + tag + "." + extension
        # ensure unique filenames for now
        name = person.attributes.get(Person.NAME)
        return (
            str(name).replace(" ", "_")
            + "_"
            + str(person.attributes.get(Person.ID))
            + tag
            + "."
            + extension
        )


class SupportedFhirVersion(StrEnum):
    """Java: Exporter.SupportedFhirVersion."""

    DSTU2 = "DSTU2"
    STU3 = "STU3"
    R4 = "R4"


class ExporterRuntimeOptions:
    """Java: Exporter.ExporterRuntimeOptions."""

    def __init__(self, init: ExporterRuntimeOptions | None = None) -> None:
        """Java: ExporterRuntimeOptions#ExporterRuntimeOptions.

        Java overloads:
        ()
        (ExporterRuntimeOptions init)
        """
        if init is not None:
            self.years_of_history: int = init.years_of_history
            self.defer_exports: bool = init.defer_exports
            self.terminology_service: bool = init.terminology_service
            self.record_queue: Queue[str] | None = init.record_queue
            self.fhir_version: SupportedFhirVersion | None = init.fhir_version
            self.flexporter_mappings: list[Mapping] | None = init.flexporter_mappings
            return
        self.years_of_history = Config.get_as_integer("exporter.years_of_history", 10)
        self.defer_exports = False
        self.terminology_service = Config.get("generate.terminology_service_url", "") != ""
        self.record_queue = None
        self.fhir_version = None
        self.flexporter_mappings = None

    def enable_queue(self, version: SupportedFhirVersion) -> None:
        """Java: ExporterRuntimeOptions#enableQueue(SupportedFhirVersion)."""
        self.record_queue = Queue(maxsize=1)
        self.fhir_version = version

    def queued_fhir_version(self) -> SupportedFhirVersion | None:
        """Java: ExporterRuntimeOptions#queuedFhirVersion."""
        return self.fhir_version

    def is_queue_enabled(self) -> bool:
        """Java: ExporterRuntimeOptions#isQueueEnabled."""
        return self.record_queue is not None

    def get_next_record(self) -> str | None:
        """Java: ExporterRuntimeOptions#getNextRecord."""
        if self.record_queue is None:
            return None
        return self.record_queue.get()

    def is_record_queue_empty(self) -> bool:
        """Java: ExporterRuntimeOptions#isRecordQueueEmpty."""
        return self.record_queue is None or self.record_queue.qsize() == 0

    def add_flexporter_mapping(self, mapping: Mapping) -> None:
        """Java: ExporterRuntimeOptions#addFlexporterMapping(Mapping)."""
        if self.flexporter_mappings is None:
            self.flexporter_mappings = []
        self.flexporter_mappings.append(mapping)


setattr(Exporter, "SupportedFhirVersion", SupportedFhirVersion)  # noqa: B010
setattr(Exporter, "ExporterRuntimeOptions", ExporterRuntimeOptions)  # noqa: B010
