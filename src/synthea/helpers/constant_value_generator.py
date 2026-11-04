"""Java port skeleton: java/src/main/java/org/mitre/synthea/helpers/ConstantValueGenerator.java."""

from __future__ import annotations

from synthea.helpers.value_generator import ValueGenerator


class ConstantValueGenerator(ValueGenerator):
    """Java: ConstantValueGenerator; pending T07."""

    def __init__(self, person: object, value: float) -> None:
        """Java: ConstantValueGenerator#ConstantValueGenerator(Person,double); pending T07."""
        self.value: float = value
        raise NotImplementedError("Java: ConstantValueGenerator#constructor — pending T07")

    def get_value(self, time: int) -> float:
        """Java: ConstantValueGenerator#getValue; pending T07."""
        raise NotImplementedError("Java: ConstantValueGenerator#getValue — pending T07")
