"""Java API skeleton: VitalSign.java."""

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

    @staticmethod
    def from_string(text: str) -> VitalSign:
        """Java: VitalSign#fromString.

        Java overloads:
        (String text)
        """
        raise NotImplementedError("Java: VitalSign#fromString — pending T11")

    def to_string(self) -> str:
        """Java: VitalSign#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: VitalSign#toString — pending T11")


# Java static data initialization; constructors remain stubs.
VITAL_SIGN_DISPLAY_NAMES: dict[VitalSign, str] = {
    VitalSign.HEIGHT: "Height",
    VitalSign.WEIGHT: "Weight",
    VitalSign.HEIGHT_PERCENTILE: "Height Percentile",
    VitalSign.WEIGHT_PERCENTILE: "Weight Percentile",
    VitalSign.BMI: "BMI",
    VitalSign.HEAD: "Head Circumference",
    VitalSign.HEAD_PERCENTILE: "Head Circumference Percentile",
    VitalSign.SYSTOLIC_BLOOD_PRESSURE: "Systolic Blood Pressure",
    VitalSign.DIASTOLIC_BLOOD_PRESSURE: "Diastolic Blood Pressure",
    VitalSign.OXYGEN_SATURATION: "Oxygen Saturation",
    VitalSign.BLOOD_GLUCOSE: "Blood Glucose",
    VitalSign.GLUCOSE: "Glucose",
    VitalSign.UREA_NITROGEN: "Urea Nitrogen",
    VitalSign.CREATININE: "Creatinine",
    VitalSign.CALCIUM: "Calcium",
    VitalSign.SODIUM: "Sodium",
    VitalSign.POTASSIUM: "Potassium",
    VitalSign.CHLORIDE: "Chloride",
    VitalSign.CARBON_DIOXIDE: "Carbon Dioxide",
    VitalSign.TOTAL_CHOLESTEROL: "Total Cholesterol",
    VitalSign.TRIGLYCERIDES: "Triglycerides",
    VitalSign.LDL: "LDL",
    VitalSign.HDL: "HDL",
    VitalSign.MICROALBUMIN_CREATININE_RATIO: "Microalbumin Creatinine Ratio",
    VitalSign.EGFR: "EGFR",
    VitalSign.LVEF: "Left ventricular Ejection fraction",
    VitalSign.HEART_RATE: "Heart Rate",
    VitalSign.RESPIRATION_RATE: "Respiration Rate",
}
