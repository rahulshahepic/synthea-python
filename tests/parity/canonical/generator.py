"""Java: support.CanonicalGenerator; full T27 records and claims."""

from __future__ import annotations

from synthea.javacompat.bigdecimal import to_string
from synthea.world.concepts.claim import Claim, ClaimCost, ClaimEntry

_COST_FIELDS = (
    "cost",
    "copay_paid_by_patient",
    "deductible_paid_by_patient",
    "adjustment",
    "coinsurance_paid_by_payer",
    "paid_by_payer",
    "paid_by_secondary_payer",
    "patient_out_of_pocket",
)


def cost(item: ClaimCost) -> dict[str, object]:
    """Java: CanonicalGenerator#cost; all declared ClaimCost fields, without computing costs."""
    return {key: to_string(getattr(item, key)) for key in _COST_FIELDS}


def claim_entry(item: ClaimEntry) -> dict[str, object]:
    """Java: CanonicalGenerator#claimEntry; entry owner is an explicit UUID link."""
    return {**cost(item), "entry_uuid": str(item.entry.uuid)}


def claim(item: Claim) -> dict[str, object]:
    """Java: CanonicalGenerator#claim; full claim state, implicit owning Person link."""
    return {
        "uuid": str(item.uuid),
        "member_id": item.get_plan_record_member_id(),
        "payer_id": item.get_payer().uuid,
        "secondary_id": item.get_secondary_payer().uuid,
        "main_entry": claim_entry(item.main_entry),
        "totals": cost(item.totals),
        "items": [claim_entry(entry) for entry in item.items],
    }
