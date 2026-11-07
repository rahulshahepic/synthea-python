"""Java: NHANESSample and its Apache Commons Math 3.6.1 sampling collaborators."""

from __future__ import annotations

import bisect
import csv
import io

from synthea.helpers.synced_enumerated_distro import _Well19937c
from synthea.javacompat.fmt import format as java_format
from synthea.resources import read_resource


class EnumeratedDistribution:
    """Java: Apache Commons Math 3.6.1 EnumeratedDistribution<NHANESSample>."""

    def __init__(self, pairs: list[tuple[NHANESSample, float]]) -> None:
        """Java: EnumeratedDistribution#EnumeratedDistribution."""
        self.samples = [p[0] for p in pairs]
        total = 0.0
        for _, prob in pairs:
            total += prob
        self.probabilities = [prob / total for _, prob in pairs]
        self.cumulative: list[float] = []
        total = 0.0
        for prob in self.probabilities:
            total += prob
            self.cumulative.append(total)
        self.random: _Well19937c | None = None

    def reseed_random_generator(self, seed: int) -> None:
        """Java: EnumeratedDistribution#reseedRandomGenerator."""
        self.random = _Well19937c(seed)

    def sample(self) -> NHANESSample:
        """Java: EnumeratedDistribution#sample."""
        if self.random is None:
            raise ValueError("Seed the NHANES distribution before sampling")
        value = self.random.next_double()
        index = bisect.bisect_left(self.cumulative, value)
        if index < len(self.samples) and value < self.cumulative[index]:
            return self.samples[index]
        return self.samples[-1]

    def get_pmf(self) -> list[tuple[NHANESSample, float]]:
        """Java: EnumeratedDistribution#getPmf."""
        return list(zip(self.samples, self.probabilities, strict=True))


class NHANESSample:
    """Java: org.mitre.synthea.world.concepts.NHANESSample."""

    def __init__(self) -> None:
        """Java: NHANESSample#NHANESSample (default field initialization)."""
        self.id: int = 0
        self.sex: int = 0
        self.agem: int = 0
        self.wt: float = 0.0
        self.ht: float = 0.0
        self.swt: float = 0.0
        self.bmi: float = 0.0
        self.prob: float = 0.0
        self.racec: str | None = None

    def to_string(self) -> str:
        """Java: NHANESSample#toString."""
        return java_format(
            "{%d %d %d %f %f %f %s %f %f}",
            self.id,
            self.sex,
            self.agem,
            self.wt,
            self.ht,
            self.swt,
            self.racec,
            self.bmi,
            self.prob,
        )

    @staticmethod
    def load_samples() -> list[NHANESSample]:
        """Java: NHANESSample#loadSamples."""
        samples = []
        for row in csv.DictReader(io.StringIO(read_resource("nhanes_two_year_olds_bmi.csv"))):
            sample = NHANESSample()
            for key in ("id", "sex", "agem"):
                setattr(sample, key, int(row[key]))
            for key in ("wt", "ht", "swt", "bmi", "prob"):
                setattr(sample, key, float(row[key]))
            sample.racec = row["racec"]
            samples.append(sample)
        return samples

    @staticmethod
    def load_distribution() -> EnumeratedDistribution:
        """Java: NHANESSample#loadDistribution."""
        return EnumeratedDistribution([(s, s.prob) for s in NHANESSample.load_samples()])

    @staticmethod
    def load_distribution_by_sex(sex_code: int) -> EnumeratedDistribution:
        """Java: NHANESSample#loadDistributionBySex."""
        samples = [s for s in NHANESSample.load_samples() if s.sex == sex_code]
        if not samples:
            return NHANESSample.load_distribution()
        total, compensation = 0.0, 0.0
        for s in samples:
            corrected = s.prob - compensation
            next_total = total + corrected
            compensation = (next_total - total) - corrected
            total = next_total
        total -= compensation
        return EnumeratedDistribution([(s, s.prob / total) for s in samples])
