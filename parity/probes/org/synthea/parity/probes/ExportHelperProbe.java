package org.synthea.parity.probes;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.hl7.fhir.dstu3.model.Condition;
import org.mitre.synthea.engine.Components;
import org.mitre.synthea.export.Exporter;
import org.mitre.synthea.export.ExportHelper;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;
import org.mitre.synthea.helpers.TimeSeriesData;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.modules.DeathModule;
import org.mitre.synthea.world.agents.Clinician;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.HealthRecord.Code;
import org.mitre.synthea.world.concepts.HealthRecord.Encounter;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;
import org.mitre.synthea.world.concepts.HealthRecord.Entry;
import org.mitre.synthea.world.concepts.HealthRecord.Medication;
import org.mitre.synthea.world.concepts.HealthRecord.Observation;
import org.synthea.parity.probes.support.Canonical;
import org.synthea.parity.probes.support.CanonicalExport;

/**
 * Probe for T25: every ExportHelper method, plus Exporter record filtering
 * (years_of_history), filterAfterDeath, entryWithinTimeRange, export(),
 * filename and getOutputFolder for scripted records. All timestamps are fixed
 * constants so the output is deterministic.
 */
public class ExportHelperProbe {
  static final Gson GSON = new GsonBuilder().serializeNulls().disableHtmlEscaping().create();
  static final long TIME = 1700000000000L;
  static final int YEARS = 5;
  static final Code DUMMY_CODE = new Code("", "", "");
  static PrintWriter out;

  static long years(long n) {
    return Utilities.convertTime("years", n);
  }

  static void line(JsonObject o) {
    out.println(GSON.toJson(o));
  }

  static JsonObject base(String kind) {
    JsonObject o = new JsonObject();
    o.addProperty("case", kind);
    return o;
  }

  public static void main(String[] args) throws Exception {
    CanonicalExport.registerAll();
    Path outDir = Paths.get(args[0]);
    Files.createDirectories(outDir);
    Config.set("exporter.split_records", "false");
    out = new PrintWriter(Files.newBufferedWriter(
        outDir.resolve("export_helper.jsonl"), StandardCharsets.UTF_8));
    dates();
    systems();
    fhirUrls();
    uuids();
    observationValues();
    sampledData();
    attachments();
    filterScenarios();
    entryWithinTimeRange();
    filterAfterDeath();
    exportScenarios();
    filenames(outDir);
    out.close();
  }

  static void dates() {
    long[] stamps = {
      0L, -1L, 1L, 86399999L, 1700000000000L, -2208988800000L, 1709164800000L,
      1735689599000L, 1735689600000L, 253402300799000L, -62135596800000L,
      951782400000L, 4102444800000L
    };
    for (long t : stamps) {
      JsonObject o = base("dates");
      o.addProperty("time", Long.toString(t));
      o.addProperty("date", ExportHelper.dateFromTimestamp(t));
      o.addProperty("iso", ExportHelper.iso8601Timestamp(t));
      line(o);
    }
    List<Long> fridays = new ArrayList<>();
    for (long k = -10; k <= 10; k++) {
      fridays.add(TIME + k * 86400000L);
    }
    fridays.addAll(Arrays.asList(
        1703808000000L, 1704067200000L, 1709164800000L, 1709251200000L,
        -86400000L, -432000000L, 0L));
    for (long t : fridays) {
      JsonObject o = base("next_friday");
      o.addProperty("time", Long.toString(t));
      o.addProperty("result", Long.toString(ExportHelper.nextFriday(t)));
      line(o);
    }
  }

  static void systems() {
    String[] systems = {
      "SNOMED-CT", "snomed-ct", "Loinc", "LOINC", "RxNorm", "rxnorm", "CVX",
      "DICOM-DCM", "dicom-dcm", "CDT", "ICD9", "ICD10", "ICD10-CM", "icd10-cm",
      "CPT", "SNOMED", "unknown-system", ""
    };
    for (String s : systems) {
      JsonObject o = base("system_uri");
      o.addProperty("in", s);
      o.addProperty("out", ExportHelper.getSystemURI(s));
      line(o);
    }
    String[] uris = {
      "http://snomed.info/sct", "http://loinc.org",
      "http://www.nlm.nih.gov/research/umls/rxnorm", "http://hl7.org/fhir/sid/cvx",
      "http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_29.html",
      "http://www.ada.org/cdt", "http://hl7.org/fhir/sid/icd-9-cm",
      "http://hl7.org/fhir/sid/icd-10", "http://hl7.org/fhir/sid/icd-10-cm",
      "http://www.ama-assn.org/go/cpt", "http://example.org", ""
    };
    for (String u : uris) {
      JsonObject o = base("system_from_uri");
      o.addProperty("in", u);
      o.addProperty("out", ExportHelper.getSystemFromURI(u));
      line(o);
    }
    JsonObject o = base("unduplicated");
    JsonArray arr = new JsonArray();
    for (String s : ExportHelper.UNDUPLICATED_FHIR_RESOURCES) {
      arr.add(s);
    }
    o.add("values", arr);
    line(o);
  }

  static void fhirUrls() {
    String[][] cases = {{"Patient", "123"}, {"Observation", "abc-def"}, {"Practitioner", ""}};
    for (String[] c : cases) {
      JsonObject o = base("fhir_url");
      o.addProperty("resource", c[0]);
      o.addProperty("id", c[1]);
      o.addProperty("out", ExportHelper.buildFhirSearchUrl(c[0], c[1]));
      line(o);
    }
    Clinician clinician = new Clinician(7L, new DefaultRandomNumberGenerator(7L), 123456L, null);
    JsonObject o = base("fhir_npi_url");
    o.addProperty("npi", clinician.npi);
    o.addProperty("out", ExportHelper.buildFhirNpiSearchUrl(clinician));
    line(o);
    JsonObject n = base("fhir_npi_url_null");
    n.addProperty("out", ExportHelper.buildFhirNpiSearchUrl(null));
    line(n);
  }

  static void uuids() {
    long[] seeds = {0L, 1L, -1L, 12345L, Long.MAX_VALUE, Long.MIN_VALUE};
    long[] stamps = {0L, 1700000000000L, -1L};
    String[] keys = {"", "a", "Condition", "69453-9", "café", "日本語",
      "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"};
    for (long seed : seeds) {
      for (long ts : stamps) {
        for (String key : keys) {
          JsonObject o = base("uuid");
          o.addProperty("seed", Long.toString(seed));
          o.addProperty("time", Long.toString(ts));
          o.addProperty("key", key);
          o.addProperty("out", ExportHelper.buildUUID(seed, ts, key));
          line(o);
        }
      }
    }
    Person p = newPatient();
    JsonObject o = base("uuid_person");
    o.addProperty("seed", Long.toString(p.getSeed()));
    o.addProperty("time", Long.toString(TIME));
    o.addProperty("key", "Condition");
    o.addProperty("out", ExportHelper.buildUUID(p, TIME, "Condition"));
    line(o);
  }

  static Person newPatient() {
    Person p = new Person(12345L);
    p.attributes.put(Person.BIRTHDATE, TIME - years(30));
    p.attributes.put(Person.INCOME, 100000);
    PayerManager.clear();
    PayerManager.loadNoInsurance();
    p.coverage.setPlanToNoInsurance((long) p.attributes.get(Person.BIRTHDATE));
    p.coverage.setPlanToNoInsurance(TIME);
    return p;
  }

  static Observation obs(HealthRecord record, Object value) {
    Observation o = record.new Observation(TIME, "test", value);
    o.codes.add(new Code("SNOMED-CT", "1234", "Test Code"));
    return o;
  }

  static void obsCase(HealthRecord record, String name, Object value) {
    Observation o = obs(record, value);
    JsonObject line = base("obs_value");
    line.addProperty("name", name);
    try {
      line.addProperty("result", ExportHelper.getObservationValue(o));
    } catch (ClassCastException e) {
      line.addProperty("result", "ERR:ClassCastException");
    }
    line.addProperty("type", ExportHelper.getObservationType(o));
    line(line);
  }

  static void observationValues() {
    Person p = newPatient();
    HealthRecord record = p.record;
    obsCase(record, "code", new Code("SNOMED-CT", "705129", "Fake Code Display"));
    obsCase(record, "string", "some text");
    double[] doubles = {
      0.0, -0.0, 1.05, 1.15, 2.675, 0.125, 123.456, -7.25, 1e20,
      Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY,
      0.05, 0.25, 99.95
    };
    for (double d : doubles) {
      obsCase(record, "double_" + Double.toString(d), d);
    }
    obsCase(record, "boolean_true", Boolean.TRUE);
    obsCase(record, "boolean_false", Boolean.FALSE);
    obsCase(record, "integer", 42);
    obsCase(record, "long", 123456789012345L);
    obsCase(record, "null", null);
    obsCase(record, "fhir_condition", new Condition());

    // by-code lookups over a nested panel
    Observation panel = record.new Observation(TIME, "panel", "panel value");
    panel.codes.add(new Code("SNOMED-CT", "panel-code", "Panel"));
    Observation childA = record.new Observation(TIME, "child", 42.5);
    childA.codes.add(new Code("SNOMED-CT", "child-a", "Child A"));
    Observation grand = record.new Observation(TIME, "grandchild", "deep");
    grand.codes.add(new Code("SNOMED-CT", "grand", "Grandchild"));
    childA.observations.add(grand);
    Observation childB = record.new Observation(TIME, "child", "b text");
    childB.codes.add(new Code("SNOMED-CT", "child-b", "Child B"));
    Observation childA2 = record.new Observation(TIME, "child", "second a");
    childA2.codes.add(new Code("SNOMED-CT", "child-a", "Child A2"));
    panel.observations.add(childA);
    panel.observations.add(childB);
    panel.observations.add(childA2);
    String[] queries = {"panel-code", "child-a", "child-b", "grand", "missing"};
    for (String q : queries) {
      JsonObject line = base("obs_by_code");
      line.addProperty("code", q);
      line.addProperty("result", ExportHelper.getObservationValue(panel, q));
      line(line);
    }
  }

  static Components.SampledData sampled(String pattern, List<List<Double>> seriesValues) {
    Components.SampledData sd = new Components.SampledData();
    sd.series = new ArrayList<>();
    for (List<Double> values : seriesValues) {
      sd.series.add(new TimeSeriesData(values, 1.0));
    }
    sd.decimalFormat = pattern;
    return sd;
  }

  static void sampledCase(String name, Components.SampledData sd) {
    JsonObject o = base("sampled");
    o.addProperty("name", name);
    o.addProperty("result", ExportHelper.sampledDataToValueString(sd));
    line(o);
  }

  static void sampledData() {
    Person p = newPatient();
    HealthRecord record = p.record;
    sampledCase("default_two_series", sampled(null, Arrays.asList(
        Arrays.asList(1.2345, 1234567.891, 0.0005),
        Arrays.asList(2.675, 0.125, 999.9999))));
    sampledCase("pattern_0.00", sampled("0.00", Arrays.asList(
        Arrays.asList(2.675, 1.005, 0.125))));
    sampledCase("pattern_0.0", sampled("0.0", Arrays.asList(
        Arrays.asList(2.65, 2.75, -0.05))));
    sampledCase("pattern_hash", sampled("#.##", Arrays.asList(
        Arrays.asList(0.5, 0.05, 123.456))));
    sampledCase("pattern_grouped", sampled("#,##0.00", Arrays.asList(
        Arrays.asList(1234567.891, 42.0))));
    sampledCase("pattern_0", sampled("0", Arrays.asList(
        Arrays.asList(2.5, 3.5, 4.5))));
    sampledCase("default_special", sampled(null, Arrays.asList(
        Arrays.asList(Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY))));
    // one observation-wrapped case
    obsCase(record, "sampled_wrapped",
        sampled("0.00", Arrays.asList(Arrays.asList(1.005, 2.675))));
  }

  static void attachments() {
    Person p = newPatient();
    HealthRecord record = p.record;
    Components.Attachment data = new Components.Attachment();
    data.data = "data payload";
    obsCase(record, "attachment_data", data);
    Components.Attachment url = new Components.Attachment();
    url.url = "http://example.org/file";
    obsCase(record, "attachment_url", url);
    Components.Attachment both = new Components.Attachment();
    both.data = "d";
    both.url = "u";
    obsCase(record, "attachment_both", both);
    obsCase(record, "attachment_none", new Components.Attachment());
  }

  static void filterCase(String name, Person p) {
    Person filtered = Exporter.filterForExport(p, YEARS, TIME);
    JsonObject o = base("filter");
    o.addProperty("name", name);
    o.add("record", Canonical.record(filtered.record));
    line(o);
  }

  static void filterScenarios() {
    { // testExportFilterSimpleCutoff
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(8), EncounterType.WELLNESS);
      record.observation(TIME - years(8), "height", 64);
      record.encounterStart(TIME - years(4), EncounterType.WELLNESS);
      record.observation(TIME - years(4), "weight", 128);
      filterCase("simple_cutoff", p);
    }
    { // testExportFilterShouldKeepOldActiveMedication
      Person p = newPatient();
      HealthRecord record = p.record;
      Code code = new Code("SNOMED-CT", "705129", "Fake Code");
      record.encounterStart(TIME - years(10), EncounterType.AMBULATORY);
      record.medicationStart(TIME - years(10), "fakeitol", true);
      record.encounterStart(TIME - years(8), EncounterType.AMBULATORY);
      Medication med = record.medicationStart(TIME - years(8), "placebitol", true);
      med.codes.add(code);
      record.medicationEnd(TIME - years(6), "placebitol", DUMMY_CODE);
      filterCase("keep_old_active_medication", p);
    }
    { // testExportFilterShouldKeepMedicationThatEndedDuringTarget
      Person p = newPatient();
      HealthRecord record = p.record;
      Code code = new Code("SNOMED-CT", "705129", "Fake Code");
      record.encounterStart(TIME - years(10), EncounterType.AMBULATORY);
      Medication med = record.medicationStart(TIME - years(10), "dimoxinil", false);
      med.codes.add(code);
      record.medicationEnd(TIME - years(9), "dimoxinil", DUMMY_CODE);
      record.encounterStart(TIME - years(8), EncounterType.AMBULATORY);
      med = record.medicationStart(TIME - years(8), "placebitol", true);
      med.codes.add(code);
      record.medicationEnd(TIME - years(4), "placebitol", DUMMY_CODE);
      filterCase("medication_ended_during_target", p);
    }
    { // testExportFilterShouldKeepOldActiveCareplan
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.careplanStart(TIME - years(10), "stop_smoking");
      record.careplanEnd(TIME - years(8), "stop_smoking", DUMMY_CODE);
      record.encounterStart(TIME - years(12), EncounterType.WELLNESS);
      record.careplanStart(TIME - years(12), "healthy_diet");
      filterCase("keep_old_active_careplan", p);
    }
    { // testExportFilterShouldKeepCareplanThatEndedDuringTarget
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.careplanStart(TIME - years(10), "stop_smoking");
      record.careplanEnd(TIME - years(1), "stop_smoking", DUMMY_CODE);
      filterCase("careplan_ended_during_target", p);
    }
    { // testExportFilterShouldKeepOldActiveConditions
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.conditionStart(TIME - years(10), "fakitis");
      record.conditionEnd(TIME - years(8), "fakitis");
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.conditionStart(TIME - years(10), "fakosis");
      filterCase("keep_old_active_conditions", p);
    }
    { // testExportFilterShouldKeepConditionThatEndedDuringTarget
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.conditionStart(TIME - years(10), "boneitis");
      record.conditionEnd(TIME - years(2), "boneitis");
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.conditionStart(TIME - years(10), "smallpox");
      record.conditionEnd(TIME - years(9), "smallpox");
      filterCase("condition_ended_during_target", p);
    }
    { // testExportFilterShouldKeepCauseOfDeath
      Person p = newPatient();
      // DeathModule.process creates its encounter through EncounterModule,
      // which needs a location and loaded providers (mirrors ExporterTest.setup).
      org.mitre.synthea.engine.Generator.DEFAULT_STATE =
          Config.get("test_state.default", "Massachusetts");
      org.mitre.synthea.world.geography.Location location =
          new org.mitre.synthea.world.geography.Location(
              org.mitre.synthea.engine.Generator.DEFAULT_STATE, null);
      location.assignPoint(p, location.randomCityName(p));
      org.mitre.synthea.world.agents.Provider.loadProviders(
          location, new DefaultRandomNumberGenerator(1L));
      Code causeOfDeath = new Code("SNOMED-CT", "Todo-lookup-code", "Rabies");
      p.recordDeath(TIME - years(20), causeOfDeath);
      DeathModule.process(p, TIME - years(20));
      filterCase("keep_cause_of_death", p);
    }
    { // testExportFilterShouldNotKeepOldStuff
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(18), EncounterType.EMERGENCY);
      record.procedure(TIME - years(20), "appendectomy");
      record.immunization(TIME - years(12), "flu_shot");
      record.observation(TIME - years(10), "weight", 123);
      filterCase("not_keep_old_stuff", p);
    }
    { // testExportFilterShouldKeepOldActiveStuff
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(18), EncounterType.EMERGENCY);
      record.conditionStart(TIME - years(18), "diabetes");
      filterCase("keep_old_active_stuff", p);
    }
    { // testExportFilterShouldFilterClaimItems
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(10), EncounterType.EMERGENCY);
      record.conditionStart(TIME - years(10), "something_permanent");
      record.procedure(TIME - years(10), "xray");
      filterCase("filter_claim_items", p);
    }
    { // testExportFilterShouldNotKeepOldStuffWhenActiveOfSameType
      Person p = newPatient();
      HealthRecord record = p.record;
      long oneWeek = Utilities.convertTime("weeks", 1);
      for (int i = 0; i < 3; i++) {
        record.encounterStart(TIME - years(10 - i), EncounterType.EMERGENCY);
        record.conditionStart(TIME - years(10 - i), "viral_sinusitis");
        record.conditionEnd(TIME - years(10 - i) + oneWeek, "viral_sinusitis");
      }
      record.encounterStart(TIME - oneWeek, EncounterType.EMERGENCY);
      record.conditionStart(TIME - oneWeek, "viral_sinusitis");
      filterCase("not_keep_old_same_type", p);
    }
    { // future-dated entries and future stop times (extra beyond the JUnit set)
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(1), EncounterType.WELLNESS);
      record.observation(TIME + 1000, "future_obs", 1);
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      Entry condition = record.conditionStart(TIME - years(10), "long_condition");
      condition.stop = TIME + years(5);
      record.encounterStart(TIME - years(10), EncounterType.WELLNESS);
      record.allergyStart(TIME - years(10), "peanuts");
      record.immunization(TIME - years(10), "flu_shot");
      filterCase("future_entries", p);
    }
  }

  static void entryWithinTimeRange() throws Exception {
    Method m = Exporter.class.getDeclaredMethod(
        "entryWithinTimeRange", Entry.class, long.class, long.class);
    m.setAccessible(true);
    long cutoff = TIME - years(YEARS);
    long[][] cases = {
      {cutoff + 1, 0},
      {cutoff, 0},
      {TIME, 0},
      {TIME + 1, 0},
      {cutoff - 100, cutoff + 1},
      {cutoff - 100, TIME + 500},
      {cutoff - 100, cutoff},
      {cutoff + 50, TIME + 500},
      {cutoff - 100, TIME},
    };
    Person p = newPatient();
    for (long[] c : cases) {
      Entry e = p.record.new Entry(c[0], "x");
      e.stop = c[1];
      boolean result = (boolean) m.invoke(null, e, cutoff, TIME);
      JsonObject o = base("entry_within_range");
      o.addProperty("start", Long.toString(c[0]));
      o.addProperty("stop", Long.toString(c[1]));
      o.addProperty("result", result);
      o.addProperty("stop_after", Long.toString(e.stop));
      line(o);
    }
  }

  static void filterAfterDeath() throws Exception {
    Method m = Exporter.class.getDeclaredMethod("filterAfterDeath", Person.class);
    m.setAccessible(true);
    Person p = newPatient();
    HealthRecord record = p.record;
    long death = TIME - 5000;
    p.attributes.put(Person.DEATHDATE, death);
    record.encounterStart(death - 1000, EncounterType.WELLNESS);
    record.encounterStart(death + 1000, EncounterType.WELLNESS);
    Encounter cert = record.encounterStart(death + 2000, EncounterType.WELLNESS);
    cert.codes.add(DeathModule.DEATH_CERTIFICATION);
    m.invoke(null, p);
    JsonObject o = base("filter_after_death");
    JsonArray starts = new JsonArray();
    for (Encounter e : record.encounters) {
      starts.add(Long.toString(e.start));
    }
    o.add("encounter_starts", starts);
    line(o);
  }

  static void setAllExporterFlagsFalse() {
    String[] flags = {
      "exporter.fhir_stu3.export", "exporter.fhir_dstu2.export", "exporter.fhir.export",
      "exporter.ccda.export", "exporter.json.export", "exporter.csv.export",
      "exporter.bfd.export", "exporter.cpcds.export", "exporter.text.export",
      "exporter.text.per_encounter_export", "exporter.symptoms.csv.export",
      "exporter.symptoms.text.export", "exporter.cdw.export", "exporter.clinical_note.export"
    };
    for (String f : flags) {
      Config.set(f, "false");
    }
  }

  static void exportScenarios() throws Exception {
    setAllExporterFlagsFalse();
    { // deferred export: nothing is filtered or written, the pair is queued
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(8), EncounterType.WELLNESS);
      record.observation(TIME - years(8), "height", 64);
      Exporter.ExporterRuntimeOptions options = new Exporter.ExporterRuntimeOptions();
      options.yearsOfHistory = 0;
      options.deferExports = true;
      boolean result = Exporter.export(p, TIME, options);
      Field f = Exporter.class.getDeclaredField("deferredExports");
      f.setAccessible(true);
      List<?> deferred = (List<?>) f.get(null);
      JsonObject o = base("export_defer");
      o.addProperty("result", result);
      o.addProperty("deferred_size", deferred.size());
      o.addProperty("encounters", record.encounters.size());
      line(o);
      deferred.clear();
    }
    { // plain export of a living person, no filtering (yearsOfHistory = 0)
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(8), EncounterType.WELLNESS);
      record.observation(TIME - years(8), "height", 64);
      Exporter.ExporterRuntimeOptions options = new Exporter.ExporterRuntimeOptions();
      options.yearsOfHistory = 0;
      boolean result = Exporter.export(p, TIME, options);
      JsonObject o = base("export_plain");
      o.addProperty("result", result);
      o.addProperty("encounters", record.encounters.size());
      line(o);
    }
    { // export of a dead person drops post-death encounters
      Person p = newPatient();
      HealthRecord record = p.record;
      long death = TIME - 5000;
      p.attributes.put(Person.DEATHDATE, death);
      record.encounterStart(death - 1000, EncounterType.WELLNESS);
      record.encounterStart(death + 1000, EncounterType.WELLNESS);
      Exporter.ExporterRuntimeOptions options = new Exporter.ExporterRuntimeOptions();
      options.yearsOfHistory = 0;
      boolean result = Exporter.export(p, TIME, options);
      JsonObject o = base("export_after_death");
      o.addProperty("result", result);
      o.addProperty("encounters", record.encounters.size());
      line(o);
    }
    { // export with yearsOfHistory applies the same filter as filterForExport
      Person p = newPatient();
      HealthRecord record = p.record;
      record.encounterStart(TIME - years(8), EncounterType.WELLNESS);
      record.observation(TIME - years(8), "height", 64);
      record.encounterStart(TIME - years(4), EncounterType.WELLNESS);
      record.observation(TIME - years(4), "weight", 128);
      Exporter.ExporterRuntimeOptions options = new Exporter.ExporterRuntimeOptions();
      options.yearsOfHistory = YEARS;
      boolean result = Exporter.export(p, TIME, options);
      JsonObject o = base("export_filtered");
      o.addProperty("result", result);
      o.add("record", Canonical.record(record));
      line(o);
    }
  }

  static void filenames(Path outDir) {
    Person p = newPatient();
    p.attributes.put(Person.NAME, "Jane Q Public");
    p.attributes.put(Person.ID, "abcdef-1234");
    Config.set("exporter.use_uuid_filenames", "false");
    JsonObject o = base("filename");
    o.addProperty("uuid", false);
    o.addProperty("out", Exporter.filename(p, "", "json"));
    o.addProperty("out_tagged", Exporter.filename(p, "0", "json"));
    line(o);
    Config.set("exporter.use_uuid_filenames", "true");
    JsonObject o2 = base("filename");
    o2.addProperty("uuid", true);
    o2.addProperty("out", Exporter.filename(p, "", "json"));
    o2.addProperty("out_tagged", Exporter.filename(p, "0", "json"));
    line(o2);
    Config.set("exporter.use_uuid_filenames", "false");

    Path base = outDir.resolve("outbase");
    Config.set("exporter.baseDirectory", base.toString());
    Config.set("exporter.subfolders_by_id_substring", "false");
    JsonObject o3 = base("output_folder");
    o3.addProperty("subfolders", false);
    o3.addProperty("out", base.relativize(Exporter.getOutputFolder("csv", null).toPath()).toString());
    line(o3);
    Config.set("exporter.subfolders_by_id_substring", "true");
    JsonObject o4 = base("output_folder");
    o4.addProperty("subfolders", true);
    o4.addProperty("out", base.relativize(Exporter.getOutputFolder("csv", p).toPath()).toString());
    line(o4);
    Config.set("exporter.subfolders_by_id_substring", "false");
  }
}
