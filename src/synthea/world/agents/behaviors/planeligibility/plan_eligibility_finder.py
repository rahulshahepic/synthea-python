"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/P
lanEligibilityFinder.java.
"""

from __future__ import annotations

import re
from typing import ClassVar, TypeVar

from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.world.agents.behaviors.planeligibility.csv_eligibility import CSVEligibility
from synthea.world.agents.behaviors.planeligibility.default_plan_eligibility import (
    DefaultPlanEligibility,
)
from synthea.world.agents.behaviors.planeligibility.i_plan_eligibility import IPlanEligibility

_WHITESPACE = re.compile(r"[ \t\n\x0b\f\r]")
_TRIM = re.compile(r"^[\x00-\x20]+|[\x00-\x20]+$")

T = TypeVar("T")


def _is_blank(value: str | None) -> bool:
    """Apache Commons Lang StringUtils.isBlank."""
    return value is None or value.strip(" \t\n\x0b\f\r") == ""


def _java_trim(value: str) -> str:
    """Java String.trim: removes leading/trailing chars <= U+0020."""
    return _TRIM.sub("", value)


def _clean_name(value: str) -> str:
    """Java: value.replaceAll("\\\\s", "").toUpperCase() (en-US parity JVM)."""
    return _WHITESPACE.sub("", value).upper()


class PlanEligibilityFinder:
    """Java: PlanEligibilityFinder."""

    planEligibilities: ClassVar[JavaHashMap[str, IPlanEligibility] | None] = None
    ELIGIBILITY_NAME: ClassVar[str] = "Name"
    GENERIC: ClassVar[str] = "GENERIC"
    DEFAULT: ClassVar[IPlanEligibility] = DefaultPlanEligibility()

    def __init__(self) -> None:
        """Java: PlanEligibilityFinder#PlanEligibilityFinder.

        Java overloads:
        ()
        """

    @staticmethod
    def get_eligibility_algorithm(eligibility: str) -> IPlanEligibility:
        """Java: PlanEligibilityFinder#getEligibilityAlgorithm.

        Java overloads:
        (String eligibility)
        """
        cleaned_eligibility = _clean_name(eligibility)
        if cleaned_eligibility == PlanEligibilityFinder.GENERIC:
            return PlanEligibilityFinder.DEFAULT
        eligibilities = PlanEligibilityFinder.planEligibilities
        if eligibilities is not None and cleaned_eligibility in eligibilities:
            return eligibilities[cleaned_eligibility]
        raise RuntimeError("Plan eligibility " + eligibility + " does not exist.")

    @staticmethod
    def build_plan_eligibilities(state: str, file_name: str) -> None:
        """Java: PlanEligibilityFinder#buildPlanEligibilities.

        Java overloads:
        (String state, String fileName)
        """
        built: JavaHashMap[str, IPlanEligibility] = JavaHashMap()
        PlanEligibilityFinder.planEligibilities = built
        # Build the CSV input eligibility algorithms.
        CSVEligibility.build_eligibility_options(state)
        resource = Utilities.read_resource(file_name, True, True)
        csv = SimpleCSV.parse_line_by_line(resource)
        for raw_row in csv:
            row = PlanEligibilityFinder.remove_blank_map_string_values(raw_row)
            for key in list(row.keys()):
                row[key] = _java_trim(row[key])
            eligibility_name = _clean_name(row.pop(PlanEligibilityFinder.ELIGIBILITY_NAME))
            if eligibility_name in built:
                raise ValueError(
                    "Plan eligibility name '"
                    + eligibility_name
                    + "'' is reserved or already in use."
                )
            # CSVEligibility iterates its argument in order; a plain dict in
            # Java-HashMap iteration order reproduces the JVM's criteria order.
            built[eligibility_name] = CSVEligibility(dict(row))

    @staticmethod
    def remove_blank_map_string_values(map: dict[T, str]) -> JavaHashMap[T, str]:
        """Java: PlanEligibilityFinder#removeBlankMapStringValues.

        Java overloads:
        (Map map)

        Java collects the surviving entries into a fresh HashMap
        (Collectors.toMap), so the result iterates in Java HashMap order,
        not in CSV column order. JavaHashMap reproduces that order exactly.
        """
        kept: JavaHashMap[T, str] = JavaHashMap()
        for key, value in map.items():
            if not _is_blank(value):
                kept[key] = value
        return kept
