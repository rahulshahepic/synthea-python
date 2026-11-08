package org.synthea.parity.probes;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import org.mitre.synthea.engine.Module;
import org.mitre.synthea.engine.Module.ModuleSupplier;
import org.mitre.synthea.engine.State;
import org.mitre.synthea.helpers.TimeSeriesData;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.VitalSign;

/**
 * Probe for T20 (clinical States).
 *
 * Every top-level JSON module is run for 20 scripted persons, stepping
 * 7 days at a time up to 200 steps; per person the outcome line, the
 * state history, a canonical attribute snapshot, and a canonical
 * health-record summary (present entries with codes and start/stop,
 * encounter count, symptom values) are dumped. Modules that need the
 * EncounterModule or a core module record an ERROR line with the
 * exception class instead.
 */
public class StateProbe {

  static final long TIME = 1609459200000L; // 2021-01-01T00:00:00Z
  static final long WEEK = 7L * 24 * 3600 * 1000;
  static final int SEEDS = 20;
  static final int MAX_STEPS = 200;

  public static void main(String[] args) throws Exception {
    Path outDir = Path.of(args[0]);
    Files.createDirectories(outDir);
    List<String> runLines = new ArrayList<>();
    for (ModuleSupplier supplier : Module.getModuleSuppliers()) {
      if (supplier.core) {
        continue;
      }
      Module probe = supplier.get();
      if (probe.getStateNames().isEmpty()) {
        continue;
      }
      for (int seed = 0; seed < SEEDS; seed++) {
        runOne(runLines, "RUN", supplier.path, supplier, seed);
      }
    }
    Files.write(outDir.resolve("run.txt"), runLines, StandardCharsets.UTF_8);
  }

  static Person scriptedPerson(int seed) {
    Person person = new Person(seed);
    long birthdate = LocalDate.of(2021, 1, 1).minusYears(1 + (seed % 80))
        .atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
    person.attributes.put(Person.BIRTHDATE, birthdate);
    person.attributes.put(Person.GENDER, seed % 2 == 0 ? "M" : "F");
    person.attributes.put("race", "White");
    person.attributes.put(Person.INCOME, 10000 * (seed % 12));
    person.setVitalSign(VitalSign.BMI, 18.0 + (seed % 25));
    return person;
  }

  static void runOne(List<String> lines, String tag, String path,
                     ModuleSupplier supplier, int seed) {
    Person person = scriptedPerson(seed);
    Module module = supplier.get();
    long time = TIME;
    boolean completed = false;
    int steps = 0;
    try {
      for (steps = 0; steps < MAX_STEPS; steps++) {
        completed = module.process(person, time);
        if (completed) {
          steps++;
          break;
        }
        time += WEEK;
      }
    } catch (RuntimeException e) {
      lines.add(tag + "|" + path + "|" + seed + "|ERROR|"
          + e.getClass().getSimpleName());
      return;
    }
    lines.add(tag + "|" + path + "|" + seed + "|completed=" + completed
        + "|steps=" + steps);
    if (person.history != null) {
      for (int i = 0; i < person.history.size(); i++) {
        State state = person.history.get(i);
        lines.add("H|" + i + "|" + state.name + "|" + state.entered + "|" + state.exited);
      }
    }
    Map<String, Object> sorted = new TreeMap<>();
    for (Map.Entry<String, Object> entry : person.attributes.entrySet()) {
      sorted.put(entry.getKey(), entry.getValue());
    }
    for (Map.Entry<String, Object> entry : sorted.entrySet()) {
      lines.add("A|" + entry.getKey() + "|" + canonicalValue(entry.getValue()));
    }
    lines.add("E|" + person.record.encounters.size());
    List<String> presentKeys = new ArrayList<>(person.record.present.keySet());
    Collections.sort(presentKeys);
    for (String key : presentKeys) {
      HealthRecord.Entry entry = person.record.present.get(key);
      StringBuilder codes = new StringBuilder();
      for (HealthRecord.Code code : entry.codes) {
        if (codes.length() > 0) {
          codes.append(";");
        }
        codes.append(code.system).append(":").append(code.code).append(":")
            .append(code.display);
      }
      lines.add("R|" + key + "|" + entry.type + "|" + entry.name + "|"
          + entry.start + "|" + entry.stop + "|" + codes);
    }
    List<String> symptomNames = new ArrayList<>(person.getSymptoms());
    Collections.sort(symptomNames);
    for (String symptom : symptomNames) {
      lines.add("Y|" + symptom + "|" + person.getSymptom(symptom));
    }
  }

  static String canonicalValue(Object value) {
    if (value == null) {
      return "null";
    } else if (value instanceof Double d) {
      return Double.toString(d);
    } else if (value instanceof Boolean || value instanceof Number
        || value instanceof String) {
      return value.toString();
    } else if (value instanceof TimeSeriesData data) {
      StringBuilder sb = new StringBuilder("TS[");
      boolean first = true;
      for (double v : data.getValues()) {
        if (!first) {
          sb.append(",");
        }
        sb.append(Double.toString(v));
        first = false;
      }
      return sb.append("]").toString();
    } else if (value instanceof List) {
      return "List";
    } else if (value instanceof LocalDate) {
      return "LocalDate";
    }
    return value.getClass().getSimpleName();
  }
}
