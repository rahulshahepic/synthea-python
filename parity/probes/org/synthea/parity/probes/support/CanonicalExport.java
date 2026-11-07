package org.synthea.parity.probes.support;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import org.mitre.synthea.world.agents.Provider;
import org.mitre.synthea.world.concepts.Claim;

/**
 * Canonical encoders for the export area (T25): registers a Claim encoder with
 * the T08 Canonical registry so records containing encounters can be dumped.
 * A Claim is rendered as the ordered list of its line items' entry type and
 * start, which is exactly what Exporter.filterForExport can change (it removes
 * items by entry identity); the Claim's person/payer back-references are not
 * part of the record's canonical form. Python counterpart:
 * tests/parity/canonical/export.py.
 */
public final class CanonicalExport {
  private CanonicalExport() { }

  static {
    Canonical.register(Claim.class, CanonicalExport::claim);
    // Same rendering CanonicalPerson uses for Provider references.
    Canonical.register(Provider.class,
        provider -> new JsonPrimitive("provider:" + provider.getResourceID()));
    Canonical.register(org.mitre.synthea.world.agents.Clinician.class,
        clinician -> new JsonPrimitive("clinician:" + clinician.getResourceID()));
  }

  /** Force the static registration above to run. */
  public static void registerAll() { }

  public static JsonObject claim(Claim value) {
    JsonObject out = new JsonObject();
    JsonArray items = new JsonArray();
    for (Claim.ClaimEntry item : value.items) {
      JsonObject entry = new JsonObject();
      entry.addProperty("entry_type", item.entry.type);
      entry.addProperty("entry_start", Long.toString(item.entry.start));
      items.add(entry);
    }
    out.add("items", items);
    return out;
  }
}
