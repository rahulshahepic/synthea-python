"""Java: org.mitre.synthea.engine.ReactionProbabilities."""

from __future__ import annotations

import math
import struct
from bisect import bisect_left
from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.synced_enumerated_distro import _Well19937c

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code as HealthRecordCode
    from synthea.world.concepts.health_record import (
        ReactionSeverity as HealthRecordReactionSeverity,
    )


def _float32(value: float) -> float:
    """Java: a ``float`` field stores the float32 rounding of the value."""
    return struct.unpack("f", struct.pack("f", value))[0]


class EnumeratedDistribution:
    """Java: Apache Commons Math 3.6.1 EnumeratedDistribution<String> boundary.

    Same port as in ``synthea.world.concepts.telemedicine_config``: Synthea
    reseeds immediately before sampling, so the unseeded constructor entropy
    is never observed; sampling before a reseed raises instead.
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


class ReactionProbabilities:
    """Java: ReactionProbabilities."""

    SEVERE: ClassVar[str] = "severe"
    MODERATE: ClassVar[str] = "moderate"
    MILD: ClassVar[str] = "mild"
    NONE: ClassVar[str] = "none"

    def __init__(
        self, code: HealthRecordCode, possible_reactions: list[SeverityProbability]
    ) -> None:
        """Java: ReactionProbabilities#ReactionProbabilities.

        Java overloads:
        (HealthRecord.Code code, List possibleReactions)
        """
        self.reaction: HealthRecordCode = code
        self.possible_severities: list[SeverityProbability] = possible_reactions
        self.severity_distribution: EnumeratedDistribution | None = None

    def get_reaction(self) -> HealthRecordCode:
        """Java: ReactionProbabilities#getReaction.

        Java overloads:
        ()
        """
        return self.reaction

    def set_reaction(self, reaction: HealthRecordCode) -> None:
        """Java: ReactionProbabilities#setReaction.

        Java overloads:
        (HealthRecord.Code reaction)
        """
        self.reaction = reaction

    def is_populated(self) -> bool:
        """Java: ReactionProbabilities#isPopulated.

        Java overloads:
        ()
        """
        return len(self.possible_severities) != 0

    def build_reaction_distributions(self) -> None:
        """Java: ReactionProbabilities#buildReactionDistributions.

        Java overloads:
        ()
        """
        if not self.validate():
            raise RuntimeError("Invalid distribution values specified")
        prob_pairs = [(sp.get_level(), float(sp.get_value())) for sp in self.possible_severities]
        self.severity_distribution = EnumeratedDistribution(prob_pairs)

    def validate(self) -> bool:
        """Java: ReactionProbabilities#validate.

        Java overloads:
        ()
        """
        # less than 1.001 to deal with floating point rounding issues
        total = 0.0
        for sp in self.possible_severities:
            total += float(sp.get_value())
        return total <= 1.001

    def generate_severity(self, person: Person) -> HealthRecordReactionSeverity | None:
        """Java: ReactionProbabilities#generateSeverity.

        Java overloads:
        (Person person)
        """
        from synthea.world.concepts.health_record import ReactionSeverity

        if self.is_populated() and self.severity_distribution is None:
            self.build_reaction_distributions()
        if self.severity_distribution is None:
            # Java throws NullPointerException here on an unpopulated instance.
            raise RuntimeError("Java NullPointerException: severityDistribution is null")
        self.severity_distribution.reseed_random_generator(person.rand_long())
        severity = self.severity_distribution.sample()
        if severity == ReactionProbabilities.SEVERE:
            return ReactionSeverity.SEVERE
        elif severity == ReactionProbabilities.MODERATE:
            return ReactionSeverity.MODERATE
        elif severity == ReactionProbabilities.MILD:
            return ReactionSeverity.MILD
        elif severity == ReactionProbabilities.NONE:
            # do nothing
            return None
        # should never get here
        return None


class SeverityProbability:
    """Java: SeverityProbability."""

    def __init__(self, level: str, value: float) -> None:
        """Java: SeverityProbability#SeverityProbability.

        Java overloads:
        (String level, float value)
        """
        self.level: str = level
        self.value: float = _float32(value)

    def get_level(self) -> str:
        """Java: SeverityProbability#getLevel.

        Java overloads:
        ()
        """
        return self.level

    def set_level(self, level: str) -> None:
        """Java: SeverityProbability#setLevel.

        Java overloads:
        (String level)
        """
        self.level = level

    def get_value(self) -> float:
        """Java: SeverityProbability#getValue.

        Java overloads:
        ()
        """
        return self.value

    def set_value(self, value: float) -> None:
        """Java: SeverityProbability#setValue.

        Java overloads:
        (float value)
        """
        self.value = _float32(value)


setattr(ReactionProbabilities, "SeverityProbability", SeverityProbability)  # noqa: B010
