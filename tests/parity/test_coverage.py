"""Java: CoverageProbe; exact canonical comparisons, no skips or tolerances."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from decimal import Decimal
from pathlib import Path

import pytest

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.modules.health_insurance_module import HealthInsuranceModule
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Entry
from synthea.world.concepts.healthinsurance.coverage_record import _add_one_calendar_year
from synthea.world.geography.location import Location
from tests.parity.canonical.coverage import dump_coverage, dump_payer_stats

pytestmark = pytest.mark.parity
PERSONS = 240
YEARS = 30


@pytest.fixture
def coverage_boundary(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Scope all global payer/config state to this test (Java probe parity)."""
    monkeypatch.setattr(Config, "properties", Config.properties.copy())
    Config.set("generate.payers.selection_behavior", "random")
    PayerManager.clear()
    yield
    PayerManager.clear()


def person(i: int) -> Person:
    """Mirror CoverageProbe.person."""
    p = Person(1000 + i * 7919)
    birth = Utilities.convert_calendar_years_to_time(1935 + (i % 80)) + (i % 27) * 86400000
    p.attributes[Person.BIRTHDATE] = birth
    p.attributes[Person.ID] = "person-" + str(i)
    p.attributes[Person.NAME] = "Person" + str(i) + " Sample" + str(i)
    p.attributes[Person.LAST_NAME] = "Sample" + str(i)
    p.attributes[Person.NAME_MOTHER] = "Mom" + str(i)
    p.attributes[Person.NAME_FATHER] = "Dad" + str(i)
    p.attributes[Person.GENDER] = "M" if i % 2 == 0 else "F"
    p.attributes[Person.MARITAL_STATUS] = "M" if i % 3 == 0 else "S"
    p.attributes[Person.SEXUAL_ORIENTATION] = "homosexual" if i % 7 == 0 else "heterosexual"
    p.attributes[Person.INCOME] = (i % 13) * 12000 + (i % 5) * 1750
    p.attributes[Person.OCCUPATION_LEVEL] = (i % 5) * 0.2
    if i % 11 == 0:
        p.attributes["pregnant"] = True
    if i % 17 == 0:
        p.attributes[Person.BLINDNESS] = True
    if i % 19 == 0:
        p.attributes["end_stage_renal_disease"] = True
    if i % 23 == 0:
        # SSD qualifying condition (burn injury), present from birth; see the
        # probe for why the entry is inserted directly into the present map.
        assert p.record is not None
        p.record.present["403192003"] = p.record.new_entry(lambda: Entry(birth, "403192003"))
    return p


def add_years(time: int, years: int) -> int:
    """Mirror CoverageProbe.addYears: repeated Calendar.add(YEAR, 1)."""
    for _ in range(years):
        time = _add_one_calendar_year(time)
    return time


def test_coverage_selection(golden: Callable[[str], Path], coverage_boundary: None) -> None:
    """Integration parity: real PayerManager + HealthInsuranceModule + CoverageRecord."""
    PayerManager.load_payers(Location("Massachusetts", None))
    module = HealthInsuranceModule()
    timestep = Config.get_as_long("generate.timestep")
    rows = [
        json.loads(line)
        for line in (golden("CoverageProbe") / "coverage.jsonl").read_text().splitlines()
    ]
    assert len(rows) == PERSONS + 1
    for expected in rows[:PERSONS]:
        i = expected["i"]
        p = person(i)
        birth = p.attributes[Person.BIRTHDATE]
        assert isinstance(birth, int)
        end = add_years(birth, YEARS)
        last = birth
        step = 0
        t = birth
        while t < end:
            module.process(p, t)
            last = t
            if step % 26 == 13:
                record = p.coverage.get_plan_record_at_time(t)
                record.increment_primary_coverage(Decimal(f"{100 + (step % 9) * 7}.50"))
                record.increment_out_of_pocket_expenses(Decimal(f"{20 + (step % 4) * 3}.75"))
                record.increment_secondary_coverage(Decimal(f"{5 + (step % 3)}.00"))
            t += timestep
            step += 1
        actual = {
            "i": i,
            "coverage": dump_coverage(p.coverage),
            "income_remaining": p.coverage.income_remaining(last),
            "insurance_status": p.attributes.get(Person.INSURANCE_STATUS),
            "rng_count": p.get_count(),
        }
        assert actual == expected, i
    payers = [*PayerManager.get_all_payers(), PayerManager.get_no_insurance_plan().get_payer()]
    payers.sort(key=lambda payer: payer.get_name())
    assert {"payers": [dump_payer_stats(payer) for payer in payers]} == rows[PERSONS]
