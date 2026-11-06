"""Test doubles for T09 component parity (PORTING_GUIDE §10).

Person's production code calls the real collaborator classes unconditionally.
These doubles stand in for collaborators owned by tasks that have not merged
yet, and supply only the state Person itself reads or writes:

* ``HealthRecordDouble`` (T08): the ``death`` and ``provider`` fields Person
  writes/reads, and ``encounter_start`` returning an encounter whose ``uuid``
  is drawn from the person's own RNG, exactly as Java's ``Entry`` constructor
  does (``record.person.randUUID()``). Behaviour that is T08's own (provider
  counts, last encounter time) raises instead of being reimplemented.
* ``CoverageRecordDouble`` (T16): constructed by Person; its behaviour
  (income, plans, premiums) is T16's and is not exercised by the probe,
  except ``set_plan_to_no_insurance`` as enrolment plumbing: Java's Claim
  constructor requires a plan record at encounter times, and the one
  Person-visible effect (``insurance_status = "none"``) is mirrored.
* ``ProviderDouble`` (T13): a resource id (``uuid``), the only Provider state
  Person reads.
* ``StateDouble`` (T19): the ``name``/``exited`` fields Person reads.
* ``CodeDouble`` (T08): a code's system/code/display fields, which Person
  stores as the cause of death.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType


class EncounterDouble:
    """Java: HealthRecord.Encounter, reduced to what the probe dumps."""

    def __init__(self, person: Person, time: int, type: EncounterType) -> None:
        """Java: Entry(long, String) + Encounter(long, String).

        Two RNG draws, in Java's order: the entry's own uuid (Entry field
        initialiser), then the uuid of the Claim the Encounter constructor
        creates (Claim is T14; only its draw is modelled, not the claim).
        """
        self.uuid: UUID = person.rand_uuid()
        self.claim_uuid: UUID = person.rand_uuid()
        self.start: int = time
        # Java: Encounter's type is type.toString(), which lowercases the name.
        self.type: str = type.to_string()


class HealthRecordDouble:
    """Java: org.mitre.synthea.world.concepts.HealthRecord (T08 stand-in)."""

    def __init__(self, person: Person) -> None:
        """Java: HealthRecord#HealthRecord(Person)."""
        self.person: Person = person
        self.death: int | None = None
        self.provider: ProviderDouble | None = None
        self.encounters: list[EncounterDouble] = []

    def encounter_start(self, time: int, type: EncounterType) -> EncounterDouble:
        """Java: HealthRecord#encounterStart(long, EncounterType)."""
        encounter = EncounterDouble(self.person, time, type)
        self.encounters.append(encounter)
        return encounter

    def provider_count(self) -> int:
        """T08 behaviour; not part of T09 component parity."""
        raise AssertionError("HealthRecordDouble.provider_count is T08 behaviour")

    def last_encounter_time(self) -> int:
        """T08 behaviour; not part of T09 component parity."""
        raise AssertionError("HealthRecordDouble.last_encounter_time is T08 behaviour")


class CoverageRecordDouble:
    """Java: org.mitre.synthea.world.concepts.healthinsurance.CoverageRecord (T16)."""

    def __init__(self, person: Person) -> None:
        """Java: CoverageRecord#CoverageRecord(Person)."""
        self.person: Person = person

    def income_remaining(self, time: int) -> int:
        """T16 behaviour; not part of T09 component parity."""
        raise AssertionError("CoverageRecordDouble.income_remaining is T16 behaviour")

    def get_plan_at_time(self, time: int) -> object:
        """T16 behaviour; not part of T09 component parity."""
        raise AssertionError("CoverageRecordDouble.get_plan_at_time is T16 behaviour")

    def set_plan_to_no_insurance(self, time: int) -> None:
        """Java: CoverageRecord#setPlanToNoInsurance, reduced to its Person-visible effects.

        Java enrols a no-insurance PlanRecord covering the encounter times
        (its Claim constructor throws without one). Two effects are visible
        on the Person and are mirrored: setPlanAtTime's first-plan age check
        calls Person#ageInDecimalYears, which lazily caches
        birthdate_as_localdate in the attributes; and it sets the person's
        insurance_status attribute to the plan's status, "none". The plan
        history itself is T16 behaviour and is not modelled here.
        """
        from synthea.world.agents.person import Person

        self.person.age_in_decimal_years(time)
        self.no_insurance_from: int = time
        self.person.attributes[Person.INSURANCE_STATUS] = "none"

    def pay_monthly_premiums_at_time(self, time: int, employer_level: float, income: int) -> None:
        """T16 behaviour; not part of T09 component parity."""
        raise AssertionError("CoverageRecordDouble.pay_monthly_premiums_at_time is T16 behaviour")


class ProviderDouble:
    """Java: org.mitre.synthea.world.agents.Provider (T13 stand-in)."""

    def __init__(self, uuid: str) -> None:
        """A provider identified only by its resource id."""
        self.uuid: str = uuid

    def get_resource_id(self) -> str:
        """Java: Provider#getResourceID."""
        return self.uuid


class StateDouble:
    """Java: org.mitre.synthea.engine.State (T19 stand-in)."""

    def __init__(self, name: str, exited: int | None) -> None:
        """The two State fields Person#hadPriorState reads."""
        self.name: str = name
        self.exited: int | None = exited


class CodeDouble:
    """Java: org.mitre.synthea.world.concepts.HealthRecord.Code (T08 stand-in)."""

    def __init__(self, system: str, code: str, display: str) -> None:
        """Java: Code#Code(String, String, String)."""
        self.system: str = system
        self.code: str = code
        self.display: str = display
