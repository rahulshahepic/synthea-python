"""Java: org.mitre.synthea.world.concepts.TelemedicineConfig."""

from __future__ import annotations

import json
import math
from bisect import bisect_left
from datetime import date
from typing import ClassVar, cast

from synthea.helpers.synced_enumerated_distro import _Well19937c
from synthea.helpers.utilities import Utilities


class EnumeratedDistribution:
    """Java: Apache Commons Math 3.6.1 EnumeratedDistribution<String> boundary.

    Synthea reseeds immediately before sampling. Java's unseeded constructor uses
    wall-clock/identity entropy; require that explicit reseed for reproducibility.
    """

    def __init__(self, pmf: list[tuple[str, float]]) -> None:
        """Java: EnumeratedDistribution#EnumeratedDistribution(List)."""
        total = 0.0
        for _, probability in pmf:
            if not math.isfinite(probability) or probability < 0:
                raise ValueError("probabilities must be nonnegative finite numbers")
            total += probability
        if total == 0.0:
            raise ValueError("probability sum must be positive")
        self.pmf = [(value, probability * 1.0 / total) for value, probability in pmf]
        self.cumulative: list[float] = []
        cumulative = 0.0
        for _, probability in self.pmf:
            cumulative += probability
            self.cumulative.append(cumulative)
        self._random: _Well19937c | None = None

    def get_pmf(self) -> list[tuple[str, float]]:
        """Java: EnumeratedDistribution#getPmf (a fresh list)."""
        return list(self.pmf)

    def reseed_random_generator(self, seed: int) -> None:
        """Java: EnumeratedDistribution#reseedRandomGenerator(long)."""
        self._random = _Well19937c(seed)

    def sample(self) -> str:
        """Java: EnumeratedDistribution#sample; deterministic after explicit reseed."""
        if self._random is None:
            raise RuntimeError(
                "unseeded EnumeratedDistribution sampling is nondeterministic; reseed first"
            )
        draw = self._random.next_double()
        index = bisect_left(self.cumulative, draw)
        if index < len(self.pmf) and draw < self.cumulative[index]:
            return self.pmf[index][0]
        return self.pmf[-1][0]


class TelemedicineConfig:
    """Java: org.mitre.synthea.world.concepts.TelemedicineConfig."""

    AMBULATORY: ClassVar[str] = "ambulatory"
    EMERGENCY: ClassVar[str] = "emergency"
    TELEMEDICINE: ClassVar[str] = "telemedicine"

    def __init__(self) -> None:
        """Java: TelemedicineConfig#TelemedicineConfig (implicit constructor)."""
        self.telemedicine_start_time: int = 0
        self.high_emergency_use_insurance_names: list[str] | None = None
        self.pre_telemed_high_emergency: EnumeratedDistribution | None = None
        self.pre_telemed_typical_emergency: EnumeratedDistribution | None = None
        self.telemed_high_emergency: EnumeratedDistribution | None = None
        self.telemed_typical_emergency: EnumeratedDistribution | None = None

    def get_telemedicine_start_time(self) -> int:
        """Java: TelemedicineConfig#getTelemedicineStartTime."""
        return self.telemedicine_start_time

    def get_high_emergency_use_insurance_names(self) -> list[str] | None:
        """Java: TelemedicineConfig#getHighEmergencyUseInsuranceNames."""
        return self.high_emergency_use_insurance_names

    def get_pre_telemed_high_emergency(self) -> EnumeratedDistribution | None:
        """Java: TelemedicineConfig#getPreTelemedHighEmergency."""
        return self.pre_telemed_high_emergency

    def get_pre_telemed_typical_emergency(self) -> EnumeratedDistribution | None:
        """Java: TelemedicineConfig#getPreTelemedTypicalEmergency."""
        return self.pre_telemed_typical_emergency

    def get_telemed_high_emergency(self) -> EnumeratedDistribution | None:
        """Java: TelemedicineConfig#getTelemedHighEmergency."""
        return self.telemed_high_emergency

    def get_telemed_typical_emergency(self) -> EnumeratedDistribution | None:
        """Java: TelemedicineConfig#getTelemedTypicalEmergency."""
        return self.telemed_typical_emergency

    @staticmethod
    def from_json() -> TelemedicineConfig:
        """Java: TelemedicineConfig#fromJSON."""
        config = TelemedicineConfig()
        raw = cast(
            dict[str, object], json.loads(Utilities.read_resource("telemedicine_config.json"))
        )
        config.telemedicine_start_time = Utilities.local_date_to_timestamp(
            date(int(cast(float, raw["start_year"])), 1, 1)
        )
        config.high_emergency_use_insurance_names = cast(
            list[str], raw["high_emergency_use_insurance_names"]
        )
        pre = cast(dict[str, dict[str, float]], raw["pre_telemedicine"])
        during = cast(dict[str, dict[str, float]], raw["during_telemedicine"])
        config.pre_telemed_high_emergency = TelemedicineProbabilities(
            pre["high_emergency_distribution"]
        ).to_enumerated_distribution()
        config.pre_telemed_typical_emergency = TelemedicineProbabilities(
            pre["typical_emergency_distribution"]
        ).to_enumerated_distribution()
        config.telemed_high_emergency = TelemedicineProbabilities(
            during["high_emergency_distribution"]
        ).to_enumerated_distribution()
        config.telemed_typical_emergency = TelemedicineProbabilities(
            during["typical_emergency_distribution"]
        ).to_enumerated_distribution()
        return config


class TelemedicineProbabilities:
    """Java: TelemedicineConfig.TelemedicineProbabilities."""

    def __init__(self, json: dict[str, float]) -> None:
        """Java: TelemedicineProbabilities#TelemedicineProbabilities(Map)."""
        self.ambulatory: float = json[TelemedicineConfig.AMBULATORY]
        self.emergency: float = json[TelemedicineConfig.EMERGENCY]
        self.telemedicine: float = json.get(TelemedicineConfig.TELEMEDICINE, 0.0)

    def to_enumerated_distribution(self) -> EnumeratedDistribution:
        """Java: TelemedicineProbabilities#toEnumeratedDistribution."""
        pmf = [
            (TelemedicineConfig.AMBULATORY, self.ambulatory),
            (TelemedicineConfig.EMERGENCY, self.emergency),
        ]
        if self.telemedicine != 0:
            pmf.append((TelemedicineConfig.TELEMEDICINE, self.telemedicine))
        return EnumeratedDistribution(pmf)


setattr(TelemedicineConfig, "TelemedicineProbabilities", TelemedicineProbabilities)  # noqa: B010
