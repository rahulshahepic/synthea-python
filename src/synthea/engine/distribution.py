"""Java: org.mitre.synthea.engine.Distribution."""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Protocol, overload

from synthea.javacompat.numbers import math_round
from synthea.javacompat.random import _strict_log


def _java_divide(numerator: float, denominator: float) -> float:
    """Java: double division, including signed zero, NaN and infinities."""
    if denominator == 0.0:
        if numerator == 0.0 or math.isnan(numerator):
            return math.nan
        return math.copysign(math.inf, numerator * math.copysign(1.0, denominator))
    return numerator / denominator


def _java_log(value: float) -> float:
    """Java: Math#log with the reference VM's _dlog intrinsic disabled (#66).

    Reuse T01's fdlibm StrictMath.log; preserve IEEE zero, negative, NaN and infinity.
    """
    return -math.inf if value == 0.0 else math.nan if value < 0.0 else _strict_log(value)


def _java_sqrt(value: float) -> float:
    """Java: Math#sqrt, returning NaN for negative arguments."""
    return math.nan if value < 0.0 else math.sqrt(value)


class RandomSource(Protocol):
    """Java: Person random-number methods used by Distribution."""

    @overload
    def rand(self) -> float:
        """Java: Person#rand()."""
        ...

    @overload
    def rand(self, low: float, high: float) -> float:
        """Java: Person#rand(double,double)."""
        ...

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
        if self.kind is None:
            raise TypeError("Distribution kind is null")
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
            lam = _java_divide(-1.0, average)
            value = 1.0 + _java_divide(_java_log(1.0 - person.rand()), lam)
        elif self.kind == Kind.TRIANGULAR:
            minimum, mode, maximum = p["min"], p["mode"], p["max"]
            f = _java_divide(mode - minimum, maximum - minimum)
            draw = person.rand()
            if draw < f:
                value = minimum + _java_sqrt(draw * (maximum - minimum) * (mode - minimum))
            else:
                value = maximum - _java_sqrt((1.0 - draw) * (maximum - minimum) * (maximum - mode))
        else:
            value = -1.0
        if self.round:
            value = float(math_round(value))
        return value

    def validate(self) -> bool:
        """Java: Distribution#validate()."""
        if self.parameters is None:
            return False
        if self.kind is None:
            raise TypeError("Distribution kind is null")
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
