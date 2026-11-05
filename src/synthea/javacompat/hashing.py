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
    if values is None:
        raise ValueError("Java NullPointerException: List.hashCode receiver")
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


# Java 21 Character data: Unicode 15.0.0 simple mappings, not locale/full case folding.
# Source: https://www.unicode.org/Public/15.0.0/ucd/UnicodeData.txt
# SHA-256: 806e9aed65037197f1ec85e12be6e8cd870fc5608b4de0fffd990f689f376a73
# Generated from fields 12 and 13 of that specification; no probe goldens are used.
_UPPER_RANGES: tuple[tuple[int, int, int, int], ...] = (
    (0x61, 0x7A, 1, -32),
    (0xE0, 0xF6, 1, -32),
    (0xF8, 0xFE, 1, -32),
    (0x101, 0x12F, 2, -1),
    (0x133, 0x137, 2, -1),
    (0x13A, 0x148, 2, -1),
    (0x14B, 0x177, 2, -1),
    (0x17A, 0x17E, 2, -1),
    (0x1A1, 0x1A5, 2, -1),
    (0x1CE, 0x1DC, 2, -1),
    (0x1DF, 0x1EF, 2, -1),
    (0x1F9, 0x21F, 2, -1),
    (0x223, 0x233, 2, -1),
    (0x247, 0x24F, 2, -1),
    (0x37B, 0x37D, 1, 130),
    (0x3AD, 0x3AF, 1, -37),
    (0x3B1, 0x3C1, 1, -32),
    (0x3C3, 0x3CB, 1, -32),
    (0x3D9, 0x3EF, 2, -1),
    (0x430, 0x44F, 1, -32),
    (0x450, 0x45F, 1, -80),
    (0x461, 0x481, 2, -1),
    (0x48B, 0x4BF, 2, -1),
    (0x4C2, 0x4CE, 2, -1),
    (0x4D1, 0x52F, 2, -1),
    (0x561, 0x586, 1, -48),
    (0x10D0, 0x10FA, 1, 3008),
    (0x10FD, 0x10FF, 1, 3008),
    (0x13F8, 0x13FD, 1, -8),
    (0x1E01, 0x1E95, 2, -1),
    (0x1EA1, 0x1EFF, 2, -1),
    (0x1F00, 0x1F07, 1, 8),
    (0x1F10, 0x1F15, 1, 8),
    (0x1F20, 0x1F27, 1, 8),
    (0x1F30, 0x1F37, 1, 8),
    (0x1F40, 0x1F45, 1, 8),
    (0x1F51, 0x1F57, 2, 8),
    (0x1F60, 0x1F67, 1, 8),
    (0x1F72, 0x1F75, 1, 86),
    (0x1F80, 0x1F87, 1, 8),
    (0x1F90, 0x1F97, 1, 8),
    (0x1FA0, 0x1FA7, 1, 8),
    (0x2170, 0x217F, 1, -16),
    (0x24D0, 0x24E9, 1, -26),
    (0x2C30, 0x2C5F, 1, -48),
    (0x2C68, 0x2C6C, 2, -1),
    (0x2C81, 0x2CE3, 2, -1),
    (0x2D00, 0x2D25, 1, -7264),
    (0xA641, 0xA66D, 2, -1),
    (0xA681, 0xA69B, 2, -1),
    (0xA723, 0xA72F, 2, -1),
    (0xA733, 0xA76F, 2, -1),
    (0xA77F, 0xA787, 2, -1),
    (0xA797, 0xA7A9, 2, -1),
    (0xA7B5, 0xA7C3, 2, -1),
    (0xAB70, 0xABBF, 1, -38864),
    (0xFF41, 0xFF5A, 1, -32),
    (0x10428, 0x1044F, 1, -40),
    (0x104D8, 0x104FB, 1, -40),
    (0x10597, 0x105A1, 1, -39),
    (0x105A3, 0x105B1, 1, -39),
    (0x105B3, 0x105B9, 1, -39),
    (0x10CC0, 0x10CF2, 1, -64),
    (0x118C0, 0x118DF, 1, -32),
    (0x16E60, 0x16E7F, 1, -32),
    (0x1E922, 0x1E943, 1, -34),
)
_UPPER_EXCEPTIONS: dict[int, int] = {
    0xB5: 0x39C,
    0xFF: 0x178,
    0x131: 0x49,
    0x17F: 0x53,
    0x180: 0x243,
    0x183: 0x182,
    0x185: 0x184,
    0x188: 0x187,
    0x18C: 0x18B,
    0x192: 0x191,
    0x195: 0x1F6,
    0x199: 0x198,
    0x19A: 0x23D,
    0x19E: 0x220,
    0x1A8: 0x1A7,
    0x1AD: 0x1AC,
    0x1B0: 0x1AF,
    0x1B4: 0x1B3,
    0x1B6: 0x1B5,
    0x1B9: 0x1B8,
    0x1BD: 0x1BC,
    0x1BF: 0x1F7,
    0x1C5: 0x1C4,
    0x1C6: 0x1C4,
    0x1C8: 0x1C7,
    0x1C9: 0x1C7,
    0x1CB: 0x1CA,
    0x1CC: 0x1CA,
    0x1DD: 0x18E,
    0x1F2: 0x1F1,
    0x1F3: 0x1F1,
    0x1F5: 0x1F4,
    0x23C: 0x23B,
    0x23F: 0x2C7E,
    0x240: 0x2C7F,
    0x242: 0x241,
    0x250: 0x2C6F,
    0x251: 0x2C6D,
    0x252: 0x2C70,
    0x253: 0x181,
    0x254: 0x186,
    0x256: 0x189,
    0x257: 0x18A,
    0x259: 0x18F,
    0x25B: 0x190,
    0x25C: 0xA7AB,
    0x260: 0x193,
    0x261: 0xA7AC,
    0x263: 0x194,
    0x265: 0xA78D,
    0x266: 0xA7AA,
    0x268: 0x197,
    0x269: 0x196,
    0x26A: 0xA7AE,
    0x26B: 0x2C62,
    0x26C: 0xA7AD,
    0x26F: 0x19C,
    0x271: 0x2C6E,
    0x272: 0x19D,
    0x275: 0x19F,
    0x27D: 0x2C64,
    0x280: 0x1A6,
    0x282: 0xA7C5,
    0x283: 0x1A9,
    0x287: 0xA7B1,
    0x288: 0x1AE,
    0x289: 0x244,
    0x28A: 0x1B1,
    0x28B: 0x1B2,
    0x28C: 0x245,
    0x292: 0x1B7,
    0x29D: 0xA7B2,
    0x29E: 0xA7B0,
    0x345: 0x399,
    0x371: 0x370,
    0x373: 0x372,
    0x377: 0x376,
    0x3AC: 0x386,
    0x3C2: 0x3A3,
    0x3CC: 0x38C,
    0x3CD: 0x38E,
    0x3CE: 0x38F,
    0x3D0: 0x392,
    0x3D1: 0x398,
    0x3D5: 0x3A6,
    0x3D6: 0x3A0,
    0x3D7: 0x3CF,
    0x3F0: 0x39A,
    0x3F1: 0x3A1,
    0x3F2: 0x3F9,
    0x3F3: 0x37F,
    0x3F5: 0x395,
    0x3F8: 0x3F7,
    0x3FB: 0x3FA,
    0x4CF: 0x4C0,
    0x1C80: 0x412,
    0x1C81: 0x414,
    0x1C82: 0x41E,
    0x1C83: 0x421,
    0x1C84: 0x422,
    0x1C85: 0x422,
    0x1C86: 0x42A,
    0x1C87: 0x462,
    0x1C88: 0xA64A,
    0x1D79: 0xA77D,
    0x1D7D: 0x2C63,
    0x1D8E: 0xA7C6,
    0x1E9B: 0x1E60,
    0x1F70: 0x1FBA,
    0x1F71: 0x1FBB,
    0x1F76: 0x1FDA,
    0x1F77: 0x1FDB,
    0x1F78: 0x1FF8,
    0x1F79: 0x1FF9,
    0x1F7A: 0x1FEA,
    0x1F7B: 0x1FEB,
    0x1F7C: 0x1FFA,
    0x1F7D: 0x1FFB,
    0x1FB0: 0x1FB8,
    0x1FB1: 0x1FB9,
    0x1FB3: 0x1FBC,
    0x1FBE: 0x399,
    0x1FC3: 0x1FCC,
    0x1FD0: 0x1FD8,
    0x1FD1: 0x1FD9,
    0x1FE0: 0x1FE8,
    0x1FE1: 0x1FE9,
    0x1FE5: 0x1FEC,
    0x1FF3: 0x1FFC,
    0x214E: 0x2132,
    0x2184: 0x2183,
    0x2C61: 0x2C60,
    0x2C65: 0x23A,
    0x2C66: 0x23E,
    0x2C73: 0x2C72,
    0x2C76: 0x2C75,
    0x2CEC: 0x2CEB,
    0x2CEE: 0x2CED,
    0x2CF3: 0x2CF2,
    0x2D27: 0x10C7,
    0x2D2D: 0x10CD,
    0xA77A: 0xA779,
    0xA77C: 0xA77B,
    0xA78C: 0xA78B,
    0xA791: 0xA790,
    0xA793: 0xA792,
    0xA794: 0xA7C4,
    0xA7C8: 0xA7C7,
    0xA7CA: 0xA7C9,
    0xA7D1: 0xA7D0,
    0xA7D7: 0xA7D6,
    0xA7D9: 0xA7D8,
    0xA7F6: 0xA7F5,
    0xAB53: 0xA7B3,
    0x105BB: 0x10594,
    0x105BC: 0x10595,
}
_UPPER_CASE: dict[int, int] = {
    **_UPPER_EXCEPTIONS,
    **{
        cp: cp + delta
        for low, high, step, delta in _UPPER_RANGES
        for cp in range(low, high + 1, step)
    },
}

_LOWER_RANGES: tuple[tuple[int, int, int, int], ...] = (
    (0x41, 0x5A, 1, 32),
    (0xC0, 0xD6, 1, 32),
    (0xD8, 0xDE, 1, 32),
    (0x100, 0x12E, 2, 1),
    (0x132, 0x136, 2, 1),
    (0x139, 0x147, 2, 1),
    (0x14A, 0x176, 2, 1),
    (0x179, 0x17D, 2, 1),
    (0x1A0, 0x1A4, 2, 1),
    (0x1CB, 0x1DB, 2, 1),
    (0x1DE, 0x1EE, 2, 1),
    (0x1F8, 0x21E, 2, 1),
    (0x222, 0x232, 2, 1),
    (0x246, 0x24E, 2, 1),
    (0x388, 0x38A, 1, 37),
    (0x391, 0x3A1, 1, 32),
    (0x3A3, 0x3AB, 1, 32),
    (0x3D8, 0x3EE, 2, 1),
    (0x3FD, 0x3FF, 1, -130),
    (0x400, 0x40F, 1, 80),
    (0x410, 0x42F, 1, 32),
    (0x460, 0x480, 2, 1),
    (0x48A, 0x4BE, 2, 1),
    (0x4C1, 0x4CD, 2, 1),
    (0x4D0, 0x52E, 2, 1),
    (0x531, 0x556, 1, 48),
    (0x10A0, 0x10C5, 1, 7264),
    (0x13A0, 0x13EF, 1, 38864),
    (0x13F0, 0x13F5, 1, 8),
    (0x1C90, 0x1CBA, 1, -3008),
    (0x1CBD, 0x1CBF, 1, -3008),
    (0x1E00, 0x1E94, 2, 1),
    (0x1EA0, 0x1EFE, 2, 1),
    (0x1F08, 0x1F0F, 1, -8),
    (0x1F18, 0x1F1D, 1, -8),
    (0x1F28, 0x1F2F, 1, -8),
    (0x1F38, 0x1F3F, 1, -8),
    (0x1F48, 0x1F4D, 1, -8),
    (0x1F59, 0x1F5F, 2, -8),
    (0x1F68, 0x1F6F, 1, -8),
    (0x1F88, 0x1F8F, 1, -8),
    (0x1F98, 0x1F9F, 1, -8),
    (0x1FA8, 0x1FAF, 1, -8),
    (0x1FC8, 0x1FCB, 1, -86),
    (0x2160, 0x216F, 1, 16),
    (0x24B6, 0x24CF, 1, 26),
    (0x2C00, 0x2C2F, 1, 48),
    (0x2C67, 0x2C6B, 2, 1),
    (0x2C80, 0x2CE2, 2, 1),
    (0xA640, 0xA66C, 2, 1),
    (0xA680, 0xA69A, 2, 1),
    (0xA722, 0xA72E, 2, 1),
    (0xA732, 0xA76E, 2, 1),
    (0xA77E, 0xA786, 2, 1),
    (0xA796, 0xA7A8, 2, 1),
    (0xA7B4, 0xA7C2, 2, 1),
    (0xFF21, 0xFF3A, 1, 32),
    (0x10400, 0x10427, 1, 40),
    (0x104B0, 0x104D3, 1, 40),
    (0x10570, 0x1057A, 1, 39),
    (0x1057C, 0x1058A, 1, 39),
    (0x1058C, 0x10592, 1, 39),
    (0x10C80, 0x10CB2, 1, 64),
    (0x118A0, 0x118BF, 1, 32),
    (0x16E40, 0x16E5F, 1, 32),
    (0x1E900, 0x1E921, 1, 34),
)
_LOWER_EXCEPTIONS: dict[int, int] = {
    0x130: 0x69,
    0x178: 0xFF,
    0x181: 0x253,
    0x182: 0x183,
    0x184: 0x185,
    0x186: 0x254,
    0x187: 0x188,
    0x189: 0x256,
    0x18A: 0x257,
    0x18B: 0x18C,
    0x18E: 0x1DD,
    0x18F: 0x259,
    0x190: 0x25B,
    0x191: 0x192,
    0x193: 0x260,
    0x194: 0x263,
    0x196: 0x269,
    0x197: 0x268,
    0x198: 0x199,
    0x19C: 0x26F,
    0x19D: 0x272,
    0x19F: 0x275,
    0x1A6: 0x280,
    0x1A7: 0x1A8,
    0x1A9: 0x283,
    0x1AC: 0x1AD,
    0x1AE: 0x288,
    0x1AF: 0x1B0,
    0x1B1: 0x28A,
    0x1B2: 0x28B,
    0x1B3: 0x1B4,
    0x1B5: 0x1B6,
    0x1B7: 0x292,
    0x1B8: 0x1B9,
    0x1BC: 0x1BD,
    0x1C4: 0x1C6,
    0x1C5: 0x1C6,
    0x1C7: 0x1C9,
    0x1C8: 0x1C9,
    0x1CA: 0x1CC,
    0x1F1: 0x1F3,
    0x1F2: 0x1F3,
    0x1F4: 0x1F5,
    0x1F6: 0x195,
    0x1F7: 0x1BF,
    0x220: 0x19E,
    0x23A: 0x2C65,
    0x23B: 0x23C,
    0x23D: 0x19A,
    0x23E: 0x2C66,
    0x241: 0x242,
    0x243: 0x180,
    0x244: 0x289,
    0x245: 0x28C,
    0x370: 0x371,
    0x372: 0x373,
    0x376: 0x377,
    0x37F: 0x3F3,
    0x386: 0x3AC,
    0x38C: 0x3CC,
    0x38E: 0x3CD,
    0x38F: 0x3CE,
    0x3CF: 0x3D7,
    0x3F4: 0x3B8,
    0x3F7: 0x3F8,
    0x3F9: 0x3F2,
    0x3FA: 0x3FB,
    0x4C0: 0x4CF,
    0x10C7: 0x2D27,
    0x10CD: 0x2D2D,
    0x1E9E: 0xDF,
    0x1FB8: 0x1FB0,
    0x1FB9: 0x1FB1,
    0x1FBA: 0x1F70,
    0x1FBB: 0x1F71,
    0x1FBC: 0x1FB3,
    0x1FCC: 0x1FC3,
    0x1FD8: 0x1FD0,
    0x1FD9: 0x1FD1,
    0x1FDA: 0x1F76,
    0x1FDB: 0x1F77,
    0x1FE8: 0x1FE0,
    0x1FE9: 0x1FE1,
    0x1FEA: 0x1F7A,
    0x1FEB: 0x1F7B,
    0x1FEC: 0x1FE5,
    0x1FF8: 0x1F78,
    0x1FF9: 0x1F79,
    0x1FFA: 0x1F7C,
    0x1FFB: 0x1F7D,
    0x1FFC: 0x1FF3,
    0x2126: 0x3C9,
    0x212A: 0x6B,
    0x212B: 0xE5,
    0x2132: 0x214E,
    0x2183: 0x2184,
    0x2C60: 0x2C61,
    0x2C62: 0x26B,
    0x2C63: 0x1D7D,
    0x2C64: 0x27D,
    0x2C6D: 0x251,
    0x2C6E: 0x271,
    0x2C6F: 0x250,
    0x2C70: 0x252,
    0x2C72: 0x2C73,
    0x2C75: 0x2C76,
    0x2C7E: 0x23F,
    0x2C7F: 0x240,
    0x2CEB: 0x2CEC,
    0x2CED: 0x2CEE,
    0x2CF2: 0x2CF3,
    0xA779: 0xA77A,
    0xA77B: 0xA77C,
    0xA77D: 0x1D79,
    0xA78B: 0xA78C,
    0xA78D: 0x265,
    0xA790: 0xA791,
    0xA792: 0xA793,
    0xA7AA: 0x266,
    0xA7AB: 0x25C,
    0xA7AC: 0x261,
    0xA7AD: 0x26C,
    0xA7AE: 0x26A,
    0xA7B0: 0x29E,
    0xA7B1: 0x287,
    0xA7B2: 0x29D,
    0xA7B3: 0xAB53,
    0xA7C4: 0xA794,
    0xA7C5: 0x282,
    0xA7C6: 0x1D8E,
    0xA7C7: 0xA7C8,
    0xA7C9: 0xA7CA,
    0xA7D0: 0xA7D1,
    0xA7D6: 0xA7D7,
    0xA7D8: 0xA7D9,
    0xA7F5: 0xA7F6,
    0x10594: 0x105BB,
    0x10595: 0x105BC,
}
_LOWER_CASE: dict[int, int] = {
    **_LOWER_EXCEPTIONS,
    **{
        cp: cp + delta
        for low, high, step, delta in _LOWER_RANGES
        for cp in range(low, high + 1, step)
    },
}


def _simple_upper(cp: int) -> int:
    """Java: Character#toUpperCase(int), frozen Unicode 15 simple mapping."""
    return _UPPER_CASE.get(cp, cp)


def _simple_lower(cp: int) -> int:
    """Java: Character#toLowerCase(int), frozen Unicode 15 simple mapping."""
    return _LOWER_CASE.get(cp, cp)


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
