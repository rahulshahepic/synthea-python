"""Java API skeleton for csv_file_manager.py.
Java: org.mitre.synthea.export.CSVFileManager.
"""

from __future__ import annotations


class CSVFileManager:
    """Java: CSVFileManager; pending T25."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: CSVFileManager constructor; pending T25."""
        self.charset: object | None = None
        self.append: bool = False
        self.outputDirectory: object | None = None
        self.includedFiles: list[object] = []
        self.excludedFiles: list[object] = []
        self.filenameMap: dict[object, object] = {}
        self.writerMap: dict[object, object] = {}
        self.resourceCountMap: dict[object, object] = {}
        self.maxLinesPerFile: int = 0
        self.fileNumberDigits: int = 0
        raise NotImplementedError("Java: CSVFileManager — pending T25")

    def initialize_append(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#initializeAppend."""
        raise NotImplementedError("Java: initializeAppend — pending T25")

    def initialize_max_lines_per_file(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#initializeMaxLinesPerFile."""
        raise NotImplementedError("Java: initializeMaxLinesPerFile — pending T25")

    def initialize_file_number_digits(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#initializeFileNumberDigits."""
        raise NotImplementedError("Java: initializeFileNumberDigits — pending T25")

    def initialize_output_directory(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#initializeOutputDirectory."""
        raise NotImplementedError("Java: initializeOutputDirectory — pending T25")

    def multiple_files_per_resource(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#multipleFilesPerResource."""
        raise NotImplementedError("Java: multipleFilesPerResource — pending T25")

    def filename(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#filename."""
        raise NotImplementedError("Java: filename — pending T25")

    def initialize_included_and_excluded_files(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#initializeIncludedAndExcludedFiles."""
        raise NotImplementedError("Java: initializeIncludedAndExcludedFiles — pending T25")

    def prop_string_to_list(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#propStringToList."""
        raise NotImplementedError("Java: propStringToList — pending T25")

    def increment_resource_count(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#incrementResourceCount."""
        raise NotImplementedError("Java: incrementResourceCount — pending T25")

    def resource_is_excluded(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#resourceIsExcluded."""
        raise NotImplementedError("Java: resourceIsExcluded — pending T25")

    def initialize_resource_writer(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#initializeResourceWriter."""
        raise NotImplementedError("Java: initializeResourceWriter — pending T25")

    def get_resource_count(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#getResourceCount."""
        raise NotImplementedError("Java: getResourceCount — pending T25")

    def get_writer(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#getWriter."""
        raise NotImplementedError("Java: getWriter — pending T25")

    def get_writer_for_multiple_files(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#getWriterForMultipleFiles."""
        raise NotImplementedError("Java: getWriterForMultipleFiles — pending T25")

    def flush_writer(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#flushWriter."""
        raise NotImplementedError("Java: flushWriter — pending T25")

    def write_resource_line(self, *args: object, **kwargs: object) -> object:
        """Java: CSVFileManager#writeResourceLine."""
        raise NotImplementedError("Java: writeResourceLine — pending T25")
