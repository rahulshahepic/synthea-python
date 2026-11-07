"""Java: org.mitre.synthea.world.concepts.Costs."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.engine.distribution import Distribution, RandomSource
from synthea.engine.distribution import Kind as DistributionKind
from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import parse_double
from synthea.world.agents.person import Person
from synthea.world.geography.location import Location

if TYPE_CHECKING:
    from synthea.world.concepts.health_record import Encounter as HealthRecordEncounter
    from synthea.world.concepts.health_record import Entry


class Costs:
    """Java: Costs."""

    COST_METHOD: ClassVar[DistributionKind]  # Initialized below, in Java static order.
    PROCEDURE_COSTS: ClassVar[dict[str, CostData]]
    MEDICATION_COSTS: ClassVar[dict[str, CostData]]
    ENCOUNTER_COSTS: ClassVar[dict[str, CostData]]
    IMMUNIZATION_COSTS: ClassVar[dict[str, CostData]]
    DEVICE_COSTS: ClassVar[dict[str, CostData]]
    SUPPLY_COSTS: ClassVar[dict[str, CostData]]
    DEFAULT_PROCEDURE_COST: ClassVar[float]
    DEFAULT_MEDICATION_COST: ClassVar[float]
    DEFAULT_ENCOUNTER_COST: ClassVar[float]
    DEFAULT_IMMUNIZATION_COST: ClassVar[float]
    DEFAULT_LAB_COST: ClassVar[float]
    DEFAULT_DEVICE_COST: ClassVar[float]
    DEFAULT_SUPPLY_COST: ClassVar[float]
    DEVICE_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]
    SUPPLY_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]
    MEDICATION_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]
    LAB_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]
    DIALYSIS_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]
    PROCEDURES_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]
    ENCOUNTER_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]

    def __init__(self) -> None:
        """Java: Costs#Costs.

        Java overloads:
        ()
        """

    @staticmethod
    def get_location_adjustment_factor(person: Person, table: dict[str, float]) -> float:
        """Java: Costs#getLocationAdjustmentFactor.

        Java overloads:
        (Person person, Map table)
        """
        # Retrieve the location adjustment factor.
        location_adjustment = 1.0
        if person is not None and Person.STATE in person.attributes:
            state = person.attributes.get(Person.STATE)
            abbreviation = Location.get_abbreviation(state)  # type: ignore[arg-type]
            if abbreviation in table:
                location_adjustment = table[abbreviation]
        return location_adjustment

    @staticmethod
    def get_encounter_adjustment_factor(person: Person, entry: HealthRecordEncounter) -> float:
        """Java: Costs#getEncounterAdjustmentFactor.

        Java overloads:
        (Person person, HealthRecord.Encounter entry)
        """
        # Retrieve the location adjustment factor.
        location_adjustment = 1.0
        if person is not None and Person.STATE in person.attributes:
            state = person.attributes.get(Person.STATE)
            abbreviation = Location.get_abbreviation(state)  # type: ignore[arg-type]
            # Java string concatenation renders a null abbreviation as "null".
            key = ("null" if abbreviation is None else abbreviation) + "|" + entry.type
            if key in Costs.ENCOUNTER_ADJUSTMENT_FACTORS:
                location_adjustment = Costs.ENCOUNTER_ADJUSTMENT_FACTORS[key]
        return location_adjustment

    @staticmethod
    def determine_cost_of_entry(entry: Entry, person: Person) -> float:
        """Java: Costs#determineCostOfEntry.

        Java overloads:
        (Entry entry, Person person)
        """
        from synthea.world.concepts.health_record import (
            Device,
            Encounter,
            Immunization,
            Medication,
            Procedure,
            Report,
            Supply,
        )

        # Retrieve the location adjustment factor.
        location_adjustment = 1.0
        default_cost = 0.0
        costs: dict[str, CostData] | None = None

        if isinstance(entry, Procedure):
            costs = Costs.PROCEDURE_COSTS
            default_cost = Costs.DEFAULT_PROCEDURE_COST
            dialysis = False
            for entry_code in entry.codes:
                if "dialysis" in entry_code.display.lower():
                    dialysis = True
            if dialysis:
                location_adjustment = Costs.get_location_adjustment_factor(
                    person, Costs.DIALYSIS_ADJUSTMENT_FACTORS
                )
            else:
                location_adjustment = Costs.get_location_adjustment_factor(
                    person, Costs.PROCEDURES_ADJUSTMENT_FACTORS
                )
        elif isinstance(entry, Medication):
            costs = Costs.MEDICATION_COSTS
            default_cost = Costs.DEFAULT_MEDICATION_COST
            location_adjustment = Costs.get_location_adjustment_factor(
                person, Costs.MEDICATION_ADJUSTMENT_FACTORS
            )
        elif isinstance(entry, Encounter):
            costs = Costs.ENCOUNTER_COSTS
            default_cost = Costs.DEFAULT_ENCOUNTER_COST
            location_adjustment = Costs.get_encounter_adjustment_factor(person, entry)
        elif isinstance(entry, Immunization):
            costs = Costs.IMMUNIZATION_COSTS
            default_cost = Costs.DEFAULT_IMMUNIZATION_COST
        elif isinstance(entry, Device):
            costs = Costs.DEVICE_COSTS
            default_cost = Costs.DEFAULT_DEVICE_COST
            location_adjustment = Costs.get_location_adjustment_factor(
                person, Costs.DEVICE_ADJUSTMENT_FACTORS
            )
        elif isinstance(entry, Supply):
            costs = Costs.SUPPLY_COSTS
            default_cost = Costs.DEFAULT_SUPPLY_COST
            location_adjustment = Costs.get_location_adjustment_factor(
                person, Costs.SUPPLY_ADJUSTMENT_FACTORS
            )
        elif isinstance(entry, Report):
            default_cost = Costs.DEFAULT_LAB_COST
            location_adjustment = Costs.get_location_adjustment_factor(
                person, Costs.LAB_ADJUSTMENT_FACTORS
            )
        else:
            # Not an entry type that has an associated cost.
            return 0.0

        if not entry.codes:
            # No specific code found — use default cost for this entry type
            return default_cost * location_adjustment
        code = entry.codes[0].code
        # Retrieve the base cost based on the code.
        if costs is not None and code in costs:
            base_cost = costs[code].choose_cost(person)
            if isinstance(entry, Medication):
                # baseCost for medications is PER UNIT, so need to multiply by quantity
                base_cost = base_cost * entry.get_quantity()
        else:
            base_cost = default_cost

        # Return the total cost of the given entry.
        return base_cost * location_adjustment

    @staticmethod
    def load_cost_data() -> None:
        """Java: Costs#loadCostData.

        Java overloads:
        ()
        """
        # intentionally do nothing
        # this method is only called to ensure the static data is loaded at a
        # predictable time (in Python, at import of this module)

    @staticmethod
    def parse_csv_to_map(filename: str) -> dict[str, CostData]:
        """Java: Costs#parseCsvToMap.

        Java overloads:
        (String filename)
        """
        raw_data = Utilities.read_resource_and_strip_bom(filename)
        lines = SimpleCSV.parse(raw_data)

        cost_map: dict[str, CostData] = {}
        for line in lines:
            code = line.get("CODE")
            min_str = line.get("MIN")
            mode_str = line.get("MODE")
            max_str = line.get("MAX")

            try:
                min_cost = parse_double(min_str)  # type: ignore[arg-type]
                mode = parse_double(mode_str)  # type: ignore[arg-type]
                max_cost = parse_double(max_str)  # type: ignore[arg-type]
                cost_map[code] = CostData(min_cost, mode, max_cost)  # type: ignore[index]
            except ValueError:
                # Java prints the error and a stack trace to System.err; the
                # stack trace has no Python counterpart and is not reproduced.
                print(
                    f"{filename}: Invalid cost for code: '{code}' -- costs should be "
                    f"numeric but were '{min_str}', '{mode_str}', '{max_str}'",
                    file=sys.stderr,
                )
                print(f"Code '{code}' will use the default cost", file=sys.stderr)
        return cost_map

    @staticmethod
    def parse_adjustment_factors(resource: str) -> dict[str, float]:
        """Java: Costs#parseAdjustmentFactors.

        Java overloads:
        (String resource)
        """
        raw_data = Utilities.read_resource_and_strip_bom(resource)
        lines = SimpleCSV.parse(raw_data)

        cost_map: dict[str, float] = {}
        for line in lines:
            state = line.get("STATE")
            factor_str = line.get("ADJ_FACTOR")
            try:
                factor = parse_double(factor_str)  # type: ignore[arg-type]
            except ValueError as exc:
                raise RuntimeError(f"Invalid cost adjustment factor: {factor_str}") from exc
            cost_map[state] = factor  # type: ignore[index]
        return cost_map

    @staticmethod
    def parse_encounter_adjustment_factors(resource: str) -> dict[str, float]:
        """Java: Costs#parseEncounterAdjustmentFactors.

        Java overloads:
        (String resource)
        """
        raw_data = Utilities.read_resource_and_strip_bom(resource)
        lines = SimpleCSV.parse(raw_data)

        cost_map: dict[str, float] = {}
        for line in lines:
            state = line.get("STATE")
            encounter_type = line.get("ENCOUNTER")
            key = state + "|" + encounter_type.lower()  # type: ignore[operator,union-attr]
            factor_str = line.get("ADJ_FACTOR")
            try:
                factor = parse_double(factor_str)  # type: ignore[arg-type]
            except ValueError as exc:
                raise RuntimeError(f"Invalid cost adjustment factor: {factor_str}") from exc
            cost_map[key] = factor
        return cost_map

    @staticmethod
    def parse_cost_method() -> DistributionKind:
        """Java: Costs#parseCostMethod.

        Java overloads:
        ()
        """
        config_value = Config.get("generate.costs.method", DistributionKind.TRIANGULAR.value)
        return DistributionKind(config_value.upper())  # type: ignore[union-attr]

    @staticmethod
    def has_cost(entry: Entry) -> bool:
        """Java: Costs#hasCost.

        Java overloads:
        (Entry entry)
        """
        from synthea.world.concepts.health_record import (
            Device,
            Encounter,
            Immunization,
            Medication,
            Procedure,
            Report,
            Supply,
        )

        return isinstance(
            entry, (Procedure, Medication, Encounter, Immunization, Report, Device, Supply)
        )

    @staticmethod
    def has_specified_cost(code: str) -> bool:
        """Java: Costs#hasSpecifiedCost.

        Java overloads:
        (String code)
        """
        return (
            code in Costs.PROCEDURE_COSTS
            or code in Costs.MEDICATION_COSTS
            or code in Costs.ENCOUNTER_COSTS
            or code in Costs.IMMUNIZATION_COSTS
            or code in Costs.DEVICE_COSTS
            or code in Costs.SUPPLY_COSTS
        )


class CostData:
    """Java: CostData."""

    def __init__(self, min: float, mode: float, max: float) -> None:
        """Java: CostData#CostData.

        Java overloads:
        (double min, double mode, double max)
        """
        self.min: float = min
        self.mode: float = mode
        self.max: float = max
        self.distribution: Distribution = Distribution()
        self.distribution.kind = Costs.COST_METHOD
        self.distribution.round = False
        self.distribution.parameters = {}
        method = Costs.COST_METHOD
        if method is DistributionKind.EXACT:
            self.distribution.parameters["value"] = self.mode
        elif method is DistributionKind.UNIFORM:
            self.distribution.parameters["low"] = self.min
            self.distribution.parameters["high"] = self.max
        elif method is DistributionKind.GAUSSIAN:
            self.distribution.parameters["mean"] = self.mode
            self.distribution.parameters["min"] = self.min
            self.distribution.parameters["max"] = self.max
            left = (self.mode - self.min) / 4.0
            right = (self.max - self.mode) / 4.0
            sd = left if left < right else right
            self.distribution.parameters["standardDeviation"] = sd
        elif method is DistributionKind.EXPONENTIAL:
            self.distribution.parameters["mean"] = self.mode
        elif method is DistributionKind.TRIANGULAR:
            self.distribution.parameters["min"] = self.min
            self.distribution.parameters["mode"] = self.mode
            self.distribution.parameters["max"] = self.max

    def choose_cost(self, person: Person) -> float:
        """Java: CostData#chooseCost.

        Java overloads:
        (Person person)
        """
        # Person's rand(low, high) overload is added by T09-fix #54; until
        # it lands, Person does not structurally match RandomSource to mypy.
        value = self.distribution.generate(cast(RandomSource, person))

        if Costs.COST_METHOD is DistributionKind.EXPONENTIAL:
            value = value - 1.0

        if value < self.min:
            value = self.min
        elif value > self.max:
            value = self.max
        return value


setattr(Costs, "CostData", CostData)  # noqa: B010


# Java static initializer, in declaration order.
Costs.COST_METHOD = Costs.parse_cost_method()
Costs.PROCEDURE_COSTS = Costs.parse_csv_to_map("costs/procedures.csv")
Costs.MEDICATION_COSTS = Costs.parse_csv_to_map("costs/medications.csv")
Costs.ENCOUNTER_COSTS = Costs.parse_csv_to_map("costs/encounters.csv")
Costs.IMMUNIZATION_COSTS = Costs.parse_csv_to_map("costs/immunizations.csv")
Costs.DEVICE_COSTS = Costs.parse_csv_to_map("costs/devices.csv")
Costs.SUPPLY_COSTS = Costs.parse_csv_to_map("costs/supplies.csv")
Costs.DEFAULT_PROCEDURE_COST = Config.get_as_double("generate.costs.default_procedure_cost", 500)
Costs.DEFAULT_MEDICATION_COST = Config.get_as_double("generate.costs.default_medication_cost", 255)
Costs.DEFAULT_ENCOUNTER_COST = Config.get_as_double("generate.costs.default_encounter_cost", 125)
Costs.DEFAULT_IMMUNIZATION_COST = Config.get_as_double(
    "generate.costs.default_immunization_cost", 136
)
Costs.DEFAULT_LAB_COST = Config.get_as_double("generate.costs.default_lab_cost", 100)
Costs.DEFAULT_DEVICE_COST = Config.get_as_double("generate.costs.default_device_cost", 0)
Costs.DEFAULT_SUPPLY_COST = Config.get_as_double("generate.costs.default_supply_cost", 0)
Costs.DEVICE_ADJUSTMENT_FACTORS = Costs.parse_adjustment_factors("costs/devices_adjustments.csv")
Costs.SUPPLY_ADJUSTMENT_FACTORS = Costs.parse_adjustment_factors("costs/supplies_adjustments.csv")
Costs.MEDICATION_ADJUSTMENT_FACTORS = Costs.parse_adjustment_factors(
    "costs/medications_adjustments.csv"
)
Costs.LAB_ADJUSTMENT_FACTORS = Costs.parse_adjustment_factors("costs/labs_adjustments.csv")
Costs.DIALYSIS_ADJUSTMENT_FACTORS = Costs.parse_adjustment_factors("costs/dialysis_adjustments.csv")
Costs.PROCEDURES_ADJUSTMENT_FACTORS = Costs.parse_adjustment_factors(
    "costs/procedures_adjustments.csv"
)
Costs.ENCOUNTER_ADJUSTMENT_FACTORS = Costs.parse_encounter_adjustment_factors(
    "costs/encounters_adjustments.csv"
)
