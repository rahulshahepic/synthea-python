"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/CSVEligibili
ty.java.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.javacompat.numbers import parse_double, parse_int
from synthea.modules.health_insurance_module import HealthInsuranceModule
from synthea.world.agents.behaviors.planeligibility.i_plan_eligibility import IPlanEligibility
from synthea.world.agents.behaviors.planeligibility.income_spenddown_eligibility import (
    IncomeSpenddownEligibility,
)
from synthea.world.agents.behaviors.planeligibility.poverty_multiplier_file_eligibility import (
    PovertyMultiplierFileEligibility,
)
from synthea.world.agents.behaviors.planeligibility.qualifying_attributes_eligibility import (
    QualifyingAttributesEligibility,
)
from synthea.world.agents.behaviors.planeligibility.qualifying_condition_codes_eligibility import (
    QualifyingConditionCodesEligibility,
)

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

_WHITESPACE = re.compile(r"[ \t\n\x0b\f\r]")


class _IncomeThresholdEligibility:
    """Java: the anonymous IPlanEligibility for the INCOME_THRESHOLD column."""

    def __init__(self, input: str) -> None:
        self._input = input

    def is_person_eligible(self, person: Person, time: int) -> bool:
        from synthea.world.agents.person import Person

        income = cast(int, person.attributes[Person.INCOME])
        income_threshold = parse_double(self._input)
        return income <= income_threshold


class _PovertyMultiplierEligibility:
    """Java: the anonymous IPlanEligibility for the POVERTY_MULTIPLIER column."""

    def __init__(self, input: str) -> None:
        self._input = input

    def is_person_eligible(self, person: Person, time: int) -> bool:
        from synthea.world.agents.person import Person

        poverty_multiplier = parse_double(self._input)
        poverty_level = HealthInsuranceModule.povertyLevel
        income_threshold = poverty_level * poverty_multiplier
        income = cast(int, person.attributes[Person.INCOME])
        return income <= income_threshold


class _AgeThresholdEligibility:
    """Java: the anonymous IPlanEligibility for the AGE_THRESHOLD column."""

    def __init__(self, input: str) -> None:
        self._input = input

    def is_person_eligible(self, person: Person, time: int) -> bool:
        age = person.age_in_years(time)
        age_threshold = parse_int(self._input)
        return age >= age_threshold


class _AcceptanceLikelihoodEligibility:
    """Java: the anonymous IPlanEligibility for the ACCEPTANCE_LIKELIHOOD column."""

    def __init__(self, input: str) -> None:
        self._input = input

    def is_person_eligible(self, person: Person, time: int) -> bool:
        acceptance_likelihood = parse_double(self._input)
        return person.rand() < acceptance_likelihood


class CSVEligibility:
    """Java: CSVEligibility."""

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
    eligbilityOptions: ClassVar[dict[str, Callable[[str], IPlanEligibility]]]

    def __init__(self, input_eligibilities: dict[str, str]) -> None:
        """Java: CSVEligibility#CSVEligibility.

        Java overloads:
        (Map inputEligibilities)

        The constructor removes LOGICAL_OPERATOR and SUB_ELIGIBILITIES from
        the given map, exactly as the Java constructor mutates its argument.
        The caller (PlanEligibilityFinder) hands over a plain dict whose
        iteration order reproduces the Java HashMap order of the filtered
        CSV row, so criteria are built in the same order the JVM builds them
        (sub-eligibilities first, then the remaining columns).
        """
        from synthea.world.agents.behaviors.planeligibility.plan_eligibility_finder import (
            PlanEligibilityFinder,
        )

        self.eligibility_criteria: list[IPlanEligibility] = []

        logical_operator = input_eligibilities.pop(self.LOGICAL_OPERATOR, None)
        self.eligibility_logic: Callable[[Person, int], bool] = self.convert_to_logic(
            logical_operator
        )
        sub_eligibilities_str = input_eligibilities.pop(self.SUB_ELIGIBILITIES, None)
        if sub_eligibilities_str is not None:
            sub_eligibilities = re.split(r"\|", sub_eligibilities_str)
            if sub_eligibilities_str:
                while sub_eligibilities and not sub_eligibilities[-1]:
                    sub_eligibilities.pop()
            for sub_eligibility in sub_eligibilities:
                self.eligibility_criteria.append(
                    PlanEligibilityFinder.get_eligibility_algorithm(sub_eligibility)
                )

        for key in input_eligibilities:
            if key == "Notes":
                continue
            if key not in CSVEligibility.eligbilityOptions:
                raise ValueError("Invalid CSV eligibility input column: " + key + ".")
            input_value = input_eligibilities[key]
            new_eligibility = CSVEligibility.eligbilityOptions[key](input_value)
            self.eligibility_criteria.append(new_eligibility)

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: CSVEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        return self.eligibility_logic(person, time)

    @staticmethod
    def build_eligibility_options(state: str) -> None:
        """Java: CSVEligibility#buildEligibilityOptions.

        Java overloads:
        (String state)
        """
        options: dict[str, Callable[[str], IPlanEligibility]] = {}
        options[CSVEligibility.INCOME_THRESHOLD] = lambda value: _IncomeThresholdEligibility(value)
        options[CSVEligibility.POVERTY_MULTIPLIER] = lambda value: _PovertyMultiplierEligibility(
            value
        )
        options[CSVEligibility.AGE_THRESHOLD] = lambda value: _AgeThresholdEligibility(value)
        options[CSVEligibility.QUALIFYING_CONDITIONS] = lambda value: (
            QualifyingConditionCodesEligibility(value)
        )
        options[CSVEligibility.QUALIFYING_ATTRIBUTES] = lambda value: (
            QualifyingAttributesEligibility(value)
        )
        options[CSVEligibility.ACCEPTANCE_LIKELIHOOD] = lambda value: (
            _AcceptanceLikelihoodEligibility(value)
        )
        options[CSVEligibility.POVERTY_MULTIPLIER_FILE] = lambda value: (
            PovertyMultiplierFileEligibility(state, value)
        )
        options[CSVEligibility.SPENDDOWN_FILE] = lambda value: IncomeSpenddownEligibility(
            state, value
        )
        CSVEligibility.eligbilityOptions = options

    def convert_to_logic(self, logical_operator: str | None) -> Callable[[Person, int], bool]:
        """Java: CSVEligibility#convertToLogic.

        Java overloads:
        (String logicalOperator)
        """
        if logical_operator is None:
            logical_operator = ""
        operator = _WHITESPACE.sub("", logical_operator)
        if operator == "" or operator.lower() == self.OR:
            return lambda person, time: any(
                eligibility.is_person_eligible(person, time)
                for eligibility in self.eligibility_criteria
            )
        if operator.lower() == self.AND:
            return lambda person, time: all(
                eligibility.is_person_eligible(person, time)
                for eligibility in self.eligibility_criteria
            )
        raise ValueError(
            "Invalid logical operator '" + operator + "' for input eligibilities table."
        )

    def to_string(self) -> str:
        """Java: CSVEligibility#toString.

        Java overloads:
        ()

        Java's rendering embeds each criterion's default Object.toString
        (identity hash), so it is not reproducible across runs in either
        language; the shape (including the missing closing brace) is kept.
        """
        return "{CSVEligiblity: [" + ", ".join(str(c) for c in self.eligibility_criteria) + "]"

    def __str__(self) -> str:
        """Java: CSVEligibility#toString."""
        return self.to_string()
