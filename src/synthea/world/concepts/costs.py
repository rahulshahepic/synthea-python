"""Java API skeleton: Costs.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.engine.distribution import Distribution
    from synthea.engine.distribution import Kind as DistributionKind
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Encounter as HealthRecordEncounter
    from synthea.world.concepts.health_record import Entry


class Costs:
    """Java: Costs; pending T14."""

    COST_METHOD: ClassVar[DistributionKind]  # Java initialization deferred to T14.
    PROCEDURE_COSTS: ClassVar[dict[str, CostData]]  # Java initialization deferred to T14.
    MEDICATION_COSTS: ClassVar[dict[str, CostData]]  # Java initialization deferred to T14.
    ENCOUNTER_COSTS: ClassVar[dict[str, CostData]]  # Java initialization deferred to T14.
    IMMUNIZATION_COSTS: ClassVar[dict[str, CostData]]  # Java initialization deferred to T14.
    DEVICE_COSTS: ClassVar[dict[str, CostData]]  # Java initialization deferred to T14.
    SUPPLY_COSTS: ClassVar[dict[str, CostData]]  # Java initialization deferred to T14.
    DEFAULT_PROCEDURE_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEFAULT_MEDICATION_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEFAULT_ENCOUNTER_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEFAULT_IMMUNIZATION_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEFAULT_LAB_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEFAULT_DEVICE_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEFAULT_SUPPLY_COST: ClassVar[float]  # Java initialization deferred to T14.
    DEVICE_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]  # Java initialization deferred to T14.
    SUPPLY_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]  # Java initialization deferred to T14.
    MEDICATION_ADJUSTMENT_FACTORS: ClassVar[
        dict[str, float]
    ]  # Java initialization deferred to T14.
    LAB_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]  # Java initialization deferred to T14.
    DIALYSIS_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]  # Java initialization deferred to T14.
    PROCEDURES_ADJUSTMENT_FACTORS: ClassVar[
        dict[str, float]
    ]  # Java initialization deferred to T14.
    ENCOUNTER_ADJUSTMENT_FACTORS: ClassVar[dict[str, float]]  # Java initialization deferred to T14.

    def __init__(self) -> None:
        """Java: Costs#Costs.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Costs#Costs — pending T14")

    @staticmethod
    def get_location_adjustment_factor(person: Person, table: dict[str, float]) -> float:
        """Java: Costs#getLocationAdjustmentFactor.

        Java overloads:
        (Person person, Map table)
        """
        raise NotImplementedError("Java: Costs#getLocationAdjustmentFactor — pending T14")

    @staticmethod
    def get_encounter_adjustment_factor(person: Person, entry: HealthRecordEncounter) -> float:
        """Java: Costs#getEncounterAdjustmentFactor.

        Java overloads:
        (Person person, HealthRecord.Encounter entry)
        """
        raise NotImplementedError("Java: Costs#getEncounterAdjustmentFactor — pending T14")

    @staticmethod
    def determine_cost_of_entry(entry: Entry, person: Person) -> float:
        """Java: Costs#determineCostOfEntry.

        Java overloads:
        (Entry entry, Person person)
        """
        raise NotImplementedError("Java: Costs#determineCostOfEntry — pending T14")

    @staticmethod
    def load_cost_data() -> None:
        """Java: Costs#loadCostData.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Costs#loadCostData — pending T14")

    @staticmethod
    def parse_csv_to_map(filename: str) -> dict[str, CostData]:
        """Java: Costs#parseCsvToMap.

        Java overloads:
        (String filename)
        """
        raise NotImplementedError("Java: Costs#parseCsvToMap — pending T14")

    @staticmethod
    def parse_adjustment_factors(resource: str) -> dict[str, float]:
        """Java: Costs#parseAdjustmentFactors.

        Java overloads:
        (String resource)
        """
        raise NotImplementedError("Java: Costs#parseAdjustmentFactors — pending T14")

    @staticmethod
    def parse_encounter_adjustment_factors(resource: str) -> dict[str, float]:
        """Java: Costs#parseEncounterAdjustmentFactors.

        Java overloads:
        (String resource)
        """
        raise NotImplementedError("Java: Costs#parseEncounterAdjustmentFactors — pending T14")

    @staticmethod
    def parse_cost_method() -> DistributionKind:
        """Java: Costs#parseCostMethod.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Costs#parseCostMethod — pending T14")

    @staticmethod
    def has_cost(entry: Entry) -> bool:
        """Java: Costs#hasCost.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: Costs#hasCost — pending T14")

    @staticmethod
    def has_specified_cost(code: str) -> bool:
        """Java: Costs#hasSpecifiedCost.

        Java overloads:
        (String code)
        """
        raise NotImplementedError("Java: Costs#hasSpecifiedCost — pending T14")


class CostData:
    """Java: CostData; pending T14."""

    def __init__(self, min: float, mode: float, max: float) -> None:
        """Java: CostData#CostData.

        Java overloads:
        (double min, double mode, double max)
        """
        self.min: float
        self.mode: float
        self.max: float
        self.distribution: Distribution
        raise NotImplementedError("Java: CostData#CostData — pending T14")

    def choose_cost(self, person: Person) -> float:
        """Java: CostData#chooseCost.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: CostData#chooseCost — pending T14")


setattr(Costs, "CostData", CostData)  # noqa: B010
