"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/P
lanEligibilityFinder.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.planeligibility.i_plan_eligibility import IPlanEligibility


class PlanEligibilityFinder:
    """Java: PlanEligibilityFinder;
    pending T16.
    """

    planEligibilities: ClassVar[dict[str, IPlanEligibility]]  # Java initialization deferred to T16.
    ELIGIBILITY_NAME: ClassVar[str] = "Name"
    GENERIC: ClassVar[str] = "GENERIC"
    DEFAULT: ClassVar[IPlanEligibility]  # Java initialization deferred to T16.

    def __init__(self) -> None:
        """Java: PlanEligibilityFinder#PlanEligibilityFinder.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanEligibilityFinder#PlanEligibilityFinder — pending T16")

    @staticmethod
    def get_eligibility_algorithm(eligibility: str) -> IPlanEligibility:
        """Java: PlanEligibilityFinder#getEligibilityAlgorithm.

        Java overloads:
        (String eligibility)
        """
        raise NotImplementedError(
            "Java: PlanEligibilityFinder#getEligibilityAlgorithm — pending T16"
        )

    @staticmethod
    def build_plan_eligibilities(state: str, file_name: str) -> None:
        """Java: PlanEligibilityFinder#buildPlanEligibilities.

        Java overloads:
        (String state, String fileName)
        """
        raise NotImplementedError(
            "Java: PlanEligibilityFinder#buildPlanEligibilities — pending T16"
        )

    @staticmethod
    def remove_blank_map_string_values[T](map: dict[T, str]) -> dict[T, str]:
        """Java: PlanEligibilityFinder#removeBlankMapStringValues.

        Java overloads:
        (Map map)
        """
        raise NotImplementedError(
            "Java: PlanEligibilityFinder#removeBlankMapStringValues — pending T16"
        )
