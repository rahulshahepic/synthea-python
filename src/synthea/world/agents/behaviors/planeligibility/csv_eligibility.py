"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/CSVEligibili
ty.java.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.planeligibility.i_plan_eligibility import IPlanEligibility
    from synthea.world.agents.person import Person


class CSVEligibility:
    """Java: CSVEligibility; pending T16."""

    POVERTY_MULTIPLIER: ClassVar[str] = "Poverty Multiplier"
    INCOME_THRESHOLD: ClassVar[str] = "Income Threshold"
    AGE_THRESHOLD: ClassVar[str] = "Age Threshold"
    QUALIFYING_CONDITIONS: ClassVar[str] = "Qualifying Codes"
    QUALIFYING_ATTRIBUTES: ClassVar[str] = "Qualifying Attributes"
    ACCEPTANCE_LIKELIHOOD: ClassVar[str] = "Acceptance Likelihood"
    POVERTY_MULTIPLIER_FILE: ClassVar[str] = "Poverty Multiplier File"
    SPENDDOWN_FILE: ClassVar[str] = "Spenddown File"
    LOGICAL_OPERATOR: ClassVar[str] = "Logical Operator"
    SUB_ELIGIBILITIES: ClassVar[str] = "Sub-Eligibilities"
    AND: ClassVar[str] = "and"
    OR: ClassVar[str] = "or"
    eligbilityOptions: ClassVar[
        dict[str, Callable[[str], IPlanEligibility]]
    ]  # Java initialization deferred to T16.

    def __init__(self, input_eligibilities: dict[str, str]) -> None:
        """Java: CSVEligibility#CSVEligibility.

        Java overloads:
        (Map inputEligibilities)
        """
        self.eligibility_logic: Callable[[Person, int], bool]
        self.eligibility_criteria: list[IPlanEligibility]
        raise NotImplementedError("Java: CSVEligibility#CSVEligibility — pending T16")

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: CSVEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CSVEligibility#isPersonEligible — pending T16")

    @staticmethod
    def build_eligibility_options(state: str) -> None:
        """Java: CSVEligibility#buildEligibilityOptions.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: CSVEligibility#buildEligibilityOptions — pending T16")

    def convert_to_logic(self, logical_operator: str) -> Callable[[Person, int], bool]:
        """Java: CSVEligibility#convertToLogic.

        Java overloads:
        (String logicalOperator)
        """
        raise NotImplementedError("Java: CSVEligibility#convertToLogic — pending T16")

    def to_string(self) -> str:
        """Java: CSVEligibility#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CSVEligibility#toString — pending T16")
