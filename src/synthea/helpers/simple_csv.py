"""SimpleCSV port.

Java: org.mitre.synthea.helpers.SimpleCSV — Jackson CSV 2.13.4
(``CsvSchema.emptySchema().withHeader()``, ``readerFor(LinkedHashMap)``)
behaviour, reproduced from the Java reference's observed behaviour:

* the first row is the header; header names are trimmed (Java
  ``String.trim``) and trailing empty header names are dropped — a header
  with no remaining names is a ``CsvReadException`` ("Empty header line");
* rows with fewer fields than the header simply lack the missing keys;
  rows with more fields raise ``CsvReadException`` ("Too many entries"),
  except that extra fields whose raw token is empty, whitespace-only or a
  quoted empty string are silently dropped (Jackson is schema-aware here);
* quoted fields keep their content verbatim (a CRLF pair inside quotes
  stays a CRLF pair); after a closing quote only spaces, tabs, the
  separator, end-of-line or end-of-input may follow;
* ``unparse`` (default schema) quotes a field when any of its characters
  has code <= 0x2C (comma) or is a backslash — Jackson's quoting rule —
  doubling internal quotes; with an explicit separator the quote character
  is disabled and nothing is ever quoted.
"""

from __future__ import annotations

import re
from collections.abc import Iterator


class CsvReadException(Exception):  # noqa: N818 - Java exception name kept for parity error reporting
    """Java: com.fasterxml.jackson.dataformat.csv.CsvReadException."""


class CsvWriteException(Exception):  # noqa: N818 - Java exception name kept for parity error reporting
    """Java: com.fasterxml.jackson.dataformat.csv.CsvWriteException."""


class JsonParseException(Exception):  # noqa: N818 - Java exception name kept for parity error reporting
    """Java: com.fasterxml.jackson.core.JsonParseException."""


class RuntimeJsonMappingException(Exception):  # noqa: N818 - Java exception name kept for parity error reporting
    """Java: com.fasterxml.jackson.databind.RuntimeJsonMappingException."""


class RuntimeException(RuntimeError):  # noqa: N818 - Java exception name kept for parity error reporting
    """Java: java.lang.RuntimeException (as raised by MappingIterator)."""


_QUOTED_FIELD_RE = re.compile(r'"(?:[^"]|"")*"[ \t]*')
_UNQUOTED_FIELD_RES: dict[str, re.Pattern[str]] = {}


def _unquoted_field_re(separator: str) -> re.Pattern[str]:
    pattern = _UNQUOTED_FIELD_RES.get(separator)
    if pattern is None:
        pattern = re.compile("[^" + re.escape(separator) + "\r\n]*")
        _UNQUOTED_FIELD_RES[separator] = pattern
    return pattern


def _trim_java(name: str) -> str:
    """Java: String#trim — strip leading/trailing chars <= U+0020."""
    lo, hi = 0, len(name)
    while lo < hi and ord(name[lo]) <= 0x20:
        lo += 1
    while hi > lo and ord(name[hi - 1]) <= 0x20:
        hi -= 1
    return name[lo:hi]


def _tokenize(csv_data: str, separator: str) -> list[list[tuple[str, str]]]:
    """Split CSV text into rows of (value, raw-token) field pairs."""
    unquoted = _unquoted_field_re(separator)
    rows: list[list[tuple[str, str]]] = []
    pos = 0
    end = len(csv_data)
    while pos < end:
        fields: list[tuple[str, str]] = []
        while True:
            if pos < end and csv_data[pos] == '"':
                match = _QUOTED_FIELD_RE.match(csv_data, pos)
                if match is None:
                    raise JsonParseException("Missing closing quote for value")
                raw = match.group(0)
                core = raw.rstrip(" \t")
                inner = core[1:-1].replace('""', '"')
                fields.append((inner, raw))
                pos = match.end()
            else:
                match = unquoted.match(csv_data, pos)
                assert match is not None  # the pattern always matches, possibly empty
                raw = match.group(0)
                fields.append((raw, raw))
                pos = match.end()
            if pos >= end:
                break
            ch = csv_data[pos]
            if ch == separator:
                pos += 1
                continue
            if ch == "\r":
                pos += 1
                if pos < end and csv_data[pos] == "\n":
                    pos += 1
                break
            if ch == "\n":
                pos += 1
                break
            raise JsonParseException(
                f"Unexpected character ({ch!r}): Expected column separator "
                f"character ({separator!r}) or end-of-line"
            )
        rows.append(fields)
    return rows


def _parse_rows(csv_data: str, separator: str) -> list[dict[str, str]]:
    """Shared body of SimpleCSV#parse and SimpleCSV#parseLineByLine."""
    token_rows = _tokenize(csv_data, separator)
    header: list[str] | None = None
    parsed: list[dict[str, str]] = []
    for fields in token_rows:
        if header is None:
            names = [_trim_java(value) for value, _raw in fields]
            while names and names[-1] == "":
                names.pop()
            if not names:
                raise CsvReadException("Empty header line: can not bind data")
            header = names
            continue
        values = [value for value, _raw in fields]
        if len(values) > len(header):
            extras = fields[len(header) :]
            droppable = all(raw.strip(" \t") in ("", '""') for _value, raw in extras)
            if not droppable:
                value = values[len(header)]
                raise CsvReadException(
                    f"Too many entries: expected at most {len(header)} "
                    f'(value #{len(header)} ({len(value)} chars) "{value}")'
                )
            values = values[: len(header)]
        row: dict[str, str] = {}
        for name, value in zip(header, values, strict=False):
            row[name] = value
        parsed.append(row)
    if header is None:
        raise CsvReadException("Empty header line: can not bind data")
    return parsed


def _needs_quoting(value: str) -> bool:
    """Jackson CsvGenerator quoting rule for the default schema."""
    return any(ord(ch) <= 0x2C or ch == "\\" for ch in value)


def _quote(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


class SimpleCSV:
    """Java: org.mitre.synthea.helpers.SimpleCSV."""

    def __init__(self) -> None:
        """Java: SimpleCSV#SimpleCSV.

        Java overloads:
        ()
        """

    @staticmethod
    def parse(csv_data: str, field_separator: str | None = None) -> list[dict[str, str]]:
        """Java: SimpleCSV#parse.

        Java overloads:
        (String csvData)
        (String csvData, char fieldSeparator)
        """
        return _parse_rows(csv_data, "," if field_separator is None else field_separator)

    @staticmethod
    def parse_line_by_line(csv_data: str) -> Iterator[dict[str, str]]:
        """Java: SimpleCSV#parseLineByLine.

        Java overloads:
        (String csvData)

        Java returns a MappingIterator; iteration wraps mapping failures
        in RuntimeJsonMappingException and parse failures in a plain
        RuntimeException, while the empty-header CsvReadException (raised
        before iteration starts) propagates unchanged. This generator
        defers all errors to iteration and mirrors those wrappings.
        """
        try:
            rows = _parse_rows(csv_data, ",")
        except JsonParseException as exc:
            raise RuntimeException(str(exc)) from exc
        except CsvReadException as exc:
            if str(exc).startswith("Too many entries"):
                raise RuntimeJsonMappingException(str(exc)) from exc
            raise
        yield from rows

    @staticmethod
    def unparse(data: list[dict[str, str]], separator: str | None = None) -> str:
        """Java: SimpleCSV#unparse.

        Java overloads:
        (List data)
        (List data, char separator) — quote character disabled: no quoting

        Java: data.get(0) on an empty list throws IndexOutOfBoundsException,
        mirrored here by indexing the list directly.
        """
        sep = "," if separator is None else separator
        columns = list(data[0].keys())
        lines: list[str] = []
        if separator is None:
            lines.append(
                sep.join(_quote(name) if _needs_quoting(name) else name for name in columns)
            )
        else:
            lines.append(sep.join(columns))
        for row in data:
            extra = [key for key in row if key not in columns]
            if extra:
                raise CsvWriteException(
                    f"Unrecognized column '{extra[0]}': known columns: {columns}"
                )
            cells: list[str] = []
            for name in columns:
                value = row.get(name)
                cell = "" if value is None else value
                if separator is None and _needs_quoting(cell):
                    cell = _quote(cell)
                cells.append(cell)
            lines.append(sep.join(cells))
        return "".join(line + "\n" for line in lines)

    @staticmethod
    def is_valid(csv_data: str, separator: str | None = None) -> bool:
        """Java: SimpleCSV#isValid.

        Java overloads:
        (String csvData)
        (String csvData, char separator)

        Java bug, reproduced: the separator argument is ignored and the
        commas (',') on every line are counted, whatever the separator.
        Java String.split("\\n") drops trailing empty strings; a string
        with no newline at all splits to a single element (itself), so the
        empty string is "valid" while a string of only newlines is not.
        """
        if "\n" not in csv_data:
            lines = [csv_data]
        else:
            lines = csv_data.split("\n")
            while lines and lines[-1] == "":
                lines.pop()
        counts = {line.count(",") for line in lines}
        return len(counts) == 1
