"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/payeradjustment/P
ayerAdjustmentFixed.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

from synthea.javacompat import bigdecimal as bd

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry


class PayerAdjustmentFixed:
    """Java: PayerAdjustmentFixed."""

    serialVersionUID: ClassVar[int] = -1515831606680338099

    def __init__(self, rate: float) -> None:
        """Java: PayerAdjustmentFixed#PayerAdjustmentFixed.

        Java overloads:
        (double rate)
        """
        self.rate: float = 0.0 if rate < 0.0 else 1.0 if rate > 1.0 else rate

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: PayerAdjustmentFixed#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        current_rate = self.rate
        claim_entry.adjustment = bd.set_scale(
            bd.multiply(bd.value_of(current_rate), claim_entry.cost), 2, bd.RoundingMode.HALF_EVEN
        )
        return claim_entry.adjustment
