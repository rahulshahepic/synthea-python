"""Java: org.mitre.synthea.modules.Immunizations."""

from __future__ import annotations

import json
from collections.abc import MutableMapping
from typing import ClassVar, cast

from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.numbers import double_to_string
from synthea.modules.encounter_module import Inventory, _inventory
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Code


def _string(value: object) -> str:
    """Java: Object#toString for Gson raw-map scalar fields."""
    return double_to_string(value) if isinstance(value, float) else str(value)


class Immunizations:
    """Java: org.mitre.synthea.modules.Immunizations."""

    IMMUNIZATIONS: ClassVar[str] = "immunizations"
    immunizationSchedule: ClassVar[JavaHashMap[str, dict[str, object]]]

    def __init__(self) -> None:
        """Java: Immunizations#Immunizations (implicit constructor)."""

    @staticmethod
    def load_immunization_schedule() -> JavaHashMap[str, dict[str, object]]:
        """Java: Immunizations#loadImmunizationSchedule; root HashMap, nested Gson maps."""
        data = cast(
            dict[str, dict[str, object]],
            json.loads(
                Utilities.read_resource("immunization_schedule.json"),
                parse_int=float,
                parse_float=float,
            ),
        )
        schedule: JavaHashMap[str, dict[str, object]] = JavaHashMap()
        for key, item in data.items():
            schedule[key] = item
        return schedule

    @staticmethod
    def perform_encounter(person: Person, time: int) -> None:
        """Java: Immunizations#performEncounter; preserve root HashMap iteration/RNG order."""
        if Immunizations.IMMUNIZATIONS in person.attributes:
            given = cast(
                MutableMapping[str, list[int]], person.attributes[Immunizations.IMMUNIZATIONS]
            )
        else:
            given = JavaHashMap[str, list[int]]()
            person.attributes[Immunizations.IMMUNIZATIONS] = given
        for immunization in Immunizations.immunizationSchedule:
            series = Immunizations.immunization_due(immunization, person, time, given)
            if series > 0:
                given[immunization].append(time)
                assert person.record is not None
                entry = person.record.immunization(time, immunization)
                code = cast(
                    dict[str, object], Immunizations.immunizationSchedule[immunization]["code"]
                )
                entry.codes.append(
                    Code(_string(code["system"]), _string(code["code"]), _string(code["display"]))
                )
                entry.series = series

    @staticmethod
    def immunization_due(
        immunization: str,
        person: Person,
        time: int,
        immunizations_given: MutableMapping[str, list[int]],
    ) -> int:
        """Java: Immunizations#immunizationDue; four-year windows and historical availability."""
        months = person.age_in_months(time)
        if immunization in immunizations_given:
            history = immunizations_given[immunization]
        else:
            history = []
            immunizations_given[immunization] = history
        schedule = Immunizations.immunizationSchedule[immunization]
        available = schedule.get("first_available", 1900)
        if not isinstance(available, float):
            raise TypeError("Java ClassCastException: first_available must be a Double")
        if time < Utilities.convert_calendar_years_to_time(int(available)):
            return -1
        at_months = list(cast(list[float], schedule["at_months"]))
        if len(history) >= len(at_months):
            return -1
        at_months = [age for age in at_months if not (months - age >= 48)]
        if not at_months:
            return -1
        for date in history:
            at_date = person.age_in_months(date)
            age = at_months[0]
            if at_date >= age and at_date - age < 48:
                at_months.pop(0)
                if not at_months:
                    return -1
        if at_months and months >= at_months[0]:
            return len(history) + 1
        return -1

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: Immunizations#getAllCodes."""
        converted = []
        for schedule in Immunizations.immunizationSchedule.values():
            code = cast(dict[str, object], schedule["code"])
            converted.append(
                Code(_string(code["system"]), _string(code["code"]), _string(code["display"]))
            )
        return converted

    @staticmethod
    def get_maximum_doses(code: str | None) -> int:
        """Java: Immunizations#getMaximumDoses; missing/null codes default to one dose."""
        for schedule in Immunizations.immunizationSchedule.values():
            coding = cast(dict[str, object], schedule["code"])
            if coding["code"] == code:
                return len(cast(list[object], schedule["at_months"]))
        return 1

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: Immunizations#inventoryAttributes."""
        _inventory(
            attributes,
            "Immunizations",
            Immunizations.IMMUNIZATIONS,
            True,
            True,
            "Map<String, List<Long>>",
        )


Immunizations.immunizationSchedule = Immunizations.load_immunization_schedule()
