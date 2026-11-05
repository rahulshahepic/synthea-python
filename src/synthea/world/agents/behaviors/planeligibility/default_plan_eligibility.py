"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/D
efaultPlanEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class DefaultPlanEligibility:
    """Java: DefaultPlanEligibility;
    pending T16.
    """

    def __init__(self) -> None:
        """Java: DefaultPlanEligibility#DefaultPlanEligibility.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: DefaultPlanEligibility#DefaultPlanEligibility — pending T16"
        )

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: DefaultPlanEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: DefaultPlanEligibility#isPersonEligible — pending T16")
