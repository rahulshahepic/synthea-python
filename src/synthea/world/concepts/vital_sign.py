"""Java port skeleton: java/src/main/java/org/mitre/synthea/world/concepts/VitalSign.java."""

from __future__ import annotations

from enum import StrEnum


class VitalSign(StrEnum):
    """Java: VitalSign; pending T11."""
    HEIGHT = "HEIGHT"
    WEIGHT = "WEIGHT"
    HEIGHT_PERCENTILE = "HEIGHT_PERCENTILE"
    WEIGHT_PERCENTILE = "WEIGHT_PERCENTILE"
    BMI = "BMI"
    HEAD = "HEAD"
    HEAD_PERCENTILE = "HEAD_PERCENTILE"
    SYSTOLIC_BLOOD_PRESSURE = "SYSTOLIC_BLOOD_PRESSURE"
    DIASTOLIC_BLOOD_PRESSURE = "DIASTOLIC_BLOOD_PRESSURE"
    OXYGEN_SATURATION = "OXYGEN_SATURATION"
    BLOOD_GLUCOSE = "BLOOD_GLUCOSE"
    GLUCOSE = "GLUCOSE"
    UREA_NITROGEN = "UREA_NITROGEN"
    CREATININE = "CREATININE"
    CALCIUM = "CALCIUM"
    SODIUM = "SODIUM"
    POTASSIUM = "POTASSIUM"
    CHLORIDE = "CHLORIDE"
    CARBON_DIOXIDE = "CARBON_DIOXIDE"
    TOTAL_CHOLESTEROL = "TOTAL_CHOLESTEROL"
    TRIGLYCERIDES = "TRIGLYCERIDES"
    LDL = "LDL"
    HDL = "HDL"
    MICROALBUMIN_CREATININE_RATIO = "MICROALBUMIN_CREATININE_RATIO"
    EGFR = "EGFR"
    LVEF = "LVEF"
    HEART_RATE = "HEART_RATE"
    RESPIRATION_RATE = "RESPIRATION_RATE"

    def from_string(self, *args: object, **kwargs: object) -> object:
        """Java: VitalSign#fromString; pending T11."""
        raise NotImplementedError("Java: VitalSign#fromString — pending T11")

    def to_string(self, *args: object, **kwargs: object) -> object:
        """Java: VitalSign#toString; pending T11."""
        raise NotImplementedError("Java: VitalSign#toString — pending T11")
