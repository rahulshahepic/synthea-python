"""Config port.

Java: org.mitre.synthea.helpers.Config — static ``java.util.Properties``
loaded at class-init from the classpath resource ``/synthea.properties``
(the ``InputStream`` overload, ISO-8859-1), with ``load(File)`` reading
through a ``FileReader`` (default charset; UTF-8 in the parity JVM).
"""

from __future__ import annotations

import builtins
import os
import sys
import traceback
from collections.abc import Iterator
from pathlib import Path
from typing import IO, ClassVar

from synthea.javacompat.numbers import parse_boolean, parse_double, parse_int, parse_long
from synthea.resources import resource_path

_HEX_DIGITS = set("0123456789abcdefABCDEF")


def _load_convert(segment: str) -> str:
    """Java: ``java.util.Properties#loadConvert`` escape processing.

    ``\\t``/``\\n``/``\\r``/``\\f`` map to the control characters,
    ``\\uXXXX`` (exactly one ``u``, exactly four hex digits) maps to the
    code point, and any other escaped character stands for itself (the
    backslash is dropped). A malformed ``\\u`` escape — including a
    doubled ``\\uu``, which JDK 21 rejects despite the file-format
    folklore — raises ``ValueError`` where Java throws
    ``IllegalArgumentException``.
    """
    out: list[str] = []
    i = 0
    n = len(segment)
    while i < n:
        c = segment[i]
        i += 1
        if c != "\\":
            out.append(c)
            continue
        if i >= n:
            raise IndexError("escape at end of properties line")
        c = segment[i]
        i += 1
        if c == "u":
            if i + 4 > n or any(ch not in _HEX_DIGITS for ch in segment[i : i + 4]):
                raise ValueError("Malformed \\uxxxx encoding.")
            out.append(chr(int(segment[i : i + 4], 16)))
            i += 4
        elif c == "t":
            out.append("\t")
        elif c == "r":
            out.append("\r")
        elif c == "n":
            out.append("\n")
        elif c == "f":
            out.append("\f")
        else:
            out.append(c)
    return "".join(out)


def _logical_lines(text: str) -> Iterator[str]:
    """Java: ``java.util.Properties`` LineReader.readLine, line by line.

    Skips leading whitespace (space/tab/form-feed) and blank lines, drops
    ``#``/``!`` comment lines, and joins continuation lines: a line ending
    in an odd number of backslashes loses its last backslash and its line
    terminator, and the leading whitespace of the continuation is skipped.
    Line terminators are ``\\n``, ``\\r`` and ``\\r\\n``.
    """
    i = 0
    n = len(text)
    while True:
        buf: list[str] = []
        skip_white_space = True
        is_comment_line = False
        is_new_line = True
        appended_line_begin = False
        preceding_backslash = False
        skip_lf = False
        while True:
            if i >= n:
                if buf and not is_comment_line:
                    # At EOF the JDK returns the line without a trailing
                    # (continuation) backslash: readLine returns len - 1
                    # when precedingBackslash is set.
                    if preceding_backslash:
                        buf.pop()
                    yield "".join(buf)
                return
            c = text[i]
            i += 1
            if skip_lf:
                skip_lf = False
                if c == "\n":
                    continue
            if skip_white_space:
                if c in " \t\f":
                    continue
                if not appended_line_begin and c in "\r\n":
                    continue
                skip_white_space = False
                appended_line_begin = False
            if is_new_line:
                is_new_line = False
                if c in "#!":
                    is_comment_line = True
            if c not in "\r\n":
                buf.append(c)
                preceding_backslash = not preceding_backslash if c == "\\" else False
            else:
                # Reached the end of a physical line.
                if is_comment_line or not buf:
                    is_comment_line = False
                    is_new_line = True
                    skip_white_space = True
                    preceding_backslash = False
                    buf = []
                    continue
                if preceding_backslash:
                    buf.pop()
                    skip_white_space = True
                    appended_line_begin = True
                    preceding_backslash = False
                    if c == "\r":
                        skip_lf = True
                    continue
                yield "".join(buf)
                break


def _parse_properties(text: str) -> dict[str, str]:
    """Java: ``java.util.Properties#load0`` key/value splitting."""
    props: dict[str, str] = {}
    for line in _logical_lines(text):
        limit = len(line)
        key_len = 0
        value_start = limit
        has_sep = False
        preceding_backslash = False
        while key_len < limit:
            c = line[key_len]
            if c in "=:" and not preceding_backslash:
                value_start = key_len + 1
                has_sep = True
                break
            if c in " \t\f" and not preceding_backslash:
                value_start = key_len + 1
                break
            preceding_backslash = not preceding_backslash if c == "\\" else False
            key_len += 1
        while value_start < limit:
            c = line[value_start]
            if c not in " \t\f":
                if not has_sep and c in "=:":
                    has_sep = True
                else:
                    break
            value_start += 1
        key = _load_convert(line[:key_len])
        value = _load_convert(line[value_start:])
        props[key] = value
    return props


class Config:
    """Java: org.mitre.synthea.helpers.Config (abstract, static members only)."""

    properties: ClassVar[dict[str, str]] = {}

    def __init__(self) -> None:
        """Java: Config#Config — the Java class is abstract."""
        raise TypeError("Config is abstract (Java: abstract class Config)")

    @staticmethod
    def load(props_file_or_stream: Path | IO[bytes]) -> None:
        """Java: Config#load.

        Java overloads:
        (File propsFile) — a path: read as bytes and decode UTF-8
            (the parity JVM's FileReader charset).
        (InputStream stream) — a binary stream: decode ISO-8859-1,
            exactly as java.util.Properties.load(InputStream) does.
        """
        if isinstance(props_file_or_stream, str | os.PathLike):
            text = Path(props_file_or_stream).read_bytes().decode("utf-8")
        else:
            data = props_file_or_stream.read()
            if isinstance(data, bytes):
                text = data.decode("iso-8859-1")
            elif isinstance(data, bytearray):
                text = bytes(data).decode("iso-8859-1")
            else:
                text = data
        Config.properties.update(_parse_properties(text))

    @staticmethod
    def get(key: str, default_value: str | None = None) -> str | None:
        """Java: Config#get.

        Java overloads:
        (String key)
        (String key, String defaultValue)
        """
        return Config.properties.get(key, default_value)

    @staticmethod
    def get_as_double(key: str, default_value: float | None = None) -> float:
        """Java: Config#getAsDouble.

        Java overloads:
        (String key) — Double.parseDouble(get(key)); a missing key makes
            Java throw NullPointerException, mirrored here as TypeError.
        (String key, double defaultValue)
        """
        if default_value is not None and key not in Config.properties:
            return default_value
        value = Config.get(key)
        if value is None:
            raise TypeError("Double.parseDouble(null): NullPointerException")
        return parse_double(value)

    @staticmethod
    def get_as_boolean(key: str, default_value: bool | None = None) -> bool:
        """Java: Config#getAsBoolean.

        Java overloads:
        (String key) — Boolean.parseBoolean(null) is false, so a missing
            key yields False rather than raising.
        (String key, boolean defaultValue)
        """
        if default_value is not None and key not in Config.properties:
            return default_value
        value = Config.get(key)
        if value is None:
            return False
        return parse_boolean(value)

    @staticmethod
    def get_as_integer(key: str, default_value: int | None = None) -> int:
        """Java: Config#getAsInteger.

        Java overloads:
        (String key) — Integer.parseInt(get(key)); a missing key makes
            Java throw NumberFormatException, mirrored here as ValueError.
        (String key, int defaultValue)
        """
        if default_value is not None and key not in Config.properties:
            return default_value
        value = Config.get(key)
        if value is None:
            raise ValueError('For input string: "null"')
        return parse_int(value)

    @staticmethod
    def get_as_long(key: str, default_value: int | None = None) -> int:
        """Java: Config#getAsLong.

        Java overloads:
        (String key) — Long.parseLong(get(key)); a missing key makes
            Java throw NumberFormatException, mirrored here as ValueError.
        (String key, long defaultValue)
        """
        if default_value is not None and key not in Config.properties:
            return default_value
        value = Config.get(key)
        if value is None:
            raise ValueError('For input string: "null"')
        return parse_long(value)

    @staticmethod
    def set(key: str, value: str) -> None:
        """Java: Config#set.

        Java overloads:
        (String key, String value)
        """
        Config.properties[key] = value

    @staticmethod
    def all_property_names() -> builtins.set[str]:
        """Java: Config#allPropertyNames — a snapshot set of the keys.

        Java overloads:
        ()
        """
        return set(Config.properties)

    @staticmethod
    def remove(key: str) -> None:
        """Java: Config#remove.

        Java overloads:
        (String key)
        """
        Config.properties.pop(key, None)


# Static initializer (Java: Config's static block): load the default
# /synthea.properties through the InputStream overload (ISO-8859-1 bytes).
# On failure Java prints "Unable to load default properties file" and a
# stack trace to stderr, then continues with whatever was loaded.
try:
    with resource_path("synthea.properties").open("rb") as _stream:
        Config.load(_stream)
except Exception:
    print("Unable to load default properties file", file=sys.stderr)
    traceback.print_exc()
