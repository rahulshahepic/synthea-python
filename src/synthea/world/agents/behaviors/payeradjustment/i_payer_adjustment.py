"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/payeradjustment/I
PayerAdjustment.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry


class IPayerAdjustment(Protocol):
    """Java: IPayerAdjustment."""

    def __init__(self) -> None:
        """Java: IPayerAdjustment#IPayerAdjustment.

        Java overloads:
        ()
        """
        pass

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: IPayerAdjustment#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        ...
