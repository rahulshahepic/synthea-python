"""Java API skeleton: Framingham.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class Framingham:
    """Java: Framingham; pending T23."""

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
        """Java: Framingham#Framingham.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Framingham#Framingham — pending T23")

    @staticmethod
    def bound(value: int, min: int, max: int) -> int:
        """Java: Framingham#bound.

        Java overloads:
        (int value, int min, int max)
        """
        raise NotImplementedError("Java: Framingham#bound — pending T23")

    @staticmethod
    def chd10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#chd10Year.

        Java overloads:
        (Person person, long time, boolean perTimestep)
        """
        raise NotImplementedError("Java: Framingham#chd10Year — pending T23")

    @staticmethod
    def cvd10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#cvd10Year.

        Java overloads:
        (Person person, long time, boolean perTimestep)
        """
        raise NotImplementedError("Java: Framingham#cvd10Year — pending T23")

    @staticmethod
    def atrial_fibrillation10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#atrialFibrillation10Year.

        Java overloads:
        (Person person, long time, boolean perTimestep)
        """
        raise NotImplementedError("Java: Framingham#atrialFibrillation10Year — pending T23")

    @staticmethod
    def get_index_for_value_in_rangelist(value: int, data: list[int]) -> int:
        """Java: Framingham#getIndexForValueInRangelist.

        Java overloads:
        (int value, int data)
        """
        raise NotImplementedError("Java: Framingham#getIndexForValueInRangelist — pending T23")

    @staticmethod
    def stroke10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: Framingham#stroke10Year.

        Java overloads:
        (Person person, long time, boolean perTimestep)
        """
        raise NotImplementedError("Java: Framingham#stroke10Year — pending T23")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: Framingham#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: Framingham#inventoryAttributes — pending T23")
