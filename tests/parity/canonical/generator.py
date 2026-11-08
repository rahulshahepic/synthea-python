"""Java: support.CanonicalGenerator; full T27 records and claims."""

from __future__ import annotations

from enum import Enum

from synthea.javacompat.bigdecimal import to_string
from synthea.world.agents.person import Person
from synthea.world.concepts.claim import Claim, ClaimCost, ClaimEntry
from tests.parity.canonical.person import dump, render_value

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


def enum_attributes(person: Person) -> dict[str, str]:
    """Java: CanonicalGenerator#enumAttributes; explicit enum type and constant name."""
    return {
        key: type(value).__name__ + ":" + value.name
        for key, value in sorted(person.attributes.items())
        if isinstance(value, Enum)
    }


def _render_attribute(value: object) -> str:
    """Java: CanonicalPerson#renderValue, checking Enum before Python StrEnum strings."""
    if isinstance(value, Enum):
        return "object:" + type(value).__name__
    if isinstance(value, dict) or hasattr(value, "items"):
        items = list(value.items())  # type: ignore[attr-defined]
        by_rendered = {str(key): val for key, val in items}
        return (
            "map:{"
            + ", ".join(
                f"{key}={_render_attribute(by_rendered[key])}" for key in sorted(by_rendered)
            )
            + "}"
        )
    if isinstance(value, (list, tuple)):
        return "list:[" + ", ".join(_render_attribute(item) for item in value) + "]"
    return render_value(value)


def dump_person(person: Person) -> str:
    """Java: CanonicalPerson#dump; T27 extends attribute encoding for Python enums."""
    header, remainder = dump(person).split("\nattributes:\n", 1)
    _, tail = remainder.split("\nvitalSigns:", 1)
    attributes = "\n".join(
        f"  {key} = {_render_attribute(person.attributes[key])}"
        for key in sorted(person.attributes)
    )
    return header + "\nattributes:\n" + attributes + "\nvitalSigns:" + tail
