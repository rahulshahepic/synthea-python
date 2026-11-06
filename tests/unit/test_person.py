"""Unit tests for Person control flow that routes through unmerged tasks.

The parity probe cannot exercise these paths yet: ``providerCount``'s
single-record delegation is T08 behaviour, ``stillHasIncome`` /
``checkToPayMonthlyPremium`` run through CoverageRecord (T16), and
``canAffordPlan`` through InsurancePlan (T15). Per PORTING_GUIDE §10, unit
tests may isolate those unported callees with ``unittest.mock`` to test
Person's own control flow; these tests never feed a parity comparison.
"""

from __future__ import annotations

from decimal import Decimal
from unittest import mock

import pytest

import synthea.world.agents.person as person_module
from synthea.helpers.config import Config
from synthea.world.agents.person import Person
from tests.parity.person_doubles import CoverageRecordDouble, HealthRecordDouble


@pytest.fixture
def person(monkeypatch: pytest.MonkeyPatch) -> Person:
    """A Person built on the component doubles (T08/T16 stand-ins)."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    return Person(42)


def test_provider_count_delegates_to_record(person: Person) -> None:
    """Java: Person#providerCount delegates when not hasMultipleRecords."""
    record = person.record
    assert isinstance(record, HealthRecordDouble)
    with mock.patch.object(HealthRecordDouble, "provider_count", return_value=3) as provider_count:
        assert person.provider_count() == 3
    provider_count.assert_called_once_with()


def test_still_has_income_switches_to_no_insurance(person: Person) -> None:
    """Java: Person#stillHasIncome flips the plan when income runs out."""
    coverage = mock.Mock()
    coverage.income_remaining.return_value = 0
    coverage.get_plan_at_time.return_value.is_no_insurance.return_value = False
    person.coverage = coverage  # type: ignore[assignment]
    assert person.still_has_income(1000) is False
    coverage.set_plan_to_no_insurance.assert_called_once_with(1000)


def test_still_has_income_keeps_plan_when_income_remains(person: Person) -> None:
    """Java: Person#stillHasIncome leaves the plan alone while income > 0."""
    coverage = mock.Mock()
    coverage.income_remaining.return_value = 5
    person.coverage = coverage  # type: ignore[assignment]
    assert person.still_has_income(1000) is True
    coverage.set_plan_to_no_insurance.assert_not_called()


def test_check_to_pay_monthly_premium_pays_in_new_month(person: Person) -> None:
    """Java: Person#checkToPayMonthlyPremium pays once per new month."""
    coverage = mock.Mock()
    coverage.income_remaining.return_value = 10
    person.coverage = coverage  # type: ignore[assignment]
    person.attributes[Person.INCOME] = 50000
    person.attributes[Person.OCCUPATION_LEVEL] = 0.5
    january = 1704067200000  # 2024-01-01T00:00Z, month 1
    person.check_to_pay_monthly_premium(january)
    coverage.pay_monthly_premiums_at_time.assert_called_once_with(january, 0.5, 50000)
    assert person.attributes[Person.LAST_MONTH_PAID] == 1
    # Same month again: no second payment.
    person.check_to_pay_monthly_premium(january + 86400000)
    coverage.pay_monthly_premiums_at_time.assert_called_once()


def test_can_afford_plan(person: Person) -> None:
    """Java: Person#canAffordPlan compares income * ratio to the yearly cost."""
    ratio = Config.get_as_double("generate.payers.insurance_plans.income_premium_ratio")
    person.attributes[Person.INCOME] = 100000
    plan = mock.Mock()
    plan.get_yearly_cost.return_value = Decimal("1")
    assert person.can_afford_plan(plan) is True
    plan.get_yearly_cost.return_value = Decimal(str(100000 * ratio + 1))
    assert person.can_afford_plan(plan) is False
    plan.get_yearly_cost.assert_called_with(100000)
