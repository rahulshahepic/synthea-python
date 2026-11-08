package org.synthea.parity.probes;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.modules.covid.C19ImmunizationModule;
import org.mitre.synthea.modules.covid.C19ImmunizationModule.VaccinationStatus;
import org.mitre.synthea.modules.covid.C19Vaccine;
import org.mitre.synthea.modules.covid.C19VaccineAgeDistributions;
import org.mitre.synthea.modules.covid.C19VaccineAgeDistributions.AgeRange;
import org.mitre.synthea.modules.covid.LateAdopterModel;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.agents.Provider;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.geography.Location;

/**
 * Probe for T24 (COVID-19 immunization modules).
 *
 * Sections, in order: module constants; AgeRange parsing/equality;
 * the EUA table; first-shot probabilities by age; shot-time sampling;
 * vaccine selection (C19Vaccine.selectShot and
 * C19ImmunizationModule.selectVaccine); LateAdopterModel trajectories;
 * eligibility and decideOnShot matrices; and full module runs: 200
 * seeded persons of all ages (0-99), stepped weekly from 2020-12-04
 * through 2025-12-31, dumping every vaccination-status transition,
 * the final attribute snapshot, the COVID immunization history and
 * every recorded immunization.
 */
public class CovidProbe {

  static final long START = LocalDateTime.of(2020, 12, 4, 12, 0)
      .toInstant(ZoneOffset.UTC).toEpochMilli();
  static final long END = LocalDateTime.of(2025, 12, 31, 12, 0)
      .toInstant(ZoneOffset.UTC).toEpochMilli();
  static final long WEEK = 7L * 24 * 3600 * 1000;
  static final long JUNE_2021 = LocalDateTime.of(2021, 6, 1, 12, 0)
      .toInstant(ZoneOffset.UTC).toEpochMilli();
  static final int SEEDS = 200;
  static final String[] DISPLAYS = {
    "Ages_12-15_yrs", "Ages_16-17_yrs", "Ages_18-29_yrs", "Ages_30-39_yrs",
    "Ages_40-49_yrs", "Ages_50-64_yrs", "Ages_65-74_yrs", "Ages_75+_yrs"
  };

  public static void main(String[] args) throws Exception {
    Path outDir = Path.of(args[0]);
    Files.createDirectories(outDir);
    List<String> lines = new ArrayList<>();

    lines.add("C|FIRST=" + C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME
        + "|MODERNA=" + C19ImmunizationModule.MODERNA_APPROVED
        + "|JANSSEN=" + C19ImmunizationModule.JANSSEN_APPROVED
        + "|EXPAND=" + C19ImmunizationModule.EXPAND_AGE_TO_TWELVE
        + "|LATE=" + C19ImmunizationModule.LATE_ADOPTION_START_TIME);

    int[] inAges = {0, 11, 12, 15, 16, 17, 29, 39, 49, 64, 74, 75, 100};
    for (String display : DISPLAYS) {
      AgeRange range = new AgeRange(display);
      StringBuilder in = new StringBuilder();
      for (int age : inAges) {
        in.append(range.in(age) ? "1" : "0");
      }
      lines.add("AR|" + display + "|" + range.min + "|" + range.max + "|"
          + range.hashCode() + "|" + in + "|eqSame=" + range.equals(new AgeRange(display))
          + "|eqOther=" + range.equals(new AgeRange("Ages_18-29_yrs"))
          + "|eqNull=" + range.equals(null));
    }
    try {
      new AgeRange("Ages_5-9_yrs");
      lines.add("AR|bad|no-error");
    } catch (IllegalArgumentException e) {
      lines.add("AR|bad|ERROR|IllegalArgumentException");
    }

    C19ImmunizationModule module = new C19ImmunizationModule();
    lines.add("M|" + module.name);
    for (Map.Entry<C19Vaccine.EUASet, C19Vaccine> entry : C19Vaccine.EUAs.entrySet()) {
      C19Vaccine vaccine = entry.getValue();
      lines.add("EUA|" + entry.getKey().name() + "|" + vaccine.getDisplay() + "|"
          + vaccine.getCvx() + "|" + vaccine.isTwoDose() + "|"
          + Double.toString(vaccine.getUsagePercentage()) + "|" + vaccine.getTimeBetweenDoses());
    }

    int[] probAges = {0, 5, 11, 12, 13, 15, 16, 17, 18, 25, 29, 30, 39, 40, 49, 50, 64, 65, 74,
      75, 90, 120};
    for (int age : probAges) {
      Person person = agedPerson(1000 + age, age);
      try {
        double chance = C19VaccineAgeDistributions.chanceOfGettingShot(person, JUNE_2021);
        lines.add("PROB|" + age + "|" + Double.toString(chance));
      } catch (RuntimeException e) {
        lines.add("PROB|" + age + "|ERROR|" + e.getClass().getSimpleName());
      }
    }

    int[] shotAges = {12, 14, 16, 17, 20, 29, 35, 45, 55, 70, 80, 95};
    for (int age : shotAges) {
      for (int k = 0; k < 10; k++) {
        Person person = agedPerson(777000 + age * 100 + k, age);
        try {
          long shotTime = C19VaccineAgeDistributions.selectShotTime(person, JUNE_2021);
          lines.add("ST|" + age + "|" + k + "|" + shotTime);
        } catch (RuntimeException e) {
          lines.add("ST|" + age + "|" + k + "|ERROR|" + e.getClass().getSimpleName());
        }
      }
    }

    for (int k = 0; k < 100; k++) {
      Person person = agedPerson(555000 + k, 40);
      lines.add("SS|" + k + "|" + C19Vaccine.selectShot(person).name());
    }

    long[] vaccineTimes = {
      C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME - 1,
      C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME,
      C19ImmunizationModule.MODERNA_APPROVED - 1,
      C19ImmunizationModule.MODERNA_APPROVED,
      C19ImmunizationModule.JANSSEN_APPROVED,
      C19ImmunizationModule.JANSSEN_APPROVED + 1,
      JUNE_2021
    };
    String[] vaccineTimeLabels = {"FIRST-1", "FIRST", "MODERNA-1", "MODERNA", "JANSSEN",
      "JANSSEN+1", "JUNE2021"};
    for (int t = 0; t < vaccineTimes.length; t++) {
      for (int k = 0; k < 20; k++) {
        Person person = agedPerson(444000 + t * 100 + k, 40);
        try {
          lines.add("SV|" + vaccineTimeLabels[t] + "|" + k + "|"
              + C19ImmunizationModule.selectVaccine(person, vaccineTimes[t]).name());
        } catch (RuntimeException e) {
          lines.add("SV|" + vaccineTimeLabels[t] + "|" + k + "|ERROR|"
              + e.getClass().getSimpleName());
        }
      }
    }

    long lateStart = C19ImmunizationModule.LATE_ADOPTION_START_TIME;
    int[] lateAges = {10, 15, 16, 40, 41, 70};
    for (int age : lateAges) {
      Person person = agedPersonAt(333000 + age, age, lateStart);
      LateAdopterModel model = new LateAdopterModel(person, lateStart);
      lines.add("LA|" + age + "|init|" + Double.toString(model.getChanceOfGettingShot())
          + "|" + model.getLastUpdated());
      long time = lateStart;
      for (int step = 0; step < 40; step++) {
        time += WEEK;
        boolean will = model.willGetShot(person, time);
        lines.add("LA|" + age + "|" + step + "|" + time + "|" + will + "|"
            + Double.toString(model.getChanceOfGettingShot()) + "|" + model.isNotGettingShot());
        if (will || model.isNotGettingShot()) {
          break;
        }
      }
    }

    long[] eligTimes = {
      C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME - 1,
      C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME,
      C19ImmunizationModule.EXPAND_AGE_TO_TWELVE - 1,
      C19ImmunizationModule.EXPAND_AGE_TO_TWELVE,
      LocalDateTime.of(2022, 1, 1, 12, 0).toInstant(ZoneOffset.UTC).toEpochMilli()
    };
    String[] eligLabels = {"FIRST-1", "FIRST", "EXPAND-1", "EXPAND", "Y2022"};
    int[] eligAges = {0, 11, 12, 15, 16, 17, 65};
    for (int age : eligAges) {
      for (int t = 0; t < eligTimes.length; t++) {
        Person person = agedPersonAt(888000 + age, age, eligTimes[t]);
        lines.add("EL|" + age + "|" + eligLabels[t] + "|"
            + C19ImmunizationModule.eligibleForShot(person, eligTimes[t]));
      }
    }

    int[] decideAges = {12, 16, 20, 35, 50, 70, 85};
    for (int age : decideAges) {
      for (int k = 0; k < 20; k++) {
        Person person = agedPerson(222000 + age * 100 + k, age);
        lines.add("DC|" + age + "|" + k + "|"
            + C19ImmunizationModule.decideOnShot(person, JUNE_2021));
      }
    }

    // Runtime setup for the process runs, mirroring the Generator:
    // providers loaded for Massachusetts and the no-insurance payer, so
    // vaccinate() can create real encounters and end them (costs and
    // claim assignment read the person's coverage).
    Provider.loadProviders(new Location("Massachusetts", "Boston"),
        new DefaultRandomNumberGenerator(12345L));
    PayerManager.loadNoInsurance();

    for (int seed = 0; seed < SEEDS; seed++) {
      runPerson(lines, module, seed);
    }

    Files.write(outDir.resolve("run.txt"), lines, StandardCharsets.UTF_8);
  }

  static Person agedPerson(int seed, int age) {
    return agedPersonAt(seed, age, JUNE_2021);
  }

  static Person agedPersonAt(int seed, int age, long time) {
    Person person = new Person(seed);
    LocalDate date = LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(time),
        ZoneOffset.UTC).toLocalDate();
    long birthdate = date.minusYears(age).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
    person.attributes.put(Person.BIRTHDATE, birthdate);
    return person;
  }

  static String snapshot(Person person) {
    VaccinationStatus status = (VaccinationStatus) person.attributes
        .get(C19ImmunizationModule.C19_VACCINE_STATUS);
    C19Vaccine.EUASet vaccine = (C19Vaccine.EUASet) person.attributes
        .get(C19ImmunizationModule.C19_VACCINE);
    Object first = person.attributes.get(C19ImmunizationModule.C19_SCHEDULED_FIRST_SHOT);
    Object second = person.attributes.get(C19ImmunizationModule.C19_SCHEDULED_SECOND_SHOT);
    Object fully = person.attributes.get(C19ImmunizationModule.C19_FULLY_VACCINATED);
    LateAdopterModel model = (LateAdopterModel) person.attributes
        .get(C19ImmunizationModule.C19_LATE_ADOPTER_MODEL);
    return "status=" + (status == null ? "null" : status.name())
        + "|vaccine=" + (vaccine == null ? "null" : vaccine.name())
        + "|first=" + (first == null ? "null" : first.toString())
        + "|second=" + (second == null ? "null" : second.toString())
        + "|fully=" + (fully == null ? "null" : fully.toString())
        + "|late=" + (model == null ? "null"
            : Double.toString(model.getChanceOfGettingShot()) + "," + model.getLastUpdated());
  }

  static void runPerson(List<String> lines, C19ImmunizationModule module, int seed) {
    int age = seed % 100;
    Person person = new Person(seed);
    long birthdate = LocalDate.of(2021, 1, 1).minusYears(age)
        .atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
    person.attributes.put(Person.BIRTHDATE, birthdate);
    person.attributes.put(Person.COORDINATE, new java.awt.geom.Point2D.Double(-71.0589, 42.3601));
    person.coverage.setPlanToNoInsurance(birthdate);
    long years = (END - birthdate) / Utilities.convertTime("years", 1) + 2;
    for (long i = 1; i <= years; i++) {
      person.coverage.newEnrollmentPeriod(birthdate + Utilities.convertTime("years", i));
    }
    person.coverage.setPlanToNoInsurance(START);
    try {
      String previous = snapshot(person);
      for (long time = START; time <= END; time += WEEK) {
        module.process(person, time);
        String current = snapshot(person);
        if (!current.equals(previous)) {
          lines.add("T|" + seed + "|" + time + "|" + current);
          previous = current;
        }
      }
      @SuppressWarnings("unchecked")
      Map<String, List<Long>> history = (Map<String, List<Long>>) person.attributes
          .get(org.mitre.synthea.modules.Immunizations.IMMUNIZATIONS);
      List<Long> covidHistory = history == null ? null
          : history.get(C19ImmunizationModule.C19_PERSON_ATTRS_KEY);
      StringBuilder hist = new StringBuilder();
      if (covidHistory == null) {
        hist.append("null");
      } else {
        for (int i = 0; i < covidHistory.size(); i++) {
          if (i > 0) {
            hist.append(",");
          }
          hist.append(covidHistory.get(i));
        }
      }
      lines.add("F|" + seed + "|" + snapshot(person) + "|hist=" + hist
          + "|encs=" + person.record.encounters.size());
      for (HealthRecord.Encounter encounter : person.record.encounters) {
        for (HealthRecord.Immunization imm : encounter.immunizations) {
          StringBuilder codes = new StringBuilder();
          for (int i = 0; i < imm.codes.size(); i++) {
            if (i > 0) {
              codes.append(";");
            }
            HealthRecord.Code code = imm.codes.get(i);
            codes.append(code.system).append(",").append(code.code).append(",")
                .append(code.display);
          }
          lines.add("I|" + seed + "|" + imm.start + "|" + imm.series + "|" + codes);
        }
      }
    } catch (RuntimeException e) {
      lines.add("P|" + seed + "|ERROR|" + e.getClass().getSimpleName());
    }
  }
}
