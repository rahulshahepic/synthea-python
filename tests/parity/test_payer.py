"""T15 component parity; T16 supplies the real eligibility integration later."""

from __future__ import annotations

import json
from collections.abc import Iterator
from decimal import Decimal
from typing import cast

import pytest

from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.collections import JavaConcurrentHashMap
from synthea.modules.health_insurance_module import HealthInsuranceModule
from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_fixed import (
    PayerAdjustmentFixed,
)
from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_none import PayerAdjustmentNone
from synthea.world.agents.behaviors.payeradjustment.payer_adjustment_random import (
    PayerAdjustmentRandom,
)
from synthea.world.agents.behaviors.planeligibility.plan_eligibility_finder import (
    PlanEligibilityFinder,
)
from synthea.world.agents.behaviors.planfinder.plan_finder_best_rates import PlanFinderBestRates
from synthea.world.agents.behaviors.planfinder.plan_finder_priority import PlanFinderPriority
from synthea.world.agents.behaviors.planfinder.plan_finder_random import PlanFinderRandom
from synthea.world.agents.payer import Payer
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.claim import ClaimEntry
from synthea.world.concepts.health_record import Encounter, HealthRecord
from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
from synthea.world.geography.location import Location
from tests.dependency_gate import report_pending, run_or_pending

TIME = 1582934400000


class PayerEligibility_double:  # noqa: N801
    """Opaque registry token; only the Java's unconditional GENERIC is callable."""

    def __init__(self, name: str) -> None:
        self.name = name

    def is_person_eligible(self, person: Person, time: int) -> bool:
        assert self.name.upper() == "GENERIC", "Non-GENERIC eligibility belongs to T16"
        # Java DefaultPlanEligibility is literally `return true`; no eligibility rule is modeled.
        return True


class PayerEncounter_double:  # noqa: N801
    """An encounter's timestamp only, for the look-back count."""

    def __init__(self, start: int) -> None:
        self.start = start


class PayerPerson_double(Person):  # noqa: N801
    """Only attributes, records and real RNG plumbing; inherited affordability and RNG behavior."""

    def __init__(self, seed: int, i: int = 0) -> None:
        self.random = DefaultRandomNumberGenerator(seed)
        self.attributes = JavaConcurrentHashMap()
        self.attributes[Person.INCOME] = (i % 6) * 20000
        self.attributes[Person.OCCUPATION_LEVEL] = (i % 3) * 0.25
        self.attributes[Person.BIRTHDATE] = 0
        self.has_multiple_records = i % 2 == 0
        self.default_record = HealthRecord(self)
        self.record = self.default_record
        self.records = JavaConcurrentHashMap({"a": self.default_record}) if i % 2 == 0 else None
        for j in range(i % 9):
            encounter = cast(Encounter, PayerEncounter_double(TIME - j * 90 * 86400000))
            self.default_record.encounters.insert(0, encounter)


class PayerClaimEntry_double:  # noqa: N801
    """ClaimEntry's two mutable amount fields, without invoking unmerged T14's constructor."""

    def __init__(self, cost: Decimal) -> None:
        self.cost = cost
        self.adjustment = Decimal("7.77")


@pytest.fixture
def payer_component_boundary(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Reviewer-approved state-only T16 boundary for loading and GENERIC strategy cases."""
    monkeypatch.setattr(
        PlanEligibilityFinder, "build_plan_eligibilities", lambda state, file_name: None
    )
    monkeypatch.setattr(
        PlanEligibilityFinder,
        "get_eligibility_algorithm",
        lambda name: PayerEligibility_double(name),
    )
    monkeypatch.setattr(
        HealthInsuranceModule,
        "mandateTime",
        Utilities.convert_calendar_years_to_time(
            Config.get_as_integer("generate.insurance.mandate.year", 2006)
        ),
        raising=False,
    )
    monkeypatch.setattr(
        HealthInsuranceModule,
        "mandateOccupation",
        Config.get_as_double("generate.insurance.mandate.occupation", 0.2),
        raising=False,
    )
    # All global configuration changes are scoped to this test.
    monkeypatch.setattr(Config, "properties", Config.properties.copy())
    Config.set("generate.payers.selection_behavior", "random")
    monkeypatch.setattr(PayerManager, "payers", {})
    monkeypatch.setattr(PayerManager, "statesLoaded", set())
    monkeypatch.setattr(PayerManager, "planFinder", PayerManager.build_plan_finder(), raising=False)
    monkeypatch.setattr(PayerManager, "noInsurance", None, raising=False)
    PayerManager.clear()
    yield


def _dump_payer(payer: Payer) -> dict[str, object]:
    plans = []
    for p in payer.get_plans():
        plans.append(
            {
                "id": p.id,
                "status": p.get_insurance_status(),
                "deductible": bd.to_string(p.get_deductible()),
                "premium": bd.to_string(p.get_monthly_premium(120000)),
                "yearly": bd.to_string(p.get_yearly_cost(120000)),
                "payerCoinsurance": bd.to_string(p.get_payer_coinsurance()),
                "patientCoinsurance": bd.to_string(p.get_patient_coinsurance()),
                "max": bd.to_string(p.get_max_oop()),
                "priority": p.get_priority(),
                "supplement": p.is_medicare_supplement_plan(),
                "copayBased": p.is_copay_based(),
                "maySupplement": p.may_purchase_supplement(),
                "atZero": p.is_active(0),
                "atTime": p.is_active(TIME),
                "copay": bd.to_string(p.determine_copay("ambulatory", TIME)),
                "wellness": bd.to_string(p.determine_copay("WELLNESS", TIME)),
                "coversNull": p.covers_service(None),
            }
        )
    return {
        "id": payer.get_plan_link_id(),
        "name": payer.get_name(),
        "uuid": payer.uuid,
        "ownership": payer.get_ownership(),
        "attributes": payer.get_attributes(),
        "hash": payer.hash_code(),
        "plans": plans,
    }


def _plan(
    id: int,
    payer: Payer,
    premium: Decimal,
    income: bool = False,
    priority: int = 0,
    start: int = 0,
    end: int = (1 << 31) - 1,
    services: str = "*",
    copay: Decimal = Decimal("25.00"),
) -> InsurancePlan:
    p = InsurancePlan(
        id,
        payer,
        set(services.split(",")),
        Decimal("123.40"),
        Decimal("0.80"),
        copay,
        premium,
        Decimal("8700.00"),
        False,
        False,
        income,
        start,
        end,
        priority,
        "GENERIC",
    )
    payer.add_plan(p)
    return p


def _strategies(i: int) -> dict[str, object]:
    seed = i * 7919 - 1000000
    plans = []
    for k in range(4):
        payer = Payer("Component " + str(k), k, {"*"}, "GOVERNMENT" if k == 3 else "PRIVATE")
        plans.append(
            _plan(
                k,
                payer,
                Decimal("0.075" if k == 2 else str(100 + 50 * ((k + i) % 4))),
                k == 2,
                k % 2,
                services="emergency" if k == 1 else "*",
                copay=Decimal(str(25 + 50 * k) + ".00"),
            )
        )
    selected = []
    for finder in (PlanFinderRandom(), PlanFinderPriority(), PlanFinderBestRates()):
        person = PayerPerson_double(seed, i)
        options = [] if i % 13 == 0 else plans[:1] if i % 11 == 0 else plans
        p = finder.find(options, person, None, 0 if i % 5 == 0 else TIME)
        selected.append([p.id, str(person.get_count()), str(person.rand_long())])
    adjusted = []
    rates = [-0.5, 0.0, 0.05, 0.5, 1.0, 1.5]
    for adjustment in (
        PayerAdjustmentNone(),
        PayerAdjustmentFixed(rates[i % 6]),
        PayerAdjustmentRandom(rates[i % 6]),
    ):
        person = PayerPerson_double(seed, i)
        entry = cast(ClaimEntry, PayerClaimEntry_double(Decimal(str(i) + ".125")))
        amount = adjustment.adjust_claim(entry, person)
        adjusted.append(
            [
                bd.to_string(amount),
                bd.to_string(entry.adjustment),
                str(person.get_count()),
                str(person.rand_long()),
            ]
        )
    money = plans[i % 4]
    income = 100001 + i
    costs = [
        bd.to_string(money.get_monthly_premium(income)),
        bd.to_string(money.get_yearly_cost(income)),
        bd.to_string(money.pay_monthly_premium(i % 2, income)),
        bd.to_string(money.get_payer().get_revenue()),
    ]
    for t in (
        HealthInsuranceModule.mandateTime - 1,
        HealthInsuranceModule.mandateTime,
        HealthInsuranceModule.mandateTime + 1,
    ):
        costs.append(bd.to_string(money.determine_copay("wellness", t)))
    return {"i": i, "selected": selected, "adjusted": adjusted, "money": costs}


def test_payer_component_three_state_loading(golden, payer_component_boundary: None) -> None:
    """Component: actual CSVs in source order; opaque eligibility tokens are not evaluated."""
    rows = [
        json.loads(line)
        for line in (golden("PayerProbe") / "states.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 3
    for row in rows:
        PayerManager.clear()
        PayerManager.load_payers(Location(row["state"], None))
        assert {
            "state": row["state"],
            "payers": [_dump_payer(p) for p in PayerManager.get_all_payers()],
            "none": _dump_payer(PayerManager.get_no_insurance_plan().get_payer()),
        } == row


def test_payer_component_strategies(golden, payer_component_boundary: None) -> None:
    """Component: 600 calls for each of 3 finders and 3 adjustments, with real GENERIC plans."""
    PayerManager.load_no_insurance()
    rows = [
        json.loads(line)
        for line in (golden("PayerProbe") / "strategies.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 600
    for row in rows:
        assert _strategies(row["i"]) == row


def test_payer_real_eligibility_integration(golden) -> None:
    """T16 must run all 120 scenarios with actual eligibility rules and no doubles."""
    rows = [
        json.loads(line)
        for line in (golden("PayerProbe") / "integration.jsonl").read_text().splitlines()
    ]
    results: list[object] = []
    locations = {state: Location(state, None) for state in {row["state"] for row in rows}}
    assert len(rows) == 120
    for row in rows:

        def scenario(row=row) -> None:
            PayerManager.clear()
            PayerManager.load_payers(locations[row["state"]])
            person = Person(row["i"] + 20)
            person.attributes[Person.INCOME] = (row["i"] % 6) * 20000
            person.attributes[Person.OCCUPATION_LEVEL] = (row["i"] % 3) * 0.25
            person.attributes[Person.BIRTHDATE] = 0
            person.attributes[Person.GENDER] = "M"
            person.coverage.set_plan_to_no_insurance(0)
            for year in range(1971, 2021):
                t = Utilities.convert_calendar_years_to_time(year)
                person.coverage.new_enrollment_period(t)
                person.coverage.set_plan_to_no_insurance(t)
            plans = PayerManager.get_active_plans(PayerManager.get_all_payers(), TIME)
            assert [p.accepts(person, TIME) for p in plans] == row["accepts"]

        result = run_or_pending(scenario, ("T16",))
        results.append(result)
    report_pending("payer eligibility", results)
