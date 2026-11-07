package org.synthea.parity.probes;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Comparator;
import java.util.List;
import java.util.TimeZone;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.modules.HealthInsuranceModule;
import org.mitre.synthea.world.agents.Payer;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.healthinsurance.PlanRecord;
import org.mitre.synthea.world.geography.Location;
import org.synthea.parity.probes.support.CanonicalCoverage;

/**
 * T16 parity: insurance selection for 240 seeded synthetic persons over
 * 30 years of weekly timesteps, driven by the real HealthInsuranceModule,
 * PayerManager (Massachusetts, real payer/eligibility CSVs) and
 * CoverageRecord. Twice a year a deterministic claim-sized expense hits the
 * current plan record. Canonical dumps of each coverage record plus the
 * payers' accumulated statistics must match the Python port exactly,
 * including the per-person RNG draw count.
 */
public class CoverageProbe {
  static final Gson GSON = new GsonBuilder().serializeNulls().create();
  static final int PERSONS = 240;
  static final int YEARS = 30;

  static long addYears(long time, int years) {
    Calendar c = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
    c.setTimeInMillis(time);
    for (int i = 0; i < years; i++) {
      c.add(Calendar.YEAR, 1);
    }
    return c.getTimeInMillis();
  }

  static Person person(int i) {
    Person p = new Person(1000L + i * 7919L);
    long birth = Utilities.convertCalendarYearsToTime(1935 + (i % 80)) + (i % 27) * 86400000L;
    p.attributes.put(Person.BIRTHDATE, birth);
    p.attributes.put(Person.ID, "person-" + i);
    p.attributes.put(Person.NAME, "Person" + i + " Sample" + i);
    p.attributes.put(Person.LAST_NAME, "Sample" + i);
    p.attributes.put(Person.NAME_MOTHER, "Mom" + i);
    p.attributes.put(Person.NAME_FATHER, "Dad" + i);
    p.attributes.put(Person.GENDER, i % 2 == 0 ? "M" : "F");
    p.attributes.put(Person.MARITAL_STATUS, i % 3 == 0 ? "M" : "S");
    p.attributes.put(Person.SEXUAL_ORIENTATION, i % 7 == 0 ? "homosexual" : "heterosexual");
    p.attributes.put(Person.INCOME, (i % 13) * 12000 + (i % 5) * 1750);
    p.attributes.put(Person.OCCUPATION_LEVEL, (i % 5) * 0.2);
    if (i % 11 == 0) {
      p.attributes.put("pregnant", true);
    }
    if (i % 17 == 0) {
      p.attributes.put(Person.BLINDNESS, true);
    }
    if (i % 19 == 0) {
      p.attributes.put("end_stage_renal_disease", true);
    }
    if (i % 23 == 0) {
      // A Social Security Disability qualifying condition (burn injury),
      // present from birth. Inserted directly into the record's present map:
      // conditionStart would drag in encounter/provider machinery that the
      // eligibility check (present-map lookup) never reads.
      p.record.present.put("403192003", p.record.new Entry(birth, "403192003"));
    }
    return p;
  }

  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    Config.set("generate.payers.selection_behavior", "random");
    PayerManager.clear();
    PayerManager.loadPayers(new Location("Massachusetts", null));
    HealthInsuranceModule module = new HealthInsuranceModule();
    long timestep = Config.getAsLong("generate.timestep");
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("coverage.jsonl")))) {
      for (int i = 0; i < PERSONS; i++) {
        Person p = person(i);
        long birth = (long) p.attributes.get(Person.BIRTHDATE);
        long end = addYears(birth, YEARS);
        long last = birth;
        int step = 0;
        for (long t = birth; t < end; t += timestep, step++) {
          module.process(p, t);
          last = t;
          if (step % 26 == 13) {
            PlanRecord record = p.coverage.getPlanRecordAtTime(t);
            record.incrementPrimaryCoverage(new BigDecimal((100 + (step % 9) * 7) + ".50"));
            record.incrementOutOfPocketExpenses(new BigDecimal((20 + (step % 4) * 3) + ".75"));
            record.incrementSecondaryCoverage(new BigDecimal((5 + (step % 3)) + ".00"));
          }
        }
        JsonObject o = new JsonObject();
        o.addProperty("i", i);
        o.add("coverage", CanonicalCoverage.coverage(p.coverage));
        o.addProperty("income_remaining", p.coverage.incomeRemaining(last));
        o.addProperty("insurance_status", (String) p.attributes.get(Person.INSURANCE_STATUS));
        o.addProperty("rng_count", p.getCount());
        w.println(GSON.toJson(o));
      }
      List<Payer> payers = new ArrayList<>(PayerManager.getAllPayers());
      payers.add(PayerManager.getNoInsurancePlan().getPayer());
      payers.sort(Comparator.comparing(Payer::getName));
      JsonArray stats = new JsonArray();
      for (Payer payer : payers) {
        stats.add(CanonicalCoverage.payerStats(payer));
      }
      JsonObject tail = new JsonObject();
      tail.add("payers", stats);
      w.println(GSON.toJson(tail));
    }
  }
}
