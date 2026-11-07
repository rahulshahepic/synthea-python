package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.awt.geom.Point2D;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.mitre.synthea.engine.State;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.ValueGenerator;
import org.mitre.synthea.modules.QualityOfLifeModule;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.agents.Provider;
import org.mitre.synthea.world.concepts.HealthRecord.Code;
import org.mitre.synthea.world.concepts.HealthRecord.Encounter;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;
import org.mitre.synthea.world.concepts.VitalSign;
import org.synthea.parity.probes.support.CanonicalPerson;

/**
 * T09 probe: exercises the Person API (attributes, rand*, age calculations,
 * symptoms, vital signs, records, QALY/DALY accessors) plus ExpressedSymptom and
 * ExpressedConditionRecord, and dumps canonical Person state per case.
 *
 * <p>The Python mirror is tests/parity/test_person_component.py (component
 * parity: HealthRecord, CoverageRecord, Provider and State are test doubles
 * there, because T13/T16/T19 are not merged yet and a real Python Encounter
 * needs Claim (T14); the doubles supply only the state Person reads or
 * writes). This Java side always runs the real classes, so it must enrol
 * the person in the no-insurance plan before starting encounters.
 */
public class PersonProbe {

  /** A ValueGenerator returning a fixed value (for NaN/infinity vital signs). */
  public static class FixedValueGenerator extends ValueGenerator {
    private final double value;

    public FixedValueGenerator(Person person, double value) {
      super(person);
      this.value = value;
    }

    @Override
    public double getValue(long time) {
      return value;
    }
  }

  private static String d(double value) {
    return Double.toString(value);
  }

  private static void emit(PrintWriter w, String kase, String out) {
    JsonObject o = new JsonObject();
    o.addProperty("case", kase);
    o.addProperty("out", out);
    w.println(o.toString());
  }

  public static void main(String[] args) throws Exception {
    // Every Java Encounter creates a Claim, whose constructor requires a plan
    // record at the encounter time; load the no-insurance plan up front (the
    // HealthRecordProbe / HealthRecordTest setup) so records() can enrol.
    PayerManager.loadNoInsurance();
    Path out = Path.of(args[0]);
    rngOverloads(out);
    long[] seeds = new long[25];
    for (int i = 0; i < seeds.length; i++) {
      seeds[i] = i;
    }
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("person.jsonl"), StandardCharsets.UTF_8))) {
      for (long seed : seeds) {
        rng(w, seed);
        age(w, seed);
        symptoms(w, seed);
        vitals(w, seed);
      }
      ageEdges(w);
      for (long seed = 0; seed < 5; seed++) {
        records(w, seed);
        qol(w, seed);
        states(w, seed);
        providers(w, seed);
      }
    }
  }

  /** T54: exercise every RandomNumberGenerator default overload on actual Person. */
  private static void rngOverloads(Path out) throws Exception {
    long[] seeds = {0L, 1L, 42L, -1L, 123456789L, Long.MIN_VALUE, Long.MAX_VALUE};
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(
        out.resolve("person-rng-overloads.jsonl"), StandardCharsets.UTF_8))) {
      for (long seed : seeds) {
        Person person = new Person(seed);
        for (int draw = 0; draw < 100; draw++) {
          JsonObject row = new JsonObject();
          row.addProperty("seed", Long.toString(seed));
          row.addProperty("draw", draw);
          row.addProperty("uniform", d(person.rand()));
          row.addProperty("range", d(person.rand(-12.5, 91.25)));
          row.addProperty("integerBounds", d(person.rand(0, 10)));
          row.addProperty("decimals0", d(person.rand(-12.5, 91.25, 0)));
          row.addProperty("decimals2", d(person.rand(-12.5, 91.25, 2)));
          row.addProperty("decimalsNegative", d(person.rand(-125.0, 912.5, -1)));
          row.addProperty("decimalsNull", d(person.rand(-12.5, 91.25, null)));
          row.addProperty("doubleArray", d(person.rand(new double[]{-12.5, 91.25})));
          row.addProperty("intArray", d(person.rand(new int[]{-12, 91})));
          row.addProperty("oneChoice", person.rand("single"));
          row.addProperty("twoChoices", person.rand("a", "b"));
          row.addProperty("manyChoices", person.rand("a", "b", "c", "d", "e"));
          row.addProperty("count", Long.toString(person.getCount()));
          row.addProperty("nextLong", Long.toString(person.randLong()));
          w.println(row.toString());
        }
      }
    }
  }

  private static void rng(PrintWriter w, long seed) {
    Person p = new Person(seed);
    StringBuilder sb = new StringBuilder();
    sb.append("rand=").append(d(p.rand()));
    sb.append("\nrand=").append(d(p.rand()));
    sb.append("\nrandInt=").append(p.randInt());
    sb.append("\nrandInt(100)=").append(p.randInt(100));
    sb.append("\nrandGaussian=").append(d(p.randGaussian()));
    sb.append("\nrandLong=").append(p.randLong());
    sb.append("\nrandBoolean=").append(p.randBoolean());
    sb.append("\nrandUUID=").append(p.randUUID());
    sb.append("\nrandRange=").append(d(p.rand(2.0, 3.0)));
    sb.append("\nrandArray=").append(d(p.rand(new double[] {5.0, 6.0})));
    sb.append("\ncount=").append(p.getCount());
    sb.append("\nseed=").append(p.getSeed());
    sb.append("\n---\n").append(CanonicalPerson.dump(p));
    emit(w, "rng:" + seed, sb.toString());
  }

  private static void age(PrintWriter w, long seed) {
    Person p = new Person(seed);
    long birth = 631152000000L + seed * 31536000000L + seed * 86400000L;
    p.attributes.put(Person.BIRTHDATE, birth);
    long[] times = {
      birth - 86400000L, birth, birth + 86400000L,
      birth + 568036800000L, birth + 1234567890000L, 1767225600000L
    };
    emit(w, "age:" + seed, ageLog(p, times));
  }

  private static void ageEdges(PrintWriter w) {
    // Leap-day birthdate.
    Person leap = new Person(999);
    leap.attributes.put(Person.BIRTHDATE, 1709164800000L);
    emit(w, "age-edge:leap", ageLog(leap, new long[] {
      1709251200000L, 1740700800000L, 1740787200000L, 1835395200000L}));
    // Month-end birthdate.
    Person monthEnd = new Person(998);
    monthEnd.attributes.put(Person.BIRTHDATE, 1738281600000L);
    emit(w, "age-edge:month-end", ageLog(monthEnd, new long[] {
      1738368000000L, 1740700800000L, 1743379200000L}));
    // Pre-epoch birthdate (negative epoch millis).
    Person preEpoch = new Person(997);
    preEpoch.attributes.put(Person.BIRTHDATE, -126230400000L);
    emit(w, "age-edge:pre-epoch", ageLog(preEpoch, new long[] {
      -126316800000L, 0L, 126230400000L}));
    // No birthdate at all.
    Person noBirth = new Person(996);
    emit(w, "age-edge:none", ageLog(noBirth, new long[] {1700000000000L}));
  }

  private static String ageLog(Person p, long[] times) {
    StringBuilder sb = new StringBuilder();
    for (long t : times) {
      sb.append("t=").append(t)
          .append(" period=").append(p.age(t))
          .append(" years=").append(p.ageInYears(t))
          .append(" months=").append(p.ageInMonths(t))
          .append(" dec=").append(d(p.ageInDecimalYears(t)))
          .append(" alive=").append(p.alive(t))
          .append("\n");
    }
    sb.append("---\n").append(CanonicalPerson.dump(p));
    return sb.toString();
  }

  private static void symptoms(PrintWriter w, long seed) {
    Person p = new Person(seed);
    String[] modules = {"modA", "modB"};
    for (int i = 0; i < 6; i++) {
      String module = modules[i % 2];
      String type = (i % 3 == 0) ? "fever" : "pain";
      long time = 1000000L + i * 100000L + seed;
      int value = (int) ((seed * 7 + i * 30) % 120);
      boolean addressed = (i == 4);
      p.setSymptom(module, "cause" + i, type, time, value, addressed);
    }
    StringBuilder sb = new StringBuilder();
    sb.append("pain=").append(p.getSymptom("pain"));
    sb.append("\nfever=").append(p.getSymptom("fever"));
    sb.append("\nmissing=").append(p.getSymptom("missing"));
    sb.append("\nsymptoms=").append(p.getSymptoms());
    sb.append("\ntotal=").append(p.symptomTotal());
    sb.append("\nlastPainModA=").append(p.getSymptomLastUpdatedTime("modA", "pain"));
    sb.append("\nlastPainModX=").append(p.getSymptomLastUpdatedTime("modX", "pain"));
    p.getOnsetConditionRecord().onConditionOnset("modA", "stateA", "diabetes", 900000L + seed);
    p.getOnsetConditionRecord().onConditionOnset("modA", "stateA2", "diabetes", 1500000L + seed);
    p.getOnsetConditionRecord().onConditionEnd("modA", "diabetes", 1800000L + seed);
    p.getOnsetConditionRecord().onConditionOnset("modB", "stateB", "asthma", 1100000L + seed);
    sb.append("\nonsetDiabetesModA=")
        .append(p.getOnsetConditionRecord().getConditionLastOnsetTimeFromModule("modA", "diabetes"));
    sb.append("\nendDiabetesModA=")
        .append(p.getOnsetConditionRecord().getConditionLastEndTimeFromModule("modA", "diabetes"));
    sb.append("\nfromState=").append(p.getOnsetConditionRecord().getConditionFromState("modA", "stateA2"));
    sb.append("\nfromStateMissing=").append(p.getOnsetConditionRecord().getConditionFromState("modX", "stateA"));
    p.addressLargestSymptom();
    sb.append("\npainAfterAddress=").append(p.getSymptom("pain"));
    sb.append("\ntotalAfterAddress=").append(p.symptomTotal());
    sb.append("\n---\n").append(CanonicalPerson.dump(p));
    emit(w, "symptoms:" + seed, sb.toString());
  }

  private static void vitals(PrintWriter w, long seed) {
    Person p = new Person(seed);
    p.setVitalSign(VitalSign.HEART_RATE, 60.0 + seed);
    p.setVitalSign(VitalSign.HEIGHT, 170.04);
    p.setVitalSign(VitalSign.WEIGHT, 65.25);
    p.setVitalSign(VitalSign.BMI, 22.005);
    p.setVitalSign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, 120.49);
    p.setVitalSign(VitalSign.DIASTOLIC_BLOOD_PRESSURE, 80.5);
    long t = 123456789L;
    StringBuilder sb = new StringBuilder();
    VitalSign[] queried = {
      VitalSign.HEART_RATE, VitalSign.HEIGHT, VitalSign.WEIGHT, VitalSign.BMI,
      VitalSign.SYSTOLIC_BLOOD_PRESSURE, VitalSign.DIASTOLIC_BLOOD_PRESSURE
    };
    for (VitalSign vs : queried) {
      sb.append(vs.name()).append("=").append(d(p.getVitalSign(vs, t))).append("\n");
    }
    try {
      p.getVitalSign(VitalSign.RESPIRATION_RATE, t);
      sb.append("RESPIRATION_RATE=NO-ERROR\n");
    } catch (NullPointerException e) {
      sb.append("RESPIRATION_RATE=ERR:NullPointerException\n");
    }
    p.setVitalSign(VitalSign.OXYGEN_SATURATION, new FixedValueGenerator(p, Double.NaN));
    sb.append("OXYGEN_SATURATION=").append(d(p.getVitalSign(VitalSign.OXYGEN_SATURATION, t))).append("\n");
    p.setVitalSign(VitalSign.BLOOD_GLUCOSE, new FixedValueGenerator(p, Double.POSITIVE_INFINITY));
    sb.append("BLOOD_GLUCOSE=").append(d(p.getVitalSign(VitalSign.BLOOD_GLUCOSE, t)));
    sb.append("\n---\n").append(CanonicalPerson.dump(p));
    emit(w, "vitals:" + seed, sb.toString());
  }

  private static void records(PrintWriter w, long seed) {
    Config.set("exporter.split_records", "true");
    try {
      Person p = new Person(seed);
      p.attributes.put(Person.BIRTHDATE, 1000000L);
      // Enrol at birth (age 0): Claim construction throws "Person does not
      // have insurance at time ..." when no plan record covers the encounter.
      p.coverage.setPlanToNoInsurance(1000000L);
      Provider p1 = new Provider();
      p1.uuid = "prov-" + seed + "-a";
      Provider p2 = new Provider();
      p2.uuid = "prov-" + seed + "-b";
      StringBuilder sb = new StringBuilder();
      p.setProvider(EncounterType.WELLNESS, p1);
      Encounter e1 = p.encounterStart(5000000L + seed, EncounterType.WELLNESS);
      sb.append("enc1: start=").append(e1.start).append(" type=").append(e1.type)
          .append(" uuid=").append(e1.uuid).append("\n");
      p.setProvider(EncounterType.AMBULATORY, p2);
      Encounter e2 = p.encounterStart(6000000L + seed, EncounterType.AMBULATORY);
      sb.append("enc2: start=").append(e2.start).append(" type=").append(e2.type)
          .append(" uuid=").append(e2.uuid).append("\n");
      sb.append("providerCount=").append(p.providerCount()).append("\n");
      sb.append("activeProvider=").append(p.record.provider.getResourceID()).append("\n");
      long death = 7000000L + seed;
      sb.append("aliveBeforeDeath=").append(p.alive(death - 1)).append("\n");
      p.recordDeath(death, new Code("SNOMED", "12345", "Test cause"));
      sb.append("aliveAtDeath=").append(p.alive(death)).append("\n");
      sb.append("count=").append(p.getCount());
      sb.append("\n---\n").append(CanonicalPerson.dump(p));
      emit(w, "records:" + seed, sb.toString());
    } finally {
      Config.set("exporter.split_records", "false");
    }
  }

  private static void qol(PrintWriter w, long seed) {
    Person p = new Person(seed);
    Map<Integer, Double> qalys = new HashMap<>();
    qalys.put(2019, 0.5);
    qalys.put(2020, 0.25);
    qalys.put(2021, 1e16);
    qalys.put(2022, 1.0);
    qalys.put(2023, -1e16);
    p.attributes.put(QualityOfLifeModule.QALY, qalys);
    Map<Integer, Double> dalys = new HashMap<>();
    dalys.put(2020, 2.0);
    dalys.put(2021, 3.5);
    p.attributes.put(QualityOfLifeModule.DALY, dalys);
    Map<Integer, Double> qols = new HashMap<>();
    qols.put(2019, 0.9);
    qols.put(2020, 0.8);
    p.attributes.put(QualityOfLifeModule.QOLS, qols);
    StringBuilder sb = new StringBuilder();
    sb.append("qalys=").append(d(p.getQalys()));
    sb.append("\ndalys=").append(d(p.getDalys()));
    sb.append("\nqols2019=").append(d(p.getQolsForYear(2019)));
    sb.append("\nqols2050=").append(d(p.getQolsForYear(2050)));
    sb.append("\n---\n").append(CanonicalPerson.dump(p));
    emit(w, "qol:" + seed, sb.toString());
  }

  private static State.Initial state(String name, Long exited) {
    State.Initial state = new State.Initial();
    state.name = name;
    state.exited = exited;
    return state;
  }

  private static void states(PrintWriter w, long seed) {
    Person p = new Person(seed);
    List<State> history = new ArrayList<>();
    history.add(state("A", 100L));
    history.add(state("B", null));
    history.add(state("A", 50L));
    p.history = history;
    StringBuilder sb = new StringBuilder();
    sb.append("priorA=").append(p.hadPriorState("A"));
    sb.append("\npriorB=").append(p.hadPriorState("B"));
    sb.append("\npriorC=").append(p.hadPriorState("C"));
    sb.append("\npriorASinceB=").append(p.hadPriorState("A", "B", null));
    sb.append("\npriorAWithin75=").append(p.hadPriorState("A", null, 75L));
    sb.append("\npriorAWithin150=").append(p.hadPriorState("A", null, 150L));
    sb.append("\npriorBSinceA=").append(p.hadPriorState("B", "A", null));
    sb.append("\n---\n").append(CanonicalPerson.dump(p));
    emit(w, "states:" + seed, sb.toString());
  }

  private static void providers(PrintWriter w, long seed) {
    Person p = new Person(seed);
    StringBuilder sb = new StringBuilder();
    sb.append("reserve1=").append(p.reserveCurrentEncounter(1000L, "mod1"));
    sb.append("\nreserve2=").append(p.reserveCurrentEncounter(1001L, "mod2"));
    sb.append("\ncurrentModule=").append(p.getCurrentEncounterModule());
    p.releaseCurrentEncounter(1002L, "mod1");
    sb.append("\nhasAfterRelease=").append(p.hasCurrentEncounter());
    Provider p1 = new Provider();
    p1.uuid = "cur-" + seed;
    Provider p2 = new Provider();
    p2.uuid = "cur2-" + seed;
    p.addCurrentProvider("ctx1", p1);
    p.addCurrentProvider("ctx2", p2);
    Provider got1 = p.getCurrentProvider("ctx1");
    sb.append("\ncurrentCtx1=").append(got1 == null ? "null" : got1.getResourceID());
    Provider got2 = p.getCurrentProvider("ctx2");
    sb.append("\ncurrentCtx2=").append(got2 == null ? "null" : got2.getResourceID());
    p.removeCurrentProvider("ctx1");
    sb.append("\ncurrentCtx1AfterRemove=")
        .append(p.getCurrentProvider("ctx1") == null ? "null" : "present");
    p.attributes.put(Person.COORDINATE, new Point2D.Double(1.5, -2.25));
    sb.append("\nx=").append(d(p.getX()));
    sb.append("\ny=").append(d(p.getY()));
    sb.append("\nlonLat=").append(CanonicalPerson.renderValue(p.getLonLat()));
    sb.append("\n---\n").append(CanonicalPerson.dump(p));
    emit(w, "providers:" + seed, sb.toString());
  }
}
