"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/P
overtyMultiplierFileEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class PovertyMultiplierFileEligibility:
    """Java:
    org.mitre.synthea.world.agents.behaviors.planeligibility.PovertyMultiplierFileEligib
    ility;
    pending T16.
    """

    povertyAge1: ClassVar[float]  # Java initialization deferred to T16.
    povertyAge5: ClassVar[float]  # Java initialization deferred to T16.
    povertyAge18: ClassVar[float]  # Java initialization deferred to T16.
    povertyPregnant: ClassVar[float]  # Java initialization deferred to T16.
    povertyAdult: ClassVar[float]  # Java initialization deferred to T16.

    def __init__(self, state: str, file_name: str) -> None:
        """Java: PovertyMultiplierFileEligibility#PovertyMultiplierFileEligibility.

        Java overloads:
        (String state, String fileName)
        """
        raise NotImplementedError(
            "Java: PovertyMultiplierFileEligibility#PovertyMultiplierFileEligibility — pending T16"
        )

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: PovertyMultiplierFileEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: PovertyMultiplierFileEligibility#isPersonEligible — pending T16"
        )

    def determine_poverty_multiplier(self, person: Person, time: int) -> float:
        """Java: PovertyMultiplierFileEligibility#determinePovertyMultiplier.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: PovertyMultiplierFileEligibility#determinePovertyMultiplier — pending T16"
        )

    def build_poverty_multiplier_eligibility(self, state: str, file_name: str) -> None:
        """Java: PovertyMultiplierFileEligibility#buildPovertyMultiplierEligibility.

        Java overloads:
        (String state, String fileName)
        """
        raise NotImplementedError(
            "Java: PovertyMultiplierFileEligibility#buildPovertyMultiplierEligibility — pending T16"
        )
