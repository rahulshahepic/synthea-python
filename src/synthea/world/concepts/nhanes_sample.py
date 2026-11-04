"""Java API skeleton for nhanes_sample.py.
Java: org.mitre.synthea.world.concepts.NHANESSample.
"""

from __future__ import annotations


class NHANESSample:
    """Java: NHANESSample; pending T12."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: NHANESSample constructor; pending T12."""
        self.id: int = 0
        self.sex: int = 0
        self.agem: int = 0
        self.wt: float = 0.0
        self.ht: float = 0.0
        self.swt: float = 0.0
        self.racec: str | None = None
        self.bmi: float = 0.0
        self.prob: float = 0.0
        raise NotImplementedError("Java: NHANESSample — pending T12")

    def to_string(self, *args: object, **kwargs: object) -> object:
        """Java: NHANESSample#toString."""
        raise NotImplementedError("Java: toString — pending T12")

    def load_samples(self, *args: object, **kwargs: object) -> object:
        """Java: NHANESSample#loadSamples."""
        raise NotImplementedError("Java: loadSamples — pending T12")

    def load_distribution(self, *args: object, **kwargs: object) -> object:
        """Java: NHANESSample#loadDistribution."""
        raise NotImplementedError("Java: loadDistribution — pending T12")

    def load_distribution_by_sex(self, *args: object, **kwargs: object) -> object:
        """Java: NHANESSample#loadDistributionBySex."""
        raise NotImplementedError("Java: loadDistributionBySex — pending T12")
