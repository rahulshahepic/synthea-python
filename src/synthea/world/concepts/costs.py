"""Java API skeleton for costs.py.
Java: org.mitre.synthea.world.concepts.Costs.
"""

from __future__ import annotations


class Costs:
    """Java: Costs; pending T14."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Costs constructor; pending T14."""
        raise NotImplementedError("Java: Costs — pending T14")

    def get_location_adjustment_factor(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#getLocationAdjustmentFactor."""
        raise NotImplementedError("Java: getLocationAdjustmentFactor — pending T14")

    def get_encounter_adjustment_factor(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#getEncounterAdjustmentFactor."""
        raise NotImplementedError("Java: getEncounterAdjustmentFactor — pending T14")

    def determine_cost_of_entry(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#determineCostOfEntry."""
        raise NotImplementedError("Java: determineCostOfEntry — pending T14")

    def load_cost_data(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#loadCostData."""
        raise NotImplementedError("Java: loadCostData — pending T14")

    def parse_csv_to_map(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#parseCsvToMap."""
        raise NotImplementedError("Java: parseCsvToMap — pending T14")

    def parse_adjustment_factors(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#parseAdjustmentFactors."""
        raise NotImplementedError("Java: parseAdjustmentFactors — pending T14")

    def parse_encounter_adjustment_factors(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#parseEncounterAdjustmentFactors."""
        raise NotImplementedError("Java: parseEncounterAdjustmentFactors — pending T14")

    def parse_cost_method(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#parseCostMethod."""
        raise NotImplementedError("Java: parseCostMethod — pending T14")

    def has_cost(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#hasCost."""
        raise NotImplementedError("Java: hasCost — pending T14")

    def has_specified_cost(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#hasSpecifiedCost."""
        raise NotImplementedError("Java: hasSpecifiedCost — pending T14")

    def choose_cost(self, *args: object, **kwargs: object) -> object:
        """Java: Costs#chooseCost."""
        raise NotImplementedError("Java: chooseCost — pending T14")


class CostData:
    """Java: CostData; pending T14."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: CostData constructor; pending T14."""
        self.min: float = 0.0
        self.mode: float = 0.0
        self.max: float = 0.0
        self.distribution: object | None = None
        raise NotImplementedError("Java: CostData — pending T14")
