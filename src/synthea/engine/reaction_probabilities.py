"""Java API skeleton: ReactionProbabilities.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code as HealthRecordCode
    from synthea.world.concepts.health_record import (
        ReactionSeverity as HealthRecordReactionSeverity,
    )

    class EnumeratedDistribution(Protocol):
        """Java boundary type: EnumeratedDistribution; external to the mapped Python port."""


class ReactionProbabilities:
    """Java: ReactionProbabilities; pending T20."""

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
        self.reaction: HealthRecordCode
        self.possible_severities: list[SeverityProbability]
        self.severity_distribution: EnumeratedDistribution
        raise NotImplementedError("Java: ReactionProbabilities#ReactionProbabilities — pending T20")

    def get_reaction(self) -> HealthRecordCode:
        """Java: ReactionProbabilities#getReaction.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ReactionProbabilities#getReaction — pending T20")

    def set_reaction(self, reaction: HealthRecordCode) -> None:
        """Java: ReactionProbabilities#setReaction.

        Java overloads:
        (HealthRecord.Code reaction)
        """
        raise NotImplementedError("Java: ReactionProbabilities#setReaction — pending T20")

    def is_populated(self) -> bool:
        """Java: ReactionProbabilities#isPopulated.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ReactionProbabilities#isPopulated — pending T20")

    def build_reaction_distributions(self) -> None:
        """Java: ReactionProbabilities#buildReactionDistributions.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: ReactionProbabilities#buildReactionDistributions — pending T20"
        )

    def validate(self) -> bool:
        """Java: ReactionProbabilities#validate.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ReactionProbabilities#validate — pending T20")

    def generate_severity(self, person: Person) -> HealthRecordReactionSeverity:
        """Java: ReactionProbabilities#generateSeverity.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: ReactionProbabilities#generateSeverity — pending T20")


class SeverityProbability:
    """Java: SeverityProbability; pending T20."""

    def __init__(self, level: str, value: float) -> None:
        """Java: SeverityProbability#SeverityProbability.

        Java overloads:
        (String level, float value)
        """
        self.level: str
        self.value: float
        raise NotImplementedError("Java: SeverityProbability#SeverityProbability — pending T20")

    def get_level(self) -> str:
        """Java: SeverityProbability#getLevel.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SeverityProbability#getLevel — pending T20")

    def set_level(self, level: str) -> None:
        """Java: SeverityProbability#setLevel.

        Java overloads:
        (String level)
        """
        raise NotImplementedError("Java: SeverityProbability#setLevel — pending T20")

    def get_value(self) -> float:
        """Java: SeverityProbability#getValue.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SeverityProbability#getValue — pending T20")

    def set_value(self, value: float) -> None:
        """Java: SeverityProbability#setValue.

        Java overloads:
        (float value)
        """
        raise NotImplementedError("Java: SeverityProbability#setValue — pending T20")


setattr(ReactionProbabilities, "SeverityProbability", SeverityProbability)  # noqa: B010
