"""Ported from java/src/test/java/org/mitre/synthea/helpers/SimpleCSVTest.java,
plus coverage for the Jackson quirks the parity probe pins down.
"""

from __future__ import annotations

import pytest

from synthea.helpers.simple_csv import (
    CsvReadException,
    CsvWriteException,
    JsonParseException,
    RuntimeException,
    RuntimeJsonMappingException,
    SimpleCSV,
)

TEST_CSV = "ID,NAME,AGE\n0,Alice,30\n1,Bob,25\n2,Charles,50\n"
TEST_CSV_SEP = "ID|NAME|AGE\n0|Alice|30\n1|Bob|25\n2|Charles|50\n"


def test_simple_csv() -> None:
    """Java: SimpleCSVTest#testSimpleCSV."""
    data = SimpleCSV.parse(TEST_CSV)
    assert len(data) == 3
    assert "ID" in data[0]
    assert "NAME" in data[0]
    assert "AGE" in data[0]
    csv = SimpleCSV.unparse(data)
    assert csv == TEST_CSV
    assert SimpleCSV.is_valid(csv)


def test_simple_csv_with_alt_sep() -> None:
    """Java: SimpleCSVTest#testSimpleCSVWithAltSep."""
    data = SimpleCSV.parse(TEST_CSV_SEP, "|")
    assert len(data) == 3
    assert "ID" in data[0]
    assert "NAME" in data[0]
    assert "AGE" in data[0]
    csv = SimpleCSV.unparse(data, "|")
    assert csv == TEST_CSV_SEP
    assert SimpleCSV.is_valid(csv, "|")


def test_parse_line_by_line() -> None:
    """Java: SimpleCSV#parseLineByLine parses with the default separator."""
    assert list(SimpleCSV.parse_line_by_line(TEST_CSV)) == SimpleCSV.parse(TEST_CSV)
    # The separator is not a parameter: pipes are ordinary characters here.
    rows = list(SimpleCSV.parse_line_by_line(TEST_CSV_SEP))
    assert rows[0] == {"ID|NAME|AGE": "0|Alice|30"}


def test_is_valid_comma_bug() -> None:
    """Java bug: isValid counts ',' characters whatever the separator is."""
    assert SimpleCSV.is_valid("a|b|c\n1|2|3\n", "|") is True  # zero commas per line
    assert SimpleCSV.is_valid("a,b\n1,2,3\n") is False
    assert SimpleCSV.is_valid("") is True  # "".split("\n") is [""] in Java
    assert SimpleCSV.is_valid("\n") is False  # "\n".split("\n") is [] in Java
    assert SimpleCSV.is_valid("\n\n") is False


def test_blank_line_is_a_row_with_one_empty_field() -> None:
    """Jackson: a blank line between rows is not skipped."""
    rows = SimpleCSV.parse("A,B\n1,2\n\n3,4\n")
    assert rows == [{"A": "1", "B": "2"}, {"A": ""}, {"A": "3", "B": "4"}]


def test_too_many_columns_and_line_by_line_wrapping() -> None:
    """Jackson: extra non-empty fields fail; iteration wraps the failure."""
    with pytest.raises(CsvReadException):
        SimpleCSV.parse("A,B\n1,2,3\n")
    with pytest.raises(RuntimeJsonMappingException):
        list(SimpleCSV.parse_line_by_line("A,B\n1,2,3\n"))
    with pytest.raises(JsonParseException):
        SimpleCSV.parse('A,B\n"x,y\n')
    with pytest.raises(RuntimeException):
        list(SimpleCSV.parse_line_by_line('A,B\n"x,y\n'))


def test_empty_header() -> None:
    """Jackson: no usable header names is a CsvReadException in both APIs."""
    with pytest.raises(CsvReadException):
        SimpleCSV.parse("")
    with pytest.raises(CsvReadException):
        SimpleCSV.parse(",\n1,2\n")
    with pytest.raises(CsvReadException):
        list(SimpleCSV.parse_line_by_line(""))


def test_unparse_quoting_and_errors() -> None:
    """Jackson writer: quoting rule, disabled quoting, and write failures."""
    rows = [{"A": "x,y", "B": "a b", "C": "plain", "D": 'he"llo'}]
    assert SimpleCSV.unparse(rows) == 'A,B,C,D\n"x,y","a b",plain,"he""llo"\n'
    assert SimpleCSV.unparse(rows, "|") == 'A|B|C|D\nx,y|a b|plain|he"llo\n'
    with pytest.raises(IndexError):
        SimpleCSV.unparse([])
    with pytest.raises(CsvWriteException):
        SimpleCSV.unparse([{"A": "1"}, {"A": "2", "B": "3"}])
