package org.synthea.parity.probes;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import org.mitre.synthea.engine.Logic;
import org.mitre.synthea.engine.State;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.HealthRecord.Allergy;
import org.mitre.synthea.world.concepts.HealthRecord.CarePlan;
import org.mitre.synthea.world.concepts.HealthRecord.Code;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;
import org.mitre.synthea.world.concepts.HealthRecord.Entry;
import org.mitre.synthea.world.concepts.HealthRecord.Medication;
import org.mitre.synthea.world.concepts.HealthRecord.Observation;
import org.mitre.synthea.world.concepts.VitalSign;

/**
 * T17 probe: evaluates every Logic condition type used in
 * {@code resources/modules/**} (plus False / At Most, which only LogicTest
 * uses) against 60 scripted persons and dumps the boolean results
 * (T/F, or X when the Java code throws) in definition order.
 *
 * <p>The definitions are also written to the golden directory as
 * {@code definitions.json}; the Python mirror (tests/parity/test_logic.py)
 * builds the same Logic objects from that file, rebuilds the same scripted
 * persons with the identical index-driven script, and compares the result
 * strings exactly. Scripted-person construction is duplicated in the Python
 * test; keep the two in sync.
 *
 * <p>This is component parity (PORTING_GUIDE §10) on the Python side: Claim
 * (T14) and CoverageRecord (T16) are test doubles there, and State (T19) is
 * a field-only double. The Java side always runs the real classes.
 */
public class LogicProbe {

  /** 2016-09-21 00:00:00 UTC, the LogicTest reference time. */
  static final long TIME = 1474416000000L;

  static final Code MMSE = new Code("LOINC", "72107-6", "Mini Mental State Examination");
  static final Code DIABETES = new Code("SNOMED-CT", "73211009", "Diabetes mellitus");
  static final Code ALZHEIMERS = new Code("SNOMED-CT", "26929004", "Alzheimer's disease (disorder)");
  static final Code PENICILLIN = new Code("RxNorm", "7984", "Penicillin V");
  static final Code MED_CODE = new Code("RxNorm", "617314", "Metformin");
  static final Code CAREPLAN_CODE =
      new Code("SNOMED-CT", "698360004", "Diabetes self management plan");
  static final String MED_TYPE = "617314";
  static final String CAREPLAN_TYPE = "698360004";

  static final String[] DEFINITIONS = {
    "{\"condition_type\":\"True\"}",
    "{\"condition_type\":\"False\"}",
    "{\"condition_type\":\"Gender\",\"gender\":\"M\"}",
    "{\"condition_type\":\"Gender\",\"gender\":\"F\"}",
    "{\"condition_type\":\"Age\",\"operator\":\"<\",\"quantity\":40,\"unit\":\"years\"}",
    "{\"condition_type\":\"Age\",\"operator\":\"<=\",\"quantity\":40,\"unit\":\"years\"}",
    "{\"condition_type\":\"Age\",\"operator\":\"==\",\"quantity\":40,\"unit\":\"years\"}",
    "{\"condition_type\":\"Age\",\"operator\":\">=\",\"quantity\":40,\"unit\":\"years\"}",
    "{\"condition_type\":\"Age\",\"operator\":\">\",\"quantity\":40,\"unit\":\"years\"}",
    "{\"condition_type\":\"Age\",\"operator\":\"!=\",\"quantity\":40,\"unit\":\"years\"}",
    "{\"condition_type\":\"Age\",\"operator\":\"<\",\"quantity\":12,\"unit\":\"months\"}",
    "{\"condition_type\":\"Age\",\"operator\":\">=\",\"quantity\":24,\"unit\":\"months\"}",
    "{\"condition_type\":\"Age\",\"operator\":\"<\",\"quantity\":40,\"unit\":\"days\"}",
    "{\"condition_type\":\"Date\",\"operator\":\"<\",\"year\":2016}",
    "{\"condition_type\":\"Date\",\"operator\":\">=\",\"year\":2000}",
    "{\"condition_type\":\"Date\",\"operator\":\"<=\",\"month\":9}",
    "{\"condition_type\":\"Date\",\"operator\":\">=\",\"month\":4}",
    "{\"condition_type\":\"Date\",\"operator\":\"==\",\"month\":7}",
    "{\"condition_type\":\"Date\",\"operator\":\"==\",\"date\":{\"year\":2007,\"month\":10,"
        + "\"day\":31,\"hour\":0,\"minute\":0,\"second\":0,\"millisecond\":0}}",
    "{\"condition_type\":\"Date\",\"operator\":\"<=\",\"date\":{\"year\":2016,\"month\":12,"
        + "\"day\":25,\"hour\":0,\"minute\":0,\"second\":0,\"millisecond\":0}}",
    "{\"condition_type\":\"Date\",\"operator\":\">=\",\"date\":{\"year\":2000,\"month\":7,"
        + "\"day\":4,\"hour\":0,\"minute\":0,\"second\":0,\"millisecond\":0}}",
    "{\"condition_type\":\"Socioeconomic Status\",\"category\":\"High\"}",
    "{\"condition_type\":\"Socioeconomic Status\",\"category\":\"Middle\"}",
    "{\"condition_type\":\"Socioeconomic Status\",\"category\":\"Low\"}",
    "{\"condition_type\":\"Race\",\"race\":\"White\"}",
    "{\"condition_type\":\"Race\",\"race\":\"white\"}",
    "{\"condition_type\":\"Race\",\"race\":\"foo\"}",
    "{\"condition_type\":\"Symptom\",\"symptom\":\"PainLevel\",\"operator\":\">\",\"value\":50}",
    "{\"condition_type\":\"Symptom\",\"symptom\":\"PainLevel\",\"operator\":\"<=\",\"value\":80}",
    "{\"condition_type\":\"Symptom\",\"symptom\":\"PainLevel\",\"operator\":\"==\",\"value\":60}",
    "{\"condition_type\":\"Symptom\",\"symptom\":\"LackOfAppetite\",\"operator\":\">\",\"value\":50}",
    "{\"condition_type\":\"Symptom\",\"symptom\":\"NoSuchSymptom\",\"operator\":\">\",\"value\":0}",
    "{\"condition_type\":\"Symptom\",\"symptom\":\"NoSuchSymptom\",\"operator\":\"==\",\"value\":0}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"72107-6\","
        + "\"display\":\"Mini Mental State Examination\"}],\"operator\":\">\",\"value\":22}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"72107-6\","
        + "\"display\":\"Mini Mental State Examination\"}],\"operator\":\"<=\",\"value\":22}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"72107-6\","
        + "\"display\":\"Mini Mental State Examination\"}],\"operator\":\"is nil\"}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"72107-6\","
        + "\"display\":\"Mini Mental State Examination\"}],\"operator\":\"is not nil\"}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"00000-0\","
        + "\"display\":\"No such observation\"},{\"system\":\"LOINC\",\"code\":\"72107-6\","
        + "\"display\":\"Mini Mental State Examination\"}],\"operator\":\">\",\"value\":22}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"99999-9\","
        + "\"display\":\"Value Code Test\"}],\"operator\":\"==\",\"value_code\":{\"system\":\"LOINC\","
        + "\"code\":\"72107-7\",\"display\":\"Some Observation Value\"}}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"88888-8\","
        + "\"display\":\"Loss Panel\"}],\"operator\":\">\",\"value\":20}",
    "{\"condition_type\":\"Observation\",\"codes\":[{\"system\":\"LOINC\",\"code\":\"88888-8\","
        + "\"display\":\"Loss Panel\"}],\"operator\":\"is nil\"}",
    "{\"condition_type\":\"Observation\",\"referenced_by_attribute\":\"Diabetes Test Performed\","
        + "\"operator\":\"is not nil\"}",
    "{\"condition_type\":\"Observation\",\"referenced_by_attribute\":\"Diabetes Test Performed\","
        + "\"operator\":\"==\",\"value\":\"12345\"}",
    "{\"condition_type\":\"Observation\",\"referenced_by_attribute\":\"Never Set Attribute\","
        + "\"operator\":\"is not nil\"}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"Test_Attribute_Key\",\"operator\":\"==\","
        + "\"value\":\"TestValue\"}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"Test_Attribute_Key\",\"operator\":\"<=\","
        + "\"value\":\"UComesAfterTandBeforeW\"}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"Test_Attribute_Key\",\"operator\":\">\","
        + "\"value\":100}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"Test_Attribute_Key\",\"operator\":\"is nil\"}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"Test_Attribute_Key\","
        + "\"operator\":\"is not nil\"}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"score\",\"operator\":\">=\",\"value\":50}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"score\",\"operator\":\"<\",\"value\":50}",
    "{\"condition_type\":\"Attribute\",\"attribute\":\"score\",\"operator\":\"==\",\"value\":\"abc\"}",
    "{\"condition_type\":\"And\",\"conditions\":[{\"condition_type\":\"True\"},"
        + "{\"condition_type\":\"Gender\",\"gender\":\"M\"},"
        + "{\"condition_type\":\"Age\",\"operator\":\"<\",\"quantity\":40,\"unit\":\"years\"}]}",
    "{\"condition_type\":\"And\",\"conditions\":[{\"condition_type\":\"True\"},"
        + "{\"condition_type\":\"False\"}]}",
    "{\"condition_type\":\"Or\",\"conditions\":[{\"condition_type\":\"False\"},"
        + "{\"condition_type\":\"Gender\",\"gender\":\"F\"}]}",
    "{\"condition_type\":\"Or\",\"conditions\":[{\"condition_type\":\"False\"},"
        + "{\"condition_type\":\"False\"}]}",
    "{\"condition_type\":\"Not\",\"condition\":{\"condition_type\":\"Gender\",\"gender\":\"M\"}}",
    "{\"condition_type\":\"Not\",\"condition\":{\"condition_type\":\"True\"}}",
    "{\"condition_type\":\"At Least\",\"minimum\":2,\"conditions\":["
        + "{\"condition_type\":\"Gender\",\"gender\":\"M\"},"
        + "{\"condition_type\":\"Age\",\"operator\":\">=\",\"quantity\":40,\"unit\":\"years\"},"
        + "{\"condition_type\":\"Socioeconomic Status\",\"category\":\"High\"},"
        + "{\"condition_type\":\"True\"}]}",
    "{\"condition_type\":\"At Most\",\"maximum\":1,\"conditions\":["
        + "{\"condition_type\":\"Gender\",\"gender\":\"M\"},"
        + "{\"condition_type\":\"Age\",\"operator\":\">=\",\"quantity\":40,\"unit\":\"years\"},"
        + "{\"condition_type\":\"Socioeconomic Status\",\"category\":\"High\"}]}",
    "{\"condition_type\":\"And\",\"conditions\":["
        + "{\"condition_type\":\"Or\",\"conditions\":["
        + "{\"condition_type\":\"Gender\",\"gender\":\"F\"},"
        + "{\"condition_type\":\"Age\",\"operator\":\"<\",\"quantity\":18,\"unit\":\"years\"}]},"
        + "{\"condition_type\":\"Not\",\"condition\":"
        + "{\"condition_type\":\"Active Condition\",\"codes\":[{\"system\":\"SNOMED-CT\","
        + "\"code\":\"73211009\",\"display\":\"Diabetes mellitus\"}]}}]}",
    "{\"condition_type\":\"PriorState\",\"name\":\"DoctorVisit\"}",
    "{\"condition_type\":\"PriorState\",\"name\":\"CarePlan\",\"since\":\"DoctorVisit\"}",
    "{\"condition_type\":\"PriorState\",\"name\":\"DoctorVisit\",\"within\":{\"quantity\":3,"
        + "\"unit\":\"years\"}}",
    "{\"condition_type\":\"PriorState\",\"name\":\"CarePlan\",\"since\":\"DoctorVisit\","
        + "\"within\":{\"quantity\":3,\"unit\":\"years\"}}",
    "{\"condition_type\":\"Active Condition\",\"codes\":[{\"system\":\"SNOMED-CT\","
        + "\"code\":\"73211009\",\"display\":\"Diabetes mellitus\"}]}",
    "{\"condition_type\":\"Active Condition\",\"codes\":[{\"system\":\"SNOMED-CT\","
        + "\"code\":\"26929004\",\"display\":\"Alzheimer's disease (disorder)\"}]}",
    "{\"condition_type\":\"Active Condition\",\"referenced_by_attribute\":\"Alzheimer's Variant\"}",
    "{\"condition_type\":\"Active Allergy\",\"codes\":[{\"system\":\"RxNorm\",\"code\":\"7984\","
        + "\"display\":\"Penicillin V\"}]}",
    "{\"condition_type\":\"Active Medication\",\"codes\":[{\"system\":\"RxNorm\",\"code\":\"617314\","
        + "\"display\":\"Metformin\"}]}",
    "{\"condition_type\":\"Active Medication\",\"referenced_by_attribute\":\"Current Medication\"}",
    "{\"condition_type\":\"Active CarePlan\",\"codes\":[{\"system\":\"SNOMED-CT\","
        + "\"code\":\"698360004\",\"display\":\"Diabetes self management plan\"}]}",
    "{\"condition_type\":\"Active CarePlan\",\"referenced_by_attribute\":\"Angina_CarePlan\"}",
    "{\"condition_type\":\"Active Condition\"}",
    "{\"condition_type\":\"Vital Sign\",\"vital_sign\":\"Systolic Blood Pressure\","
        + "\"operator\":\">\",\"value\":120}",
    "{\"condition_type\":\"Vital Sign\",\"vital_sign\":\"Systolic Blood Pressure\","
        + "\"operator\":\"<=\",\"value\":120}",
    "{\"condition_type\":\"Vital Sign\",\"vital_sign\":\"Diastolic Blood Pressure\","
        + "\"operator\":\">=\",\"value\":80}",
  };

  public static void main(String[] args) throws Exception {
    PayerManager.loadNoInsurance();
    Path out = Path.of(args[0]);

    JsonArray definitions = new JsonArray();
    List<Logic> logics = new ArrayList<>();
    for (String definition : DEFINITIONS) {
      definitions.add(JsonParser.parseString(definition));
      logics.add(Utilities.getGson().fromJson(definition, Logic.class));
    }
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("definitions.json"), StandardCharsets.UTF_8))) {
      w.println(definitions.toString());
    }

    Config.set("exporter.split_records", "false");
    Config.set("exporter.split_records.duplicate_data", "false");
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("logic.jsonl"), StandardCharsets.UTF_8))) {
      for (int i = 0; i < 60; i++) {
        emit(w, "person:" + i, evaluate(logics, scriptedPerson(i)));
      }
      // Second pass over the split-record persons with duplicate_data on:
      // the Active*/Observation history fallbacks now copy entries into the
      // current encounter as a side effect.
      Config.set("exporter.split_records.duplicate_data", "true");
      for (int i = 0; i < 60; i++) {
        if (i % 7 != 6) {
          continue;
        }
        emit(w, "dup:" + i, evaluate(logics, scriptedPerson(i)));
      }
      Config.set("exporter.split_records.duplicate_data", "false");
    }
  }

  private static void emit(PrintWriter w, String kase, String results) {
    JsonObject o = new JsonObject();
    o.addProperty("case", kase);
    o.addProperty("results", results);
    w.println(o.toString());
  }

  private static String evaluate(List<Logic> logics, Person person) {
    StringBuilder sb = new StringBuilder();
    for (Logic logic : logics) {
      try {
        sb.append(logic.test(person, TIME) ? "T" : "F");
      } catch (Exception e) {
        sb.append("X");
      }
    }
    return sb.toString();
  }

  /** The scripted-person script; mirrored exactly by the Python parity test. */
  static Person scriptedPerson(int i) {
    boolean lossOfCare = (i % 22 == 10 || i % 22 == 21);
    if (lossOfCare) {
      Config.set("generate.payers.loss_of_care", "true");
    }
    Person p = new Person(i);
    if (lossOfCare) {
      Config.set("generate.payers.loss_of_care", "false");
    }
    long time = TIME;
    p.attributes.put(Person.INCOME, 10000000);

    int ageSlot = i % 12;
    long birth;
    if (ageSlot == 1) {
      birth = time - (long) (i % 24 + 1) * 2592000000L; // 30-day "months"
    } else {
      int[] ages = {0, 0, 2, 5, 12, 17, 18, 35, 40, 41, 65, 90};
      birth = time - (long) ages[ageSlot] * 31557600000L; // 365.25-day years
    }
    p.attributes.put(Person.BIRTHDATE, birth);
    // Enrol in the no-insurance plan from birth, so Claim construction
    // (inside every Encounter/Medication) finds a plan record. PlanRecords
    // span one calendar year each, so this is LogicTest's enrolment loop
    // verbatim. (On the Python side CoverageRecord is a double and Claim is
    // doubled, so only the setPlanToNoInsurance call is mirrored there; the
    // loop has no other observable effect.)
    p.coverage.setPlanToNoInsurance(birth);
    for (int y = 1; y <= Utilities.getYear(time - birth); y++) {
      p.coverage.newEnrollmentPeriod(birth + Utilities.convertTime("years", y));
    }
    p.coverage.setPlanToNoInsurance(time);
    // A base encounter so record.currentEncounter(time) never has to create
    // one. It must not predate the birthdate: Claim construction requires a
    // plan record, and a not-yet-born person has no insurance history.
    p.record.encounterStart(Math.max(time - 1000, birth), EncounterType.WELLNESS);

    if (i % 3 == 0) {
      p.attributes.put(Person.GENDER, "M");
    } else if (i % 3 == 1) {
      p.attributes.put(Person.GENDER, "F");
    }
    if (i % 13 != 12) {
      String[] races = {"white", "black", "asian", "hispanic", "native", "other", "White", "WHITE"};
      p.attributes.put(Person.RACE, races[i % 8]);
    }
    if (i % 4 != 3) {
      String[] ses = {"High", "Middle", "Low"};
      p.attributes.put(Person.SOCIOECONOMIC_CATEGORY, ses[i % 4]);
    }
    switch (i % 6) {
      case 1 -> p.attributes.put("Test_Attribute_Key", "TestValue");
      case 2 -> p.attributes.put("Test_Attribute_Key", "Wrong Value");
      case 3 -> p.attributes.put("Test_Attribute_Key", 120);
      case 4 -> p.attributes.put("Test_Attribute_Key", 100.5);
      case 5 -> p.attributes.put("Test_Attribute_Key", true);
      default -> { }
    }
    p.attributes.put("score", (i * 7) % 100);

    int[] pain = {0, 10, 50, 60, 80, 100};
    p.setSymptom("Module1", "Appendicitis", "PainLevel", time, pain[i % 6], false);
    if (i % 3 == 0) {
      p.setSymptom("Module2", "Appendicitis", "PainLevel", time, 30, false);
    }
    if (i % 4 == 0) {
      p.setSymptom("Module1", "Appendicitis", "LackOfAppetite", time, 100, false);
    }

    if (i % 4 != 0) {
      double[] systolic = {0, 90, 120, 140};
      p.setVitalSign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, systolic[i % 4]);
    }
    if (i % 5 == 0) {
      p.setVitalSign(VitalSign.DIASTOLIC_BLOOD_PRESSURE, 80.0);
    }

    int mmseSlot = i % 4;
    if (mmseSlot != 0) {
      int[] mmseValues = {0, 12, 22, 29};
      Observation obs = p.record.observation(time, MMSE.code, mmseValues[mmseSlot]);
      obs.codes.add(MMSE);
    }
    if (i % 5 == 1) {
      Code valueCode = new Code("LOINC", i % 2 == 0 ? "72107-7" : "72107-8", "Some Observation Value");
      Observation obs = p.record.observation(time, "99999-9", valueCode);
      obs.codes.add(new Code("LOINC", "99999-9", "Value Code Test"));
    }
    if (i % 3 == 0) {
      Observation obs = p.record.observation(time, "Glucose Panel", "12345");
      p.attributes.put("Diabetes Test Performed", obs);
    }
    if (i % 3 == 1) {
      Observation obs = p.record.observation(time, "Blood Panel", "blah blah");
      p.attributes.put("Blood Test Performed", obs);
    }

    if (i % 3 == 0) {
      p.record.conditionStart(time, DIABETES.code);
    }
    if (i % 3 == 1) {
      p.record.conditionStart(time, DIABETES.code);
      p.record.conditionEnd(time + 1000, DIABETES.code);
    }
    if (i % 4 == 0) {
      Entry cond = p.record.conditionStart(time, ALZHEIMERS.code);
      p.attributes.put("Alzheimer's Variant", cond);
    }
    if (i % 3 == 0) {
      p.record.allergyStart(time, PENICILLIN.code);
    }
    if (i % 3 == 2) {
      p.record.allergyStart(time, PENICILLIN.code);
      p.record.allergyEnd(time + 1000, PENICILLIN.code);
    }
    if (i % 3 == 0) {
      p.record.medicationStart(time, MED_TYPE, false);
    }
    if (i % 3 == 1) {
      p.record.medicationStart(time, MED_TYPE, false);
      p.record.medicationEnd(time + 1000, MED_TYPE, new Code("SNOMED-CT", "123", "reason"));
    }
    if (i % 5 == 0) {
      Medication med = p.record.medicationStart(time, "555555", false);
      p.attributes.put("Current Medication", med);
    }
    if (i % 3 == 0) {
      CarePlan cp = p.record.careplanStart(time, CAREPLAN_TYPE);
      cp.codes.add(CAREPLAN_CODE);
    }
    if (i % 4 == 1) {
      CarePlan cp = p.record.careplanStart(time, CAREPLAN_TYPE);
      cp.codes.add(CAREPLAN_CODE);
      p.attributes.put("Angina_CarePlan", cp);
    }

    List<State> history = new LinkedList<>();
    switch (i % 4) {
      case 1 -> history.add(state("CarePlan", time));
      case 2 -> {
        history.add(state("DoctorVisit", time));
        history.add(state("CarePlan", time));
      }
      case 3 -> {
        history.add(state("CarePlan", time));
        history.add(state("DoctorVisit", time - 2 * 31557600000L));
        history.add(state("CarePlan", time - 5 * 31557600000L));
      }
      default -> { }
    }
    p.history = history;

    if (i % 7 == 6) {
      // Split records: the current record is fresh (switched provider), and
      // the earlier entries survive only in the module history.
      p.hasMultipleRecords = true;
      p.records = new ConcurrentHashMap<String, HealthRecord>();
      List<State> splitStates = new LinkedList<>();
      Entry condition = p.record.new Entry(time, DIABETES.code);
      condition.codes.add(DIABETES);
      splitStates.add(state("ConditionState", time, condition));
      Observation obs = p.record.new Observation(time, MMSE.code, 25);
      obs.codes.add(MMSE);
      splitStates.add(state("ObservationState", time, obs));
      Medication med = p.record.new Medication(time, MED_TYPE);
      med.codes.add(MED_CODE);
      splitStates.add(state("MedicationState", time, med));
      CarePlan cp = p.record.new CarePlan(time, CAREPLAN_TYPE);
      cp.codes.add(CAREPLAN_CODE);
      splitStates.add(state("CarePlanState", time, cp));
      Allergy allergy = p.record.new Allergy(time, PENICILLIN.code);
      allergy.codes.add(PENICILLIN);
      splitStates.add(state("AllergyState", time, allergy));
      history.addAll(0, splitStates);
      p.record = new HealthRecord(p);
      p.record.encounterStart(Math.max(time - 1000, birth), EncounterType.WELLNESS);
    }

    if (lossOfCare) {
      // The current record is fresh; the panel observation lives only in the
      // loss-of-care record (i % 22 == 10) or the default record (== 21).
      p.record = new HealthRecord(p);
      p.record.encounterStart(Math.max(time - 1000, birth), EncounterType.WELLNESS);
      if (i % 22 == 10) {
        p.lossOfCareRecord.encounterStart(Math.max(time - 1000, birth), EncounterType.WELLNESS);
        Observation obs = p.lossOfCareRecord.observation(time, "88888-8", 33);
        obs.codes.add(new Code("LOINC", "88888-8", "Loss Panel"));
      } else {
        Observation obs = p.defaultRecord.observation(time, "88888-8", 17);
        obs.codes.add(new Code("LOINC", "88888-8", "Loss Panel"));
      }
    }
    return p;
  }

  private static State state(String name, long exited) {
    return state(name, exited, null);
  }

  private static State state(String name, long exited, Entry entry) {
    State state = new State.Simple();
    state.name = name;
    state.entered = state.exited = exited;
    state.entry = entry;
    return state;
  }
}
