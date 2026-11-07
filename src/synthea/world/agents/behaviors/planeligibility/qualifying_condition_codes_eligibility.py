"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planeligibility/Q
ualifyingConditionCodesEligibility.java.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

_LONG_MAX_VALUE = 9223372036854775807  # Java: Long.MAX_VALUE


class QualifyingConditionCodesEligibility:
    """Java: org.mitre.synthea.world.agents.behaviors.planeligibility.QualifyingConditionCo
    desEligi
    bility.
    """

    def __init__(self, codes: str) -> None:
        """Java: QualifyingConditionCodesEligibility#QualifyingConditionCodesEligibility.

        Java overloads:
        (String codes)
        """
        if codes.endswith(".csv"):
            # The input is a csv file, so we have a file that defines the eligible conditions.
            self.qualifying_codes: list[str] = self.build_qualifying_conditions_file(codes)
        else:
            # The input is a string set of codes. Java String.split drops
            # trailing empty strings.
            self.qualifying_codes = re.split(r"\|", codes)
            if codes:
                while self.qualifying_codes and not self.qualifying_codes[-1]:
                    self.qualifying_codes.pop()

    def is_person_eligible(self, person: Person, time: int) -> bool:
        """Java: QualifyingConditionCodesEligibility#isPersonEligible.

        Java overloads:
        (Person person, long time)
        """
        assert person.record is not None
        return any(person.record.condition_active(code) for code in self.qualifying_codes)

    @staticmethod
    def build_qualifying_conditions_file(file_name: str) -> list[str]:
        """Java: QualifyingConditionCodesEligibility#buildQualifyingConditionsFile.

        Java overloads:
        (String fileName)
        """
        resource = Utilities.read_resource(file_name, True, True)

        eligible_codes: list[str] = []

        for row in SimpleCSV.parse_line_by_line(resource):
            code_value = row["codes"]
            codes = re.split(r"\|", code_value)
            if code_value:
                while codes and not codes[-1]:
                    codes.pop()
            eligible_codes.extend(codes)
        return eligible_codes

    def get_earliest_diagnosis(self, person: Person) -> int:
        """Java: QualifyingConditionCodesEligibility#getEarliestDiagnosis.

        Java overloads:
        (Person person)
        """
        assert person.record is not None
        earliest = _LONG_MAX_VALUE
        for code in self.qualifying_codes:
            onset = person.record.present_onset(code)
            if onset is not None:
                earliest = min(earliest, onset)
        return earliest
