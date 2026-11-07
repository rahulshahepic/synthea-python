package org.synthea.parity.probes;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.reflect.TypeToken;
import java.io.PrintWriter;
import java.lang.reflect.Field;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;
import org.apache.commons.lang3.Range;
import org.mitre.synthea.engine.Transition;
import org.mitre.synthea.engine.Transition.ComplexTransition;
import org.mitre.synthea.engine.Transition.ComplexTransitionOption;
import org.mitre.synthea.engine.Transition.ConditionalTransition;
import org.mitre.synthea.engine.Transition.ConditionalTransitionOption;
import org.mitre.synthea.engine.Transition.DirectTransition;
import org.mitre.synthea.engine.Transition.DistributedTransition;
import org.mitre.synthea.engine.Transition.DistributedTransitionOption;
import org.mitre.synthea.engine.Transition.LookupTableTransition;
import org.mitre.synthea.engine.Transition.LookupTableTransitionOption;
import org.mitre.synthea.engine.Transition.TypeOfCareTransition;
import org.mitre.synthea.engine.Transition.TypeOfCareTransitionOptions;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.SimpleCSV;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;

/**
 * T18 probe: builds every transition found in {@code resources/modules/**}
 * exactly the way State does (direct / distributed / conditional / complex /
 * lookup-table / type-of-care, in that priority order), then follows each one
 * with 25 scripted persons (seeds 0..24). Results (target state name, or
 * {@code X:<exception>} when the Java code throws) are dumped in scan order to
 * {@code transitions.jsonl}.
 *
 * <p>Lookup-table transitions are followed only for the first state (in scan
 * order) that loads a given table: the Java static cache makes later
 * instances share the table but leaves their {@code attributes} field null,
 * so following them would throw for every person. Their construction result
 * is still recorded. Lookup persons are scripted from the table's own CSV
 * rows (variant {@code row}) or with non-matching attributes (variant
 * {@code default}).
 *
 * <p>The Python mirror (tests/parity/test_transition.py) rebuilds the same
 * transitions and scripted persons from the same module JSON files and
 * compares every line exactly. Scripted-person construction is duplicated
 * there; keep the two in sync.
 */
public class TransitionProbe {

  /** 2021-01-01T00:00:00Z. */
  static final long TIME = 1609459200000L;
  /** 2019-01-01T00:00:00Z, before the telemedicine start year (2020). */
  static final long PRE_TIME = 1546300800000L;
  static final int SEEDS = 25;

  static final Gson GSON = Utilities.getGson();
  static final Type DIST_LIST = new TypeToken<List<DistributedTransitionOption>>() {}.getType();
  static final Type COND_LIST = new TypeToken<List<ConditionalTransitionOption>>() {}.getType();
  static final Type COMPLEX_LIST = new TypeToken<List<ComplexTransitionOption>>() {}.getType();
  static final Type LOOKUP_LIST = new TypeToken<List<LookupTableTransitionOption>>() {}.getType();

  static PrintWriter out;
  static Set<String> followedTables = new HashSet<>();

  public static void main(String[] args) throws Exception {
    Path outDir = Path.of(args[0]);
    Files.createDirectories(outDir);
    PayerManager.loadNoInsurance();
    List<Path> files = new ArrayList<>();
    Path modulesDir = Path.of("src/main/resources/modules");
    try (Stream<Path> walk = Files.walk(modulesDir)) {
      walk.filter(p -> p.toString().endsWith(".json")).sorted().forEach(files::add);
    }
    files.sort((a, b) -> modulesDir.relativize(a).toString()
        .compareTo(modulesDir.relativize(b).toString()));
    out = new PrintWriter(Files.newBufferedWriter(
        outDir.resolve("transitions.jsonl"), StandardCharsets.UTF_8));
    for (Path file : files) {
      String rel = modulesDir.relativize(file).toString();
      JsonObject module = JsonParser.parseString(Files.readString(file)).getAsJsonObject();
      if (!module.has("states") || !module.get("states").isJsonObject()) {
        continue;
      }
      JsonObject states = module.getAsJsonObject("states");
      for (Map.Entry<String, JsonElement> entry : states.entrySet()) {
        JsonObject state = entry.getValue().getAsJsonObject();
        runState(rel, entry.getKey(), state);
      }
    }
    out.close();
    System.out.println("TransitionProbe done");
  }

  static void emit(String module, String state, String kind, int seed, String variant,
      String result) {
    out.println(module + "|" + state + "|" + kind + "|" + seed + "|" + variant + "\t" + result);
  }

  static String followCatching(Transition transition, Person person, long time) {
    try {
      return transition.follow(person, time);
    } catch (Throwable e) {
      return "X:" + e.getClass().getSimpleName();
    }
  }

  /** A fresh person for (seed): identical script to the Python mirror. */
  static Person scriptedPerson(int seed) {
    Person person = new Person(seed);
    long birthdate = LocalDate.of(2021, 1, 1).minusYears(1 + (seed % 80))
        .atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
    person.attributes.put(Person.BIRTHDATE, birthdate);
    person.attributes.put(Person.GENDER, seed % 2 == 0 ? "M" : "F");
    person.attributes.put("race", "White");
    person.attributes.put(Person.INCOME, 10000 * (seed % 12));
    return person;
  }

  /**
   * Set the attributes a transition's definitions ask about, mirroring what
   * the Python builder sets: named-distribution attributes get
   * {@code (seed % 10) / 10.0}, and Attribute-logic attributes get the
   * condition's own value on seeds divisible by 3, so the condition can be
   * true as well as false across seeds.
   */
  static void scriptDefinitionAttributes(Person person, int seed, JsonObject state) {
    for (String key : new String[] {"distributed_transition", "complex_transition"}) {
      if (!state.has(key)) {
        continue;
      }
      for (JsonElement el : state.getAsJsonArray(key)) {
        JsonObject option = el.getAsJsonObject();
        if (option.has("distributions")) {
          for (JsonElement d : option.getAsJsonArray("distributions")) {
            scriptDistribution(person, seed, d.getAsJsonObject());
          }
        } else {
          scriptDistribution(person, seed, option);
        }
        if (option.has("condition")) {
          scriptConditionAttributes(person, seed, option.getAsJsonObject("condition"));
        }
      }
    }
    if (state.has("conditional_transition")) {
      for (JsonElement el : state.getAsJsonArray("conditional_transition")) {
        JsonObject option = el.getAsJsonObject();
        if (option.has("condition")) {
          scriptConditionAttributes(person, seed, option.getAsJsonObject("condition"));
        }
      }
    }
    if (state.has("complex_transition")) {
      for (JsonElement el : state.getAsJsonArray("complex_transition")) {
        JsonObject option = el.getAsJsonObject();
        if (option.has("condition")) {
          scriptConditionAttributes(person, seed, option.getAsJsonObject("condition"));
        }
      }
    }
  }

  static void scriptDistribution(Person person, int seed, JsonObject option) {
    if (option.has("distribution") && option.get("distribution").isJsonObject()) {
      JsonObject named = option.getAsJsonObject("distribution");
      person.attributes.put(named.get("attribute").getAsString(), (seed % 10) / 10.0);
    }
  }

  static void scriptConditionAttributes(Person person, int seed, JsonObject condition) {
    if (condition.has("condition_type")
        && condition.get("condition_type").getAsString().equals("Attribute")
        && seed % 3 == 0 && condition.has("value")) {
      JsonElement value = condition.get("value");
      Object converted = null;
      if (value.isJsonPrimitive()) {
        if (value.getAsJsonPrimitive().isNumber()) {
          converted = value.getAsDouble();
        } else if (value.getAsJsonPrimitive().isBoolean()) {
          converted = value.getAsBoolean();
        } else if (value.getAsJsonPrimitive().isString()) {
          converted = value.getAsString();
        }
      }
      if (converted != null) {
        person.attributes.put(condition.get("attribute").getAsString(), converted);
      }
    }
    for (Map.Entry<String, JsonElement> e : condition.entrySet()) {
      if (e.getValue().isJsonObject()) {
        scriptConditionAttributes(person, seed, e.getValue().getAsJsonObject());
      } else if (e.getValue().isJsonArray()) {
        for (JsonElement el : e.getValue().getAsJsonArray()) {
          if (el.isJsonObject()) {
            scriptConditionAttributes(person, seed, el.getAsJsonObject());
          }
        }
      }
    }
  }

  static void runState(String module, String stateName, JsonObject state) throws Exception {
    // Utilities.getGson()'s Logic adapters mutate the JsonObject they
    // deserialize from (they remove "condition_type"), so keep a pristine
    // copy for person scripting, taken before any construction.
    JsonObject pristineState = state.deepCopy();
    String kind;
    Transition transition = null;
    Throwable ctorError = null;
    try {
      if (state.has("direct_transition")) {
        kind = "direct";
        transition = new DirectTransition(state.get("direct_transition").getAsString());
      } else if (state.has("distributed_transition")) {
        kind = "distributed";
        List<DistributedTransitionOption> options =
            GSON.fromJson(state.get("distributed_transition"), DIST_LIST);
        transition = new DistributedTransition(options);
      } else if (state.has("conditional_transition")) {
        kind = "conditional";
        List<ConditionalTransitionOption> options =
            GSON.fromJson(state.get("conditional_transition"), COND_LIST);
        transition = new ConditionalTransition(options);
      } else if (state.has("complex_transition")) {
        kind = "complex";
        List<ComplexTransitionOption> options =
            GSON.fromJson(state.get("complex_transition"), COMPLEX_LIST);
        transition = new ComplexTransition(options);
      } else if (state.has("lookup_table_transition")) {
        kind = "lookup_table";
        List<LookupTableTransitionOption> options =
            GSON.fromJson(state.get("lookup_table_transition"), LOOKUP_LIST);
        transition = new LookupTableTransition(options);
      } else if (state.has("type_of_care_transition")) {
        kind = "type_of_care";
        TypeOfCareTransitionOptions options =
            GSON.fromJson(state.get("type_of_care_transition"), TypeOfCareTransitionOptions.class);
        transition = new TypeOfCareTransition(options);
      } else {
        return; // terminal states have no transition
      }
    } catch (Throwable e) {
      // kind was set by the key check before construction failed
      kind = kindOf(state);
      emit(module, stateName, kind, -1, "ctor", "X:" + e.getClass().getSimpleName());
      return;
    }
    emit(module, stateName, kindOf(state), -1, "ctor", "OK");
    if (transition instanceof LookupTableTransition) {
      followLookup(module, stateName, (LookupTableTransition) transition);
    } else if (transition instanceof TypeOfCareTransition) {
      for (int seed = 0; seed < SEEDS; seed++) {
        Person person = scriptedPerson(seed);
        person.coverage.setPlanToNoInsurance(0L);
        person.coverage.setPlanToNoInsurance(TIME + 1);
        emit(module, stateName, "type_of_care", seed, "t2021",
            followCatching(transition, person, TIME));
        Person prePerson = scriptedPerson(seed);
        prePerson.coverage.setPlanToNoInsurance(0L);
        prePerson.coverage.setPlanToNoInsurance(TIME + 1);
        emit(module, stateName, "type_of_care", seed, "t2019",
            followCatching(transition, prePerson, PRE_TIME));
      }
    } else {
      for (int seed = 0; seed < SEEDS; seed++) {
        Person person = scriptedPerson(seed);
        scriptDefinitionAttributes(person, seed, pristineState);
        emit(module, stateName, kindOf(state), seed, "main",
            followCatching(transition, person, TIME));
      }
    }
  }

  static String kindOf(JsonObject state) {
    if (state.has("direct_transition")) {
      return "direct";
    } else if (state.has("distributed_transition")) {
      return "distributed";
    } else if (state.has("conditional_transition")) {
      return "conditional";
    } else if (state.has("complex_transition")) {
      return "complex";
    } else if (state.has("lookup_table_transition")) {
      return "lookup_table";
    } else {
      return "type_of_care";
    }
  }

  static void followLookup(String module, String stateName, LookupTableTransition transition)
      throws Exception {
    Field nameField = LookupTableTransition.class.getDeclaredField("lookupTableName");
    nameField.setAccessible(true);
    String tableName = (String) nameField.get(transition);
    if (!followedTables.add(tableName)) {
      return; // a later instance shares the table but has null attributes
    }
    String fileName = Config.get("generate.lookup_tables") + tableName;
    String csv = Utilities.readResource(fileName, true, true);
    List<? extends Map<String, String>> rows = SimpleCSV.parse(csv);
    List<String> headers = new ArrayList<>(rows.get(0).keySet());
    Field transitionsField = LookupTableTransition.class.getDeclaredField("transitions");
    transitionsField.setAccessible(true);
    int transitionCount = ((List<?>) transitionsField.get(transition)).size();
    List<String> attributeHeaders = headers.subList(0, headers.size() - transitionCount);

    for (int seed = 0; seed < SEEDS; seed++) {
      Map<String, String> row = rows.get(seed % rows.size());
      Person person = scriptedPerson(seed);
      long followTime = TIME;
      for (String header : attributeHeaders) {
        if (header.equalsIgnoreCase("age")) {
          String cell = row.get(header);
          int low = Integer.parseInt(cell.substring(0, cell.indexOf("-")));
          long birthdate = LocalDate.of(2021, 1, 1).minusYears(low)
              .atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
          person.attributes.put(Person.BIRTHDATE, birthdate);
        } else if (header.equalsIgnoreCase("time")) {
          Range<Long> range = Utilities.parseDateRange(row.get(header));
          followTime = range.getMinimum();
        } else {
          person.attributes.put(header, row.get(header));
        }
      }
      emit(module, stateName, "lookup_table", seed, "row",
          followCatching(transition, person, followTime));

      Person defPerson = scriptedPerson(seed);
      long defTime = TIME;
      for (String header : attributeHeaders) {
        if (header.equalsIgnoreCase("age")) {
          long birthdate = LocalDate.of(2021, 1, 1).minusYears(150)
              .atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
          defPerson.attributes.put(Person.BIRTHDATE, birthdate);
        } else if (!header.equalsIgnoreCase("time")) {
          defPerson.attributes.put(header, "ZZZ_NO_MATCH");
        }
      }
      emit(module, stateName, "lookup_table", seed, "default",
          followCatching(transition, defPerson, defTime));
    }
  }
}
