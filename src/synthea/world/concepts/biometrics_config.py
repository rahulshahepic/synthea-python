"""Java API skeleton: BiometricsConfig.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.helpers.simple_yml import SimpleYML


class BiometricsConfig:
    """Java: BiometricsConfig; pending T11."""

    biometrics: ClassVar[SimpleYML]  # Java initialization deferred to T11.

    def __init__(self) -> None:
        """Java: BiometricsConfig#BiometricsConfig.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: BiometricsConfig#BiometricsConfig — pending T11")

    @staticmethod
    def load_yml() -> SimpleYML:
        """Java: BiometricsConfig#loadYML.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: BiometricsConfig#loadYML — pending T11")

    @staticmethod
    def get(path: str, default_value: object | None = None) -> object:
        """Java: BiometricsConfig#get.

        Java overloads:
        (String path)
        (String path, Object defaultValue)
        """
        raise NotImplementedError("Java: BiometricsConfig#get — pending T11")

    @staticmethod
    def ints(path: str) -> list[int]:
        """Java: BiometricsConfig#ints.

        Java overloads:
        (String path)
        """
        raise NotImplementedError("Java: BiometricsConfig#ints — pending T11")

    @staticmethod
    def doubles(path: str) -> list[float]:
        """Java: BiometricsConfig#doubles.

        Java overloads:
        (String path)
        """
        raise NotImplementedError("Java: BiometricsConfig#doubles — pending T11")
