"""T15 ports of the payer, plan-finder and adjustment JUnit component assertions."""

from __future__ import annotations

from decimal import Decimal
from typing import cast
from unittest.mock import Mock

import pytest

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_fixed import (
    PayerAdjustmentFixed,
)
from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_none import PayerAdjustmentNone
from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_random import (
    PayerAdjustmentRandom,
)
from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder
from synthea.world.agents.behaviors.planfinder.plan_finder_best_rates import PlanFinderBestRates
from synthea.world.agents.behaviors.planfinder.plan_finder_priority import PlanFinderPriority
from synthea.world.agents.behaviors.planfinder.plan_finder_random import PlanFinderRandom
from synthea.world.agents.payer import Payer, UtilizationBean
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.concepts.health_record import (
    Encounter,
    Entry,
    Immunization,
    Medication,
    Procedure,
)
from tests.parity.test_payer import (
    TIME,
    PayerEncounter_double,
    PayerPerson_double,
    _claim_entry,
    _plan,
)
from tests.parity.test_payer import (
    payer_component_boundary as payer_component_boundary,
)


def test_payer_null_name() -> None:
    """PayerTest.nullPayerName."""
    with pytest.raises(RuntimeError, match="non-null name"):
        Payer("", 7, {"*"}, "PRIVATE")


def test_payer_customers_member_years_and_qols() -> None:
    """PayerTest.incrementCustomers and payerMemberYears."""
    payer = Payer("Private", 7, {"*"}, "PRIVATE")
    assert payer.get_customer_utilization("missing") == 0
    assert str(payer.get_qols_average()) == "nan"
    for person_id in ("a", "a", "b", "a", "c"):
        payer.increment_customers(person_id)
    assert payer.get_unique_customers() == 3
    assert payer.get_num_years_covered() == 5
    assert payer.get_customer_utilization("a") == 3
    payer.add_qols(3.75)
    assert payer.get_qols_average() == 0.75


@pytest.mark.parametrize(
    "entry_type,count_name",
    [
        (Encounter, "encounters"),
        (Medication, "medications"),
        (Procedure, "procedures"),
        (Immunization, "immunizations"),
        (Entry, "no_cost"),
    ],
)
def test_payer_increment_entries(entry_type, count_name: str) -> None:
    """PayerTest.incrementEncounters, all counted subclasses and the no-cost fallback."""
    payer = Payer("Private", 7, {"*"}, "PRIVATE")
    entry = cast(Entry, Mock(spec=entry_type))
    entry.start, entry.type = TIME, "example"
    payer.increment_covered_entries(entry)
    payer.increment_covered_entries(entry)
    payer.increment_uncovered_entries(entry)
    assert payer.entry_utilization[2020]["covered-" + count_name] == 2
    assert payer.entry_utilization[2020]["uncovered-" + count_name] == 1
    assert payer.entry_utilization[2020]["covered-" + count_name + "-example"] == 2
    if count_name != "no_cost":
        assert getattr(payer, f"get_{count_name}_covered_count")() == 2
        assert getattr(payer, f"get_{count_name}_uncovered_count")() == 1


def test_payer_bigdecimal_statistics_and_equality() -> None:
    """PayerTest costsCoveredByPayer/costsUncoveredByNoInsurance arithmetic and Java equality."""
    a = Payer("Private", 7, {"*"}, "PRIVATE")
    b = Payer("Private", 7, {"*"}, "PRIVATE")
    assert a.equals(b) and a.hash_code() == b.hash_code()
    assert a.get_resource_id() == a.uuid
    assert not a.equals(None)
    a.add_covered_cost(Decimal("123.456"))
    a.add_uncovered_cost(Decimal("7.2"))
    a.add_revenue(Decimal("0.0123"))
    assert bd.to_string(a.get_amount_covered()) == "123.456"
    assert bd.to_string(a.get_amount_uncovered()) == "7.20"
    assert bd.to_string(a.get_revenue()) == "0.0123"
    assert not a.equals(b)
    b.costs_covered, b.costs_uncovered, b.revenue = a.costs_covered, a.costs_uncovered, a.revenue
    assert a.equals(b)
    b.revenue = Decimal("0.01230")
    assert not a.equals(b)  # scale-sensitive BigDecimal.equals
    assert a.equals(a)
    bean = UtilizationBean(2020, "encounter", 3)
    assert (bean.year, bean.type, bean.count) == (2020, "encounter", 3)


def test_payer_government_and_coverage(payer_component_boundary: None) -> None:
    """PayerTest getGovPlanFromPrivatePayer, payerCoversEncounter, payerDoesNotCoverEncounter."""
    private = Payer("Private", 1, {"*"}, "PRIVATE")
    gov = Payer("Medicare", 2, {"*"}, "GOVERNMENT")
    p = _plan(1, private, Decimal("100"), services="emergency")
    g = _plan(2, gov, Decimal("100"))
    assert gov.get_government_payer_plan() is g
    assert g.may_purchase_supplement() and g.is_government_plan()
    assert g.get_insurance_status() == "medicare"
    with pytest.raises(RuntimeError, match="Only government"):
        private.get_government_payer_plan()
    entry = cast(Entry, Mock(spec=Entry))
    entry.type = "emergency"
    assert private.covers_care(entry)
    entry.type = "wellness"
    assert not private.covers_care(entry)
    assert p.covers_service(None)


@pytest.mark.parametrize("rate,expected", [(-1.0, 0.0), (2.0, 1.0), (0.5, 0.5)])
def test_payer_adjustment_rate_bounds(rate: float, expected: float) -> None:
    """PayerAdjustmentTest.testRateBounds."""
    assert PayerAdjustmentFixed(rate).rate == expected
    assert PayerAdjustmentRandom(rate).rate == expected


def test_payer_adjustments(payer_component_boundary: None) -> None:
    """All three PayerAdjustmentTest adjustment tests; mocked random branches remain unit tests."""
    person = PayerPerson_double(0)
    entry = _claim_entry(Decimal("101.25"))
    assert bd.equals(PayerAdjustmentNone().adjust_claim(entry, person), Decimal("0.00"))
    assert entry.adjustment == Decimal("7.77")
    assert bd.to_string(PayerAdjustmentFixed(0.5).adjust_claim(entry, person)) == "50.62"
    assert bd.equals(PayerAdjustmentFixed(1.0).adjust_claim(entry, person), entry.cost)
    assert bd.equals(PayerAdjustmentFixed(0.0).adjust_claim(entry, person), Decimal("0.00"))
    shadow = Mock(spec=person)
    shadow.rand_boolean.return_value = True
    shadow.rand.return_value = 0.5
    assert PayerAdjustmentRandom(0.5).adjust_claim(entry, shadow) == Decimal("50.62")
    shadow.rand_boolean.return_value = False
    assert PayerAdjustmentRandom(0.5).adjust_claim(entry, shadow) == Decimal("0.00")
    assert entry.adjustment == Decimal("50.62")


def test_payer_income_and_employer_premiums(payer_component_boundary: None) -> None:
    """PayerTest.incomeBasedPremium/employerPremiumCoverage and monthlyPremiumPayment."""
    private = Payer("Private", 1, {"*"}, "PRIVATE")
    income = _plan(1, private, Decimal("0.5"), income=True)
    assert bd.to_string(income.get_monthly_premium(100000)) == "4166.67"
    ordinary = _plan(2, private, Decimal("1000"))
    Config.set("generate.insurance.employer_coverage", "0.75")
    assert bd.to_string(ordinary.pay_monthly_premium(1.0, 100000)) == "250.00"
    assert ordinary.pay_monthly_premium(0.0, 100000) == Decimal("1000")
    assert bd.to_string(private.get_revenue()) == "2000.00"
    person = PayerPerson_double(0)
    person.attributes[person.INCOME] = 100000
    person.attributes[person.OCCUPATION_LEVEL] = 0.0
    for ratio, accepted in (("0.11", False), ("0.12", True), ("0.13", True)):
        Config.set("generate.payers.insurance_plans.income_premium_ratio", ratio)
        assert IPlanFinder.meets_affordability_requirements(ordinary, person, None, 0) is accepted


def test_payer_active_range_and_copay(payer_component_boundary: None) -> None:
    """PayerTest.planTimeBoxRanges/copayBeforeAndAfterMandate, at the plan component boundary."""
    payer = Payer("Private", 1, {"*"}, "PRIVATE")
    plan = _plan(1, payer, Decimal("100"), start=1965, end=1968)
    start, end = (
        Utilities.convert_calendar_years_to_time(1965),
        Utilities.convert_calendar_years_to_time(1968),
    )
    assert not plan.is_active(start - 1)
    assert plan.is_active(start) and plan.is_active(end)
    assert not plan.is_active(end + 1)
    from synthea.modules.health_insurance_module import HealthInsuranceModule

    mandate = HealthInsuranceModule.mandateTime
    assert plan.determine_copay("wellness", mandate) == Decimal("25.00")
    assert bd.equals(plan.determine_copay("WeLlNeSs", mandate + 1), Decimal("0.00"))
    assert plan.determine_copay("emergency", mandate + 1) == Decimal("25.00")
    with pytest.raises(RuntimeError, match="start year"):
        _plan(2, payer, Decimal(0), start=2000, end=2000)
    with pytest.raises(RuntimeError, match="Income based"):
        _plan(3, payer, Decimal("1.01"), income=True)


@pytest.mark.parametrize(
    "finder", [PlanFinderRandom(), PlanFinderPriority(), PlanFinderBestRates()]
)
def test_payer_empty_and_single_plan(finder, payer_component_boundary: None) -> None:
    """PlanFinderTest noPayersRandom/onePayerRandom/noPayersBestRate/onePayerBestRate."""
    PayerManager.load_no_insurance()
    person = PayerPerson_double(0)
    person.attributes[person.INCOME] = 100000
    assert finder.find([], person, None, 0).is_no_insurance()
    plan = _plan(1, Payer("Private", 1, {"*"}, "PRIVATE"), Decimal("100"))
    assert finder.find([plan], person, None, 0) is plan


def test_payer_best_rates_multiple_records_and_leap_boundary(
    payer_component_boundary: None,
) -> None:
    """PlanFinderTest.onePayerBestRateMultipleRecordsAndEncounters; Calendar.YEAR leap clamp."""
    person = PayerPerson_double(0)
    assert person.default_record is not None
    threshold = 1551312000000  # 2019-02-28T00:00Z, one Calendar.YEAR before leap day
    person.default_record.encounters = [
        cast(Encounter, PayerEncounter_double(t))
        for t in (threshold - 1, threshold, threshold + 1, TIME)
    ]
    finder = PlanFinderBestRates()
    assert finder.twelve_month_encounter_count(person.default_record, TIME) == 3


def test_payer_priority_and_factories(payer_component_boundary: None) -> None:
    """PlanFinderTest.planFinderPriority component, invalidPayerFinderTest and adjustment config."""
    PayerManager.load_no_insurance()
    person = PayerPerson_double(0)
    person.attributes[person.INCOME] = 100000
    payer = Payer("Private", 1, {"*"}, "PRIVATE")
    low = _plan(1, payer, Decimal(100), priority=2)
    high = _plan(2, payer, Decimal(200), priority=1)
    assert PlanFinderPriority().find([low, high], person, None, TIME) is high
    for strategy, cls in (
        ("random", PlanFinderRandom),
        ("best_rate", PlanFinderBestRates),
        ("priority", PlanFinderPriority),
    ):
        Config.set("generate.payers.selection_behavior", strategy)
        assert isinstance(PayerManager.build_plan_finder(), cls)
    Config.set("generate.payers.selection_behavior", "bestrate")
    with pytest.raises(RuntimeError, match="Not a valid"):
        PayerManager.build_plan_finder()
    for strategy, cls in (
        ("fixed", PayerAdjustmentFixed),
        ("random", PayerAdjustmentRandom),
        ("unknown", PayerAdjustmentNone),
    ):
        Config.set("generate.payers.adjustment_behavior", strategy)
        assert isinstance(PayerManager.build_payer_adjustment(), cls)


def test_payer_csv_validation_and_remaining_attributes(payer_component_boundary: None) -> None:
    """PayerManager CSV validation preserves destructive reads and all second-class columns."""

    def row() -> dict[str, str]:
        return {
            "Name": "Private",
            "Id": "7",
            "States Covered": "MA, TX",
            "Ownership": "private",
            "Address": "Somewhere",
        }

    payer = PayerManager.csv_line_to_payer(row())
    assert payer.states_covered == {"MA", "TX"}
    assert payer.get_attributes() == {"Address": "Somewhere"}
    PayerManager.payers[7] = payer
    with pytest.raises(RuntimeError, match="already exists"):
        PayerManager.csv_line_to_payer(row())
    negative = row()
    negative["Id"] = "-2"
    with pytest.raises(RuntimeError, match="non-negative"):
        PayerManager.csv_line_to_payer(negative)
    invalid = row()
    invalid["Id"], invalid["Ownership"] = "8", "unknown"
    with pytest.raises(RuntimeError, match="ownership"):
        PayerManager.csv_line_to_payer(invalid)
    assert PayerManager.comma_separated_string_to_hash_set("a , b, a,") == {"a", "b"}
    assert PayerManager.comma_separated_string_to_hash_set("") == {""}
    with pytest.raises(RuntimeError, match="Plan IDs must be non-negative"):
        PayerManager.csv_line_to_plan({"Payer Id": "7", "Plan Id": "-1"})
    # Plans belonging to an unloaded state are ignored before other columns are parsed.
    PayerManager.csv_line_to_plan({"Payer Id": "999", "Plan Id": "2"})


def test_payer_best_rate_encounter_copay_tradeoff(payer_component_boundary: None) -> None:
    """Best rate includes recent encounters across provider records and keeps ties stable."""
    PayerManager.load_no_insurance()
    person = PayerPerson_double(0)
    person.attributes[person.INCOME] = 100000
    payer = Payer("Private", 1, {"*"}, "PRIVATE")
    low_premium = _plan(1, payer, Decimal(100), copay=Decimal(100))
    low_copay = _plan(2, payer, Decimal(125), copay=Decimal(0))
    finder = PlanFinderBestRates()
    assert finder.find([low_premium, low_copay], person, None, TIME) is low_premium
    assert person.default_record is not None
    person.default_record.encounters = [
        cast(Encounter, PayerEncounter_double(TIME)) for _ in range(4)
    ]
    assert finder.find([low_premium, low_copay], person, None, TIME) is low_copay
    person.default_record.encounters.pop()
    assert finder.find([low_premium, low_copay], person, None, TIME) is low_premium


def test_payer_qols_ieee_zero_division() -> None:
    """Java double division preserves NaN and infinity when no member-years were recorded."""
    import math

    payer = Payer("Private", 1, {"*"}, "PRIVATE")
    payer.add_qols(float("nan"))
    assert math.isnan(payer.get_qols_average())
    payer.total_qols = -1.0
    assert payer.get_qols_average() == -math.inf


def test_payer_plan_diagnostic_string(payer_component_boundary: None) -> None:
    """Java's deterministic toString fields; eligibility identity deliberately is not asserted."""
    plan = _plan(7, Payer("Private", 1, {"*"}, "PRIVATE"), Decimal("100.50"))
    for rendering in (plan.to_string(), str(plan), repr(plan)):
        assert rendering.startswith("InsurancePlan [payer=Private, deductible=123.40")
        for field in (
            "defaultCopay=25.00",
            "defaultCoinsurance=0.80",
            "monthlyPremium=100.50",
            "medicareSupplement=false",
            "insuranceStatus=private",
            "activeTimeRange=[",
        ):
            assert field in rendering
