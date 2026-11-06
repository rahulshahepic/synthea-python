"""Java: org.mitre.synthea.export.CSVFileManager."""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import BinaryIO, ClassVar, Protocol

from synthea.export.csv_constants import CSVConstants
from synthea.export.export_helper import ExportHelper
from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV


class _Writer(Protocol):
    """Java boundary type: java.io.OutputStreamWriter (the surface CSVFileManager uses)."""

    def write(self, text: str) -> int:
        """Java: OutputStreamWriter#write(String)."""
        ...

    def flush(self) -> None:
        """Java: OutputStreamWriter#flush."""
        ...


class _FileWriter:
    """An OutputStreamWriter over a FileOutputStream: text in, charset bytes out."""

    def __init__(self, stream: BinaryIO, charset: str) -> None:
        """Java: OutputStreamWriter#OutputStreamWriter(OutputStream, Charset)."""
        self._stream = stream
        self._charset = charset

    def write(self, text: str) -> int:
        """Java: OutputStreamWriter#write(String)."""
        return self._stream.write(text.encode(self._charset))

    def flush(self) -> None:
        """Java: OutputStreamWriter#flush."""
        self._stream.flush()


class _NoOpWriter:
    """Java: the NO_OP writer over NullOutputStream; discards everything."""

    def write(self, text: str) -> int:
        """Java: OutputStreamWriter#write(String) into NullOutputStream."""
        return len(text)

    def flush(self) -> None:
        """Java: OutputStreamWriter#flush on a null stream (no-op)."""
        pass


def _java_split(text: str, sep: str) -> list[str]:
    """Java: String#split — trailing empty strings are removed."""
    parts = text.split(sep)
    while parts and parts[-1] == "":
        parts.pop()
    return parts if parts else [""] if text == "" else parts


class CSVFileManager:
    """Java: org.mitre.synthea.export.CSVFileManager."""

    NO_OP: ClassVar[_Writer] = _NoOpWriter()

    def __init__(self) -> None:
        """Java: CSVFileManager#CSVFileManager."""
        self.charset: str = Config.get("exporter.encoding", "UTF-8") or "UTF-8"
        self.append: bool
        self.output_directory: Path
        self.included_files: list[str]
        self.excluded_files: list[str]
        self.filename_map: dict[str, str] = {}
        self.writer_map: dict[str, _Writer] = {}
        self.resource_count_map: dict[str, int] = {}
        self.max_lines_per_file: int
        self.file_number_digits: int
        self.initialize_append()
        self.initialize_max_lines_per_file()
        self.initialize_file_number_digits()
        self.initialize_output_directory()
        self.initialize_included_and_excluded_files()

    def initialize_append(self) -> None:
        """Java: CSVFileManager#initializeAppend."""
        self.append = Config.get_as_boolean("exporter.csv.append_mode")

    def initialize_max_lines_per_file(self) -> None:
        """Java: CSVFileManager#initializeMaxLinesPerFile."""
        try:
            self.max_lines_per_file = Config.get_as_integer("exporter.csv.max_lines_per_file", 0)
        except ValueError:
            # if the property is present but not a numeric string
            self.max_lines_per_file = 0

    def initialize_file_number_digits(self) -> None:
        """Java: CSVFileManager#initializeFileNumberDigits."""
        try:
            self.file_number_digits = Config.get_as_integer("exporter.csv.file_number_digits", 1)
        except ValueError:
            # if the property is present but not a numeric string
            self.file_number_digits = 1

    def initialize_output_directory(self) -> None:
        """Java: CSVFileManager#initializeOutputDirectory."""
        # Function-local import: exporter -> csv_exporter -> csv_file_manager
        # would otherwise cycle (PORTING_GUIDE section 4).
        from synthea.export.exporter import Exporter

        output = Exporter.get_output_folder("csv", None)
        output.mkdir(parents=True, exist_ok=True)
        self.output_directory = output

        if Config.get_as_boolean("exporter.csv.folder_per_run"):
            # we want a folder per run, so name it based on the timestamp
            timestamp = ExportHelper.iso8601_timestamp(int(time.time() * 1000))
            subfolder_name = re.sub(r"\W+", "_", timestamp, flags=re.ASCII)
            self.output_directory = self.output_directory / subfolder_name
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def multiple_files_per_resource(self) -> bool:
        """Java: CSVFileManager#multipleFilesPerResource."""
        return self.max_lines_per_file > 0

    def filename(self, resource_key: str, file_number: int | None = None) -> str:
        """Java: CSVFileManager#filename.

        Java overloads:
        (String resourceKey)
        (String resourceKey, int fileNumber)
        """
        if file_number is None:
            return resource_key + ".csv"
        formatted_number = str(file_number)
        if self.file_number_digits > 1:
            formatted_number = f"{file_number:0{self.file_number_digits}d}"
        return resource_key + "-" + formatted_number + ".csv"

    def initialize_included_and_excluded_files(self) -> None:
        """Java: CSVFileManager#initializeIncludedAndExcludedFiles."""
        included_files_str = (Config.get("exporter.csv.included_files", "") or "").strip()
        excluded_files_str = (Config.get("exporter.csv.excluded_files", "") or "").strip()

        self.included_files = []
        self.excluded_files = []

        if included_files_str and excluded_files_str:
            self.included_files = self.prop_string_to_list(included_files_str)
            self.excluded_files = self.prop_string_to_list(excluded_files_str)

            # Check if there is any overlap
            for included_file in self.included_files:
                if included_file in self.excluded_files:
                    print(
                        "ERROR! CSV exporter is set to include and exclude the same file: "
                        + included_file,
                        file=sys.stderr,
                    )
                    raise ValueError(
                        "CSV exporter cannot include and exclude the same file: " + included_file
                    )
        elif included_files_str:
            self.included_files = self.prop_string_to_list(included_files_str)

            if "patients.csv" not in self.included_files:
                print("WARNING! CSV exporter is set to not include patients.csv!", file=sys.stderr)
                print("This is probably not what you want!", file=sys.stderr)
        else:
            self.excluded_files = self.prop_string_to_list(excluded_files_str)

    @staticmethod
    def prop_string_to_list(file_list_string: str) -> list[str]:
        """Java: CSVFileManager#propStringToList(String)."""
        files = _java_split(file_list_string, ",")
        # normalize filenames -- trim, lowercase, add .csv if not included
        normalized = []
        for f in files:
            f = f.strip().lower()
            if not f.endswith(".csv"):
                f = f + ".csv"
            normalized.append(f)
        return normalized

    def increment_resource_count(self, resource_key: str) -> int:
        """Java: CSVFileManager#incrementResourceCount(String)."""
        resource_count = self.resource_count_map.get(resource_key)
        if resource_count is None:
            resource_count = 0
        resource_count += 1
        self.resource_count_map[resource_key] = resource_count
        return resource_count

    def resource_is_excluded(self, resource_key: str) -> bool:
        """Java: CSVFileManager#resourceIsExcluded(String)."""
        base_filename = self.filename(resource_key)
        return (bool(self.included_files) and base_filename not in self.included_files) or (
            base_filename in self.excluded_files
        )

    def initialize_resource_writer(
        self, resource_key: str, resource_count: int | None = None
    ) -> _Writer:
        """Java: CSVFileManager#initializeResourceWriter.

        Java overloads:
        (String resourceKey)
        (String resourceKey, int resourceCount)
        """
        if self.resource_is_excluded(resource_key):
            return CSVFileManager.NO_OP

        if resource_count is None:
            filename = self.filename(resource_key)
            file = self.output_directory / filename
            # file writing may fail if we tell it to append to a file that doesn't already exist
            append_to_this_file = self.append and file.exists()
            stream = open(file, "ab" if append_to_this_file else "wb")  # noqa: SIM115
            writer = _FileWriter(stream, self.charset)
            if not self.append:
                writer.write(CSVConstants.HEADER_LINE_MAP[resource_key])
            return writer

        if self.append and resource_count == 1:
            resource_count = self.get_resource_count(resource_key) + 1
            self.resource_count_map[resource_key] = resource_count

        file_number = (resource_count - 1) // self.max_lines_per_file + 1
        filename = self.filename(resource_key, file_number)
        file = self.output_directory / filename
        append_to_this_file = self.append and file.exists()
        stream = open(file, "ab" if append_to_this_file else "wb")  # noqa: SIM115
        writer = _FileWriter(stream, self.charset)
        if not self.append or resource_count % self.max_lines_per_file == 1:
            writer.write(CSVConstants.HEADER_LINE_MAP[resource_key])
        return writer

    def get_resource_count(self, resource_key: str) -> int:
        """Java: CSVFileManager#getResourceCount(String)."""
        file_number = 1
        current_filename = self.filename(resource_key, file_number)
        file = self.output_directory / current_filename

        if file.exists():
            while True:
                file_number += 1
                current_filename = self.filename(resource_key, file_number)
                file = self.output_directory / current_filename
                if not file.exists():
                    break
            file_number -= 1

        current_filename = self.filename(resource_key, file_number)
        file = self.output_directory / current_filename

        resource_count = (file_number - 1) * self.max_lines_per_file

        if file.exists():
            csv_data = file.read_bytes().decode("utf-8")
            resource_count += len(SimpleCSV.parse(csv_data))

        return resource_count

    def get_writer(self, resource_key: str) -> _Writer | None:
        """Java: CSVFileManager#getWriter(String)."""
        if self.multiple_files_per_resource():
            return self.get_writer_for_multiple_files(resource_key)

        writer = self.writer_map.get(resource_key)
        if writer is None:
            writer = self.initialize_resource_writer(resource_key)
            self.writer_map[resource_key] = writer
        return writer

    def get_writer_for_multiple_files(self, resource_key: str) -> _Writer | None:
        """Java: CSVFileManager#getWriterForMultipleFiles(String)."""
        if self.resource_is_excluded(resource_key):
            return CSVFileManager.NO_OP

        resource_count = self.increment_resource_count(resource_key)
        writer = self.writer_map.get(resource_key)

        if resource_count % self.max_lines_per_file == 1:
            if writer is not None:
                writer.flush()
            writer = self.initialize_resource_writer(resource_key, resource_count)
            self.writer_map[resource_key] = writer

        return writer

    def flush_writer(self, resource_key: str) -> None:
        """Java: CSVFileManager#flushWriter(String)."""
        writer = self.writer_map.get(resource_key)
        if writer is not None:
            writer.flush()

    def write_resource_line(self, resource_line: str, resource_key: str) -> None:
        """Java: CSVFileManager#writeResourceLine(String, String)."""
        writer = self.get_writer(resource_key)
        if writer is None:
            # Java throws NullPointerException here (see porting notes T25).
            raise TypeError("Java NullPointerException: getWriter returned null")
        writer.write(resource_line)
