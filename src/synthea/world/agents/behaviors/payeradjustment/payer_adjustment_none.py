"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/payeradjustment/P
ayerAdjustmentNone.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry


class PayerAdjustmentNone:
    """Java: PayerAdjustmentNone; pending
    T15.
    """

    serialVersionUID: ClassVar[int] = 3288715364746907944

    def __init__(self) -> None:
        """Java: PayerAdjustmentNone#PayerAdjustmentNone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerAdjustmentNone#PayerAdjustmentNone — pending T15")

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: PayerAdjustmentNone#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        raise NotImplementedError("Java: PayerAdjustmentNone#adjustClaim — pending T15")
