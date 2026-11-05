"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/I
ncomeSpenddownEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class IncomeSpenddownEligibility:
    """Java: IncomeSpenddownEligibility;
    pending T16.
    """

    spenddownAvailable: ClassVar[bool]  # Java initialization deferred to T16.
    spenddownDisabilityLimited: ClassVar[bool]  # Java initialization deferred to T16.
    yearlySpenddown: ClassVar[int]  # Java initialization deferred to T16.
    SPENDDOWN_AVAILABLE: ClassVar[str] = "spenddown-available"
    DISABILITY_LIMITED: ClassVar[str] = "age-blind-disabled-limit"
    MONTHLY_SPENDDOWN_REQ: ClassVar[str] = "monthly-spenddown-req"

    def __init__(self, state: str, file_name: str) -> None:
        """Java: IncomeSpenddownEligibility#IncomeSpenddownEligibility.

        Java overloads:
        (String state, String fileName)
        """
        raise NotImplementedError(
            "Java: IncomeSpenddownEligibility#IncomeSpenddownEligibility — pending T16"
        )

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: IncomeSpenddownEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: IncomeSpenddownEligibility#isPersonEligible — pending T16")
