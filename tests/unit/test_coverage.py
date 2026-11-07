"""JUnit ports: org.mitre.synthea.world.agents.PayerTest (T16 surface).

Covers the tests that exercise HealthInsuranceModule, CoverageRecord,
PlanRecord and the planeligibility package against the generic test payers.
Setup mirrors PayerTest's @BeforeClass/@Before: the test payer/plan/
eligibility CSVs are loaded through the real PayerManager; Config file keys
point at java/src/test/resources (read via Utilities.readResource's
free-path fallback, the Python analogue of the Java test classpath).

Adaptation: receiveMedicareSsdBreastCancerEligible inserts the condition
entry directly into the record's present map instead of using a mock
provider + conditionStart; conditionActive only reads that map, so the
eligibility-relevant state is identical.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.bigdecimal import RoundingMode
from synthea.modules.health_insurance_module import HealthInsuranceModule
from synthea.world.agents.payer import Payer
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Entry
from synthea.world.concepts.healthinsurance.coverage_record import _add_one_calendar_year
from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
from synthea.world.geography.location import Location

TEST_RESOURCES = Path(__file__).resolve().parents[2] / "java" / "src" / "test" / "resources"
TEST_STATE = "Massachusetts"
# In MA, the minimum poverty multiplier is 1.33.
MEDICAID_LEVEL = 1.33 * HealthInsuranceModule.povertyLevel
MANDATE_TIME = Utilities.convert_calendar_years_to_time(
    Config.get_as_integer("generate.insurance.mandate.year", 2006)
)


@pytest.fixture
def payer_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[SimpleNamespace]:
    """Java: PayerTest.setup + PayerTest.before."""
    monkeypatch.setattr(Config, "properties", Config.properties.copy())
    Config.set("generate.payers.insurance_companies.medicare", "Medicare")
    Config.set("generate.payers.insurance_companies.medicaid", "Medicaid")
    Config.set("generate.payers.insurance_companies.dual_eligible", "Dual Eligible")
    Config.set(
        "generate.payers.insurance_companies.default_file",
        str(TEST_RESOURCES / "generic" / "payers" / "test_payers.csv"),
    )
    Config.set(
        "generate.payers.insurance_plans.default_file",
        str(TEST_RESOURCES / "generic" / "payers" / "test_plans.csv"),
    )
    Config.set(
        "generate.payers.insurance_plans.eligibilities_file",
        str(TEST_RESOURCES / "generic" / "payers" / "test_insurance_eligibilities.csv"),
    )
    Config.set("generate.payers.insurance_plans.income_premium_ratio", "1.0")
    PayerManager.clear()
    PayerManager.load_payers(Location(TEST_STATE, None))
    private = [
        payer
        for payer in PayerManager.get_all_payers()
        if payer.get_ownership() == PayerManager.PRIVATE_OWNERSHIP
    ]
    payer1 = next(p for p in private if p.get_name() == "Test Private Payer 1")
    payer2 = next(p for p in private if p.get_name() == "Test Private Payer 2")
    min_affordability = (
        max(
            bd.double_value(
                bd.multiply(next(iter(payer1.get_plans())).get_monthly_premium(0), Decimal(12))
            ),
            bd.double_value(
                bd.multiply(next(iter(payer2.get_plans())).get_monthly_premium(0), Decimal(12))
            ),
        )
        * 2
    )
    yield SimpleNamespace(
        module=HealthInsuranceModule(),
        payer1=payer1,
        payer2=payer2,
        min_private_affordability=min_affordability,
    )
    PayerManager.clear()


def government_payer(name: str) -> Payer:
    """Java: PayerTest.getGovernmentPayer."""
    return next(p for p in PayerManager.get_all_payers() if p.get_name() == name)


def make_person(birth: int, **attributes: object) -> Person:
    person = Person(0)
    person.attributes[Person.BIRTHDATE] = birth
    for key, value in attributes.items():
        person.attributes[key] = value
    return person


def add_years(time: int, years: int) -> int:
    """java.util.Calendar.add(Calendar.YEAR, years) applied one year at a time."""
    for _ in range(years):
        time = _add_one_calendar_year(time)
    return time


def process_insurance_for_ages(
    module: HealthInsuranceModule, person: Person, start_age: int, end_age: int
) -> None:
    """Java: PayerTest.processInsuranceForAges."""
    timestep = Config.get_as_long("generate.timestep")
    birth_date = person.attributes[Person.BIRTHDATE]
    assert isinstance(birth_date, int)
    current_time = add_years(birth_date, start_age)
    for current_age in range(start_age, end_age + 1):
        # Java advances a Calendar anchored at the birth date, so each year
        # ends exactly on the (age + 1)-th birthday: no drift.
        year_end = add_years(birth_date, current_age + 1)
        while current_time < year_end:
            module.process(person, current_time)
            current_time += timestep


def test_receive_medicare_age_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicareAgeEligible."""
    module: HealthInsuranceModule = payer_state.module
    birth_year = 1900
    birth_time = Utilities.convert_calendar_years_to_time(birth_year)
    person = make_person(
        birth_time,
        **{
            Person.GENDER: "F",
            Person.OCCUPATION_LEVEL: 1.0,
            "end_stage_renal_disease": False,
            Person.INCOME: int(MEDICAID_LEVEL) * 100,
        },
    )
    # Process the person's health insurance for 64 years, should have private
    # insurance for all.
    for age in range(0, 65):
        current_time = Utilities.convert_calendar_years_to_time(birth_year + age)
        assert person.age(current_time).get_years() == age
        module.process(person, current_time)
        assert (
            person.coverage.get_plan_at_time(current_time).get_payer().get_ownership()
            == PayerManager.PRIVATE_OWNERSHIP
        )
    # Process their insurance for ages 65-69, should have medicare every year.
    for age in range(65, 70):
        current_time = Utilities.convert_calendar_years_to_time(birth_year + age)
        module.process(person, current_time)
        payer_name = person.coverage.get_plan_at_time(current_time).get_payer().get_name()
        assert person.age(current_time).get_years() == age
        assert payer_name == "Medicare"
        assert person.coverage.get_plan_at_time(current_time).accepts(person, current_time)


def test_receive_medicare_esrd_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicareEsrdEligible."""
    module: HealthInsuranceModule = payer_state.module
    time = Utilities.convert_calendar_years_to_time(1980)
    person = make_person(
        time,
        **{
            Person.GENDER: "M",
            "end_stage_renal_disease": True,
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) * 100,
        },
    )
    module.process(person, time)
    current_payer = person.coverage.get_plan_at_time(time).get_payer()
    assert government_payer(PayerManager.MEDICARE) is current_payer


def test_receive_medicare_ssd_breast_cancer_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicareSsdBreastCancerEligible."""
    module: HealthInsuranceModule = payer_state.module
    time = Utilities.convert_calendar_years_to_time(1980)
    person = make_person(
        time,
        **{
            Person.GENDER: "F",
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) * 100,
        },
    )
    # Process health insurance prior to condition start to prevent null pointer.
    module.process(person, time)
    assert person.record is not None
    person.record.present["254837009"] = person.record.new_entry(lambda: Entry(time, "254837009"))
    # Process health insurance after condition start now that the person is eligible.
    time = add_years(time, 1)
    module.process(person, time)
    assert (
        government_payer(PayerManager.MEDICARE)
        is person.coverage.get_plan_at_time(time).get_payer()
    )


def test_receive_medicaid_pregnancy_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicaidPregnancyEligible."""
    module: HealthInsuranceModule = payer_state.module
    time = Utilities.convert_calendar_years_to_time(1980)
    person = make_person(
        time,
        **{
            Person.GENDER: "F",
            "pregnant": True,
            Person.OCCUPATION_LEVEL: 1.0,
            # A pregnant person is eligble in MA when their income is less
            # than 2 * the poverty level.
            Person.INCOME: int(HealthInsuranceModule.povertyLevel * 2) - 1,
        },
    )
    module.process(person, time)
    assert person.coverage.get_plan_at_time(time).get_payer().get_name() == PayerManager.MEDICAID
    assert person.coverage.get_plan_at_time(time).accepts(person, time)


def test_receive_medicaid_poverty_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicaidPovertyEligible."""
    module: HealthInsuranceModule = payer_state.module
    time = 0
    person = make_person(
        time,
        **{
            Person.GENDER: "F",
            Person.OCCUPATION_LEVEL: 1.0,
            Person.BLINDNESS: False,
            Person.INCOME: int(MEDICAID_LEVEL) - 1,
        },
    )
    module.process(person, time)
    assert person.coverage.get_plan_at_time(time).get_payer().get_name() == "Medicaid"


def test_receive_medicaid_blindness_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicaidBlindnessEligble."""
    module: HealthInsuranceModule = payer_state.module
    time = 0
    person = make_person(
        time,
        **{
            Person.GENDER: "M",
            Person.BLINDNESS: True,
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) * 100,
        },
    )
    module.process(person, time)
    assert person.coverage.get_plan_at_time(time).get_payer().get_name() == "Medicaid"


def test_plan_time_box_ranges(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.planTimeBoxRanges."""
    module: HealthInsuranceModule = payer_state.module
    # Load the time-boxed plans.
    PayerManager.clear()
    PayerManager.load_payers(Location(TEST_STATE, None))

    current_year = 1960
    time = Utilities.convert_calendar_years_to_time(current_year)
    person = make_person(
        time,
        **{
            Person.GENDER: "M",
            "time-boxed-test": True,
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) * 100,
        },
    )
    # For the first 5 years, they should not have Dual Eligible (1960-1964).
    for _ in range(5):
        module.process(person, time)
        assert person.coverage.get_plan_at_time(time).get_payer().get_name() != "Dual Eligible"
        current_year += 1
        time = Utilities.convert_calendar_years_to_time(current_year)
    # For the next 4 years, they should have Dual Eligible (1965-1968).
    for _ in range(4):
        module.process(person, time)
        assert person.coverage.get_plan_at_time(time).get_payer().get_name() == "Dual Eligible"
        current_year += 1
        time = Utilities.convert_calendar_years_to_time(current_year)
    # After that, they should no longer have Dual Eligible (1969).
    module.process(person, time)
    assert person.coverage.get_plan_at_time(time).get_payer().get_name() != "Dual Eligible"


def test_receive_medicaid_mnil_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveMedicaidMnilEligble."""
    module: HealthInsuranceModule = payer_state.module
    time = Utilities.convert_calendar_years_to_time(1980)
    person = make_person(
        time,
        **{
            Person.GENDER: "M",
            Person.OCCUPATION_LEVEL: 0.1,
            # The minimum income that does not qualify for MA Medicaid at
            # age 0 is FPL * 2.0 + 1.
            Person.INCOME: int(HealthInsuranceModule.povertyLevel * 2 + 1),
        },
    )
    income = person.attributes[Person.INCOME]
    assert isinstance(income, int)
    module.process(person, time)
    # They should not have Medicaid in this first year.
    assert person.coverage.get_plan_at_time(time).get_payer().get_name() != "Medicaid"
    # The MA yearly spenddown amount is $6264. They need $(income - 6264) in
    # healthcare expenses.
    person.coverage.get_plan_record_at_time(time).increment_out_of_pocket_expenses(
        Decimal(income - 6264)
    )
    # Now process their insurance and they should switch to Medicaid.
    time = add_years(time, 1)
    module.process(person, time)
    assert person.coverage.get_plan_at_time(time).get_payer().get_name() == "Medicaid"


def test_receive_dual_eligible(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveDualEligible."""
    module: HealthInsuranceModule = payer_state.module
    birth_year = 1950
    birth_time = Utilities.convert_calendar_years_to_time(birth_year)
    person = make_person(
        birth_time,
        **{
            Person.GENDER: "M",
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) - 1,
        },
    )
    # Process the person's health insurance for 64 years, should have
    # Medicaid for all.
    for age in range(0, 65):
        current_time = Utilities.convert_calendar_years_to_time(birth_year + age)
        assert person.age(current_time).get_years() == age
        module.process(person, current_time)
        assert (
            government_payer(PayerManager.MEDICAID)
            is person.coverage.get_plan_at_time(current_time).get_payer()
        )
    age64_time = Utilities.convert_calendar_years_to_time(birth_year + 64)
    assert (
        person.coverage.get_plan_at_time(age64_time).get_payer().get_name() == PayerManager.MEDICAID
    )
    # The person is now 65 and qualifies for Medicare in addition to Medicaid.
    age65_time = Utilities.convert_calendar_years_to_time(birth_year + 65)
    module.process(person, age65_time)
    assert (
        person.coverage.get_plan_at_time(age65_time).get_payer().get_name()
        == PayerManager.DUAL_ELIGIBLE
    )
    assert person.coverage.get_plan_at_time(age65_time).accepts(person, age65_time)


def test_receive_no_insurance(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receiveNoInsurance."""
    module: HealthInsuranceModule = payer_state.module
    plan: InsurancePlan = next(iter(payer_state.payer1.get_plans()))
    monthly_premium = plan.get_monthly_premium(0)
    deductible = plan.get_deductible()
    total_yearly_cost = bd.add(bd.multiply(monthly_premium, Decimal(12)), deductible)
    birth_time = Utilities.convert_calendar_years_to_time(1980)
    person = make_person(
        birth_time,
        **{Person.GENDER: "F", Person.OCCUPATION_LEVEL: 0.001},
    )
    # Give the person an income lower than the totalYearlyCost divided by the
    # max income ratio a person is willing to spend on health insurance.
    ratio = Config.get_as_double("generate.payers.insurance_plans.income_premium_ratio")
    cost_threshold = bd.divide_round(total_yearly_cost, bd.value_of(ratio), RoundingMode.HALF_UP)
    cost_threshold = bd.subtract(cost_threshold, Decimal(10))
    person.attributes[Person.INCOME] = bd.int_value(cost_threshold)

    module.process(person, birth_time)
    new_plan = person.coverage.get_plan_at_time(birth_time)
    assert new_plan.is_no_insurance()


def test_receive_private_insurance_post_mandate(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receivePrivateInsurancePostMandate."""
    module: HealthInsuranceModule = payer_state.module
    time = add_years(MANDATE_TIME, 1)
    person = make_person(
        time,
        **{
            Person.GENDER: "F",
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) + 100,
        },
    )
    module.process(person, time)
    assert not person.coverage.get_plan_at_time(time).is_no_insurance()


def test_receive_private_insurance_with_wealth(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.receivePrivateInsuranceWithWealth."""
    module: HealthInsuranceModule = payer_state.module
    time = add_years(MANDATE_TIME, -50)
    person = make_person(
        time,
        **{
            Person.GENDER: "F",
            Person.OCCUPATION_LEVEL: 1.0,
            Person.INCOME: int(MEDICAID_LEVEL) * 100,
        },
    )
    module.process(person, time)
    assert not person.coverage.get_plan_at_time(time).is_no_insurance()


def test_overwrite_insurance(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.overwriteInsurance."""
    person = make_person(0)
    plan: InsurancePlan = next(iter(payer_state.payer1.get_plans()))
    person.coverage.set_plan_at_time(0, plan, PayerManager.get_no_insurance_plan())
    person.coverage.set_plan_at_time(0, plan, PayerManager.get_no_insurance_plan())
    assert len(person.coverage.get_plan_history()) == 2


def test_monthly_premium_payment(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.monthlyPremiumPayment."""
    module: HealthInsuranceModule = payer_state.module
    person = make_person(
        Utilities.convert_calendar_years_to_time(1930),
        **{
            Person.GENDER: "F",
            Person.ID: "monthly-premium-person",
            Person.INCOME: int(payer_state.min_private_affordability),
            Person.OCCUPATION_LEVEL: 0.0,
        },
    )
    # Predetermine person's Payer.
    process_insurance_for_ages(module, person, 0, 64)

    person_id = person.attributes[Person.ID]
    assert isinstance(person_id, str)
    payer1_member_years = Decimal(payer_state.payer1.get_customer_utilization(person_id))
    payer2_member_years = Decimal(payer_state.payer2.get_customer_utilization(person_id))
    assert payer1_member_years + payer2_member_years == Decimal(65)

    total_monthly_premiums_owed = Decimal(0)
    payer_one_yearly_premium = bd.multiply(
        next(iter(payer_state.payer1.get_plans())).get_monthly_premium(0), Decimal(12)
    )
    total_monthly_premiums_owed = bd.add(
        total_monthly_premiums_owed, bd.multiply(payer_one_yearly_premium, payer1_member_years)
    )
    payer_two_yearly_premium = bd.multiply(
        next(iter(payer_state.payer2.get_plans())).get_monthly_premium(0), Decimal(12)
    )
    total_monthly_premiums_owed = bd.set_scale(
        bd.add(
            total_monthly_premiums_owed,
            bd.multiply(payer_two_yearly_premium, payer2_member_years),
        ),
        2,
        RoundingMode.CEILING,
    )

    total_revenue = bd.add(payer_state.payer1.get_revenue(), payer_state.payer2.get_revenue())
    # The payer's revenue should equal the total monthly premiums.
    assert bd.compare_to(total_monthly_premiums_owed, total_revenue) == 0
    # The person's health care expenses should equal the total monthly premiums.
    assert bd.equals(total_monthly_premiums_owed, person.coverage.get_total_premium_expenses())


def test_monthly_premium_payment_to_null_payer(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.monthlyPremiumPaymentToNullPayer (expects RuntimeException).

    The Java person has no occupation/income attributes, so the JVM throws
    NullPointerException unboxing them; the Python Person API requires those
    attributes, so they are set here and the failure lands where the test's
    intent points: paying a monthly premium with no plan at that time raises
    CoverageRecord's RuntimeException.
    """
    person = make_person(
        0,
        **{
            Person.ID: "null-payer-person",
            Person.OCCUPATION_LEVEL: 0.0,
            Person.INCOME: 0,
        },
    )
    with pytest.raises(RuntimeError):
        person.check_to_pay_monthly_premium(0)


def test_get_nonexistant_eligibility(payer_state: SimpleNamespace) -> None:
    """Java: PayerTest.getNonexistantEligibility (expects RuntimeException)."""
    from synthea.world.agents.behaviors.planeligibility.plan_eligibility_finder import (
        PlanEligibilityFinder,
    )

    with pytest.raises(RuntimeError):
        PlanEligibilityFinder.get_eligibility_algorithm("FAKE")


def test_qualifying_attributes_file_eligibility() -> None:
    """Java: PayerTest.qualifyingAttributesFileEligibility."""
    from synthea.world.agents.behaviors.planeligibility.qualifying_attributes_eligibility import (
        QualifyingAttributesEligibility,
    )

    file_name = str(TEST_RESOURCES / "generic" / "payers" / "test_attributes_eligibility.csv")
    qae = QualifyingAttributesEligibility(file_name)
    time = Utilities.convert_calendar_years_to_time(1975)
    person = Person(0)
    person.attributes["test2"] = "TEST"
    assert not qae.is_person_eligible(person, time)
    person.attributes["test1"] = True
    assert qae.is_person_eligible(person, time)
    person.attributes["test1"] = False
    assert not qae.is_person_eligible(person, time)
    person.attributes["test2"] = "NOT TEST"
    assert qae.is_person_eligible(person, time)
    person.attributes["test2"] = "TEST"
    assert not qae.is_person_eligible(person, time)
    person.attributes["test3"] = 5.5
    assert not qae.is_person_eligible(person, time)
    person.attributes["test3"] = 5.49
    assert not qae.is_person_eligible(person, time)
    person.attributes["test3"] = 5.501
    assert qae.is_person_eligible(person, time)
    del person.attributes["test3"]
    assert not qae.is_person_eligible(person, time)
    person.attributes["test4"] = 4.2
    assert qae.is_person_eligible(person, time)
    person.attributes["test4"] = 4.21
    assert not qae.is_person_eligible(person, time)
    person.attributes["test5"] = "TEST"
    assert qae.is_person_eligible(person, time)
    person.attributes["test5"] = "INVALID"
    assert not qae.is_person_eligible(person, time)
    person.attributes["test6"] = -50
    assert qae.is_person_eligible(person, time)
    person.attributes["test6"] = 12.1
    assert not qae.is_person_eligible(person, time)
    person.attributes["test6"] = 12.09
    assert qae.is_person_eligible(person, time)
    person.attributes["test6"] = 14
    assert not qae.is_person_eligible(person, time)
    person.attributes["test7"] = "FALSE"
    assert qae.is_person_eligible(person, time)
    person.attributes["test7"] = "TRUE"
    assert not qae.is_person_eligible(person, time)
    person.attributes["test8"] = True
    assert qae.is_person_eligible(person, time)
    person.attributes["test8"] = False
    assert not qae.is_person_eligible(person, time)
    person.attributes["test9"] = 10.0
    assert qae.is_person_eligible(person, time)
    person.attributes["test9"] = 10
    assert qae.is_person_eligible(person, time)
    person.attributes["test9"] = 9.9
    assert not qae.is_person_eligible(person, time)
    person.attributes["test10"] = 5
    assert qae.is_person_eligible(person, time)
    person.attributes["test10"] = 5.0
    assert qae.is_person_eligible(person, time)
    person.attributes["test10"] = 6
    assert not qae.is_person_eligible(person, time)
    person.attributes["test11"] = 456
    assert qae.is_person_eligible(person, time)
    person.attributes["test11"] = 456.0
    assert qae.is_person_eligible(person, time)
    person.attributes["test11"] = 457
    assert qae.is_person_eligible(person, time)
    person.attributes["test11"] = 455
    assert not qae.is_person_eligible(person, time)
