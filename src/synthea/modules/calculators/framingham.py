"""Java: org.mitre.synthea.modules.calculators.Framingham."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import d2i
from synthea.modules.calculators.ascvd import Inventory, _inventory
from synthea.world.concepts.vital_sign import VitalSign

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Framingham:
    """Java: Framingham Heart Study lookup calculators."""

    TEN_YEARS_IN_MS: ClassVar[int] = 315360000000
    age_chd_m: ClassVar[list[int]] = [-9, -9, -9, -4, 0, 3, 6, 8, 10, 11, 12, 13]
    age_chd_f: ClassVar[list[int]] = [-7, -7, -7, -3, 0, 3, 6, 8, 10, 12, 14, 16]
    age_chol_chd_m: ClassVar[list[list[int]]] = [
        [0, 4, 7, 9, 11],
        [0, 4, 7, 9, 11],
        [0, 3, 5, 6, 8],
        [0, 2, 3, 4, 5],
        [0, 1, 1, 2, 3],
        [0, 0, 0, 1, 1],
    ]
    age_chol_chd_f: ClassVar[list[list[int]]] = [
        [0, 4, 8, 11, 13],
        [0, 4, 8, 11, 13],
        [0, 3, 6, 8, 10],
        [0, 2, 4, 5, 7],
        [0, 1, 2, 3, 4],
        [0, 1, 1, 2, 2],
    ]
    age_smoke_chd_m: ClassVar[list[int]] = [8, 8, 5, 3, 1, 1]
    age_smoke_chd_f: ClassVar[list[int]] = [9, 9, 7, 4, 2, 1]
    sys_bp_chd_m: ClassVar[list[list[int]]] = [[0, 0], [1, 0], [2, 1], [2, 1], [2, 1], [3, 2]]
    sys_bp_chd_f: ClassVar[list[list[int]]] = [[0, 0], [3, 1], [4, 2], [5, 3], [5, 3], [6, 4]]
    hdl_lookup_chd: ClassVar[list[int]] = [2, 1, 0, -1]
    risk_chd_m: ClassVar[dict[int, float]] = {
        -1: 0.005,
        0: 0.01,
        1: 0.01,
        2: 0.01,
        3: 0.01,
        4: 0.01,
        5: 0.02,
        6: 0.02,
        7: 0.03,
        8: 0.04,
        9: 0.05,
        10: 0.06,
        11: 0.08,
        12: 0.1,
        13: 0.12,
        14: 0.16,
        15: 0.2,
        16: 0.25,
        17: 0.3,
    }
    risk_chd_f: ClassVar[dict[int, float]] = {
        8: 0.005,
        9: 0.01,
        10: 0.01,
        11: 0.01,
        12: 0.01,
        13: 0.02,
        14: 0.02,
        15: 0.03,
        16: 0.04,
        17: 0.05,
        18: 0.06,
        19: 0.08,
        20: 0.11,
        21: 0.14,
        22: 0.17,
        23: 0.22,
        24: 0.27,
        25: 0.3,
    }
    age_cvd_points: ClassVar[list[list[int]]] = [
        [0, 2, 5, 6, 8, 10, 11, 12, 14, 15],
        [0, 2, 4, 5, 7, 8, 9, 10, 11, 12],
    ]
    hdl_cvd_points: ClassVar[list[int]] = [2, 1, 1, 0, -1, -1, -2]
    totalChol_cvd_points: ClassVar[list[list[int]]] = [[0, 1, 2, 3, 4], [0, 1, 3, 4, 5]]
    sbp_cvd_points: ClassVar[list[list[list[int]]]] = [
        [[-2, 0, 1, 2, 2, 3], [0, 2, 3, 4, 4, 5]],
        [[-3, 0, 1, 2, 4, 5], [-1, 2, 3, 5, 6, 7]],
    ]
    cvd_smoker_points: ClassVar[list[int]] = [4, 3]
    cvd_diabetes_points: ClassVar[list[int]] = [3, 4]
    risk_cvd_m: ClassVar[dict[int, float]] = {
        -3: 0.01,
        -2: 0.011,
        -1: 0.014,
        0: 0.016,
        1: 0.019,
        2: 0.023,
        3: 0.028,
        4: 0.033,
        5: 0.039,
        6: 0.047,
        7: 0.056,
        8: 0.067,
        9: 0.079,
        10: 0.094,
        11: 0.112,
        12: 0.132,
        13: 0.156,
        14: 0.184,
        15: 0.216,
        16: 0.253,
        17: 0.294,
        18: 0.3,
    }
    risk_cvd_f: ClassVar[dict[int, float]] = {
        -2: 0.005,
        -1: 0.01,
        0: 0.012,
        1: 0.015,
        2: 0.017,
        3: 0.02,
        4: 0.024,
        5: 0.028,
        6: 0.033,
        7: 0.039,
        8: 0.045,
        9: 0.053,
        10: 0.063,
        11: 0.073,
        12: 0.086,
        13: 0.1,
        14: 0.117,
        15: 0.137,
        16: 0.159,
        17: 0.185,
        18: 0.215,
        19: 0.248,
        20: 0.285,
        21: 0.3,
    }
    age_af: ClassVar[list[list[int]]] = [[1, 2, 3, 4, 5, 6, 7, 7, 8], [-3, -2, 0, 1, 3, 4, 6, 7, 8]]
    risk_af_table: ClassVar[list[float]] = [
        0.01,
        0.02,
        0.02,
        0.03,
        0.04,
        0.06,
        0.08,
        0.12,
        0.16,
        0.22,
        0.3,
    ]
    stroke_rate_20_39: ClassVar[list[float]] = [0.002, 0.007]
    stroke_rate_40_59: ClassVar[list[float]] = [0.019, 0.022]
    ten_year_stroke_risk: ClassVar[list[list[float]]] = [
        [
            0,
            0.03,
            0.03,
            0.04,
            0.04,
            0.05,
            0.05,
            0.06,
            0.07,
            0.08,
            0.1,
            0.11,
            0.13,
            0.15,
            0.17,
            0.2,
            0.22,
            0.26,
            0.29,
            0.33,
            0.37,
            0.42,
            0.47,
            0.52,
            0.57,
            0.63,
            0.68,
            0.74,
            0.79,
            0.84,
            0.88,
        ],
        [
            0,
            0.01,
            0.01,
            0.02,
            0.02,
            0.02,
            0.03,
            0.04,
            0.04,
            0.05,
            0.06,
            0.08,
            0.09,
            0.11,
            0.13,
            0.16,
            0.19,
            0.23,
            0.27,
            0.32,
            0.37,
            0.43,
            0.5,
            0.57,
            0.64,
            0.71,
            0.78,
            0.84,
        ],
    ]
    age_stroke: ClassVar[list[list[int]]] = [
        [54, 57, 60, 63, 66, 69, 73, 76, 79, 82, 85],
        [54, 57, 60, 63, 65, 68, 71, 74, 77, 79, 82],
    ]
    untreated_sys_bp_stroke: ClassVar[list[list[int]]] = [
        [0, 106, 116, 126, 136, 146, 156, 166, 176, 185, 196],
        [0, 95, 107, 119, 131, 144, 156, 168, 181, 193, 205],
    ]
    treated_sys_bp_stroke: ClassVar[list[list[int]]] = [
        [0, 106, 113, 118, 124, 130, 136, 143, 151, 162, 177],
        [0, 95, 107, 114, 120, 126, 132, 140, 149, 161, 205],
    ]
    diabetes_stroke: ClassVar[list[float]] = [2, 3]
    chd_stroke_points: ClassVar[list[float]] = [4, 2]
    atrial_fibrillation_stroke_points: ClassVar[list[float]] = [4, 6]

    def __init__(self) -> None:
        """Java: Framingham#Framingham, implicit empty constructor."""

    @staticmethod
    def bound(value: int, min: int, max: int) -> int:
        """Java: Framingham#bound."""
        return min if value < min else max if value > max else value

    @staticmethod
    def chd10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#chd10Year; integer quotients truncate towards zero."""
        f = Framingham
        age = person.age_in_years(time)
        male = person.attributes.get("gender") == "M"
        sbp = person.get_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, time)
        dbp = person.get_vital_sign(VitalSign.DIASTOLIC_BLOOD_PRESSURE, time)
        chol = person.get_vital_sign(VitalSign.TOTAL_CHOLESTEROL, time)
        if sbp is None or dbp is None or chol is None:
            return -1.0
        treated = bool(person.attributes.get("blood_pressure_controlled", False))
        hdl = person.get_vital_sign(VitalSign.HDL, time)
        short = f.bound(int((age - 20) / 5), 0, 11)
        long = f.bound(int((age - 20) / 10), 0, 5)
        crange = f.bound(int((d2i(chol) - 160) / 40) + 1, 0, 4)
        brange = f.bound(int((d2i(sbp) - 120) / 10) + 1, 0, 5)
        points = (f.age_chd_m if male else f.age_chd_f)[short]
        points += (f.age_chol_chd_m if male else f.age_chol_chd_f)[long][crange]
        if person.attributes.get("smoker", False):
            points += (f.age_smoke_chd_m if male else f.age_smoke_chd_f)[long]
        hrange = f.bound(int((d2i(hdl) - 40) / 10) + 1, 0, 3)
        points += f.hdl_lookup_chd[hrange]
        points += (f.sys_bp_chd_m if male else f.sys_bp_chd_f)[brange][0 if treated else 1]
        risk = (
            f.risk_chd_m[f.bound(points, 0, 17)] if male else f.risk_chd_f[f.bound(points, 8, 25)]
        )
        return Utilities.convert_risk_to_timestep(risk, f.TEN_YEARS_IN_MS) if per_timestep else risk

    @staticmethod
    def cvd10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#cvd10Year."""
        f = Framingham
        age = person.age_in_years(time)
        if age < 30:
            return -1.0
        male = person.attributes.get("gender") == "M"
        sbp = person.get_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, time)
        chol = person.get_vital_sign(VitalSign.TOTAL_CHOLESTEROL, time)
        if sbp is None or chol is None:
            return -1.0
        treated = bool(person.attributes.get("blood_pressure_controlled", False))
        hdl = person.get_vital_sign(VitalSign.HDL, time)
        g = 0 if male else 1
        points = f.age_cvd_points[g][f.bound(int((age - 30) / 5), 0, 9)]
        points += f.hdl_cvd_points[f.bound(int((d2i(hdl) - 35) / 5) + 1, 0, 6)]
        points += f.totalChol_cvd_points[g][f.bound(int((d2i(chol) - 160) / 40) + 1, 0, 4)]
        points += f.sbp_cvd_points[g][int(treated)][f.bound(int((d2i(sbp) - 120) / 10) + 1, 0, 5)]
        if person.attributes.get("smoker", False):
            points += f.cvd_smoker_points[g]
        if person.attributes.get("diabetes", False):
            points += f.cvd_diabetes_points[g]
        risk = (
            f.risk_cvd_m[f.bound(points, -3, 18)] if male else f.risk_cvd_f[f.bound(points, -2, 21)]
        )
        return Utilities.convert_risk_to_timestep(risk, f.TEN_YEARS_IN_MS) if per_timestep else risk

    @staticmethod
    def atrial_fibrillation10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#atrialFibrillation10Year, including attribute presence semantics."""
        f = Framingham
        age = person.age_in_years(time)
        if age < 45 or "atrial_fibrillation" in person.attributes:
            return -1.0
        if person.get_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, time) is None:
            return -1.0
        if person.get_vital_sign(VitalSign.BMI, time) is None:
            return -1.0
        g = 0 if person.attributes.get("gender") == "M" else 1
        score = f.age_af[g][min(int((age - 45) / 5), 8)]
        if person.get_vital_sign(VitalSign.BMI, time) >= 30:
            score += 1
        if person.get_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, time) >= 160:
            score += 1
        if person.attributes.get("blood_pressure_controlled", False):
            score += 1
        risk = f.risk_af_table[f.bound(score, 0, 10)]
        return Utilities.convert_risk_to_timestep(risk, f.TEN_YEARS_IN_MS) if per_timestep else risk

    @staticmethod
    def get_index_for_value_in_rangelist(value: int, data: list[int]) -> int:
        """Java: Framingham#getIndexForValueInRangelist; both bounds inclusive."""
        for i in range(len(data) - 1):
            if data[i] <= value <= data[i + 1]:
                return i
        if value >= data[-1]:
            return len(data) - 1
        raise RuntimeError(f"unexpected value {value} for data {data}")

    @staticmethod
    def stroke10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#stroke10Year."""
        f = Framingham
        bp = person.get_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, time)
        if bp is None:
            return -1.0
        g = 0 if person.attributes.get("gender") == "M" else 1
        age = person.age_in_years(time)
        if age < 20:
            return -1.0
        if age < 40:
            risk = f.stroke_rate_20_39[g]
        elif age < 55:
            risk = f.stroke_rate_40_59[g]
        else:
            points = 3 if person.attributes.get("smoker", False) else 0
            if person.attributes.get("left_ventricular_hypertrophy", False):
                points += 5
            points += f.get_index_for_value_in_rangelist(age, f.age_stroke[g])
            table = (
                f.treated_sys_bp_stroke
                if person.attributes.get("blood_pressure_controlled", False)
                else f.untreated_sys_bp_stroke
            )
            points += f.get_index_for_value_in_rangelist(d2i(bp), table[g])
            if person.attributes.get("diabetes", False):
                points = int(points + f.diabetes_stroke[g])
            if person.attributes.get("coronary_heart_disease", False):
                points = int(points + f.chd_stroke_points[g])
            if "atrial_fibrillation" in person.attributes:
                points = int(points + f.atrial_fibrillation_stroke_points[g])
            risk = f.ten_year_stroke_risk[g][min(points, len(f.ten_year_stroke_risk[g]) - 1)]
        return Utilities.convert_risk_to_timestep(risk, f.TEN_YEARS_IN_MS) if per_timestep else risk

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: Framingham#inventoryAttributes."""
        for key, example in [
            ("atrial_fibrillation", "ConditionOnset"),
            ("blood_pressure_controlled", "true"),
            ("coronary_heart_disease", "true"),
            ("diabetes", "true"),
            ("left_ventricular_hypertrophy", "false"),
            ("gender", "M"),
            ("smoker", "true"),
        ]:
            _inventory(attributes, "Framingham", key, True, False, example)
