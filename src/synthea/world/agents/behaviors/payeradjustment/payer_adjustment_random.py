"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/payeradjustment/P
ayerAdjustmentRandom.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

from synthea.javacompat import bigdecimal as bd

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry


class PayerAdjustmentRandom:
    """Java: PayerAdjustmentRandom;
    pending T15.
    """

    serialVersionUID: ClassVar[int] = -5292509643177122361

    def __init__(self, rate: float) -> None:
        """Java: PayerAdjustmentRandom#PayerAdjustmentRandom.

        Java overloads:
        (double rate)
        """
        self.rate: float = 0.0 if rate < 0.0 else 1.0 if rate > 1.0 else rate

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: PayerAdjustmentRandom#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        from synthea.world.concepts.claim import Claim

        if person.rand_boolean():
            current_rate = person.rand(0.0, self.rate)
            claim_entry.adjustment = bd.set_scale(
                bd.multiply(bd.value_of(current_rate), claim_entry.cost),
                2,
                bd.RoundingMode.HALF_EVEN,
            )
            return claim_entry.adjustment
        return Claim.ZERO_CENTS
