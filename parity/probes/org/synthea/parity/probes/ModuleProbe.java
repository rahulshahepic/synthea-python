package org.synthea.parity.probes;

import java.lang.reflect.Field;
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
import org.mitre.synthea.engine.Transition;
import org.mitre.synthea.helpers.TimeSeriesData;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.VitalSign;

/**
 * Probe for T19 (Module + control-flow States).
 *
 * Part 1 ("modules.txt"): every registered supplier, its module's name /
 * submodule flag, and for every state (sorted by name) its type and
 * transition targets, extracted reflectively so the dump does not depend
 * on transition internals beyond field names.
 *
 * Part 2 ("run.txt"): every top-level JSON module whose states are all
 * control-flow states (Initial, Terminal, Simple, Guard, Delay,
 * SetAttribute, Counter) is run for 25 scripted persons, stepping 7 days
 * at a time; the state history (name, entered, exited) and a canonical
 * attribute snapshot are dumped per person.
 *
 * Part 3 ("synthetic.txt"): temporary local modules exercising
 * CallSubmodule (with a nested submodule), Death and Delay rewinding,
 * added via Module.addModules and run the same way.
 */
public class ModuleProbe {

  static final long TIME = 1609459200000L; // 2021-01-01T00:00:00Z
  static final long WEEK = 7L * 24 * 3600 * 1000;
  static final int SEEDS = 25;
  static final int MAX_STEPS = 200;
  static final List<String> CONTROL_FLOW = List.of(
      "Initial", "Terminal", "Simple", "Guard", "Delay", "SetAttribute", "Counter");

  public static void main(String[] args) throws Exception {
    Path outDir = Path.of(args[0]);
    Files.createDirectories(outDir);
    List<String> moduleLines = new ArrayList<>();
    List<ModuleSupplier> suppliers = Module.getModuleSuppliers();
    for (ModuleSupplier supplier : suppliers) {
      Module module = supplier.get();
      moduleLines.add("S|" + supplier.path + "|core=" + supplier.core
          + "|submodule=" + supplier.submodule);
      moduleLines.add("M|" + module.name + "|submodule=" + module.submodule
          + "|remarks=" + (module.remarks == null ? "null" : module.remarks.size()));
      List<String> stateNames = new ArrayList<>(module.getStateNames());
      Collections.sort(stateNames);
      for (String stateName : stateNames) {
        State state = module.getState(stateName);
        moduleLines.add("ST|" + stateName + "|" + state.getClass().getSimpleName()
            + "|" + transitionTargets(state));
      }
    }
    Files.write(outDir.resolve("modules.txt"), moduleLines, StandardCharsets.UTF_8);

    List<String> runLines = new ArrayList<>();
    for (ModuleSupplier supplier : suppliers) {
      if (supplier.core) {
        continue;
      }
      Module probe = supplier.get();
      boolean controlFlowOnly = !probe.getStateNames().isEmpty();
      for (String stateName : probe.getStateNames()) {
        if (!CONTROL_FLOW.contains(probe.getState(stateName).getClass().getSimpleName())) {
          controlFlowOnly = false;
          break;
        }
      }
      if (!controlFlowOnly) {
        continue;
      }
      for (int seed = 0; seed < SEEDS; seed++) {
        runOne(runLines, "RUN", supplier.path, supplier, seed);
      }
    }
    Files.write(outDir.resolve("run.txt"), runLines, StandardCharsets.UTF_8);

    List<String> syntheticLines = new ArrayList<>();
    Path tmp = Files.createTempDirectory("moduleprobe");
    writeSyntheticModules(tmp);
    Module.addModules(tmp.toFile());
    for (String path : List.of("delayer", "parent")) {
      for (int seed = 0; seed < 5; seed++) {
        ModuleSupplier supplier = findSupplier(path);
        runOne(syntheticLines, "SYN", path, supplier, seed);
      }
    }
    Files.write(outDir.resolve("synthetic.txt"), syntheticLines, StandardCharsets.UTF_8);
  }

  static ModuleSupplier findSupplier(String path) {
    for (ModuleSupplier supplier : Module.getModuleSuppliers()) {
      if (supplier.path.equals(path)) {
        return supplier;
      }
    }
    throw new IllegalStateException("no supplier for " + path);
  }

  static void writeSyntheticModules(Path dir) throws Exception {
    String child = """
        {
          "name": "child",
          "states": {
            "Initial": {"type": "Initial", "direct_transition": "Mark"},
            "Mark": {"type": "SetAttribute", "attribute": "child_ran",
                     "value": "yes", "direct_transition": "Count"},
            "Count": {"type": "Counter", "attribute": "child_count",
                      "action": "increment", "direct_transition": "Done"},
            "Done": {"type": "Terminal"}
          }
        }
        """;
    String parent = """
        {
          "name": "parent",
          "states": {
            "Initial": {"type": "Initial", "direct_transition": "CallChild"},
            "CallChild": {"type": "CallSubmodule", "submodule": "sub/child",
                          "direct_transition": "Die"},
            "Die": {"type": "Death",
                    "codes": [{"system": "SNOMED-CT", "code": "44054006",
                               "display": "Diabetes"}],
                    "direct_transition": "Terminal"},
            "Terminal": {"type": "Terminal"}
          }
        }
        """;
    String delayer = """
        {
          "name": "delayer",
          "states": {
            "Initial": {"type": "Initial", "direct_transition": "Wait"},
            "Wait": {"type": "Delay", "exact": {"quantity": 10, "unit": "days"},
                     "direct_transition": "Terminal"},
            "Terminal": {"type": "Terminal"}
          }
        }
        """;
    Files.createDirectories(dir.resolve("sub"));
    Files.writeString(dir.resolve("sub/child.json"), child, StandardCharsets.UTF_8);
    Files.writeString(dir.resolve("parent.json"), parent, StandardCharsets.UTF_8);
    Files.writeString(dir.resolve("delayer.json"), delayer, StandardCharsets.UTF_8);
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
      java.util.List<Double> values = data.getValues();
      for (int i = 0; i < values.size(); i++) {
        if (i > 0) {
          sb.append(",");
        }
        sb.append(Double.toString(values.get(i)));
      }
      return sb.append("]").toString();
    } else if (value instanceof List) {
      return "List";
    }
    return value.getClass().getSimpleName();
  }

  static Object field(Object target, String name) throws Exception {
    Class<?> cls = target.getClass();
    while (cls != null) {
      try {
        Field f = cls.getDeclaredField(name);
        f.setAccessible(true);
        return f.get(target);
      } catch (NoSuchFieldException e) {
        cls = cls.getSuperclass();
      }
    }
    throw new NoSuchFieldException(name + " on " + target.getClass());
  }

  @SuppressWarnings("unchecked")
  static String transitionTargets(State state) throws Exception {
    Transition transition = state.getTransition();
    if (transition == null) {
      return "none";
    }
    String kind = transition.getClass().getSimpleName();
    List<String> targets = new ArrayList<>();
    switch (kind) {
      case "DirectTransition":
        targets.add((String) field(transition, "transition"));
        break;
      case "DistributedTransition":
      case "ConditionalTransition":
      case "LookupTableTransition":
        for (Object option : (List<Object>) field(transition, "transitions")) {
          targets.add((String) field(option, "transition"));
        }
        break;
      case "ComplexTransition":
        for (Object option : (List<Object>) field(transition, "transitions")) {
          String direct = (String) field(option, "transition");
          if (direct != null) {
            targets.add(direct);
          } else {
            for (Object dist : (List<Object>) field(option, "distributions")) {
              targets.add((String) field(dist, "transition"));
            }
          }
        }
        break;
      case "TypeOfCareTransition":
        targets.add((String) field(transition, "ambulatory"));
        targets.add((String) field(transition, "emergency"));
        targets.add((String) field(transition, "telemedicine"));
        break;
      default:
        targets.add("?" + kind);
        break;
    }
    return kind + ":" + String.join(",", targets);
  }
}
