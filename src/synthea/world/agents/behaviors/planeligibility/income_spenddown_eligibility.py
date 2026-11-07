"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/I
ncomeSpenddownEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import parse_int

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


def _parse_boolean(value: str) -> bool:
    """Java: Boolean.parseBoolean — true only for "true", ignoring case."""
    return value.lower() == "true"


class IncomeSpenddownEligibility:
    """Java: IncomeSpenddownEligibility."""

    spenddownAvailable: ClassVar[bool]  # Java: static boolean spenddownAvailable.
    spenddownDisabilityLimited: ClassVar[bool]  # Java: static boolean spenddownDisabilityLimited.
    yearlySpenddown: ClassVar[int]  # Java: static int yearlySpenddown.
    SPENDDOWN_AVAILABLE: ClassVar[str] = "spenddown-available"
    DISABILITY_LIMITED: ClassVar[str] = "age-blind-disabled-limit"
    MONTHLY_SPENDDOWN_REQ: ClassVar[str] = "monthly-spenddown-req"

    def __init__(self, state: str, file_name: str) -> None:
        """Java: IncomeSpenddownEligibility#IncomeSpenddownEligibility.

        Java overloads:
        (String state, String fileName)
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
        for row in rows:
            if row["state"] == state:
                IncomeSpenddownEligibility.spenddownAvailable = _parse_boolean(
                    row[self.SPENDDOWN_AVAILABLE]
                )
                if IncomeSpenddownEligibility.spenddownAvailable:
                    IncomeSpenddownEligibility.spenddownDisabilityLimited = _parse_boolean(
                        row[self.DISABILITY_LIMITED]
                    )
                    IncomeSpenddownEligibility.yearlySpenddown = (
                        parse_int(row[self.MONTHLY_SPENDDOWN_REQ]) * 12
                    )
                else:
                    IncomeSpenddownEligibility.spenddownDisabilityLimited = False
                    IncomeSpenddownEligibility.yearlySpenddown = -1
                return
        raise RuntimeError("Invalid state " + state + " used.")

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: IncomeSpenddownEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        # For now, we'll skip spenddowns for those states without an age/disability requirement.
        if (
            not IncomeSpenddownEligibility.spenddownAvailable
            or IncomeSpenddownEligibility.spenddownDisabilityLimited
        ):
            return False
        # Check for the previous year to see if they were spenddown eligible.
        income_remaining = person.coverage.income_remaining(
            time - Config.get_as_long("generate.timestep")
        )
        spenddown_eligible = income_remaining <= IncomeSpenddownEligibility.yearlySpenddown
        return spenddown_eligible
