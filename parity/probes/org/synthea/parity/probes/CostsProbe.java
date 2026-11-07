package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import org.mitre.synthea.helpers.SimpleCSV;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.world.agents.PayerManager;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.Claim;
import org.mitre.synthea.world.concepts.Costs;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.HealthRecord.Code;
import org.mitre.synthea.world.concepts.HealthRecord.Device;
import org.mitre.synthea.world.concepts.HealthRecord.Encounter;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;
import org.mitre.synthea.world.concepts.HealthRecord.Entry;
import org.mitre.synthea.world.concepts.HealthRecord.Immunization;
import org.mitre.synthea.world.concepts.HealthRecord.Medication;
import org.mitre.synthea.world.concepts.HealthRecord.Observation;
import org.mitre.synthea.world.concepts.HealthRecord.Procedure;
import org.mitre.synthea.world.concepts.HealthRecord.Report;
import org.mitre.synthea.world.concepts.HealthRecord.Supply;
import org.mitre.synthea.world.concepts.healthinsurance.PlanRecord;

/**
 * T14 probe: seeded cost lookups across every cost CSV, code type and several
 * states, plus claim assembly for scripted encounters under the no-insurance
 * plan (the only plan path T14 exercises; Payer/InsurancePlan are T15).
 *
 * <p>Every person is enrolled in no-insurance at their birthdate before any
 * entry is built, because building a Medication builds its Claim, and the
 * Claim constructor requires a plan record at the entry time. Entry times
 * sit 30 days after the birthdate, inside the first plan record's year.
 *
 * <p>The Python mirror is tests/parity/test_costs.py; it replays this file
 * step for step so the per-person RNG streams stay aligned (each emitted
 * line carries the person's draw count after the call).
 */
public class CostsProbe {

  private static final long BIRTHDATE = 946684800000L; // 2000-01-01T00:00:00Z
  private static final long TIME = BIRTHDATE + 30L * 86400000L;
  private static final String[] STATES = {"Massachusetts", "California", "Texas", "Wyoming"};
  private static final long[] SEEDS = {42L, 12345L};
  private static final int STRIDE = 53;

  private static void emit(PrintWriter w, String kase, String out) {
    JsonObject o = new JsonObject();
    o.addProperty("case", kase);
    o.addProperty("out", out);
    w.println(o.toString());
  }

  /** One cost-CSV row: its CODE and its COMMENTS (used as the code display). */
  private record CostRow(String code, String display) {}

  private static List<CostRow> costRows(String resource) throws Exception {
    String raw = Utilities.readResourceAndStripBOM(resource);
    List<CostRow> rows = new ArrayList<>();
    for (LinkedHashMap<String, String> line : SimpleCSV.parse(raw)) {
      rows.add(new CostRow(line.get("CODE"), line.get("COMMENTS")));
    }
    return rows;
  }

  private static Person newPerson(long seed, String state) {
    Person person = new Person(seed);
    person.attributes.put(Person.BIRTHDATE, BIRTHDATE);
    if (state != null) {
      person.attributes.put(Person.STATE, state);
    }
    person.coverage.setPlanToNoInsurance(BIRTHDATE);
    return person;
  }

  private static List<Integer> indices(int size, boolean full) {
    List<Integer> idx = new ArrayList<>();
    if (full) {
      for (int i = 0; i < size; i++) {
        idx.add(i);
      }
    } else {
      for (int i = 0; i < size; i += STRIDE) {
        idx.add(i);
      }
      if (idx.get(idx.size() - 1) != size - 1) {
        idx.add(size - 1);
      }
    }
    return idx;
  }

  private static String lookup(String tag, Entry entry, Person person) {
    double cost = Costs.determineCostOfEntry(entry, person);
    return tag + " -> " + Double.toString(cost) + " count=" + person.getCount();
  }

  public static void main(String[] args) throws Exception {
    PayerManager.loadNoInsurance();
    List<CostRow> procedures = costRows("costs/procedures.csv");
    List<CostRow> medications = costRows("costs/medications.csv");
    List<CostRow> encounters = costRows("costs/encounters.csv");
    List<CostRow> devices = costRows("costs/devices.csv");
    List<CostRow> supplies = costRows("costs/supplies.csv");

    Path out = Path.of(args[0]);
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("costs.jsonl"), StandardCharsets.UTF_8))) {
      for (String state : STATES) {
        for (long seed : SEEDS) {
          boolean full = (state.equals("Massachusetts") && seed == 42L)
              || (state.equals("Texas") && seed == 12345L);
          emit(w, "lookups:" + state + ":" + seed,
              lookupsCase(state, seed, full, procedures, medications, encounters, devices,
                  supplies));
        }
      }
      emit(w, "nostate:42", noStateCase(procedures, medications, encounters, devices, supplies));
      emit(w, "nullperson", nullPersonCase());
      emit(w, "claims:encounter", claimEncounterCase(procedures, encounters, devices, supplies));
      emit(w, "claims:medication", claimMedicationCase(procedures, medications));
      emit(w, "claims:medicationclaim", claimMedicationClaimCase(medications));
      emit(w, "claims:dead", claimDeadCase(procedures, encounters));
    }
  }

  private static String lookupsCase(String state, long seed, boolean full,
      List<CostRow> procedures, List<CostRow> medications, List<CostRow> encounters,
      List<CostRow> devices, List<CostRow> supplies) {
    Person person = newPerson(seed, state);
    HealthRecord record = person.record;
    StringBuilder sb = new StringBuilder();
    sb.append("state=").append(state).append(" seed=").append(seed)
        .append(" full=").append(full);

    for (int i : indices(procedures.size(), full)) {
      CostRow row = procedures.get(i);
      Procedure entry = record.new Procedure(TIME, "procedure");
      entry.codes.add(new Code("SNOMED-CT", row.code(), row.display()));
      sb.append("\n").append(lookup("P " + row.code(), entry, person));
    }
    for (int i : indices(medications.size(), full)) {
      CostRow row = medications.get(i);
      Medication entry = record.new Medication(TIME, "medication");
      entry.codes.add(new Code("RxNorm", row.code(), row.display()));
      sb.append("\n").append(lookup("M " + row.code(), entry, person));
    }
    EncounterType[] types = EncounterType.values();
    for (int i : indices(encounters.size(), full)) {
      CostRow row = encounters.get(i);
      Encounter entry = record.new Encounter(TIME, types[i % types.length].toString());
      entry.codes.add(new Code("SNOMED-CT", row.code(), row.display()));
      sb.append("\n").append(lookup("E " + row.code(), entry, person));
    }
    for (int i : indices(devices.size(), full)) {
      CostRow row = devices.get(i);
      Device entry = record.new Device(TIME, "device");
      entry.codes.add(new Code("SNOMED-CT", row.code(), row.display()));
      sb.append("\n").append(lookup("D " + row.code(), entry, person));
    }
    for (int i : indices(supplies.size(), full)) {
      CostRow row = supplies.get(i);
      Supply entry = record.new Supply(TIME, "supply");
      entry.codes.add(new Code("SNOMED-CT", row.code(), row.display()));
      sb.append("\n").append(lookup("S " + row.code(), entry, person));
    }

    // Unknown codes: the default cost for the type, still location-adjusted.
    Procedure unknownProc = record.new Procedure(TIME, "procedure");
    unknownProc.codes.add(new Code("SNOMED-CT", "999999999", "Unknown procedure"));
    sb.append("\n").append(lookup("X P unknown", unknownProc, person));
    Medication unknownMed = record.new Medication(TIME, "medication");
    unknownMed.codes.add(new Code("RxNorm", "999999999", "Unknown medication"));
    sb.append("\n").append(lookup("X M unknown", unknownMed, person));
    Encounter unknownEnc = record.new Encounter(TIME, "wellness");
    unknownEnc.codes.add(new Code("SNOMED-CT", "999999999", "Unknown encounter"));
    sb.append("\n").append(lookup("X E unknown", unknownEnc, person));
    Immunization unknownImm = record.new Immunization(TIME, "immunization");
    unknownImm.codes.add(new Code("CVX", "999999999", "Unknown immunization"));
    sb.append("\n").append(lookup("X I unknown", unknownImm, person));
    Device unknownDev = record.new Device(TIME, "device");
    unknownDev.codes.add(new Code("SNOMED-CT", "999999999", "Unknown device"));
    sb.append("\n").append(lookup("X D unknown", unknownDev, person));
    Supply unknownSup = record.new Supply(TIME, "supply");
    unknownSup.codes.add(new Code("SNOMED-CT", "999999999", "Unknown supply"));
    sb.append("\n").append(lookup("X S unknown", unknownSup, person));

    // No codes at all: default cost for the type, location-adjusted.
    sb.append("\n").append(lookup("X P empty", record.new Procedure(TIME, "procedure"), person));
    sb.append("\n").append(lookup("X M empty", record.new Medication(TIME, "medication"), person));
    sb.append("\n").append(lookup("X E empty", record.new Encounter(TIME, "wellness"), person));
    sb.append("\n").append(lookup("X I empty",
        record.new Immunization(TIME, "immunization"), person));
    sb.append("\n").append(lookup("X D empty", record.new Device(TIME, "device"), person));
    sb.append("\n").append(lookup("X S empty", record.new Supply(TIME, "supply"), person));

    // Dialysis procedures draw from the dialysis adjustment table, keyed on
    // any code display containing "dialysis", case-insensitively.
    String[] dialysisDisplays = {"Dialysis", "DIALYSIS TREATMENT", "hemodialysis session"};
    for (int i = 0; i < dialysisDisplays.length; i++) {
      Procedure entry = record.new Procedure(TIME, "procedure");
      entry.codes.add(new Code("SNOMED-CT", procedures.get(0).code(), dialysisDisplays[i]));
      sb.append("\n").append(lookup("X P dialysis" + i, entry, person));
    }

    // Medication quantity variants for the first medication code.
    CostRow firstMed = medications.get(0);
    Medication administered = record.new Medication(TIME, "medication");
    administered.codes.add(new Code("RxNorm", firstMed.code(), firstMed.display()));
    administered.administration = true;
    sb.append("\n").append(lookup("X M admin", administered, person));
    Medication detailed = record.new Medication(TIME, "medication");
    detailed.codes.add(new Code("RxNorm", firstMed.code(), firstMed.display()));
    JsonObject details = new JsonObject();
    JsonObject dosage = new JsonObject();
    dosage.addProperty("amount", 2);
    dosage.addProperty("frequency", 3);
    dosage.addProperty("period", 1);
    dosage.addProperty("unit", "days");
    details.add("dosage", dosage);
    JsonObject duration = new JsonObject();
    duration.addProperty("quantity", 2);
    duration.addProperty("unit", "months");
    details.add("duration", duration);
    detailed.prescriptionDetails = details;
    sb.append("\n").append(lookup("X M details", detailed, person));

    // Reports have no cost table: always the default lab cost, adjusted.
    Report reportWithCode = record.new Report(TIME, "laboratory", new ArrayList<>());
    reportWithCode.codes.add(new Code("LOINC", "123456", "Some lab panel"));
    sb.append("\n").append(lookup("X R code", reportWithCode, person));
    sb.append("\n").append(lookup("X R empty",
        record.new Report(TIME, "laboratory", new ArrayList<>()), person));

    // Observations are not a costed entry type.
    Observation observation = record.new Observation(TIME, "vital-signs", 1.0);
    sb.append("\n").append(lookup("X O", observation, person));

    sb.append("\nhasCost P=").append(Costs.hasCost(unknownProc))
        .append(" M=").append(Costs.hasCost(unknownMed))
        .append(" E=").append(Costs.hasCost(unknownEnc))
        .append(" I=").append(Costs.hasCost(unknownImm))
        .append(" D=").append(Costs.hasCost(unknownDev))
        .append(" S=").append(Costs.hasCost(unknownSup))
        .append(" R=").append(Costs.hasCost(reportWithCode))
        .append(" O=").append(Costs.hasCost(observation));
    sb.append("\nhasSpecifiedCost ").append(procedures.get(0).code())
        .append("=").append(Costs.hasSpecifiedCost(procedures.get(0).code()));
    sb.append("\nhasSpecifiedCost ").append(medications.get(0).code())
        .append("=").append(Costs.hasSpecifiedCost(medications.get(0).code()));
    sb.append("\nhasSpecifiedCost ").append(encounters.get(0).code())
        .append("=").append(Costs.hasSpecifiedCost(encounters.get(0).code()));
    sb.append("\nhasSpecifiedCost ").append(devices.get(0).code())
        .append("=").append(Costs.hasSpecifiedCost(devices.get(0).code()));
    sb.append("\nhasSpecifiedCost ").append(supplies.get(0).code())
        .append("=").append(Costs.hasSpecifiedCost(supplies.get(0).code()));
    sb.append("\nhasSpecifiedCost 999999999=").append(Costs.hasSpecifiedCost("999999999"));
    return sb.toString();
  }

  private static String noStateCase(List<CostRow> procedures, List<CostRow> medications,
      List<CostRow> encounters, List<CostRow> devices, List<CostRow> supplies) {
    Person person = newPerson(42L, null);
    HealthRecord record = person.record;
    StringBuilder sb = new StringBuilder();
    sb.append("state=null seed=42");
    for (int i : indices(procedures.size(), false)) {
      CostRow row = procedures.get(i);
      Procedure entry = record.new Procedure(TIME, "procedure");
      entry.codes.add(new Code("SNOMED-CT", row.code(), row.display()));
      sb.append("\n").append(lookup("P " + row.code(), entry, person));
    }
    for (int i : indices(medications.size(), false)) {
      CostRow row = medications.get(i);
      Medication entry = record.new Medication(TIME, "medication");
      entry.codes.add(new Code("RxNorm", row.code(), row.display()));
      sb.append("\n").append(lookup("M " + row.code(), entry, person));
    }
    Procedure unknownProc = record.new Procedure(TIME, "procedure");
    unknownProc.codes.add(new Code("SNOMED-CT", "999999999", "Unknown procedure"));
    sb.append("\n").append(lookup("X P unknown", unknownProc, person));
    sb.append("\n").append(lookup("X P empty", record.new Procedure(TIME, "procedure"), person));
    sb.append("\n").append(lookup("X E empty", record.new Encounter(TIME, "wellness"), person));
    sb.append("\n").append(lookup("X R empty",
        record.new Report(TIME, "laboratory", new ArrayList<>()), person));
    return sb.toString();
  }

  private static String nullPersonCase() {
    // Entries still need an owning record (their uuid is drawn from its
    // person), but the cost calls themselves pass a null person: only paths
    // that never sample a cost distribution are safe, and all must use the
    // unadjusted (1.0) location factor.
    Person scratch = newPerson(7L, "Massachusetts");
    HealthRecord record = scratch.record;
    StringBuilder sb = new StringBuilder();
    sb.append("person=null");
    Procedure unknownProc = record.new Procedure(TIME, "procedure");
    unknownProc.codes.add(new Code("SNOMED-CT", "999999999", "Unknown procedure"));
    sb.append("\nNP P unknown -> ")
        .append(Double.toString(Costs.determineCostOfEntry(unknownProc, null)));
    sb.append("\nNP P empty -> ").append(Double.toString(
        Costs.determineCostOfEntry(record.new Procedure(TIME, "procedure"), null)));
    sb.append("\nNP E empty -> ").append(Double.toString(
        Costs.determineCostOfEntry(record.new Encounter(TIME, "wellness"), null)));
    Report report = record.new Report(TIME, "laboratory", new ArrayList<>());
    report.codes.add(new Code("LOINC", "123456", "Some lab panel"));
    sb.append("\nNP R code -> ")
        .append(Double.toString(Costs.determineCostOfEntry(report, null)));
    return sb.toString();
  }

  private static void dumpClaimEntry(StringBuilder sb, String label, Claim.ClaimEntry entry) {
    sb.append("\n").append(label)
        .append(" cost=").append(entry.cost)
        .append(" copay=").append(entry.copayPaidByPatient)
        .append(" deductible=").append(entry.deductiblePaidByPatient)
        .append(" adjustment=").append(entry.adjustment)
        .append(" coinsurance=").append(entry.coinsurancePaidByPayer)
        .append(" paid=").append(entry.paidByPayer)
        .append(" secondaryPaid=").append(entry.paidBySecondaryPayer)
        .append(" oop=").append(entry.patientOutOfPocket)
        .append(" patientCost=").append(entry.getPatientCost())
        .append(" coveredCost=").append(entry.getCoveredCost())
        .append(" coinsurancePaid=").append(entry.getCoinsurancePaid());
  }

  private static String dumpClaim(Person person, Claim claim) {
    StringBuilder sb = new StringBuilder();
    sb.append("uuid=").append(claim.uuid);
    sb.append("\npayer=").append(claim.getPayer().getName())
        .append(" secondary=").append(claim.getSecondaryPayer().getName())
        .append(" medicare=").append(claim.coveredByMedicare())
        .append(" memberId=").append(claim.getPlanRecordMemberId());
    dumpClaimEntry(sb, "main", claim.mainEntry);
    for (int i = 0; i < claim.items.size(); i++) {
      dumpClaimEntry(sb, "item" + i, claim.items.get(i));
    }
    dumpClaimEntry(sb, "totals", claim.totals);
    sb.append("\ngetters totalClaim=").append(claim.getTotalClaimCost())
        .append(" totalCovered=").append(claim.getTotalCoveredCost())
        .append(" totalDeductible=").append(claim.getTotalDeductiblePaid())
        .append(" totalCopay=").append(claim.getTotalCopayPaid())
        .append(" totalSecondary=").append(claim.getTotalPaidBySecondaryPayer())
        .append(" totalAdjustment=").append(claim.getTotalAdjustment())
        .append(" totalCoinsurance=").append(claim.getTotalCoinsurancePaid())
        .append(" totalPatient=").append(claim.getTotalPatientCost());
    PlanRecord planRecord = person.coverage.getPlanRecordAtTime(TIME);
    sb.append("\nplan oop=").append(planRecord.getOutOfPocketExpenses())
        .append(" covered=").append(planRecord.getCoveredExpenses())
        .append(" insurance=").append(planRecord.getInsuranceExpenses())
        .append(" remainingDeductible=").append(planRecord.remainingDeductible);
    sb.append("\ncount=").append(person.getCount());
    return sb.toString();
  }

  private static String claimEncounterCase(List<CostRow> procedures, List<CostRow> encounters,
      List<CostRow> devices, List<CostRow> supplies) {
    Person person = newPerson(4242L, "Massachusetts");
    HealthRecord record = person.record;
    Encounter encounter = record.new Encounter(TIME, "wellness");
    encounter.codes.add(new Code("SNOMED-CT", encounters.get(0).code(),
        encounters.get(0).display()));
    Claim claim = new Claim(encounter, person);
    Procedure procedure = record.new Procedure(TIME, "procedure");
    procedure.codes.add(new Code("SNOMED-CT", procedures.get(0).code(),
        procedures.get(0).display()));
    claim.addLineItem(procedure);
    Immunization immunization = record.new Immunization(TIME, "immunization");
    immunization.codes.add(new Code("CVX", "90732", "Pneumococcal vaccine"));
    claim.addLineItem(immunization);
    Device device = record.new Device(TIME, "device");
    device.codes.add(new Code("SNOMED-CT", devices.get(0).code(), devices.get(0).display()));
    claim.addLineItem(device);
    Supply supply = record.new Supply(TIME, "supply");
    supply.codes.add(new Code("SNOMED-CT", supplies.get(0).code(), supplies.get(0).display()));
    claim.addLineItem(supply);
    Report report = record.new Report(TIME, "laboratory", new ArrayList<>());
    report.codes.add(new Code("LOINC", "123456", "Some lab panel"));
    claim.addLineItem(report);
    Procedure unknown = record.new Procedure(TIME, "procedure");
    unknown.codes.add(new Code("SNOMED-CT", "999999999", "Unknown procedure"));
    claim.addLineItem(unknown);
    claim.assignCosts();
    return "claim=encounter seed=4242\n" + dumpClaim(person, claim);
  }

  private static String claimMedicationCase(List<CostRow> procedures, List<CostRow> medications) {
    Person person = newPerson(777L, "Massachusetts");
    HealthRecord record = person.record;
    Medication medication = record.new Medication(TIME, "medication");
    medication.codes.add(new Code("RxNorm", medications.get(0).code(),
        medications.get(0).display()));
    Claim claim = new Claim(medication, person);
    Procedure procedure = record.new Procedure(TIME, "procedure");
    procedure.codes.add(new Code("SNOMED-CT", procedures.get(0).code(),
        procedures.get(0).display()));
    claim.addLineItem(procedure);
    claim.assignCosts();
    return "claim=medication seed=777\n" + dumpClaim(person, claim);
  }

  private static String claimMedicationClaimCase(List<CostRow> medications) {
    Person person = newPerson(778L, "Massachusetts");
    HealthRecord record = person.record;
    Medication medication = record.new Medication(TIME, "medication");
    medication.codes.add(new Code("RxNorm", medications.get(0).code(),
        medications.get(0).display()));
    medication.claim.assignCosts();
    return "claim=medicationclaim seed=778\n" + dumpClaim(person, medication.claim);
  }

  private static String claimDeadCase(List<CostRow> procedures, List<CostRow> encounters) {
    Person person = newPerson(999L, "Massachusetts");
    person.attributes.put(Person.DEATHDATE, TIME - 1000L);
    HealthRecord record = person.record;
    Encounter encounter = record.new Encounter(TIME, "emergency");
    encounter.codes.add(new Code("SNOMED-CT", encounters.get(1).code(),
        encounters.get(1).display()));
    Claim claim = new Claim(encounter, person);
    Procedure procedure = record.new Procedure(TIME, "procedure");
    procedure.codes.add(new Code("SNOMED-CT", procedures.get(0).code(),
        procedures.get(0).display()));
    claim.addLineItem(procedure);
    claim.assignCosts();
    return "claim=dead seed=999\n" + dumpClaim(person, claim);
  }
}
