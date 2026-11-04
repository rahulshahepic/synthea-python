"""Formatting java.util.UUID from two signed Java longs."""

from __future__ import annotations


def java_uuid(most_significant_bits: int, least_significant_bits: int) -> str:
    """Java: java.util.UUID#UUID(long,long) and #toString()."""
    msb = most_significant_bits & 0xFFFFFFFFFFFFFFFF
    lsb = least_significant_bits & 0xFFFFFFFFFFFFFFFF
    return (
        f"{msb >> 32:08x}-{(msb >> 16) & 0xFFFF:04x}-{msb & 0xFFFF:04x}-"
        f"{lsb >> 48:04x}-{lsb & 0xFFFFFFFFFFFF:012x}"
    )


def uuid_to_string(most_significant_bits: int, least_significant_bits: int) -> str:
    """Java: java.util.UUID#toString, compatibility alias."""
    return java_uuid(most_significant_bits, least_significant_bits)
