"""Java: BiometricsConfig.java."""

from __future__ import annotations

from typing import ClassVar

from synthea.helpers.simple_yml import SimpleYML
from synthea.helpers.utilities import Utilities


class BiometricsConfig:
    """Java: BiometricsConfig."""

    biometrics: ClassVar[SimpleYML]  # Java initialization deferred to T11.

    def __init__(self) -> None:
        """Java: BiometricsConfig#BiometricsConfig.

        Java overloads:
        ()
        """
        raise TypeError("BiometricsConfig is abstract")

    @staticmethod
    def load_yml() -> SimpleYML:
        """Java: BiometricsConfig#loadYML.

        Java overloads:
        ()
        """
        return SimpleYML(Utilities.read_resource("biometrics.yml"))

    @staticmethod
    def get(path: str, default_value: object | None = None) -> object:
        """Java: BiometricsConfig#get.

        Java overloads:
        (String path)
        (String path, Object defaultValue)
        """
        value = BiometricsConfig.biometrics.get(path)
        return default_value if value is None else value

    @staticmethod
    def ints(path: str) -> list[int]:
        """Java: BiometricsConfig#ints.

        Java overloads:
        (String path)
        """
        values = BiometricsConfig.get(path)
        if not isinstance(values, list) or any(type(v) is not int for v in values):
            raise TypeError("expected List<Integer>")
        return list(values)

    @staticmethod
    def doubles(path: str) -> list[float]:
        """Java: BiometricsConfig#doubles.

        Java overloads:
        (String path)
        """
        values = BiometricsConfig.get(path)
        if not isinstance(values, list) or any(type(v) not in (int, float) for v in values):
            raise TypeError("expected List<Number>")
        return [float(value) for value in values]


BiometricsConfig.biometrics = BiometricsConfig.load_yml()
