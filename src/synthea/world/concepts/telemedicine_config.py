"""Java: telemedicine_config skeleton (pending implementation)."""

from __future__ import annotations


class TelemedicineConfig:
    """Java: TelemedicineConfig; pending T11."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: TelemedicineConfig constructor; pending T11."""
        self.telemedicineStartTime: int = 0
        self.highEmergencyUseInsuranceNames: list[object] = []
        self.preTelemedHighEmergency: object | None = None
        self.preTelemedTypicalEmergency: object | None = None
        self.telemedHighEmergency: object | None = None
        self.telemedTypicalEmergency: object | None = None
        raise NotImplementedError("Java: TelemedicineConfig#constructor — pending T11")

    def to_enumerated_distribution(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#toEnumeratedDistribution; pending T11."""
        raise NotImplementedError("Java: TelemedicineConfig#toEnumeratedDistribution — pending T11")

    def get_telemedicine_start_time(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#getTelemedicineStartTime; pending T11."""
        raise NotImplementedError("Java: TelemedicineConfig#getTelemedicineStartTime — pending T11")

    def get_high_emergency_use_insurance_names(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#getHighEmergencyUseInsuranceNames; pending T11."""
        raise NotImplementedError(
            "Java: TelemedicineConfig#getHighEmergencyUseInsuranceNames — pending T11"
        )

    def get_pre_telemed_high_emergency(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#getPreTelemedHighEmergency; pending T11."""
        raise NotImplementedError(
            "Java: TelemedicineConfig#getPreTelemedHighEmergency — pending T11"
        )

    def get_pre_telemed_typical_emergency(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#getPreTelemedTypicalEmergency; pending T11."""
        raise NotImplementedError(
            "Java: TelemedicineConfig#getPreTelemedTypicalEmergency — pending T11"
        )

    def get_telemed_high_emergency(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#getTelemedHighEmergency; pending T11."""
        raise NotImplementedError("Java: TelemedicineConfig#getTelemedHighEmergency — pending T11")

    def get_telemed_typical_emergency(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#getTelemedTypicalEmergency; pending T11."""
        raise NotImplementedError(
            "Java: TelemedicineConfig#getTelemedTypicalEmergency — pending T11"
        )

    def from_json(self, *args: object, **kwargs: object) -> object:
        """Java: TelemedicineConfig#fromJSON; pending T11."""
        raise NotImplementedError("Java: TelemedicineConfig#fromJSON — pending T11")


class TelemedicineProbabilities:
    """Java: TelemedicineProbabilities; pending T11."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: TelemedicineProbabilities constructor; pending T11."""
        self.ambulatory: float = 0.0
        self.emergency: float = 0.0
        self.telemedicine: float = 0.0
        raise NotImplementedError("Java: TelemedicineProbabilities#constructor — pending T11")
