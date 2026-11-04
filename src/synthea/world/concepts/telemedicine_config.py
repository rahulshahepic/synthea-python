"""Java API skeleton: TelemedicineConfig.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:

    class EnumeratedDistribution(Protocol):
        """Java boundary type: EnumeratedDistribution; external to the mapped Python port."""


class TelemedicineConfig:
    """Java: TelemedicineConfig; pending T11."""

    AMBULATORY: ClassVar[str] = "ambulatory"
    EMERGENCY: ClassVar[str] = "emergency"
    TELEMEDICINE: ClassVar[str] = "telemedicine"

    def __init__(self) -> None:
        """Java: TelemedicineConfig#TelemedicineConfig.

        Java overloads:
        ()
        """
        self.telemedicine_start_time: int
        self.high_emergency_use_insurance_names: list[str]
        self.pre_telemed_high_emergency: EnumeratedDistribution
        self.pre_telemed_typical_emergency: EnumeratedDistribution
        self.telemed_high_emergency: EnumeratedDistribution
        self.telemed_typical_emergency: EnumeratedDistribution
        raise NotImplementedError("Java: TelemedicineConfig#TelemedicineConfig — pending T11")

    def get_telemedicine_start_time(self) -> int:
        """Java: TelemedicineConfig#getTelemedicineStartTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TelemedicineConfig#getTelemedicineStartTime — pending T11")

    def get_high_emergency_use_insurance_names(self) -> list[str]:
        """Java: TelemedicineConfig#getHighEmergencyUseInsuranceNames.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: TelemedicineConfig#getHighEmergencyUseInsuranceNames — pending T11"
        )

    def get_pre_telemed_high_emergency(self) -> EnumeratedDistribution:
        """Java: TelemedicineConfig#getPreTelemedHighEmergency.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: TelemedicineConfig#getPreTelemedHighEmergency — pending T11"
        )

    def get_pre_telemed_typical_emergency(self) -> EnumeratedDistribution:
        """Java: TelemedicineConfig#getPreTelemedTypicalEmergency.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: TelemedicineConfig#getPreTelemedTypicalEmergency — pending T11"
        )

    def get_telemed_high_emergency(self) -> EnumeratedDistribution:
        """Java: TelemedicineConfig#getTelemedHighEmergency.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TelemedicineConfig#getTelemedHighEmergency — pending T11")

    def get_telemed_typical_emergency(self) -> EnumeratedDistribution:
        """Java: TelemedicineConfig#getTelemedTypicalEmergency.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: TelemedicineConfig#getTelemedTypicalEmergency — pending T11"
        )

    @staticmethod
    def from_json() -> TelemedicineConfig:
        """Java: TelemedicineConfig#fromJSON.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TelemedicineConfig#fromJSON — pending T11")


class TelemedicineProbabilities:
    """Java: TelemedicineProbabilities; pending T11."""

    def __init__(self, json: dict[str, float]) -> None:
        """Java: TelemedicineProbabilities#TelemedicineProbabilities.

        Java overloads:
        (Map json)
        """
        self.ambulatory: float
        self.emergency: float
        self.telemedicine: float
        raise NotImplementedError(
            "Java: TelemedicineProbabilities#TelemedicineProbabilities — pending T11"
        )

    def to_enumerated_distribution(self) -> EnumeratedDistribution:
        """Java: TelemedicineProbabilities#toEnumeratedDistribution.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: TelemedicineProbabilities#toEnumeratedDistribution — pending T11"
        )


setattr(TelemedicineConfig, "TelemedicineProbabilities", TelemedicineProbabilities)  # noqa: B010
