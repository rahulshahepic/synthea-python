"""Java: org.mitre.synthea.world.concepts.BMI."""

from __future__ import annotations

import math


class BMI:
    """Java: BMI."""

    def __init__(self) -> None:
        """Java: BMI#BMI (implicit public constructor)."""

    @staticmethod
    def calculate(height_cm: float, weight_kg: float) -> float:
        """Java: BMI#calculate, including IEEE-754 division by zero."""
        denominator = (height_cm / 100.0) * (height_cm / 100.0)
        if denominator == 0.0:
            if weight_kg == 0.0 or math.isnan(weight_kg):
                return math.nan
            return math.copysign(math.inf, weight_kg) * math.copysign(1.0, denominator)
        return weight_kg / denominator

    @staticmethod
    def weight_for_height_and_bmi(height_cm: float, bmi: float) -> float:
        """Java: BMI#weightForHeightAndBMI, preserving operation order."""
        return (height_cm / 100.0) * (height_cm / 100.0) * bmi
