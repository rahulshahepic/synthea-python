"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/payeradjustment/P
ayerAdjustmentFixed.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry


class PayerAdjustmentFixed:
    """Java: PayerAdjustmentFixed; pending
    T15.
    """

    serialVersionUID: ClassVar[int] = -1515831606680338099

    def __init__(self, rate: float) -> None:
        """Java: PayerAdjustmentFixed#PayerAdjustmentFixed.

        Java overloads:
        (double rate)
        """
        self.rate: float
        raise NotImplementedError("Java: PayerAdjustmentFixed#PayerAdjustmentFixed — pending T15")

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: PayerAdjustmentFixed#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        raise NotImplementedError("Java: PayerAdjustmentFixed#adjustClaim — pending T15")
