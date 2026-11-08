package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.PrintWriter;
import java.lang.reflect.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import org.mitre.synthea.helpers.*;
import org.mitre.synthea.modules.*;
import org.mitre.synthea.modules.BloodPressureValueGenerator.SysDias;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.concepts.HealthRecord.*;
import org.mitre.synthea.world.geography.Location;
import org.synthea.parity.probes.support.CanonicalLifecycle;

/** T21 lifetime integration plus direct blood pressure and vital-sign edge cases. */
public class LifecycleProbe {
  static final Gson GSON = new GsonBuilder().serializeNulls().create();
  static final long BIRTH = -2208988800000L; // 1900-01-01 UTC
  static final long WEEK = 604800000L;
  static void flag(String name, boolean value) throws Exception {
    Field field = LifecycleModule.class.getDeclaredField(name); field.setAccessible(true); field.set(null, value);
  }
  static Object call(String name, Class<?>[] types, Object... args) throws Exception {
    Method m = LifecycleModule.class.getDeclaredMethod(name, types); m.setAccessible(true); return m.invoke(null, args);
  }
  static Person newborn(long seed, int i) {
    Person p = new Person(seed);
    p.attributes.put(Person.GENDER, i % 2 == 0 ? "F" : "M");
    p.attributes.put(Person.RACE, i % 3 == 0 ? "black" : "white");
    p.attributes.put(Person.ETHNICITY, i % 4 == 0 ? "hispanic" : "nonhispanic");
    p.attributes.put(Person.FIRST_LANGUAGE, i % 4 == 0 ? "spanish" : "english");
    p.attributes.put(Person.EDUCATION_LEVEL, (i % 10) / 10.0 + 0.05);
    p.attributes.put(Person.EMPLOYMENT_MODEL, new Employment((i % 5) * 0.04));
    p.attributes.put(Person.IDENTIFIER_PASSPORT, ""); // passport/RIF generation out of scope in T21
    LifecycleModule.birth(p, BIRTH);
    return p;
  }
  static void lifetime(Path out, int i) throws Exception {
    flag("ENABLE_DEATH_BY_NATURAL_CAUSES", i >= 50);
    Person p = newborn(1000L + i, i);
    LifecycleModule module = new LifecycleModule();
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("life_" + i + ".jsonl")))) {
      w.println(GSON.toJson(CanonicalLifecycle.person(p, BIRTH)));
      int lastAge = 0;
      long end = LocalDate.of(1991, 1, 1).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
      for (long time = BIRTH + WEEK; time < end; time += WEEK) {
        module.process(p, time);
        int age = p.ageInYears(time);
        if (age > lastAge || !p.alive(time)) {
          w.println(GSON.toJson(CanonicalLifecycle.person(p, time))); lastAge = age;
        }
        if (!p.alive(time)) break;
      }
    }
  }
  static void direct(Path out) throws Exception {
    flag("ENABLE_DEATH_BY_NATURAL_CAUSES", false);
    PayerManager.loadNoInsurance();
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("direct.jsonl")))) {
      for (int i = 0; i < 120; i++) {
        long time = 1577836800000L;
        Person p = newborn(9000L + i, i);
        p.coverage.setPlanToNoInsurance(BIRTH);
        p.coverage.getLastPlanRecord().updateStopTime(time + 10 * 31536000000L);
        p.record.encounterStart(time, EncounterType.WELLNESS);
        p.attributes.put("hypertension", i % 3 > 0);
        p.attributes.put("hypertension_severe", i % 3 == 2);
        p.attributes.put("diabetes_severity", i % 4);
        p.attributes.put("prediabetes", i % 3 == 1); p.attributes.put("diabetes", i % 3 == 2);
        p.attributes.put("ckd", i % 5);
        if (i % 2 == 0) p.attributes.put("chf", false); // presence, not value, selects hypoxemia
        if (i % 4 == 0) {
          for (String code : List.of("197499", "314076", "860975", "865098")) {
            Medication med = p.record.medicationStart(time - 1000, code, false);
            med.codes.add(new Code("RxNorm", code, "scripted"));
          }
        }
        CarePlan cp = p.record.careplanStart(time - (i % 4) * 15768000000L, "443402002");
        cp.codes.add(new Code("SNOMED-CT", "443402002", "Hypertension plan"));
        if (i % 4 == 1) cp.stop = time - 1;
        if (i % 5 != 0) p.attributes.put("htn_trial_443402002_careplan_adherent", i % 2 == 0);
        call("calculateVitalSigns", new Class<?>[] {Person.class, long.class}, p, time);
        BloodPressureValueGenerator sys = new BloodPressureValueGenerator(p, SysDias.SYSTOLIC);
        BloodPressureValueGenerator dia = new BloodPressureValueGenerator(p, SysDias.DIASTOLIC);
        JsonObject row = new JsonObject(); JsonArray values = new JsonArray();
        for (long t : new long[] {time, time, time + 43200000L, -43200001L, -1L, 0L, time}) {
          values.add(Double.toString(sys.getValue(t))); values.add(Double.toString(dia.getValue(t)));
        }
        row.add("bp", values); row.add("snapshot", CanonicalLifecycle.person(p, time)); w.println(GSON.toJson(row));
      }
    }
  }
  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]); Files.createDirectories(out);
    Config.set("generate.timestep", Long.toString(WEEK));
    flag("ENABLE_DEATH_BY_LOSS_OF_CARE", false); flag("ENABLE_PHYSIOLOGY_GENERATORS", false);
    for (int i = 0; i < 60; i++) lifetime(out, i);
    direct(out);
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("mortality.jsonl")))) {
      for (int age = -1; age <= 120; age++) {
        JsonObject row = new JsonObject(); row.addProperty("age", age);
        row.addProperty("risk", Double.toString((double)call("likelihoodOfDeath", new Class<?>[]{int.class}, age)));
        w.println(GSON.toJson(row));
      }
    }
    JsonObject scalars = new JsonObject();
    scalars.addProperty("height", Double.toString(LifecycleModule.lookupGrowthChart("height", "M", 24, 0.5)));
    scalars.addProperty("head", Double.toString(LifecycleModule.lookupGrowthChart("head", "F", 36, 0.9)));
    scalars.addProperty("bmi_percentile", Double.toString(LifecycleModule.percentileForBMI(18.37736191, "M", 26)));
    Files.writeString(out.resolve("scalars.json"), GSON.toJson(scalars));
    String[] states = {"Massachusetts", "California", "Texas"};
    String[] cities = {"Bedford", "Los Angeles", "Houston"};
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("birth_geography.jsonl")))) {
      for (int i = 0; i < 6; i++) {
        Person p = new Person(8800L + i);
        p.attributes.put(Person.GENDER, i % 2 == 0 ? "F" : "M");
        p.attributes.put(Person.RACE, "white");
        p.attributes.put(Person.ETHNICITY, i % 2 == 0 ? "hispanic" : "nonhispanic");
        p.attributes.put(Person.FIRST_LANGUAGE, i % 2 == 0 ? "spanish" : "english");
        p.attributes.put(Person.LOCATION, new Location(states[i % 3], cities[i % 3]));
        p.attributes.put(Person.CITY, cities[i % 3]);
        LifecycleModule.birth(p, BIRTH);
        w.println(GSON.toJson(CanonicalLifecycle.person(p, BIRTH)));
      }
    }
    Map<String, org.mitre.synthea.helpers.Attributes.Inventory> inventory = new TreeMap<>();
    LifecycleModule.inventoryAttributes(inventory);
    Files.writeString(out.resolve("inventory.json"), GSON.toJson(inventory));
  }
}
