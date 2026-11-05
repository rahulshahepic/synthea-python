"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/I
PlanEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class IPlanEligibility(Protocol):
    """Java: IPlanEligibility; pending T16."""

    def __init__(self) -> None:
        """Java: IPlanEligibility#IPlanEligibility.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: IPlanEligibility#IPlanEligibility — pending T16")

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: IPlanEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: IPlanEligibility#isPersonEligible — pending T16")
