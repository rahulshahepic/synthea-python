package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import org.apache.commons.validator.routines.UrlValidator;
import org.hl7.fhir.r4.model.ValueSet;
import org.mitre.synthea.helpers.RandomCodeGenerator;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.concepts.Claim;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.HealthRecord.*;
import org.synthea.parity.probes.support.Canonical;

/** Public API probes; no production classes are replaced and no golden is handwritten. */
public class HealthRecordProbe {
  static final String URI = "http://example.org/ValueSet/offline";
  static final Gson GSON = new GsonBuilder().serializeNulls().disableHtmlEscaping().create();

  static Code code(String value) { return new Code("SNOMED-CT", value, "Display " + value); }

  static void prepare(Person person, int i) {
    if (i % 2 == 0) {
      person.attributes.put(Person.HOUSEHOLD, "group");
      person.attributes.put("age", 7);
    }
  }

  static JsonObject entryScenario(int i) {
    Person person = new Person(i - 32L);
    prepare(person, i);
    HealthRecord record = new HealthRecord(person);
    long time = -2208988800000L + i * 86400000L;
    Entry entry = record.new Entry(time, "condition");
    entry.name = "state";
    entry.note = "note " + i;
    entry.mergeCodeList(Arrays.asList(code("a"), code("a"), code("b")));
    record.present.put("condition", entry);
    Observation obs = record.new Observation(time + 1, "lab", i == 0 ? -0.0 : i * 0.125);
    obs.unit = "mg";
    obs.category = "laboratory";
    obs.observations.add(record.new Observation(time + 2, "child", code("v")));
    Report report = record.new Report(time + 3, "report", Arrays.asList(obs));
    obs.report = report;
    record.present.put("lab", obs);
    record.present.put("report", report);
    Allergy allergy = record.new Allergy(time + 4, "allergy");
    allergy.name = "allergy state";
    allergy.allergyType = "allergy";
    allergy.category = "food";
    allergy.reactions = new HashMap<>();
    allergy.reactions.put(code("reaction1"), ReactionSeverity.MILD);
    allergy.reactions.put(code("reaction2"), ReactionSeverity.SEVERE);
    record.present.put("allergy", allergy);
    Procedure procedure = record.new Procedure(time + 5, "procedure");
    procedure.reasons.add(code("r"));
    procedure.mergeReasonList(Arrays.asList(code("r"), code("other"), code("other")));
    record.present.put("procedure", procedure);
    Immunization vaccine = record.new Immunization(time + 6, "vaccine");
    vaccine.series = i % 3;
    record.present.put("vaccine", vaccine);
    CarePlan plan = record.new CarePlan(time + 7, "plan");
    plan.activities.add(code("activity"));
    plan.activities.add(code("activity"));
    JsonObject goal = new JsonObject(); goal.addProperty("target", i); goal.addProperty("unit", "days");
    plan.goals.add(goal); plan.goals.add(goal.deepCopy());
    record.present.put("plan", plan);
    Device device = record.new Device(time + 8, "device");
    device.manufacturer = "Acme"; device.model = "Model " + i;
    record.present.put("device", device);
    Supply supply = record.new Supply(time + 9, "supply"); supply.quantity = i;
    record.present.put("supply", supply);
    if (i % 3 == 0) { record.conditionEndByState(time + 10, "state"); }
    if (i % 3 == 1) { record.allergyEndByState(time + 11, "allergy state"); }
    if (i % 3 == 2) { record.deviceRemove(time + 12, "device"); }
    if (i % 5 == 0) { record.death = time + 13; }
    JsonObject result = new JsonObject();
    result.addProperty("i", i);
    result.add("record", Canonical.record(record));
    result.addProperty("condition_active", record.conditionActive("condition"));
    result.addProperty("allergy_active", record.allergyActive("allergy"));
    result.add("onset", Canonical.value(record.presentOnset("condition")));
    result.addProperty("last_encounter", Long.toString(record.lastEncounterTime()));
    result.addProperty("since_wellness", Long.toString(record.timeSinceLastWellnessEncounter(time)));
    result.addProperty("summary", record.textSummary());
    result.addProperty("entry_string", entry.toString());
    result.addProperty("rng_count", person.getCount());
    return result;
  }

  static JsonObject fullScenario(int i) {
    Person person = new Person(i - 32L);
    HealthRecord record = person.record;
    long time = 1609459200000L + i * 86400000L;
    person.attributes.put(Person.BIRTHDATE, time);
    person.coverage.setPlanToNoInsurance(time);
    EncounterType kind = EncounterType.values()[i % EncounterType.values().length];
    Encounter encounter = record.encounterStart(time, kind);
    record.observation(time + 1, "a", i * 0.125);
    record.observation(time + 2, "b", "text");
    encounter.addObservation(time + 3, "a", i * 0.25, "Second a");
    record.report(time + 4, "report", i % 5);
    record.multiObservation(time + 5, "panel", i % 4);
    Entry condition = record.conditionStart(time + 6, "condition");
    condition.name = "condition state"; condition.codes.add(code("condition"));
    record.conditionStart(time + 7, "condition");
    Allergy allergy = record.allergyStart(time + 8, "allergy");
    allergy.name = "allergy state";
    record.procedure(time + 9, "procedure").codes.add(code("procedure"));
    record.immunization(time + 10, "vaccine").series = 2;
    Medication med = record.medicationStart(time + 11, "rx", i % 2 == 0);
    med.name = "rx state";
    med.codes.add(code("rx"));
    JsonObject details = JsonParser.parseString(
        "{\"dosage\":{\"amount\":2,\"frequency\":3,\"period\":1,\"unit\":\"days\"},"
        + "\"duration\":{\"quantity\":2,\"unit\":\"weeks\"}}").getAsJsonObject();
    med.prescriptionDetails = details;
    record.medicationStart(time + 12, "rx", true);
    record.medicationAdministration(time + 13, "admin");
    CarePlan plan = record.careplanStart(time + 14, "plan"); plan.name = "plan state";
    plan.activities.add(code("activity"));
    record.careplanStart(time + 15, "plan");
    record.useSupply(time + 16, code("supply"), i + 1);
    record.deviceImplant(time + 17, "device").name = "device state";
    ImagingStudy prototype = record.new ImagingStudy(person, time + 18, "prototype");
    ImagingStudy.Series series = prototype.new Series();
    ImagingStudy.Instance instance = prototype.new Instance();
    instance.title = "Image"; instance.sopClass = code("sop");
    series.instances = Arrays.asList(instance);
    series.bodySite = code("body"); series.modality = code("modality");
    record.imagingStudy(time + 19, "image", Arrays.asList(series));
    if (i % 2 == 0) {
      record.conditionEnd(time + 20, "condition");
      record.allergyEnd(time + 21, "allergy");
      record.medicationEnd(time + 22, "rx", code("stop"));
      record.careplanEnd(time + 23, "plan", code("stop"));
      record.deviceRemove(time + 24, "device");
    } else {
      record.conditionEndByState(time + 20, "condition state");
      record.allergyEndByState(time + 21, "allergy state");
      record.medicationEndByState(time + 22, "rx state", code("stop"));
      record.careplanEndByState(time + 23, "plan state", code("stop"));
      record.deviceRemoveByState(time + 24, "device state");
    }
    encounter.end(time + 25);
    encounter.end(time + 26);
    Encounter second = record.encounterStart(time + 86400000L, EncounterType.WELLNESS);
    JsonObject result = new JsonObject();
    result.addProperty("i", i);
    result.add("record", Canonical.record(record));
    result.addProperty("quantity", Long.toString(med.getQuantity()));
    result.addProperty("previous", second.previousEncounter().uuid.toString());
    result.addProperty("current_before", record.currentEncounter(time - 1).uuid.toString());
    result.addProperty("current", record.currentEncounter(time + 30).uuid.toString());
    result.addProperty("last_encounter", Long.toString(record.lastEncounterTime()));
    result.addProperty("since_wellness", Long.toString(record.timeSinceLastWellnessEncounter(time)));
    result.addProperty("providers", record.providerCount());
    result.addProperty("rng_count", person.getCount());
    return result;
  }

  static void offline(PrintWriter out) {
    ValueSet vs = new ValueSet(); vs.setUrl(URI);
    for (int i = 0; i < 17; i++) {
      vs.getCompose().addInclude().setSystem("SNOMED-CT").addConcept()
          .setCode("c" + i).setDisplay("Display " + i);
    }
    RandomCodeGenerator.codeListCache.clear(); RandomCodeGenerator.selectedCodes.clear();
    RandomCodeGenerator.loadValueSet(null, vs);
    long[] seeds = {0, 1, -1, 42, 1234, Long.MIN_VALUE, Long.MAX_VALUE, 1735689600000L};
    for (long seed : seeds) {
      JsonObject result = new JsonObject(); result.addProperty("seed", Long.toString(seed));
      result.add("two", Canonical.code(RandomCodeGenerator.getCode(URI, seed)));
      result.add("three", Canonical.code(RandomCodeGenerator.getCode(URI, seed, code("fallback"))));
      result.addProperty("selected", RandomCodeGenerator.selectedCodes.size());
      result.addProperty("contains", RandomCodeGenerator.codeInValueSet(
          new Code("SNOMED-CT", "c0", "Changed display"), URI));
      out.println(GSON.toJson(result));
    }
  }


  static void collectValueSets(JsonElement element, Set<String> urls) {
    if (element.isJsonObject()) {
      for (Map.Entry<String, JsonElement> field : element.getAsJsonObject().entrySet()) {
        JsonElement value = field.getValue();
        if (field.getKey().equals("value_set") && value.isJsonPrimitive()
            && value.getAsJsonPrimitive().isString()) {
          urls.add(value.getAsString());
        }
        collectValueSets(value, urls);
      }
    } else if (element.isJsonArray()) {
      for (JsonElement child : element.getAsJsonArray()) { collectValueSets(child, urls); }
    }
  }

  static Set<String> urlCases() throws Exception {
    Set<String> cases = new LinkedHashSet<>();
    cases.add(null); cases.add(""); cases.add("urn:oid:1.2.3");
    String[] hosts = {"example.org", "EXAMPLE.ORG", "localhost", "invalid", "example.invalid",
      "a.c", "127.0.0.1", "256.0.0.1", "01.2.3.4", "[::1]", "[2001:db8::1]",
      "[::ffff:192.0.2.1]", "[::FFFF:192.0.2.1]", "[fe80::1%25eth0]", "bücher.de", "例子.中国",
      "example.org.", "-bad.example.org", "bad-.example.org", "example..org", "example.org:",
      "example.org:0", "example.org:65535", "example.org:65536", "example.org:-1",
      "example.org:abc", "example.org:00080", "example.org:99999999999999999999"};
    for (String scheme : new String[]{"http", "https", "ftp", "HTTP", "HtTp", "file", "gopher", "1http"}) {
      for (String host : hosts) { cases.add(scheme + "://" + host + "/ValueSet"); }
    }
    String[] paths = {"", "/", "//", "///a", "/a//b", "/../", "/..", "/../../a", "/a/../b",
      "/a/../../b", "/a/./b", "/a/..", "/a%20b", "/a%2fb", "/a%ZZ", "/a b", "/a\\b",
      "/a[0]", "/<a>", "/{a}", "/café", "/é", "/a;b", "/a:b", "/a|b", "/a^b", "/a`b",
      "/a@b", "/a!b", "/a'b", "/a(b)", "/a+b", "/a$b", "/a_b", "/a~b", "/a*b"};
    for (String path : paths) {
      cases.add("http://example.org" + path);
      cases.add("https://example.org" + path + "?x=1");
      cases.add("ftp://example.org" + path + "#fragment");
    }
    String[] users = {"user", "user:pass", "user:", ":pass", "", "u%20ser:p%40ss", "u:p:a",
      "u@v", "u!$&'()*+,;=~_-:p", "u name", "üser", "user%ZZ"};
    for (String user : users) {
      for (String host : new String[]{"example.org", "127.0.0.1", "[::1]"}) {
        cases.add("http://" + user + "@" + host + "/a");
      }
    }
    String[] tails = {"", "x=1", "fhir_vs=ecl%2F%3C%3C131148009", "a/b?x=1", "white space",
      "line\nfeed", "tab\tchar", "a%20b", "%ZZ", "[x]", "{x}", "a|b", "café", "a#b"};
    for (String tail : tails) {
      cases.add("http://example.org/?" + tail);
      cases.add("http://example.org/#" + tail);
      cases.add("http://example.org/?a=1#" + tail);
    }
    try (var files = Files.walk(Path.of("src/main/resources/modules"))) {
      for (Path file : files.filter(f -> f.toString().endsWith(".json")).sorted().toList()) {
        collectValueSets(JsonParser.parseString(Files.readString(file)), cases);
      }
    }
    if (cases.size() < 150) { throw new IllegalStateException("URL coverage below 150"); }
    return cases;
  }

  static void jsonCodes(PrintWriter writer) {
    for (String definition : new String[]{
        "{\"system\":\"RxNorm\",\"code\":1437975,\"display\":\"x\"}",
        "{\"system\":123,\"code\":true,\"display\":false}",
        "{\"system\":\"s\",\"code\":-9223372036854775808,\"display\":0}"}) {
      JsonObject input = JsonParser.parseString(definition).getAsJsonObject();
      Code actual = new Code(input);
      Code equivalent = new Code(actual.system, actual.code, actual.display);
      JsonObject result = new JsonObject();
      result.add("definition", input); result.add("code", Canonical.code(actual));
      result.addProperty("hash", actual.hashCode()); result.addProperty("equals", actual.equals(equivalent));
      result.addProperty("compare", actual.compareTo(equivalent));
      writer.println(GSON.toJson(result));
    }
  }

  public static void main(String[] args) throws Exception {
    PayerManager.loadNoInsurance();
    Path path = Path.of(args[0]); Files.createDirectories(path);
    // Claim is an external entity. Retain its UUID reference; T14 may register a richer dumper.
    Canonical.register(Claim.class, claim -> {
      JsonObject ref = new JsonObject(); ref.addProperty("uuid", claim.uuid.toString()); return ref;
    });
    try (PrintWriter entries = new PrintWriter(Files.newBufferedWriter(path.resolve("entries.jsonl"), StandardCharsets.UTF_8));
         PrintWriter full = new PrintWriter(Files.newBufferedWriter(path.resolve("records.jsonl"), StandardCharsets.UTF_8));
         PrintWriter codes = new PrintWriter(Files.newBufferedWriter(path.resolve("codes.jsonl"), StandardCharsets.UTF_8));
         PrintWriter jsonCodes = new PrintWriter(Files.newBufferedWriter(path.resolve("json_codes.jsonl"), StandardCharsets.UTF_8));
         PrintWriter urls = new PrintWriter(Files.newBufferedWriter(path.resolve("urls.jsonl"), StandardCharsets.UTF_8))) {
      for (int i = 0; i < 64; i++) { entries.println(GSON.toJson(entryScenario(i))); }
      for (int i = 0; i < 60; i++) { full.println(GSON.toJson(fullScenario(i))); }
      offline(codes);
      jsonCodes(jsonCodes);
      UrlValidator validator = new UrlValidator(UrlValidator.ALLOW_2_SLASHES);
      for (String input : urlCases()) {
        JsonObject result = new JsonObject(); result.addProperty("url", input);
        result.addProperty("valid", validator.isValid(input)); urls.println(GSON.toJson(result));
      }
    }
  }
}
