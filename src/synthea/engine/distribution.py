"""Java: org.mitre.synthea.engine.Distribution."""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Protocol, overload

from synthea.javacompat.numbers import math_round


class RandomSource(Protocol):
    """Java: Person random-number methods used by Distribution."""

    @overload
    def rand(self) -> float: ...

    @overload
    def rand(self, low: float, high: float) -> float: ...

    def rand_gaussian(self) -> float:
        """Java: Person#randGaussian()."""
        ...


class Kind(StrEnum):
    """Java: Distribution.Kind."""

    EXACT = "EXACT"
    GAUSSIAN = "GAUSSIAN"
    UNIFORM = "UNIFORM"
    EXPONENTIAL = "EXPONENTIAL"
    TRIANGULAR = "TRIANGULAR"


class Distribution:
    """Java: org.mitre.synthea.engine.Distribution."""

    Kind = Kind

    def __init__(self) -> None:
        """Java: Distribution#Distribution()."""
        self.kind: Kind | None = None
        self.round: bool | None = None
        self.parameters: dict[str, float] | None = None

    def generate(self, person: RandomSource) -> float:
        """Java: Distribution#generate(Person)."""
        if self.parameters is None:
            raise TypeError("Distribution parameters are null")
        p = self.parameters
        if self.kind == Kind.EXACT:
            value = p["value"]
        elif self.kind == Kind.UNIFORM:
            value = person.rand(p["low"], p["high"])
        elif self.kind == Kind.GAUSSIAN:
            value = p["standardDeviation"] * person.rand_gaussian() + p["mean"]
            if "min" in p and value < p["min"]:
                value = p["min"]
            if "max" in p and value > p["max"]:
                value = p["max"]
        elif self.kind == Kind.EXPONENTIAL:
            average = p["mean"]
            lam = -1.0 / average
            value = 1.0 + math.log(1.0 - person.rand()) / lam
        elif self.kind == Kind.TRIANGULAR:
            minimum, mode, maximum = p["min"], p["mode"], p["max"]
            f = (mode - minimum) / (maximum - minimum)
            draw = person.rand()
            if draw < f:
                value = minimum + math.sqrt(draw * (maximum - minimum) * (mode - minimum))
            else:
                value = maximum - math.sqrt((1.0 - draw) * (maximum - minimum) * (maximum - mode))
        else:
            value = -1.0
        if self.round:
            value = float(math_round(value))
        return value

    def validate(self) -> bool:
        """Java: Distribution#validate()."""
        if self.parameters is None:
            return False
        required = {
            Kind.EXACT: ("value",),
            Kind.UNIFORM: ("low", "high"),
            Kind.GAUSSIAN: ("mean", "standardDeviation"),
            Kind.EXPONENTIAL: ("mean",),
            Kind.TRIANGULAR: ("min", "mode", "max"),
        }
        return (
            all(key in self.parameters for key in required.get(self.kind, ()))
            if self.kind in required
            else False
        )
