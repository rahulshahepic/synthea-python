"""Java API skeleton: HealthInsuranceModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol, cast

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.world.agents.payer_manager import PayerManager

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class HealthInsuranceModule:
    """Java: HealthInsuranceModule."""

    # Java static initializers, evaluated once when the class is loaded.
    mandateTime: ClassVar[int] = Utilities.convert_calendar_years_to_time(
        Config.get_as_integer("generate.insurance.mandate.year", 2006)
    )
    mandateOccupation: ClassVar[float] = Config.get_as_double(
        "generate.insurance.mandate.occupation", 0.2
    )
    povertyLevel: ClassVar[float] = Config.get_as_double(
        "generate.demographics.socioeconomic.income.poverty", 17550
    )

    def __init__(self) -> None:
        """Java: HealthInsuranceModule#HealthInsuranceModule.

        Java overloads:
        ()
        """

    def clone(self) -> Module:
        """Java: HealthInsuranceModule#clone.

        Java overloads:
        ()
        """
        return cast("Module", self)

    def process(self, person: Person, time: int) -> bool:
        """Java: HealthInsuranceModule#process.

        Java overloads:
        (Person person, long time)
        """
        if not person.alive(time):
            return True

        # Enroll patients in new insurance for the year if a new enrollment period is reached.
        # Note: This means the person will check to change insurance yearly, within one timestep
        # after their birthday.
        if person.coverage.new_enrollment_period(time):
            # Update their last plan's payer with person's QOLS for that year.
            person.coverage.update_last_payer_qols(
                person.get_qols_for_year(Utilities.get_year(time) - 1)
            )
            # Update the insurance for this person at this time.
            self.update_insurance(person, time)

        # Checks if person has paid their premium this month. If not, they pay it.
        person.check_to_pay_monthly_premium(time)

        # java modules will never "finish"
        return False

    def update_insurance(self, person: Person, time: int) -> None:
        """Java: HealthInsuranceModule#updateInsurance.

        Java overloads:
        (Person person, long time)
        """
        from synthea.world.agents.person import Person

        new_plan = PayerManager.find_plan(person, None, time)
        secondary_plan = PayerManager.get_no_insurance_plan()
        # If the payer is Medicare, they may buy supplemental insurance.
        if new_plan.may_purchase_supplement() and (person.rand() <= 0.9):
            # 9 out of 10 Medicare patients have supplemental insurance, buy some if affordable.
            # https://www.kff.org/medicare/issue-brief/a-snapshot-of-sources-of-coverage-among-medicare-beneficiaries-in-2018/
            secondary_plan = PayerManager.find_medicare_supplement(person, None, time)
        # Set the person's new plan(s).
        person.coverage.set_plan_at_time(time, new_plan, secondary_plan)
        # Update the new Payer's customer statistics.
        person_id = cast(str, person.attributes.get(Person.ID))
        new_plan.increment_customers(person_id)
        if not secondary_plan.is_no_insurance():
            secondary_plan.increment_customers(person_id)

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: HealthInsuranceModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError(
            "Java: HealthInsuranceModule#inventoryAttributes — out of scope: "
            "helpers/Attributes.java is not in docs/port_map.toml, so the "
            "Attributes.inventory helper has no owning task in the port"
        )
