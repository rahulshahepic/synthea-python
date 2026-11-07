"""Java: support.CanonicalLifecycle; complete T21 person attribute/generator snapshots."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from enum import Enum

from synthea.helpers.value_generator import ValueGenerator
from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.concepts.employment import Employment
from synthea.world.concepts.health_record import Code
from synthea.world.concepts.nhanes_sample import NHANESSample
from synthea.world.concepts.pediatric_growth_trajectory import PediatricGrowthTrajectory, Point
from synthea.world.concepts.vital_sign import VitalSign
from synthea.world.geography.location import Location
from tests.parity.canonical import dump_code


def value(item: object) -> object:
    """Java: CanonicalLifecycle#value; fail on unregistered types rather than omit them."""
    if item is None or isinstance(item, bool):
        return item
    if isinstance(item, float):
        return double_to_string(item)
    if isinstance(item, date):
        return item.isoformat()
    if isinstance(item, int | str):
        return str(item)
    if isinstance(item, Enum):
        return item.name
    if isinstance(item, Code):
        return dump_code(item)
    if isinstance(item, Point2DDouble):
        return {"x": double_to_string(item.get_x()), "y": double_to_string(item.get_y())}
    if isinstance(item, Location):
        return {"state": item.state, "city": item.city}
    if isinstance(item, Mapping):
        # Guava Table's rowMap is represented by (drug, SysDias) keys in Python.
        if item and isinstance(next(iter(item)), tuple):
            nested: dict[str, dict[str, object]] = {}
            for (drug, kind), impact in item.items():
                nested.setdefault(drug, {})[kind.name] = impact
            return value(nested)
        return {str(key): value(child) for key, child in item.items()}
    if isinstance(item, list | tuple):
        return [value(child) for child in item]
    if isinstance(
        item, PediatricGrowthTrajectory | Point | NHANESSample | Employment | ValueGenerator
    ):
        return {name: value(child) for name, child in vars(item).items() if name != "person"}
    raise TypeError(f"No Lifecycle encoder for {type(item).__name__}")


def person_snapshot(person: Person, time: int) -> dict[str, object]:
    """Java: CanonicalLifecycle#person; read vitals in enum order before attributes/RNG."""
    vitals = {}
    for sign in VitalSign:
        if sign in person.vital_signs:
            vitals[sign.name] = {
                "value": double_to_string(person.get_vital_sign(sign, time)),
                "generator": value(person.vital_signs[sign]),
            }
    return {
        "vitals": vitals,
        "attributes": value(person.attributes),
        "rng_count": str(person.get_count()),
        "time": str(time),
    }
