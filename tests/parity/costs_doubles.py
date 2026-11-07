"""Test doubles for T14 component parity (PORTING_GUIDE §10).

Costs reads exactly two things from a Person: the ``STATE`` attribute and
the person's RNG (via ``Distribution.generate``). A real Python ``Person``
cannot yet be constructed without T16's CoverageRecord, so
``CoverageRecordDouble`` stands in for it, supplying only the plumbing the
real classes touch while Costs runs:

* Person's constructor stores the CoverageRecord; nothing else about it is
  read by Costs.
* Building a Medication builds its Claim (T14), whose constructor stores
  ``coverage.get_plan_record_at_time(entry.start)`` (or the last plan
  record). The stored record is never read by Costs or by the Claim
  constructor, so ``PlanRecordDouble`` is a bare placeholder: no plan
  behaviour is modelled here, and no probe output depends on it.

Claim *cost assignment* does depend on plan behaviour, so it is not part of
this component parity: tests/parity/test_costs.py exercises it as
integration parity, gated on T15/T16 with the real classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class PlanRecordDouble:
    """Java: org.mitre.synthea.world.concepts.healthinsurance.PlanRecord (T16).

    Placeholder stored by the Claim constructor; no behaviour.
    """


class CoverageRecordDouble:
    """Java: org.mitre.synthea.world.concepts.healthinsurance.CoverageRecord (T16)."""

    def __init__(self, person: Person) -> None:
        """Java: CoverageRecord#CoverageRecord(Person)."""
        self.person: Person = person
        self.plan_record: PlanRecordDouble = PlanRecordDouble()

    def get_plan_record_at_time(self, time: int) -> PlanRecordDouble:
        """Java: CoverageRecord#getPlanRecordAtTime, reduced to the stored record."""
        return self.plan_record

    def get_last_plan_record(self) -> PlanRecordDouble:
        """Java: CoverageRecord#getLastPlanRecord, reduced to the stored record."""
        return self.plan_record
