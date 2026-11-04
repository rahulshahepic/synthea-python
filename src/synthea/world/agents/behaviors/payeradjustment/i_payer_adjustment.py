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
    """Java: IPayerAdjustment; pending T15."""

    def __init__(self) -> None:
        """Java: IPayerAdjustment#IPayerAdjustment.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: IPayerAdjustment#IPayerAdjustment — pending T15")

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: IPayerAdjustment#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        raise NotImplementedError("Java: IPayerAdjustment#adjustClaim — pending T15")
