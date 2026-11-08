"""Java: support.CanonicalEncounter; full T22 records/claims plus participant state."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING
from unittest.mock import patch

from synthea.javacompat.bigdecimal import to_string
from synthea.world.concepts.claim import Claim, ClaimCost, ClaimEntry
from tests.parity.canonical import dump_record
from tests.parity.canonical.coverage import dump_coverage
from tests.parity.canonical.person import render_value

if TYPE_CHECKING:
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import HealthRecord

_COST_FIELDS = (
    "cost",
    "copay_paid_by_patient",
    "deductible_paid_by_patient",
    "adjustment",
    "coinsurance_paid_by_payer",
    "paid_by_payer",
    "paid_by_secondary_payer",
    "patient_out_of_pocket",
)


def cost(item: ClaimCost) -> dict[str, object]:
    """Java: CanonicalEncounter#cost; all declared ClaimCost fields, without computing costs."""
    return {key: to_string(getattr(item, key)) for key in _COST_FIELDS}


def claim_entry(item: ClaimEntry) -> dict[str, object]:
    """Java: CanonicalEncounter#claimEntry; entry owner is an explicit UUID link."""
    return {**cost(item), "entry_uuid": str(item.entry.uuid)}


def claim(item: Claim) -> dict[str, object]:
    """Java: CanonicalEncounter#claim; full claim state, implicit owning Person link."""
    return {
        "uuid": str(item.uuid),
        "member_id": item.get_plan_record_member_id(),
        "payer_id": item.get_payer().uuid,
        "secondary_id": item.get_secondary_payer().uuid,
        "main_entry": claim_entry(item.main_entry),
        "totals": cost(item.totals),
        "items": [claim_entry(entry) for entry in item.items],
    }


def person_snapshot(
    person: Person, org: Provider, clinicians: list[Clinician]
) -> dict[str, object]:
    """Java: CanonicalEncounter#person; no new RNG draws are made while rendering."""
    assert person.record is not None
    return {
        "record": dump_record(person.record),
        "attributes": {key: render_value(value) for key, value in person.attributes.items()},
        "rng_count": str(person.get_count()),
        "symptom_total": person.symptom_total(),
        "coverage": dump_coverage(person.coverage),
        "utilization": {
            f"{year}:{key}": value for (year, key), value in org.get_utilization().items()
        },
        "clinician_encounters": [c.get_encounter_count() for c in clinicians],
    }


# T22 supplies the real setup for T25's deferred cause-of-death integration.
@contextmanager
def real_death_filter_patient(
    time: int, claim_type: type[Claim]
) -> Iterator[tuple[Person, HealthRecord]]:
    """Java: ExportHelperProbe#newPatient and keep_cause_of_death setup, using real collaborators.

    The old T25 component fixture bypasses Person's constructor and supplies no
    providers. This scenario now executes T22 and needs the same real geography,
    provider/clinician and coverage setup as its existing Java probe. Registry
    patches isolate fixture state; Claim is restored to its real class only for
    this integration, overriding T25's legacy component-only Claim double.
    """
    from synthea.helpers.config import Config
    from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
    from synthea.helpers.utilities import Utilities
    from synthea.javacompat.collections import JavaHashMap
    from synthea.world.agents.payer_manager import PayerManager
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.geography.location import Location

    with ExitStack() as stack:
        stack.enter_context(patch("synthea.world.concepts.claim.Claim", claim_type))
        stack.enter_context(patch.object(Config, "properties", dict(Config.properties)))
        Config.set("exporter.split_records", "false")
        Config.set("generate.payers.loss_of_care", "false")
        for name, replacement in (
            ("providerByUuid", JavaHashMap()),
            ("statesLoaded", set()),
            ("providerMap", Provider.providerMap),
            ("providerFinder", Provider.providerFinder),
            ("loaded", 0),
        ):
            stack.enter_context(patch.object(Provider, name, replacement))
        for name, replacement in (
            ("payers", {}),
            ("statesLoaded", set()),
            ("planFinder", getattr(PayerManager, "planFinder", None)),
            ("noInsurance", getattr(PayerManager, "noInsurance", None)),
        ):
            stack.enter_context(patch.object(PayerManager, name, replacement, create=True))
        Provider.clear()
        PayerManager.clear()
        PayerManager.load_no_insurance()
        person = Person(12345)
        person.attributes[Person.BIRTHDATE] = time - Utilities.convert_time("years", 30)
        person.attributes[Person.INCOME] = 100000
        person.coverage.set_plan_to_no_insurance(person.attributes[Person.BIRTHDATE])
        person.coverage.set_plan_to_no_insurance(time)
        state = Config.get("test_state.default", "Massachusetts") or "Massachusetts"
        location = Location(state, None)
        location.assign_point(person, location.random_city_name(person))
        Provider.load_providers(location, DefaultRandomNumberGenerator(1))
        assert person.record is not None
        yield person, person.record
