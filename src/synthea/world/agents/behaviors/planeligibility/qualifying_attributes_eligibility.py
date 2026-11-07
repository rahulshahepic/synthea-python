"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/Q
ualifyingAttributesEligibility.java.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import double_to_string, parse_double

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

_WHITESPACE = re.compile(r"[ \t\n\x0b\f\r]")


def _java_split(pattern: str, value: str) -> list[str]:
    """Java String.split(regex): trailing empty strings are dropped."""
    parts = re.split(pattern, value)
    if value:
        while parts and not parts[-1]:
            parts.pop()
    return parts


def _is_creatable(value: str) -> bool:
    """Apache Commons Lang NumberUtils.isCreatable.

    Faithful port of the classic algorithm: an optional sign, an optional
    0x/0X hex body, otherwise digits with at most one decimal point, at most
    one exponent (which must follow a digit and may be signed), and an
    optional trailing d/D/f/F (floating) or l/L (long, only without point or
    exponent) suffix.
    """
    if not value:
        return False
    chars = value
    sz = len(chars)
    has_exp = False
    has_dec_point = False
    allow_signs = False
    found_digit = False
    start = 1 if chars[0] in "-+" else 0
    if sz > start + 1 and chars[start] == "0" and chars[start + 1] in "xX":
        i = start + 2
        if i == sz:
            return False
        for j in range(i, sz):
            c = chars[j]
            if not ("0" <= c <= "9" or "a" <= c <= "f" or "A" <= c <= "F"):
                return False
        return True
    sz -= 1  # don't want to loop to the last char, check it in the tail below
    i = start
    while i < sz or (i < sz + 1 and allow_signs and not found_digit):
        c = chars[i]
        if "0" <= c <= "9":
            found_digit = True
            allow_signs = False
        elif c == ".":
            if has_dec_point or has_exp:
                return False
            has_dec_point = True
        elif c in "eE":
            if has_exp:
                return False
            if not found_digit:
                return False
            has_exp = True
            allow_signs = True
        elif c in "+-":
            if not allow_signs:
                return False
            allow_signs = False
            found_digit = False
        else:
            return False
        i += 1
    if i < len(chars):
        c = chars[i]
        if "0" <= c <= "9":
            return True
        if c in "eE":
            return False
        if c == ".":
            if has_dec_point or has_exp:
                return False
            return found_digit
        if not allow_signs and c in "dDfF":
            return found_digit
        if c in "lL":
            return found_digit and not has_exp and not has_dec_point
        return False
    return not allow_signs and found_digit


class QualifyingAttributesEligibility:
    """Java:
    org.mitre.synthea.world.agents.behaviors.planeligibility.QualifyingAttributesEligibi
    lity.
    """

    def __init__(self, attribute_input: str) -> None:
        """Java: QualifyingAttributesEligibility#QualifyingAttributesEligibility.

        Java overloads:
        (String attributeInput)
        """
        if attribute_input.endswith(".csv"):
            # The input is a csv file, convert it to a list of attribute expressions.
            self.qualifying_attributes: list[AttributeQualifier] = (
                self.build_qualifying_attributes_file(attribute_input)
            )
        else:
            # The input is a set of attributes.
            self.qualifying_attributes = self.convert_attribute_expression_set(attribute_input)

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: QualifyingAttributesEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        return any(
            attribute_logic.check_logic(person) for attribute_logic in self.qualifying_attributes
        )

    @staticmethod
    def convert_attribute_expression_set(attribute_input: str) -> list[AttributeQualifier]:
        """Java: QualifyingAttributesEligibility#convertAttributeExpressionSet.

        Java overloads:
        (String attributeInput)
        """
        qualifying_attributes: list[AttributeQualifier] = []
        for attribute_expression in _java_split(r"\|", attribute_input):
            qualifying_attributes.append(
                QualifyingAttributesEligibility.convert_attribute_expression_to_logic(
                    attribute_expression
                )
            )
        return qualifying_attributes

    @staticmethod
    def convert_attribute_expression_to_logic(attribute_expression: str) -> AttributeQualifier:
        """Java: QualifyingAttributesEligibility#convertAttributeExpressionToLogic.

        Java overloads:
        (String attributeExpression)
        """
        attribute_expression = _WHITESPACE.sub("", attribute_expression)
        # We will specifically iterate over the possible operators in this order.
        operator_regexes = ["<=", ">=", "!=", "==", "<", ">", "="]
        for regex in operator_regexes:
            split_expression = _java_split(regex, attribute_expression)
            if len(split_expression) == 2:
                attribute = split_expression[0]
                operator = regex
                value = split_expression[1]
                return AttributeQualifier(attribute, value, operator)
        raise RuntimeError("Invalid attribute logic expression '" + attribute_expression + "'.")

    @staticmethod
    def build_qualifying_attributes_file(file_name: str) -> list[AttributeQualifier]:
        """Java: QualifyingAttributesEligibility#buildQualifyingAttributesFile.

        Java overloads:
        (String fileName)
        """
        try:
            resource = Utilities.read_resource(file_name, True, True)
            csv = SimpleCSV.parse_line_by_line(resource)
            rows = list(csv)
        except Exception as e:
            raise RuntimeError(
                "There was an issue reading the file '"
                + file_name
                + "'. This issue was caused by "
                + str(e)
            ) from e

        attribute_eligibilities: list[AttributeQualifier] = []
        for row in rows:
            attribute_row = row["attributes"]
            attribute_eligibilities.extend(
                QualifyingAttributesEligibility.convert_attribute_expression_set(attribute_row)
            )
        return attribute_eligibilities


class AttributeQualifier:
    """Java: AttributeQualifier."""

    def __init__(self, attribute: str, value: object, operator: str) -> None:
        """Java: AttributeQualifier#AttributeQualifier.

        Java overloads:
        (String attribute, Object value, String operator)
        """
        if operator == "=":
            operator = "=="
        true_operator = operator
        # Non-numeric logic can only use equality logic.
        valid_operators = ["!=", "=="]
        true_value: object = value
        if _is_creatable(str(value)):
            # If the value is a number, treat it and the attribute as numeric.
            true_value = parse_double(str(value))
            valid_operators = [">=", ">", "<", "<=", "==", "!="]
        if true_operator in valid_operators:

            def logic(person: Person) -> bool:
                attribute_result = person.attributes.get(attribute)
                if attribute_result is None:
                    return False
                if not isinstance(attribute_result, int | float | Decimal | str | bool):
                    raise RuntimeError(
                        "Attribute must be of Number, String, or Boolean "
                        "type. Recieved type '" + type(attribute_result).__name__ + "'."
                    )
                if isinstance(attribute_result, bool):
                    attribute_result = str(attribute_result).lower()
                return Utilities.compare(attribute_result, true_value, true_operator)

            self.logic: AttributeLogic = _CallableLogic(logic)
        else:
            value_text = (
                double_to_string(true_value) if isinstance(true_value, float) else str(true_value)
            )
            raise RuntimeError(
                "Operator '"
                + true_operator
                + "' is invalid for attribute '"
                + attribute
                + "' with value '"
                + value_text
                + "'."
            )

    def check_logic(self, person: Person) -> bool:
        """Java: AttributeQualifier#checkLogic.

        Java overloads:
        (Person person)
        """
        return self.logic.check_attribute_logic(person)


class AttributeLogic(Protocol):
    """Java: AttributeLogic."""

    def __init__(self) -> None:
        """Java: AttributeLogic#AttributeLogic.

        Java overloads:
        ()
        """
        pass

    def check_attribute_logic(self, person: Person) -> bool:
        """Java: AttributeLogic#checkAttributeLogic.

        Java overloads:
        (Person person)
        """
        ...


class _CallableLogic:
    """Adapter: a plain callable presented as the Java AttributeLogic interface."""

    def __init__(self, fn: Callable[[Person], bool]) -> None:
        """Java: AttributeQualifier#AttributeQualifier (the AttributeLogic lambda)."""
        self._fn = fn

    def check_attribute_logic(self, person: Person) -> bool:
        """Java: AttributeLogic#checkAttributeLogic."""
        return self._fn(person)


setattr(QualifyingAttributesEligibility, "AttributeQualifier", AttributeQualifier)  # noqa: B010
setattr(AttributeQualifier, "AttributeLogic", AttributeLogic)  # noqa: B010
