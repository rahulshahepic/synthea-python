"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/Q
ualifyingAttributesEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class QualifyingAttributesEligibility:
    """Java:
    org.mitre.synthea.world.agents.behaviors.planeligibility.QualifyingAttributesEligibi
    lity;
    pending T16.
    """

    def __init__(self, attribute_input: str) -> None:
        """Java: QualifyingAttributesEligibility#QualifyingAttributesEligibility.

        Java overloads:
        (String attributeInput)
        """
        self.qualifying_attributes: list[AttributeQualifier]
        raise NotImplementedError(
            "Java: QualifyingAttributesEligibility#QualifyingAttributesEligibility — pending T16"
        )

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: QualifyingAttributesEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: QualifyingAttributesEligibility#isPersonEligible — pending T16"
        )

    @staticmethod
    def convert_attribute_expression_set(attribute_input: str) -> list[AttributeQualifier]:
        """Java: QualifyingAttributesEligibility#convertAttributeExpressionSet.

        Java overloads:
        (String attributeInput)
        """
        raise NotImplementedError(
            "Java: QualifyingAttributesEligibility#convertAttributeExpressionSet — pending T16"
        )

    @staticmethod
    def convert_attribute_expression_to_logic(attribute_expression: str) -> AttributeQualifier:
        """Java: QualifyingAttributesEligibility#convertAttributeExpressionToLogic.

        Java overloads:
        (String attributeExpression)
        """
        raise NotImplementedError(
            "Java: QualifyingAttributesEligibility#convertAttributeExpressionToLogic — pending T16"
        )

    @staticmethod
    def build_qualifying_attributes_file(file_name: str) -> list[AttributeQualifier]:
        """Java: QualifyingAttributesEligibility#buildQualifyingAttributesFile.

        Java overloads:
        (String fileName)
        """
        raise NotImplementedError(
            "Java: QualifyingAttributesEligibility#buildQualifyingAttributesFile — pending T16"
        )


class AttributeQualifier:
    """Java: AttributeQualifier; pending T16."""

    def __init__(self, attribute: str, value: object, operator: str) -> None:
        """Java: AttributeQualifier#AttributeQualifier.

        Java overloads:
        (String attribute, Object value, String operator)
        """
        self.logic: AttributeLogic
        raise NotImplementedError("Java: AttributeQualifier#AttributeQualifier — pending T16")

    def check_logic(self, person: Person) -> bool:
        """Java: AttributeQualifier#checkLogic.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: AttributeQualifier#checkLogic — pending T16")


class AttributeLogic(Protocol):
    """Java: AttributeLogic; pending T16."""

    def __init__(self) -> None:
        """Java: AttributeLogic#AttributeLogic.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: AttributeLogic#AttributeLogic — pending T16")

    def check_attribute_logic(self, person: Person) -> bool:
        """Java: AttributeLogic#checkAttributeLogic.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: AttributeLogic#checkAttributeLogic — pending T16")


setattr(QualifyingAttributesEligibility, "AttributeQualifier", AttributeQualifier)  # noqa: B010
setattr(AttributeQualifier, "AttributeLogic", AttributeLogic)  # noqa: B010
