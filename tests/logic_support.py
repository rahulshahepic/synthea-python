"""Shared support for the T17 Logic/Components tests.

* ``ClaimDouble`` — a test double for Claim (T14, not yet merged). Person's
  real HealthRecord (T08) constructs a Claim for every Encounter and
  Medication and calls ``add_line_item`` from its ``*Start`` methods. The
  double supplies only that plumbing; Logic never reads claim state, so no
  probed behaviour depends on it (PORTING_GUIDE §10 component parity).
* ``CoverageRecordDouble`` is reused from tests/parity/person_doubles.py
  (T16, not yet merged): a real Person cannot be constructed without it.
* ``LogicStateDouble`` — a State stand-in (T19, not yet merged) carrying only
  the fields Logic and Person read: ``name``, ``entered``, ``exited``,
  ``entry``.
* ``build_logic`` — mirrors the Java Gson construction of Logic objects
  (``Utilities.getGson()``: LOWER_CASE_WITH_UNDERSCORES field naming,
  ``InnerClassTypeAdapterFactory`` on the ``condition_type`` field, JSON
  numbers becoming Double except for fields typed int/Integer/long, and
  Object-typed values becoming Double/String/Boolean). The real Gson
  analogue is out of scope for the Python port (see T06's
  ``Utilities.get_gson``), so the tests build Logic objects with this.
* ``patched_person`` — construct a real Person with the two doubles above
  patched in for the duration.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast
from unittest.mock import patch

import synthea.world.agents.person as person_module
import synthea.world.concepts.claim as claim_module
from synthea.engine import logic as logic_module
from synthea.engine.components import DateInput, ExactWithUnit
from synthea.engine.logic import Logic
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Code, Entry
from synthea.world.concepts.vital_sign import VITAL_SIGN_DISPLAY_NAMES
from tests.parity.person_doubles import CoverageRecordDouble


class ClaimDouble:
    """Java: Claim (T14) — test double supplying construction + line items."""

    def __init__(self, entry: object, person: object) -> None:
        self.entry = entry
        self.person = person
        self.line_items: list[object] = []

    def add_line_item(self, entry: object) -> None:
        self.line_items.append(entry)

    def assign_costs(self) -> None:
        pass


class LogicStateDouble:
    """Java: State (T19) — only the fields Person/Logic read."""

    def __init__(
        self,
        name: str,
        entered: int = 0,
        exited: int = 0,
        entry: Entry | None = None,
    ) -> None:
        self.name = name
        self.entered = entered
        self.exited = exited
        self.entry = entry


@contextmanager
def patched_person(seed: int) -> Iterator[Person]:
    """A real Person whose unmerged collaborators (T14 Claim, T16
    CoverageRecord) are doubles for the life of the context."""
    with (
        patch.object(person_module, "CoverageRecord", CoverageRecordDouble),
        patch.object(claim_module, "Claim", ClaimDouble),
    ):
        yield Person(seed)


def build_code(definition: dict[str, object]) -> Code:
    """Java: Gson construction of a HealthRecord.Code."""
    code = Code(
        cast(str, definition["system"]),
        cast(str, definition["code"]),
        cast(str, definition.get("display")),
    )
    if definition.get("version") is not None:
        code.version = cast(str, definition["version"])
    return code


_VITAL_SIGNS_BY_DISPLAY = {display: vs for vs, display in VITAL_SIGN_DISPLAY_NAMES.items()}

# Gson types for Logic fields that are not Object/String: JSON numbers for
# these become int (Integer/int fields) instead of Double.
_INT_FIELDS = {"year", "month", "minimum", "maximum"}
# ... and these become float (Double/double fields).
_FLOAT_FIELDS = {"quantity", "value"}


def _gson_object_value(value: object) -> object:
    """Gson deserialization of an Object-typed field: numbers become Double."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    return value


def build_logic(definition: dict[str, object]) -> Logic:
    """Build a Logic object from its module-JSON definition, mirroring Gson."""
    type_name = cast(str, definition["condition_type"]).replace(" ", "")
    cls = getattr(logic_module, type_name)
    logic: Logic = cls()
    for key, value in definition.items():
        if key == "condition_type":
            continue
        setattr(logic, key, _convert_field(logic, key, value))
    return logic


def _convert_field(logic: Logic, key: str, value: object) -> object:
    if key == "codes":
        return [build_code(cast("dict[str, object]", c)) for c in cast(list, value)]
    if key == "value_code":
        return build_code(cast("dict[str, object]", value))
    if key == "conditions":
        return [build_logic(cast("dict[str, object]", c)) for c in cast(list, value)]
    if key == "condition":
        return build_logic(cast("dict[str, object]", value))
    if key == "date":
        raw = cast("dict[str, object]", value)
        date = DateInput()
        for field in ("year", "month", "day", "hour", "minute", "second", "millisecond"):
            if raw.get(field) is not None:
                setattr(date, field, int(cast(float, raw[field])))
        return date
    if key == "within":
        raw = cast("dict[str, object]", value)
        within: ExactWithUnit[float] = ExactWithUnit()
        within.quantity = float(cast(float, raw["quantity"]))
        within.unit = cast(str, raw["unit"])
        return within
    if key == "vital_sign":
        return _VITAL_SIGNS_BY_DISPLAY[cast(str, value)]
    if key == "value" and type(logic).__name__ in ("Observation", "Attribute"):
        return _gson_object_value(value)
    if key in _INT_FIELDS:
        return int(cast(float, value))
    if key in _FLOAT_FIELDS:
        return float(cast(float, value))
    return value


__all__ = [
    "ClaimDouble",
    "LogicStateDouble",
    "build_code",
    "build_logic",
    "patched_person",
]
