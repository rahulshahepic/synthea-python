package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.PrintWriter;
import java.lang.reflect.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import org.mitre.synthea.helpers.*;
import org.mitre.synthea.modules.*;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.concepts.HealthRecord.*;
import org.synthea.parity.probes.support.*;

/** T22: 50 scripted component lifetimes plus 50 real Lifecycle integrations, all >40 years. */
public class EncounterProbe {
  static final Gson GSON = new GsonBuilder().serializeNulls().create();
  static final long WEEK = 604800000L;
  static long date(int year, int month, int day) {
    return LocalDate.of(year, month, day).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
  }
  static void lifecycleFlag(String name, boolean value) throws Exception {
    Field f = LifecycleModule.class.getDeclaredField(name); f.setAccessible(true); f.set(null, value);
  }
  static void scenario(Path out, int i, boolean integration) throws Exception {
    long seed = (integration ? 190000L : 90000L) + i;
    long birth = date(1950 + i, 1, 1), end = date(1990 + i, 1, 8);
    Provider org = new Provider(); org.uuid = "encounter-org"; org.npi = "1234567893";
    DefaultRandomNumberGenerator rng = new DefaultRandomNumberGenerator(42L);
    List<Clinician> clinicians = new ArrayList<>();
    for (int j = 0; j < 3; j++) clinicians.add(new Clinician(42L, rng, 100L + j, org));
    org.clinicianMap.put(ClinicianSpecialty.GENERAL_PRACTICE, new ArrayList<>(clinicians));
    Field registry = Provider.class.getDeclaredField("providerByUuid"); registry.setAccessible(true);
    Map<String, Provider> providers = (Map<String, Provider>) registry.get(null);
    providers.clear(); providers.put(org.uuid, org);
    Person p = new Person(seed);
    p.attributes.put(Person.ID, "encounter-person-" + i); p.attributes.put(Person.BIRTHDATE, birth);
    p.attributes.put(Person.GENDER, i % 2 == 0 ? "F" : "M");
    p.attributes.put(Person.RACE, "white"); p.attributes.put(Person.ETHNICITY, "nonhispanic");
    p.attributes.put(Person.FIRST_LANGUAGE, "english"); p.attributes.put(Person.INCOME, 100000);
    p.attributes.put(Person.STATE, "Massachusetts"); p.attributes.put(Person.EDUCATION_LEVEL, 0.6);
    p.attributes.put(Person.IDENTIFIER_PASSPORT, "");
    p.attributes.put(Person.EMPLOYMENT_MODEL, new Employment(0.08));
    for (EncounterType kind : EncounterType.values()) p.setProvider(kind, org);
    p.coverage.setPlanToNoInsurance(birth); p.coverage.getLastPlanRecord().updateStopTime(end + WEEK);
    LifecycleModule lifecycle = null;
    if (integration) { lifecycle = new LifecycleModule(); LifecycleModule.birth(p, birth); }
    EncounterModule module = new EncounterModule();
    int step = 0; boolean addedChronic = false;
    for (long time = birth; time < end; time += WEEK, step++) {
      if (integration) lifecycle.process(p, time);
      if (step % 251 == 0) {
        int[] severities = {300, 301, 350, 351, 500, 501};
        p.setSymptom("Fixture", "cause", "pain", time, severities[(step / 251 + i) % 6], false);
      }
      if (!addedChronic && p.ageInYears(time) >= 30 && i % 2 == 0) {
        Medication med = p.record.new Medication(time, "chronic");
        med.codes.add(new Code("RxNorm", "chronic", "Scripted chronic medication"));
        p.chronicMedications.put("chronic", med); addedChronic = true;
      }
      module.process(p, time);
      // Re-entry while the encounter is reserved must not create another encounter or draw RNG.
      module.process(p, time);
      module.endEncounterModuleEncounters(p, time + 3600000L);
    }
    p.recordDeath(end, new Code("SNOMED-CT", "12345", "Scripted cause"));
    DeathModule.process(p, end);
    JsonObject row = CanonicalEncounter.person(p, org, clinicians);
    row.addProperty("stopped", module.process(p, end));
    Files.writeString(out.resolve((integration ? "integration_" : "component_") + i + ".json"), GSON.toJson(row));
  }
  static void doses(Path out) throws Exception {
    Field f = Immunizations.class.getDeclaredField("immunizationSchedule"); f.setAccessible(true);
    Map<String, Map> schedule = (Map<String, Map>) f.get(null);
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("doses.jsonl")))) {
      for (String name : schedule.keySet()) {
        for (int months : new int[] {0, 1, 2, 3, 4, 5, 6, 11, 12, 17, 18, 23, 24, 36, 47, 48, 59, 60, 72, 120, 216, 240, 300, 780, 1000}) {
          for (int prior = 0; prior < 3; prior++) {
            long birth = date(2000, 1, 1);
            Person p = new Person(0L); p.attributes.put(Person.BIRTHDATE, birth);
            List<Long> history = new ArrayList<>();
            for (int j = 0; j < prior; j++) history.add(date(2000, 1, 1) + j * 2592000000L);
            Map<String, List<Long>> given = new HashMap<>(); given.put(name, history);
            long time = LocalDate.of(2000, 1, 1).plusMonths(months).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
            JsonObject row = new JsonObject(); row.addProperty("name", name); row.addProperty("months", months);
            row.addProperty("prior", prior); row.addProperty("series", Immunizations.immunizationDue(name, p, time, given));
            w.println(GSON.toJson(row));
          }
        }
      }
    }
    JsonArray codes = new JsonArray(); for (Code code : Immunizations.getAllCodes()) codes.add(Canonical.code(code));
    Files.writeString(out.resolve("codes.json"), GSON.toJson(codes));
    Map<String, org.mitre.synthea.helpers.Attributes.Inventory> inventory = new TreeMap<>();
    EncounterModule.inventoryAttributes(inventory); DeathModule.inventoryAttributes(inventory); Immunizations.inventoryAttributes(inventory);
    Files.writeString(out.resolve("inventory.json"), GSON.toJson(inventory));
  }
  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]); Files.createDirectories(out); Config.set("generate.timestep", Long.toString(WEEK));
    lifecycleFlag("ENABLE_DEATH_BY_NATURAL_CAUSES", false);
    lifecycleFlag("ENABLE_DEATH_BY_LOSS_OF_CARE", false); lifecycleFlag("ENABLE_PHYSIOLOGY_GENERATORS", false);
    PayerManager.loadNoInsurance(); CanonicalEncounter.registerAll();
    for (int i = 0; i < 50; i++) { scenario(out, i, false); scenario(out, i, true); }
    doses(out);
  }
}
