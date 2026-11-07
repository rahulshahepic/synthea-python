"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/D
efaultPlanEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class DefaultPlanEligibility:
    """Java: DefaultPlanEligibility."""

    def __init__(self) -> None:
        """Java: DefaultPlanEligibility#DefaultPlanEligibility.

        Java overloads:
        ()
        """

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: DefaultPlanEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        return True
