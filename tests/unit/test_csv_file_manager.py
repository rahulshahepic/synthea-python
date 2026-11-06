"""Unit tests for CSVFileManager, from the Java semantics in
java/src/main/java/org/mitre/synthea/export/CSVFileManager.java.

There is no upstream CSVFileManagerTest; CSVExporterTest (T26) exercises this
class indirectly. File contents are compared exactly, including the append
mode header quirks.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import pytest

from synthea.export.csv_constants import CSVConstants
from synthea.export.csv_file_manager import CSVFileManager
from synthea.helpers.config import Config

PATIENT_HEADER = CSVConstants.PATIENT_HEADER_LINE
CONDITION_HEADER = CSVConstants.CONDITION_HEADER_LINE


@pytest.fixture(autouse=True)
def _config(tmp_path: Path) -> Iterator[Path]:
    saved = dict(Config.properties)
    Config.properties.clear()
    Config.set("exporter.baseDirectory", str(tmp_path))
    yield tmp_path
    Config.properties.clear()
    Config.properties.update(saved)


def _manager(tmp_path: Path) -> CSVFileManager:
    return CSVFileManager()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_single_file_writes_header_then_lines(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.write_resource_line("line-one\n", CSVConstants.PATIENT_KEY)
    manager.write_resource_line("line-two\n", CSVConstants.PATIENT_KEY)
    manager.flush_writer(CSVConstants.PATIENT_KEY)
    out = tmp_path / "csv" / "patients.csv"
    assert _read(out) == PATIENT_HEADER + "line-one\n" + "line-two\n"


def test_excluded_file_is_noop(tmp_path: Path) -> None:
    Config.set("exporter.csv.excluded_files", "conditions.csv")
    manager = _manager(tmp_path)
    manager.write_resource_line("nope\n", CSVConstants.CONDITION_KEY)
    assert manager.get_writer(CSVConstants.CONDITION_KEY) is CSVFileManager.NO_OP
    assert not (tmp_path / "csv" / "conditions.csv").exists()
    # other files still work
    manager.write_resource_line("ok\n", CSVConstants.PATIENT_KEY)
    manager.flush_writer(CSVConstants.PATIENT_KEY)
    assert _read(tmp_path / "csv" / "patients.csv") == PATIENT_HEADER + "ok\n"


def test_included_files_excludes_everything_else(tmp_path: Path) -> None:
    Config.set("exporter.csv.included_files", "patients.csv")
    manager = _manager(tmp_path)
    assert manager.resource_is_excluded(CSVConstants.CONDITION_KEY)
    assert not manager.resource_is_excluded(CSVConstants.PATIENT_KEY)


def test_include_exclude_overlap_raises(tmp_path: Path) -> None:
    Config.set("exporter.csv.included_files", "patients.csv,conditions.csv")
    Config.set("exporter.csv.excluded_files", "conditions.csv")
    with pytest.raises(ValueError, match="cannot include and exclude the same file"):
        _manager(tmp_path)


def test_empty_include_exclude_quirk(tmp_path: Path) -> None:
    # Java: with neither property set, the else-branch still runs
    # propStringToList(""), and "".split(",") is [""], which normalizes to ".csv".
    manager = _manager(tmp_path)
    assert manager.included_files == []
    assert manager.excluded_files == [".csv"]
    assert not manager.resource_is_excluded(CSVConstants.PATIENT_KEY)


def test_prop_string_to_list_normalization() -> None:
    assert CSVFileManager.prop_string_to_list("patients.csv,conditions , Procedures") == [
        "patients.csv",
        "conditions.csv",
        "procedures.csv",
    ]
    # Java String.split drops trailing empty strings.
    assert CSVFileManager.prop_string_to_list("patients.csv,") == ["patients.csv"]


def test_append_mode_appends_without_new_header(tmp_path: Path) -> None:
    first = _manager(tmp_path)
    first.write_resource_line("one\n", CSVConstants.PATIENT_KEY)
    first.flush_writer(CSVConstants.PATIENT_KEY)

    Config.set("exporter.csv.append_mode", "true")
    second = _manager(tmp_path)
    second.write_resource_line("two\n", CSVConstants.PATIENT_KEY)
    second.flush_writer(CSVConstants.PATIENT_KEY)
    assert _read(tmp_path / "csv" / "patients.csv") == PATIENT_HEADER + "one\n" + "two\n"


def test_append_mode_fresh_file_gets_no_header(tmp_path: Path) -> None:
    # Java quirk: the header is written only when append mode is off.
    Config.set("exporter.csv.append_mode", "true")
    manager = _manager(tmp_path)
    manager.write_resource_line("bare\n", CSVConstants.PATIENT_KEY)
    manager.flush_writer(CSVConstants.PATIENT_KEY)
    assert _read(tmp_path / "csv" / "patients.csv") == "bare\n"


def test_max_lines_per_file_splits(tmp_path: Path) -> None:
    Config.set("exporter.csv.max_lines_per_file", "2")
    manager = _manager(tmp_path)
    for i in range(5):
        manager.write_resource_line(f"row-{i}\n", CSVConstants.PATIENT_KEY)
    manager.flush_writer(CSVConstants.PATIENT_KEY)
    csv_dir = tmp_path / "csv"
    assert _read(csv_dir / "patients-1.csv") == PATIENT_HEADER + "row-0\nrow-1\n"
    assert _read(csv_dir / "patients-2.csv") == PATIENT_HEADER + "row-2\nrow-3\n"
    assert _read(csv_dir / "patients-3.csv") == PATIENT_HEADER + "row-4\n"


def test_file_number_digits(tmp_path: Path) -> None:
    Config.set("exporter.csv.max_lines_per_file", "1")
    Config.set("exporter.csv.file_number_digits", "3")
    manager = _manager(tmp_path)
    # filename() is the observable surface here; max_lines=1 makes getWriter
    # return Java's null (see porting notes), so don't write through it.
    assert manager.filename(CSVConstants.PATIENT_KEY, 7) == "patients-007.csv"
    assert manager.filename(CSVConstants.PATIENT_KEY) == "patients.csv"


def test_non_numeric_max_lines_falls_back_to_zero(tmp_path: Path) -> None:
    Config.set("exporter.csv.max_lines_per_file", "lots")
    manager = _manager(tmp_path)
    assert manager.max_lines_per_file == 0
    assert not manager.multiple_files_per_resource()


def test_get_resource_count_counts_existing_rows(tmp_path: Path) -> None:
    Config.set("exporter.csv.max_lines_per_file", "10")
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir(parents=True)
    (csv_dir / "patients-1.csv").write_text(PATIENT_HEADER + "a,b\n" + "c,d\n", encoding="utf-8")
    manager = _manager(tmp_path)
    # (fileNumber - 1) * maxLines + data rows in the last file = 0 + 2.
    assert manager.get_resource_count(CSVConstants.PATIENT_KEY) == 2


def test_folder_per_run(tmp_path: Path) -> None:
    Config.set("exporter.csv.folder_per_run", "true")
    manager = _manager(tmp_path)
    name = manager.output_directory.name
    assert re.fullmatch(r"\d{4}_\d{2}_\d{2}T\d{2}_\d{2}_\d{2}Z", name)
    assert manager.output_directory.is_dir()
