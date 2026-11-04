"""Java API skeleton for exporter.py.
Java: org.mitre.synthea.export.Exporter.
"""

from __future__ import annotations

from enum import StrEnum


class Exporter:
    """Java: Exporter; pending T25."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Exporter constructor; pending T25."""
        raise NotImplementedError("Java: Exporter — pending T25")

    def load_custom_exporters(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#loadCustomExporters."""
        raise NotImplementedError("Java: loadCustomExporters — pending T25")

    def load_code_mappers(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#loadCodeMappers."""
        raise NotImplementedError("Java: loadCodeMappers — pending T25")

    def get_code_mapper(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#getCodeMapper."""
        raise NotImplementedError("Java: getCodeMapper — pending T25")

    def get_code_mappers(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#getCodeMappers."""
        raise NotImplementedError("Java: getCodeMappers — pending T25")

    def enable_queue(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#enableQueue."""
        raise NotImplementedError("Java: enableQueue — pending T25")

    def queued_fhir_version(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#queuedFhirVersion."""
        raise NotImplementedError("Java: queuedFhirVersion — pending T25")

    def is_queue_enabled(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#isQueueEnabled."""
        raise NotImplementedError("Java: isQueueEnabled — pending T25")

    def get_next_record(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#getNextRecord."""
        raise NotImplementedError("Java: getNextRecord — pending T25")

    def is_record_queue_empty(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#isRecordQueueEmpty."""
        raise NotImplementedError("Java: isRecordQueueEmpty — pending T25")

    def add_flexporter_mapping(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#addFlexporterMapping."""
        raise NotImplementedError("Java: addFlexporterMapping — pending T25")

    def export(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#export."""
        raise NotImplementedError("Java: export — pending T25")

    def export_record(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#exportRecord."""
        raise NotImplementedError("Java: exportRecord — pending T25")

    def write_new_file(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#writeNewFile."""
        raise NotImplementedError("Java: writeNewFile — pending T25")

    def overwrite_file(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#overwriteFile."""
        raise NotImplementedError("Java: overwriteFile — pending T25")

    def append_to_file(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#appendToFile."""
        raise NotImplementedError("Java: appendToFile — pending T25")

    def close_open_files(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#closeOpenFiles."""
        raise NotImplementedError("Java: closeOpenFiles — pending T25")

    def run_post_completion_exports(self, *args: object, **kwargs: object) -> object:
        """Java: Exporter#runPostCompletionExports."""
        raise NotImplementedError("Java: runPostCompletionExports — pending T25")


class SupportedFhirVersion(StrEnum):
    """Java: SupportedFhirVersion; pending T25."""
    DSTU2 = "DSTU2"
    STU3 = "STU3"
    R4 = "R4"
    L = "L"


class ExporterRuntimeOptions:
    """Java: ExporterRuntimeOptions; pending T25."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ExporterRuntimeOptions constructor; pending T25."""
        raise NotImplementedError("Java: ExporterRuntimeOptions — pending T25")

