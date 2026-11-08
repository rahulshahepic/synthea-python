package org.synthea.parity.probes.support;

import com.google.gson.*;
import java.lang.reflect.*;
import java.util.*;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.concepts.*;

/** T22 complete records, claims, patient attributes, RNG and provider/clinician utilization. */
public final class CanonicalEncounter {
  private CanonicalEncounter() {}
  public static void registerAll() {
    CanonicalExport.registerAll();
    Canonical.register(Claim.class, CanonicalEncounter::claim);
  }
  static JsonObject cost(Claim.ClaimCost cost) {
    TreeMap<String, JsonElement> fields = new TreeMap<>();
    for (Field f : Claim.ClaimCost.class.getDeclaredFields()) {
      if (Modifier.isStatic(f.getModifiers())) continue;
      try { fields.put(f.getName().replaceAll("([a-z0-9])([A-Z])", "$1_$2").toLowerCase(Locale.ROOT), Canonical.value(f.get(cost))); }
      catch (IllegalAccessException ex) { throw new IllegalStateException(ex); }
    }
    JsonObject o = new JsonObject(); fields.forEach(o::add); return o;
  }
  static JsonObject claimEntry(Claim.ClaimEntry entry) {
    JsonObject o = cost(entry); o.addProperty("entry_uuid", entry.entry.uuid.toString()); return o;
  }
  static JsonObject claim(Claim claim) {
    JsonObject o = new JsonObject(); o.addProperty("uuid", claim.uuid.toString());
    o.addProperty("member_id", claim.getPlanRecordMemberId());
    o.addProperty("payer_id", claim.getPayer().uuid); o.addProperty("secondary_id", claim.getSecondaryPayer().uuid);
    o.add("main_entry", claimEntry(claim.mainEntry)); o.add("totals", cost(claim.totals));
    JsonArray items = new JsonArray(); for (Claim.ClaimEntry item : claim.items) items.add(claimEntry(item));
    o.add("items", items); return o;
  }
  public static JsonObject person(Person p, Provider org, List<Clinician> clinicians) {
    JsonObject o = new JsonObject(); o.add("record", Canonical.record(p.record));
    JsonObject attrs = new JsonObject();
    new TreeMap<>(p.attributes).forEach((k, v) -> attrs.addProperty(k, CanonicalPerson.renderValue(v)));
    o.add("attributes", attrs); o.addProperty("rng_count", Long.toString(p.getCount()));
    o.addProperty("symptom_total", p.symptomTotal()); o.add("coverage", CanonicalCoverage.coverage(p.coverage));
    JsonObject utilization = new JsonObject();
    TreeMap<String, Integer> sorted = new TreeMap<>();
    org.getUtilization().cellSet().forEach(c -> sorted.put(c.getRowKey() + ":" + c.getColumnKey(), c.getValue().get()));
    sorted.forEach(utilization::addProperty); o.add("utilization", utilization);
    JsonArray counts = new JsonArray(); for (Clinician c : clinicians) counts.add(c.getEncounterCount());
    o.add("clinician_encounters", counts); return o;
  }
}
