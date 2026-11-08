"""Java: org.mitre.synthea.modules.calculators.ASCVD."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Protocol

from synthea.engine.distribution import _java_log
from synthea.helpers.utilities import Utilities
from synthea.world.concepts.growth_chart_entry import _java_exp, _java_pow
from synthea.world.concepts.vital_sign import VitalSign

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Inventory(Protocol):
    """Java boundary: Attributes.Inventory read/write/example collection fields."""

    read: dict[str, set[str]]
    write: dict[str, set[str]]
    example_values: set[str]


@dataclass
class _InventoryData:
    """Java: Attributes.Inventory's collection surface for this module's inventory entries."""

    read: dict[str, set[str]] = field(default_factory=dict)
    write: dict[str, set[str]] = field(default_factory=dict)
    example_values: set[str] = field(default_factory=set)


def _inventory(
    attributes: dict[str, Inventory],
    module: str,
    attribute: str,
    read: bool,
    write: bool,
    example: str | None,
) -> None:
    """Java boundary: Attributes#inventory, without Graphviz/reporting functionality."""
    item = attributes.setdefault(attribute, _InventoryData())
    if read:
        item.read.setdefault(module, set())
    if write:
        item.write.setdefault(module, set())
        if example is not None:
            item.example_values.add(example)


class ASCVD:
    """Java: ASCVD pooled cohort risk calculator."""

    TEN_YEARS_IN_MS: ClassVar[int] = 315360000000
    ASCVD_COEFFICIENTS: ClassVar[list[list[float]]] = [
        [-29.799, 17.114, 12.344, 2.469],
        [4.884, 0, 0, 0],
        [13.54, 0.94, 11.853, 0.302],
        [-3.114, 0, -2.664, 0],
        [-13.578, -18.92, -7.99, -0.307],
        [3.149, 4.475, 1.769, 0],
        [2.019, 29.291, 1.797, 1.916],
        [0, -6.432, 0, 0],
        [1.957, 27.82, 1.764, 1.809],
        [0, -6.087, 0, 0],
        [7.574, 0.691, 7.837, 0.549],
        [-1.665, 0, -1.795, 0],
        [0.661, 0.874, 0.658, 0.645],
        [-29.18, 86.61, 61.18, 19.54],
        [0.9665, 0.9533, 0.9144, 0.8954],
    ]

    def __init__(self) -> None:
        """Java: ASCVD#ASCVD, implicit empty constructor."""

    @staticmethod
    def ascvd10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: ASCVD#ascvd10Year, preserving evaluation and accumulation order."""
        age = person.age_in_years(time)
        gender = person.attributes.get("gender")
        race = person.attributes.get("race")
        sbp = person.get_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, time)
        dbp = person.get_vital_sign(VitalSign.DIASTOLIC_BLOOD_PRESSURE, time)
        chol = person.get_vital_sign(VitalSign.TOTAL_CHOLESTEROL, time)
        hdl = person.get_vital_sign(VitalSign.HDL, time)
        smoker = bool(person.attributes.get("smoker", False))
        diabetic = bool(person.attributes.get("diabetes", False))
        hypertensive = bool(person.attributes.get("hypertension", False))
        if sbp is None or dbp is None or chol is None:
            return -1.0
        if age < 40 or age > 79:
            return -1.0
        ln_age, ln_chol, ln_hdl = _java_log(age), _java_log(chol), _java_log(hdl)
        treated = _java_log(sbp) if hypertensive else 0.0
        untreated = 0.0 if hypertensive else _java_log(sbp)
        values = [
            ln_age,
            ln_age * ln_age,
            ln_chol,
            ln_age * ln_chol,
            ln_hdl,
            ln_age * ln_hdl,
            treated,
            ln_age * treated,
            untreated,
            ln_age * untreated,
            int(smoker),
            ln_age * int(smoker),
            int(diabetic),
        ]
        index = (2 if gender == "M" else 0) + (1 if race == "black" else 0)
        coefficients = ASCVD.ASCVD_COEFFICIENTS
        individual_sum = 0.0
        for i in range(13):
            individual_sum += coefficients[i][index] * values[i]
        risk = 1 - _java_pow(
            coefficients[14][index], _java_exp(individual_sum - coefficients[13][index])
        )
        return (
            Utilities.convert_risk_to_timestep(risk, ASCVD.TEN_YEARS_IN_MS)
            if per_timestep
            else risk
        )

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: ASCVD#inventoryAttributes."""
        for key, example in [
            ("gender", "M"),
            ("race", "black"),
            ("smoker", "false"),
            ("diabetes", "false"),
            ("hypertension", "false"),
        ]:
            _inventory(attributes, "ASCVD", key, True, False, example)
