"""Test doubles for T25 component parity (PORTING_GUIDE section 10).

* ``ClaimDouble`` (T14): stands in for ``Claim`` in scripted records. The real
  Claim constructor is still a T04 stub ("pending T14"), and every Encounter
  creates one, so no scripted record can be built without this double. It
  supplies only the plumbing Exporter's filter reads or the record writes:

  - the constructor's single RNG draw (``uuid = person.randUUID()``), which
    keeps the person's draw sequence aligned with Java;
  - ``items``: the line-item list. ``add_line_item`` appends a holder for the
    entry production code hands it, exactly as Java's one-line
    ``Claim#addLineItem`` appends ``new ClaimEntry(entry)``; the golden checks
    item entry type/start, which come from the real HealthRecord code, never
    from this double.
  - Cost behaviour (``assign_costs``, totals) is T14's own and is NOT modelled:
    it raises instead of being reimplemented. ClaimEntry cost state is not
    modelled either; ``ClaimEntryDouble`` only carries the entry reference
    that ``Exporter.filter_entries`` compares by identity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Entry


class ClaimEntryDouble:
    """Java: Claim.ClaimEntry, reduced to the entry reference."""

    def __init__(self, entry: Entry) -> None:
        """Java: ClaimEntry#ClaimEntry(Entry) — no RNG draw, costs unmodelled."""
        self.entry: Entry = entry


class ClaimDouble:
    """Java: Claim, reduced to constructor plumbing and the items list."""

    def __init__(self, entry: Entry, person: Person) -> None:
        """Java: Claim#Claim(Entry, Person)."""
        if type(entry).__name__ not in ("Encounter", "Medication"):
            raise RuntimeError("A Claim can only be made with entry types Encounter or Medication.")
        self.main_entry: ClaimEntryDouble = ClaimEntryDouble(entry)
        self.person: Person = person
        self.items: list[ClaimEntryDouble] = []
        self.totals: ClaimEntryDouble = ClaimEntryDouble(entry)
        self.uuid: UUID = person.rand_uuid()

    def add_line_item(self, entry: Entry) -> None:
        """Java: Claim#addLineItem(Entry)."""
        self.items.append(ClaimEntryDouble(entry))

    def assign_costs(self) -> None:
        """Java: Claim#assignCosts — T14 behaviour, not modelled by this double."""
        raise NotImplementedError("ClaimDouble does not model assign_costs (T14)")
