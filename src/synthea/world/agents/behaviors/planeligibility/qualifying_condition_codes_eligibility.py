"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/Q
ualifyingConditionCodesEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class QualifyingConditionCodesEligibility:
    """Java: org.mitre.synthea.world.agents.behaviors.planeligibility.QualifyingConditionCo
    desEligi
    bility; pending T16.
    """

    def __init__(self, codes: str) -> None:
        """Java: QualifyingConditionCodesEligibility#QualifyingConditionCodesEligibility.

        Java overloads:
        (String codes)
        """
        self.qualifying_codes: list[str]
        raise NotImplementedError(
            "Java: QualifyingConditionCodesEligibility#QualifyingConditionCodesEligibility"
            " — pending T16"
        )

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: QualifyingConditionCodesEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: QualifyingConditionCodesEligibility#isPersonEligible — pending T16"
        )

    @staticmethod
    def build_qualifying_conditions_file(file_name: str) -> list[str]:
        """Java: QualifyingConditionCodesEligibility#buildQualifyingConditionsFile.

        Java overloads:
        (String fileName)
        """
        raise NotImplementedError(
            "Java: QualifyingConditionCodesEligibility#buildQualifyingConditionsFile — pending T16"
        )

    def get_earliest_diagnosis(self, person: Person) -> int:
        """Java: QualifyingConditionCodesEligibility#getEarliestDiagnosis.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError(
            "Java: QualifyingConditionCodesEligibility#getEarliestDiagnosis — pending T16"
        )
