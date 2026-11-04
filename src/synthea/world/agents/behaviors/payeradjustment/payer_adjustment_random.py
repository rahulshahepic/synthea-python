"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/payeradjustment/P
ayerAdjustmentRandom.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

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
        self.rate: float
        raise NotImplementedError("Java: PayerAdjustmentRandom#PayerAdjustmentRandom — pending T15")

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: PayerAdjustmentRandom#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        raise NotImplementedError("Java: PayerAdjustmentRandom#adjustClaim — pending T15")
