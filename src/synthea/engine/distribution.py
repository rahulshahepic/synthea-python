"""Java port skeleton: java/src/main/java/org/mitre/synthea/engine/Distribution.java."""

from __future__ import annotations

from enum import StrEnum


class Distribution:
    """Java: Distribution; pending T07."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Distribution constructor; pending T07."""
        raise NotImplementedError("Java: Distribution#constructor — pending T07")

    def generate(self, *args: object, **kwargs: object) -> object:
        """Java: Distribution#generate; pending T07."""
        raise NotImplementedError("Java: Distribution#generate — pending T07")

    def validate(self, *args: object, **kwargs: object) -> object:
        """Java: Distribution#validate; pending T07."""
        raise NotImplementedError("Java: Distribution#validate — pending T07")


class Kind(StrEnum):
    """Java: Distribution.Kind; pending T07."""

    EXACT = "EXACT"
    GAUSSIAN = "GAUSSIAN"
    UNIFORM = "UNIFORM"
    EXPONENTIAL = "EXPONENTIAL"
    TRIANGULAR = "TRIANGULAR"
