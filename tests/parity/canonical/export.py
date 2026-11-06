"""Canonical encoders for the export area (T25).

Python counterpart of parity/probes/.../support/CanonicalExport.java: registers
a Claim encoder with the T08 canonical registry so records containing
encounters can be dumped. A Claim renders as the ordered list of its line
items' entry type and start — exactly what Exporter.filter_for_export can
change (it removes items by entry identity).
"""

from __future__ import annotations

from synthea.world.agents.clinician import Clinician
from synthea.world.agents.provider import Provider
from synthea.world.concepts.claim import Claim, ClaimEntry
from tests.parity.canonical import register_encoder


def dump_claim(claim: Claim) -> dict[str, object]:
    """Java: CanonicalExport#claim(Claim)."""
    items: list[dict[str, str]] = [
        {"entry_type": item.entry.type, "entry_start": str(item.entry.start)}
        for item in claim.items
    ]
    return {"items": items}


def _dump_claim_entry(item: ClaimEntry) -> dict[str, str]:
    return {"entry_type": item.entry.type, "entry_start": str(item.entry.start)}


register_encoder(Claim, dump_claim)
# Same rendering CanonicalPerson uses for Provider references.
register_encoder(Provider, lambda p: "provider:" + p.get_resource_id())
register_encoder(Clinician, lambda c: "clinician:" + c.get_resource_id())
