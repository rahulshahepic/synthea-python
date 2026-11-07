"""Java API skeleton: PayerManager.java."""

from __future__ import annotations

import builtins
import re
import sys
import traceback
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.numbers import to_int64

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.payeradjustment.i_payer_adjustment import IPayerAdjustment
    from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
    from synthea.world.geography.location import Location


class PayerManager:
    """Java: PayerManager."""

    NONE: ClassVar[str] = "none"
    FIXED: ClassVar[str] = "fixed"
    RANDOM: ClassVar[str] = "random"
    BEST_RATE: ClassVar[str] = "best_rate"
    PRIORITY: ClassVar[str] = "priority"
    NAME: ClassVar[str] = "Name"
    ID: ClassVar[str] = "Id"
    PRIORITY_LEVEL: ClassVar[str] = "Priority Level"
    STATES_COVERED: ClassVar[str] = "States Covered"
    OWNERSHIP: ClassVar[str] = "Ownership"
    PAYER_ID: ClassVar[str] = "Payer Id"
    PLAN_ID: ClassVar[str] = "Plan Id"
    SERVICES_COVERED: ClassVar[str] = "Services Covered"
    DEDUCTIBLE: ClassVar[str] = "Deductible"
    COINSURANCE: ClassVar[str] = "Default Coinsurance"
    COPAY: ClassVar[str] = "Default Copay"
    MONTHLY_PREMIUM: ClassVar[str] = "Monthly Premium"
    MAX_OOP: ClassVar[str] = "Max Out of Pocket"
    MEDICARE_SUPPLEMENT: ClassVar[str] = "Medicare Supplement"
    ACA: ClassVar[str] = "Is ACA Plan"
    INCOME_BASED_PREMIUM: ClassVar[str] = "Income Based Premium"
    START_YEAR: ClassVar[str] = "Start Year"
    END_YEAR: ClassVar[str] = "End Year"
    ELIGIBILITY_POLICY: ClassVar[str] = "Eligibility Policy"
    GOV_OWNERSHIP: ClassVar[str] = "GOVERNMENT"
    PRIVATE_OWNERSHIP: ClassVar[str] = "PRIVATE"
    NO_INSURANCE: ClassVar[str] = "NO_INSURANCE"
    MEDICARE: ClassVar[str] = (
        Config.get("generate.payers.insurance_companies.medicare", "Medicare") or "Medicare"
    )
    MEDICAID: ClassVar[str] = (
        Config.get("generate.payers.insurance_companies.medicaid", "Medicaid") or "Medicaid"
    )
    DUAL_ELIGIBLE: ClassVar[str] = (
        Config.get("generate.payers.insurance_companies.dual_eligible", "Dual Eligible")
        or "Dual Eligible"
    )
    payers: ClassVar[dict[int, Payer]] = {}
    noInsurance: ClassVar[Payer]  # Java initialization deferred to T15.
    statesLoaded: ClassVar[builtins.set[str | None]] = set()
    planFinder: ClassVar[IPlanFinder]  # Java initialization deferred to T15.

    def __init__(self) -> None:
        """Java: PayerManager#PayerManager.

        Java overloads:
        ()
        """
        pass

    @staticmethod
    def load_payers(location: Location, file_name: str | None = None) -> None:
        """Java: PayerManager#loadPayers.

        Java overloads:
        (Location location)
        (Location location, String fileName)
        """
        from synthea.world.agents.behaviors.planeligibility.plan_eligibility_finder import (
            PlanEligibilityFinder,
        )
        from synthea.world.geography.location import Location

        if file_name is None:
            eligibility_file = Config.get("generate.payers.insurance_plans.eligibilities_file")
            assert eligibility_file is not None
            PlanEligibilityFinder.build_plan_eligibilities(location.state, eligibility_file)
            PayerManager.planFinder = PayerManager.build_plan_finder()
            abbreviation = Location.get_abbreviation(location.state)
            state_name = Location.get_state_name(location.state)
            if (
                location.state not in PayerManager.statesLoaded
                or abbreviation not in PayerManager.statesLoaded
                or state_name not in PayerManager.statesLoaded
            ):
                try:
                    payer_file = Config.get("generate.payers.insurance_companies.default_file")
                    assert payer_file is not None
                    PayerManager.load_payers(location, payer_file)
                    PayerManager.statesLoaded.update((location.state, abbreviation, state_name))
                except OSError:
                    print(
                        "ERROR: unable to load payers for state: " + location.state, file=sys.stderr
                    )
                    traceback.print_exc()
            return
        PayerManager.load_no_insurance()
        resource = Utilities.read_resource(file_name, True, True)
        for row in SimpleCSV.parse_line_by_line(resource):
            payer_states = row[PayerManager.STATES_COVERED].upper()
            abbreviation = Location.get_abbreviation(location.state)
            assert abbreviation is not None
            if abbreviation.upper() in payer_states or "*" in payer_states:
                payer = PayerManager.csv_line_to_payer(row)
                payer.set_payer_adjustment(PayerManager.build_payer_adjustment())
                PayerManager.payers[payer.get_plan_link_id()] = payer
        PayerManager.load_plans()

    @staticmethod
    def load_plans() -> None:
        """Java: PayerManager#loadPlans.

        Java overloads:
        ()
        """
        file_name = Config.get("generate.payers.insurance_plans.default_file")
        assert file_name is not None
        try:
            resource = Utilities.read_resource(file_name, True, True)
        except OSError:
            traceback.print_exc()
            raise TypeError("Java NullPointerException: csv") from None
        for row in SimpleCSV.parse_line_by_line(resource):
            PayerManager.csv_line_to_plan(row)

    @staticmethod
    def build_plan_finder() -> IPlanFinder:
        """Java: PayerManager#buildPlanFinder.

        Java overloads:
        ()
        """
        from synthea.world.agents.behaviors.planfinder.plan_finder_best_rates import (
            PlanFinderBestRates,
        )
        from synthea.world.agents.behaviors.planfinder.plan_finder_priority import (
            PlanFinderPriority,
        )
        from synthea.world.agents.behaviors.planfinder.plan_finder_random import PlanFinderRandom

        behavior = Config.get("generate.payers.selection_behavior")
        assert behavior is not None
        behavior = behavior.lower()
        if behavior == PayerManager.BEST_RATE:
            return PlanFinderBestRates()
        if behavior == PayerManager.RANDOM:
            return PlanFinderRandom()
        if behavior == PayerManager.PRIORITY:
            return PlanFinderPriority()
        raise RuntimeError("Not a valid Payer Selection Algorithm: " + behavior)

    @staticmethod
    def build_payer_adjustment() -> IPayerAdjustment:
        """Java: PayerManager#buildPayerAdjustment.

        Java overloads:
        ()
        """
        from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_fixed import (
            PayerAdjustmentFixed,
        )
        from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_none import (
            PayerAdjustmentNone,
        )
        from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_random import (
            PayerAdjustmentRandom,
        )

        behavior = Config.get("generate.payers.adjustment_behavior", "none")
        rate_string = Config.get("generate.payers.adjustment_rate", "0.05")
        assert behavior is not None and rate_string is not None
        behavior = behavior.lower()
        rate = float(rate_string)
        if behavior == PayerManager.FIXED:
            return PayerAdjustmentFixed(rate)
        if behavior == PayerManager.RANDOM:
            return PayerAdjustmentRandom(rate)
        return PayerAdjustmentNone()

    @staticmethod
    def csv_line_to_payer(line: dict[str, str]) -> Payer:
        """Java: PayerManager#csvLineToPayer.

        Java overloads:
        (Map line)
        """
        from synthea.world.agents.payer import Payer

        name = line.pop(PayerManager.NAME).strip()
        id = int(line.pop(PayerManager.ID).strip())
        if id in PayerManager.payers:
            raise RuntimeError(f"The given payer id '{id}' already exists.")
        if id < 0:
            raise RuntimeError(f"Payer IDs must be non-negative. Given Id {id}.")
        states = PayerManager.comma_separated_string_to_hash_set(
            line.pop(PayerManager.STATES_COVERED).strip()
        )
        ownership = line.pop(PayerManager.OWNERSHIP).strip().upper()
        if ownership not in (PayerManager.GOV_OWNERSHIP, PayerManager.PRIVATE_OWNERSHIP):
            raise RuntimeError(
                f"A Payer's ownership must be tagged as either {PayerManager.GOV_OWNERSHIP}"
                f" or {PayerManager.PRIVATE_OWNERSHIP}. Payer {name} {id}"
                f" has ownership of {ownership}."
            )
        payer = Payer(name, id, states, ownership)
        for key, value in line.items():
            payer.add_attribute(key, value)
        return payer

    @staticmethod
    def csv_line_to_plan(line: dict[str, str]) -> None:
        """Java: PayerManager#csvLineToPlan.

        Java overloads:
        (Map line)
        """
        from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan

        payer_id = int(line.pop(PayerManager.PAYER_ID).strip())
        plan_id = int(line.pop(PayerManager.PLAN_ID).strip())
        if plan_id < 0:
            raise RuntimeError(f"Plan IDs must be non-negative. Given Id {plan_id}.")
        if payer_id not in PayerManager.payers:
            return
        services = PayerManager.comma_separated_string_to_hash_set(
            line.pop(PayerManager.SERVICES_COVERED).strip()
        )
        deductible = bd.from_string(line.pop(PayerManager.DEDUCTIBLE).strip())
        coinsurance = bd.from_string(line.pop(PayerManager.COINSURANCE).strip())
        copay = bd.from_string(line.pop(PayerManager.COPAY).strip())
        premium = bd.from_string(line.pop(PayerManager.MONTHLY_PREMIUM).strip())
        supplement = line.pop(PayerManager.MEDICARE_SUPPLEMENT).strip().lower() == "true"
        aca = line.get(PayerManager.ACA, "false").strip().lower() == "true"
        income_based = (
            line.get(PayerManager.INCOME_BASED_PREMIUM, "false").strip().lower() == "true"
        )
        start_str = line.pop(PayerManager.START_YEAR).strip()
        start = 0 if start_str == "" else int(start_str)
        end_str = line.pop(PayerManager.END_YEAR).strip()
        end = (1 << 31) - 1 if not end_str else int(end_str)
        max_oop = bd.from_string(line.get(PayerManager.MAX_OOP, "0").strip())
        priority_str = line.get(PayerManager.PRIORITY_LEVEL, "").strip()
        priority = (1 << 31) - 1 if not priority_str else int(priority_str)
        eligibility = line.pop(PayerManager.ELIGIBILITY_POLICY)
        payer = PayerManager.payers[payer_id]
        payer.add_plan(
            InsurancePlan(
                plan_id,
                payer,
                services,
                deductible,
                coinsurance,
                copay,
                premium,
                max_oop,
                supplement,
                aca,
                income_based,
                start,
                end,
                priority,
                eligibility,
            )
        )

    @staticmethod
    def comma_separated_string_to_hash_set(field: str) -> builtins.set[str]:
        """Java: PayerManager#commaSeparatedStringToHashSet.

        Java overloads:
        (String field)
        """
        fields = re.split(r"\s*,\s*", field)
        if field:
            while fields and not fields[-1]:
                fields.pop()
        return set(fields)

    @staticmethod
    def load_no_insurance() -> None:
        """Java: PayerManager#loadNoInsurance.

        Java overloads:
        ()
        """
        from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_none import (
            PayerAdjustmentNone,
        )
        from synthea.world.agents.behaviors.planeligibility.plan_eligibility_finder import (
            PlanEligibilityFinder,
        )
        from synthea.world.agents.payer import Payer
        from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan

        PayerManager.noInsurance = Payer(
            PayerManager.NO_INSURANCE, -1, {"*"}, PayerManager.NO_INSURANCE
        )
        plan = InsurancePlan(
            -1,
            PayerManager.noInsurance,
            set(),
            Decimal(0),
            Decimal(0),
            Decimal(0),
            Decimal(0),
            Decimal((1 << 31) - 1),
            False,
            False,
            False,
            0,
            (1 << 31) - 1,
            0,
            PlanEligibilityFinder.GENERIC,
        )
        PayerManager.noInsurance.add_plan(plan)
        PayerManager.noInsurance.set_payer_adjustment(PayerAdjustmentNone())

    @staticmethod
    def get_all_payers() -> list[Payer]:
        """Java: PayerManager#getAllPayers.

        Java overloads:
        ()
        """
        return list(PayerManager.payers.values())

    @staticmethod
    def clear() -> None:
        """Java: PayerManager#clear.

        Java overloads:
        ()
        """
        PayerManager.payers.clear()
        PayerManager.statesLoaded.clear()
        PayerManager.planFinder = PayerManager.build_plan_finder()

    @staticmethod
    def find_plan(person: Person, service: EncounterType | None, time: int) -> InsurancePlan:
        """Java: PayerManager#findPlan.

        Java overloads:
        (Person person, EncounterType service, long time)
        """
        from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder

        plans = [
            plan
            for plan in PayerManager.get_active_plans(PayerManager.get_all_payers(), time)
            if not plan.is_medicare_supplement_plan()
        ]
        potential = PayerManager.planFinder.find(plans, person, service, time)
        if potential.is_government_plan():
            return potential
        if person.coverage.get_plan_history():
            previous = person.coverage.get_plan_at_time(
                to_int64(time - Config.get_as_long("generate.timestep"))
            )
            if (
                not previous.is_no_insurance()
                and previous.accepts(person, time)
                and previous.is_active(time)
                and IPlanFinder.meets_affordability_requirements(previous, person, None, time)
            ):
                return previous
        return potential

    @staticmethod
    def get_active_plans(payers: list[Payer], time: int) -> list[InsurancePlan]:
        """Java: PayerManager#getActivePlans.

        Java overloads:
        (List payers, long time)
        """
        return [plan for payer in payers for plan in payer.get_plans() if plan.is_active(time)]

    @staticmethod
    def get_no_insurance_plan() -> InsurancePlan:
        """Java: PayerManager#getNoInsurancePlan.

        Java overloads:
        ()
        """
        return PayerManager.noInsurance.get_plans()[0]

    @staticmethod
    def find_medicare_supplement(
        person: Person, service: EncounterType | None, time: int
    ) -> InsurancePlan:
        """Java: PayerManager#findMedicareSupplement.

        Java overloads:
        (Person person, EncounterType service, long time)
        """
        plans = [
            plan
            for plan in PayerManager.get_active_plans(PayerManager.get_all_payers(), time)
            if plan.is_medicare_supplement_plan()
        ]
        return PayerManager.planFinder.find(plans, person, service, time)
