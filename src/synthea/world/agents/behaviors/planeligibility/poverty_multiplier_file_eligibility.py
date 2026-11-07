"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/P
overtyMultiplierFileEligibility.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import parse_double
from synthea.modules.health_insurance_module import HealthInsuranceModule

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class PovertyMultiplierFileEligibility:
    """Java:
    org.mitre.synthea.world.agents.behaviors.planeligibility.PovertyMultiplierFileEligib
    ility.
    """

    povertyAge1: ClassVar[float]  # Java: static double povertyAge1.
    povertyAge5: ClassVar[float]  # Java: static double povertyAge5.
    povertyAge18: ClassVar[float]  # Java: static double povertyAge18.
    povertyPregnant: ClassVar[float]  # Java: static double povertyPregnant.
    povertyAdult: ClassVar[float]  # Java: static double povertyAdult.

    def __init__(self, state: str, file_name: str) -> None:
        """Java: PovertyMultiplierFileEligibility#PovertyMultiplierFileEligibility.

        Java overloads:
        (String state, String fileName)
        """
        self.build_poverty_multiplier_eligibility(state, file_name)

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: PovertyMultiplierFileEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        from synthea.world.agents.person import Person

        income = cast(int, person.attributes[Person.INCOME])
        poverty_multiplier = self.determine_poverty_multiplier(person, time)
        income_threshold = poverty_multiplier * HealthInsuranceModule.povertyLevel
        return income <= income_threshold

    def determine_poverty_multiplier(self, person: Person, time: int) -> float:
        """Java: PovertyMultiplierFileEligibility#determinePovertyMultiplier.

        Java overloads:
        (Person person, long time)
        """
        from synthea.world.agents.person import Person

        age = person.age_in_years(time)
        if age <= 1:
            return PovertyMultiplierFileEligibility.povertyAge1
        if age <= 5:
            return PovertyMultiplierFileEligibility.povertyAge5
        if age <= 18:
            return PovertyMultiplierFileEligibility.povertyAge18
        female = person.attributes[Person.GENDER] == "F"
        pregnant = "pregnant" in person.attributes and cast(bool, person.attributes["pregnant"])
        if female and pregnant:
            return PovertyMultiplierFileEligibility.povertyPregnant
        return PovertyMultiplierFileEligibility.povertyAdult

    def build_poverty_multiplier_eligibility(self, state: str, file_name: str) -> None:
        """Java: PovertyMultiplierFileEligibility#buildPovertyMultiplierEligibility.

        Java overloads:
        (String state, String fileName)
        """
        resource = Utilities.read_resource(file_name, True, True)
        csv = SimpleCSV.parse_line_by_line(resource)
        for row in csv:
            if row["state"] == state:
                PovertyMultiplierFileEligibility.povertyAge1 = parse_double(row["0-1"])
                PovertyMultiplierFileEligibility.povertyAge5 = parse_double(row["2-5"])
                PovertyMultiplierFileEligibility.povertyAge18 = parse_double(row["6-18"])
                PovertyMultiplierFileEligibility.povertyPregnant = parse_double(row["pregnant"])
                PovertyMultiplierFileEligibility.povertyAdult = parse_double(row["adult"])
                return
        raise RuntimeError(
            "Poverty Eligibility File '" + file_name + "' does not contain state '" + state + "'."
        )
