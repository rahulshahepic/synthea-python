"""Java API skeleton: CSVFileManager.java."""

from __future__ import annotations

from pathlib import Path
from typing import IO, TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:

    class Charset(Protocol):
        """Java boundary type: Charset; external to the mapped Python port."""


class CSVFileManager:
    """Java: CSVFileManager; pending T25."""

    NO_OP: ClassVar[IO[bytes]]  # Java initialization deferred to T25.

    def __init__(self) -> None:
        """Java: CSVFileManager#CSVFileManager.

        Java overloads:
        ()
        """
        self.charset: Charset
        self.append: bool
        self.output_directory: Path
        self.included_files: list[str]
        self.excluded_files: list[str]
        self.filename_map: dict[str, str]
        self.writer_map: dict[str, IO[bytes]]
        self.resource_count_map: dict[str, int]
        self.max_lines_per_file: int
        self.file_number_digits: int
        raise NotImplementedError("Java: CSVFileManager#CSVFileManager — pending T25")

    def initialize_append(self) -> None:
        """Java: CSVFileManager#initializeAppend.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVFileManager#initializeAppend — pending T25")

    def initialize_max_lines_per_file(self) -> None:
        """Java: CSVFileManager#initializeMaxLinesPerFile.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVFileManager#initializeMaxLinesPerFile — pending T25")

    def initialize_file_number_digits(self) -> None:
        """Java: CSVFileManager#initializeFileNumberDigits.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVFileManager#initializeFileNumberDigits — pending T25")

    def initialize_output_directory(self) -> None:
        """Java: CSVFileManager#initializeOutputDirectory.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVFileManager#initializeOutputDirectory — pending T25")

    def multiple_files_per_resource(self) -> bool:
        """Java: CSVFileManager#multipleFilesPerResource.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVFileManager#multipleFilesPerResource — pending T25")

    def filename(self, resource_key: str, file_number: int | None = None) -> str:
        """Java: CSVFileManager#filename.

        Java overloads:
        (String resourceKey)
        (String resourceKey, int fileNumber)
        """
        raise NotImplementedError("Java: CSVFileManager#filename — pending T25")

    def initialize_included_and_excluded_files(self) -> None:
        """Java: CSVFileManager#initializeIncludedAndExcludedFiles.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: CSVFileManager#initializeIncludedAndExcludedFiles — pending T25"
        )

    @staticmethod
    def prop_string_to_list(file_list_string: str) -> list[str]:
        """Java: CSVFileManager#propStringToList.

        Java overloads:
        (String fileListString)
        """
        raise NotImplementedError("Java: CSVFileManager#propStringToList — pending T25")

    def increment_resource_count(self, resource_key: str) -> int:
        """Java: CSVFileManager#incrementResourceCount.

        Java overloads:
        (String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#incrementResourceCount — pending T25")

    def resource_is_excluded(self, resource_key: str) -> bool:
        """Java: CSVFileManager#resourceIsExcluded.

        Java overloads:
        (String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#resourceIsExcluded — pending T25")

    def initialize_resource_writer(
        self, resource_key: str, resource_count: int | None = None
    ) -> IO[bytes]:
        """Java: CSVFileManager#initializeResourceWriter.

        Java overloads:
        (String resourceKey)
        (String resourceKey, int resourceCount)
        """
        raise NotImplementedError("Java: CSVFileManager#initializeResourceWriter — pending T25")

    def get_resource_count(self, resource_key: str) -> int:
        """Java: CSVFileManager#getResourceCount.

        Java overloads:
        (String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#getResourceCount — pending T25")

    def get_writer(self, resource_key: str) -> IO[bytes]:
        """Java: CSVFileManager#getWriter.

        Java overloads:
        (String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#getWriter — pending T25")

    def get_writer_for_multiple_files(self, resource_key: str) -> IO[bytes]:
        """Java: CSVFileManager#getWriterForMultipleFiles.

        Java overloads:
        (String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#getWriterForMultipleFiles — pending T25")

    def flush_writer(self, resource_key: str) -> None:
        """Java: CSVFileManager#flushWriter.

        Java overloads:
        (String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#flushWriter — pending T25")

    def write_resource_line(self, resource_line: str, resource_key: str) -> None:
        """Java: CSVFileManager#writeResourceLine.

        Java overloads:
        (String resourceLine, String resourceKey)
        """
        raise NotImplementedError("Java: CSVFileManager#writeResourceLine — pending T25")
