"""Java API skeleton: SyncedEnumeratedDistro.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

    class Pair(Protocol):
        """Java boundary type: Pair; external to the mapped Python port."""


class SyncedEnumeratedDistro[T]:
    """Java: SyncedEnumeratedDistro; pending T07."""

    def __init__(self, pmf: list[Pair]) -> None:
        """Java: SyncedEnumeratedDistro#SyncedEnumeratedDistro.

        Java overloads:
        (List pmf)
        """
        raise NotImplementedError(
            "Java: SyncedEnumeratedDistro#SyncedEnumeratedDistro — pending T07"
        )

    def synced_reseeded_sample(self, person: Person) -> T:
        """Java: SyncedEnumeratedDistro#syncedReseededSample.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: SyncedEnumeratedDistro#syncedReseededSample — pending T07")
