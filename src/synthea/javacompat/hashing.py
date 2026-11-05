"""Java 21 boxed hashes and UTF-16 string comparison.

Java: java.lang.{String,Integer,Long,Double,Boolean,Character}, java.util.{Objects,Arrays,List}.
Python's salted hashes, code-point ordering and numeric equality are not Java semantics.
"""

from __future__ import annotations

import math
import struct
from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar, Literal, Protocol, runtime_checkable

KeyType = Literal["string", "integer", "long", "double", "boolean", "character", "object"]


@runtime_checkable
class JavaHashable(Protocol):
    """Java: Object#hashCode; an explicit deterministic interoperability boundary."""

    def java_hash_code(self) -> int:
        """Java: Object#hashCode."""
        ...


def _int32(value: int) -> int:
    """Java: narrowing an integral value to signed int, JLS 5.1.3."""
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value >= 0x80000000 else value


def utf16_units(value: str) -> tuple[int, ...]:
    """Java: String#charAt, including unpaired surrogates and supplementary characters."""
    raw = value.encode("utf-16-be", "surrogatepass")
    return tuple(int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2))


def string_hash_code(value: str) -> int:
    """Java: String#hashCode; 31-fold hash over UTF-16 code units, with int32 overflow."""
    result = 0
    for unit in utf16_units(value):
        result = (31 * result + unit) & 0xFFFFFFFF
    return _int32(result)


def integer_hash_code(value: int) -> int:
    """Java: Integer#hashCode(int)."""
    return _int32(value)


def long_hash_code(value: int) -> int:
    """Java: Long#hashCode(long), folding the unsigned high half into the low half."""
    value &= 0xFFFFFFFFFFFFFFFF
    return _int32(value ^ (value >> 32))


def double_to_long_bits(value: float) -> int:
    """Java: Double#doubleToLongBits; all NaNs canonicalize, signed zeros remain distinct."""
    if math.isnan(value):
        return 0x7FF8000000000000
    return int.from_bytes(struct.pack(">d", value), "big")


def double_hash_code(value: float) -> int:
    """Java: Double#hashCode(double)."""
    return long_hash_code(double_to_long_bits(value))


def boolean_hash_code(value: bool) -> int:
    """Java: Boolean#hashCode(boolean)."""
    return 1231 if value else 1237


def character_hash_code(value: str | int) -> int:
    """Java: Character#hashCode(char); a Character contains exactly one UTF-16 unit."""
    if isinstance(value, str):
        units = utf16_units(value)
        if len(units) != 1:
            raise ValueError("Java Character requires exactly one UTF-16 code unit")
        return units[0]
    if not 0 <= value <= 0xFFFF:
        raise ValueError("Java Character is an unsigned 16-bit code unit")
    return value


def java_hash_code(value: object, key_type: KeyType | None = None) -> int:
    """Java: Objects#hashCode; explicit key_type distinguishes Integer from Long keys."""
    if value is None:
        return 0
    if key_type == "character":
        if not isinstance(value, str | int) or isinstance(value, bool):
            raise TypeError("Character key must be a string or unsigned 16-bit integer")
        return character_hash_code(value)
    if isinstance(value, str) and key_type in {None, "string", "object"}:
        return string_hash_code(value)
    if isinstance(value, bool) and key_type in {None, "boolean", "object"}:
        return boolean_hash_code(value)
    if isinstance(value, int) and not isinstance(value, bool):
        if key_type == "long":
            return long_hash_code(value)
        if key_type in {None, "integer", "object"}:
            return integer_hash_code(value)
    if isinstance(value, float) and key_type in {None, "double", "object"}:
        return double_hash_code(value)
    if isinstance(value, JavaHashable):
        return _int32(value.java_hash_code())
    raise TypeError(f"No Java hashCode mapping for {type(value).__name__} as {key_type!r}")


def arrays_hash_code(values: Iterable[object] | None, element_type: KeyType | None = None) -> int:
    """Java: Arrays#hashCode(Object[]), plus explicit supported primitive element types."""
    if values is None:
        return 0
    result = 1
    for value in values:
        result = _int32(31 * result + java_hash_code(value, element_type))
    return result


def list_hash_code(values: Iterable[object], element_type: KeyType | None = None) -> int:
    """Java: List#hashCode; identical 31-fold rule to Arrays#hashCode(Object[])."""
    return arrays_hash_code(values, element_type)


def objects_hash(*values: object) -> int:
    """Java: Objects#hash(Object...); one argument is still an array hash, not its own hash."""
    return arrays_hash_code(values)


def java_sort_key(value: str) -> tuple[int, ...]:
    """Java: String#compareTo ordering for TreeMap/TreeSet of strings."""
    return utf16_units(value)


def string_compare_to(left: str, right: str) -> int:
    """Java: String#compareTo; return the actual first code-unit difference, not its sign."""
    a, b = utf16_units(left), utf16_units(right)
    for x, y in zip(a, b, strict=False):
        if x != y:
            return x - y
    return len(a) - len(b)


def _simple_upper(cp: int) -> int:
    """Java: Character#toUpperCase(int), Unicode 15 simple (non-expanding) mapping."""
    char = chr(cp)
    upper = char.upper()
    if len(upper) == 1:
        return ord(upper)
    title = char.title()
    return ord(title) if len(title) == 1 else cp


def _simple_lower(cp: int) -> int:
    """Java: Character#toLowerCase(int), Unicode 15 simple (non-expanding) mapping."""
    if cp == 0x130:
        return 0x69
    lower = chr(cp).lower()
    return ord(lower) if len(lower) == 1 else cp


def _compare_code_point_ci(left: int, right: int) -> int:
    """Java: StringUTF16#compareCodePointCI."""
    left, right = _simple_upper(left), _simple_upper(right)
    if left == right:
        return 0
    return _simple_lower(left) - _simple_lower(right)


def _code_point_including(units: tuple[int, ...], index: int) -> tuple[int, bool]:
    """Java: StringUTF16#codePointIncluding; indicate whether the following unit was used."""
    cp = units[index]
    if 0xD800 <= cp <= 0xDBFF and index + 1 < len(units):
        low = units[index + 1]
        if 0xDC00 <= low <= 0xDFFF:
            return 0x10000 + ((cp - 0xD800) << 10) + low - 0xDC00, True
    if 0xDC00 <= cp <= 0xDFFF and index > 0:
        high = units[index - 1]
        if 0xD800 <= high <= 0xDBFF:
            return 0x10000 + ((high - 0xD800) << 10) + cp - 0xDC00, False
    return cp, False


def string_compare_to_ignore_case(left: str, right: str) -> int:
    """Java: String#compareToIgnoreCase / StringUTF16#compareToCIImpl (not casefold)."""
    a, b = utf16_units(left), utf16_units(right)
    if all(unit <= 0xFF for unit in a) or all(unit <= 0xFF for unit in b):
        for x, y in zip(a, b, strict=False):
            difference = _compare_code_point_ci(x, y)
            if difference:
                return difference
        return len(a) - len(b)
    i = j = 0
    while i < len(a) and j < len(b):
        x, y = a[i], b[j]
        if x != y and _compare_code_point_ci(x, y) != 0:
            x, advance_a = _code_point_including(a, i)
            y, advance_b = _code_point_including(b, j)
            i += advance_a
            j += advance_b
            difference = _compare_code_point_ci(x, y)
            if difference:
                return difference
        i += 1
        j += 1
    return len(a) - len(b)


@dataclass(frozen=True, slots=True)
class JavaLong:
    """Java: java.lang.Long; retain boxed type in heterogeneous Objects/Arrays hashes."""

    value: int
    java_class_name: ClassVar[str] = "java.lang.Long"

    def java_hash_code(self) -> int:
        """Java: Long#hashCode."""
        return long_hash_code(self.value)

    def java_compare_to(self, other: object) -> int:
        """Java: Long#compareTo."""
        if not isinstance(other, JavaLong):
            raise TypeError("Java ClassCastException: Long.compareTo")
        return (self.value > other.value) - (self.value < other.value)


@dataclass(frozen=True, slots=True, init=False)
class JavaCharacter:
    """Java: java.lang.Character; retain boxed type in heterogeneous Object[] hashes."""

    value: int
    java_class_name: ClassVar[str] = "java.lang.Character"

    def __init__(self, value: int | str) -> None:
        """Java: Character#Character(char)."""
        object.__setattr__(self, "value", character_hash_code(value))

    def java_hash_code(self) -> int:
        """Java: Character#hashCode."""
        return self.value

    def java_compare_to(self, other: object) -> int:
        """Java: Character#compareTo returns the unsigned code-unit difference."""
        if not isinstance(other, JavaCharacter):
            raise TypeError("Java ClassCastException: Character.compareTo")
        return self.value - other.value
