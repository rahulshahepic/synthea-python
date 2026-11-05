"""Canonical HealthRecord rendering, matching support/Canonical.java.

Java: org.mitre.synthea.world.concepts.HealthRecord (all nested entry types).

Schema: fields use snake_case; all fields, including nulls and the private cached
cost, are included. Entry ownership is implicit in the enclosing record. Report
backlinks are UUIDs to avoid cycles. Doubles use Java Double.toString; long time
fields and UUIDs are strings. Maps use ordered key/value pairs (including Code
keys), lists retain record order, LinkedHashSets retain insertion order. No cost
or claim calculation runs while rendering.

Later tasks add canonical/<area>.py and support/Canonical<Area>.java and register
external type encoders with register_encoder/register; they never edit this file.
Encoders receive a value and return JSON-compatible data; use dump_value for its
children. Unregistered external objects fail loudly rather than lose fields.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from decimal import Decimal
from enum import Enum
from typing import cast
from uuid import UUID

from synthea.javacompat.bigdecimal import to_string
from synthea.javacompat.numbers import double_to_string
from synthea.world.concepts.health_record import (
    Code,
    Entry,
    HealthRecord,
    Instance,
    OrderedSet,
    Series,
)

_ENCODERS: dict[type, Callable[[object], object]] = {}
_LONG_FIELDS = {"start", "stop", "ended_time", "manufacture_time", "expiration_time", "death"}


def register_encoder[T](cls: type[T], encoder: Callable[[T], object]) -> None:
    """Register a later task's external-type canonical extension."""
    _ENCODERS[cls] = cast(Callable[[object], object], encoder)


def dump_code(code: Code | None) -> object:
    """Java: HealthRecord.Code; render all five fields including null metadata."""
    if code is None:
        return None
    return {
        key: getattr(code, key) for key in ("system", "code", "display", "version", "value_set")
    }


def dump_value(value: object) -> object:
    """Render a nested value without invoking simulation behavior."""
    if value is None or isinstance(value, str | bool | int):
        return value
    if isinstance(value, float):
        return double_to_string(value)
    if isinstance(value, Decimal):
        return to_string(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Code):
        return dump_code(value)
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, Entry):
        return dump_entry(value)
    if isinstance(value, Series | Instance):
        return {name: dump_value(child) for name, child in sorted(vars(value).items())}
    if isinstance(value, Mapping):
        return [{"key": dump_value(k), "value": dump_value(v)} for k, v in value.items()]
    if isinstance(value, list | tuple | OrderedSet):
        return [dump_value(v) for v in value]
    for cls, encoder in _ENCODERS.items():
        if isinstance(value, cls):
            return encoder(value)
    raise TypeError(f"Register a canonical encoder for {type(value).__name__}")


def dump_entry(entry: Entry) -> dict[str, object]:
    """Java: HealthRecord.Entry and every subtype; include inherited fields."""
    fields: dict[str, object] = {"entry_class": type(entry).__name__}
    for name, value in sorted(vars(entry).items()):
        if name == "record":
            continue
        if name in _LONG_FIELDS and value is not None:
            fields[name] = str(value)
        elif name == "report":
            fields[name] = str(value.uuid) if value is not None else None
        elif name in ("prescription_details", "goals"):
            # Gson JSON field containers retain object keys, unlike Java Map fields.
            fields[name] = dump_json(value)
        else:
            fields[name] = dump_value(value)
    return fields


def dump_json(value: object) -> object:
    """Render Gson JsonObject fields, keeping keys and canonicalizing doubles."""
    if isinstance(value, Mapping):
        return {str(k): dump_json(v) for k, v in value.items()}
    if isinstance(value, list | OrderedSet):
        return [dump_json(v) for v in value]
    return dump_value(value)


def dump_record(record: HealthRecord) -> dict[str, object]:
    """Java: HealthRecord; owner Person is rendered by a later task's wrapper."""
    return {
        "provider": dump_value(record.provider),
        "encounters": [dump_entry(e) for e in record.encounters],
        "present": dump_value(record.present),
        "death": None if record.death is None else str(record.death),
        "demographics_at_record_creation": dump_value(record.demographics_at_record_creation),
    }
