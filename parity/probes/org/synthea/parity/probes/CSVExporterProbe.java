package org.synthea.parity.probes;

import java.awt.geom.Point2D;
import java.lang.reflect.*;
import java.math.BigDecimal;
import java.nio.file.*;
import java.util.*;
import org.mitre.synthea.export.CSVExporter;
import org.mitre.synthea.export.CSVConstants;
import org.mitre.synthea.helpers.*;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.concepts.HealthRecord.*;
import org.mitre.synthea.world.concepts.healthinsurance.*;

/** T26 integration: 32 scripted real persons, all resource rows and transaction branches. */
public class CSVExporterProbe {
  static final long BIRTH = -631152000000L; // 1950-01-01
  static final long TIME = 1577836800000L; // 2020-01-01
  static BigDecimal d(String s) { return new BigDecimal(s); }
  static void field(Object obj, String name, Object value) throws Exception {
    Class<?> cls = obj.getClass();
    while (cls != null) {
      try { Field f = cls.getDeclaredField(name); f.setAccessible(true); f.set(obj, value); return; }
      catch (NoSuchFieldException e) { cls = cls.getSuperclass(); }
    }
    throw new NoSuchFieldException(name);
  }
  static void call(CSVExporter exporter, String name, Class<?>[] types, Object... args) throws Exception {
    Method m = CSVExporter.class.getDeclaredMethod(name, types); m.setAccessible(true); m.invoke(exporter, args);
  }
  static Code code(String code) { return new Code("SNOMED-CT", code, " Display,with\r\ncommas "); }
  static void entry(Entry e, String code, int i) throws Exception {
    e.codes.add(code(code)); e.stop = i % 2 == 0 ? 0L : e.start + 60000L;
    field(e, "cost", d("123.45"));
  }
  static InsurancePlan plan(Payer payer, int id) {
    InsurancePlan plan = new InsurancePlan(id, payer, new HashSet<>(List.of("*")), d("0.00"),
        d("0.80"), d("10.00"), d("20.00"), d("8700.00"), false, false, false,
        1900, 2100, 1, "GENERIC");
    payer.addPlan(plan); return plan;
  }
  static void costs(Claim claim, int i) {
    for (Claim.ClaimEntry e : claim.items) { e.cost = d("123.45"); }
    Claim.ClaimEntry e = claim.mainEntry;
    e.cost = d("123.45");
    if (i % 4 != 0) {
      e.copayPaidByPatient = d(i % 7 == 0 ? "150.00" : "10.00");
      e.adjustment = d(i % 7 == 1 ? "150.00" : "3.45");
      e.paidByPayer = d("40.00"); e.coinsurancePaidByPayer = d("10.00");
      if (i % 4 == 2) { e.paidBySecondaryPayer = d("20.00"); }
    }
    claim.totals.reset(); claim.totals.addCosts(e);
    for (Claim.ClaimEntry item : claim.items) { claim.totals.addCosts(item); }
  }
  public static void main(String[] args) throws Exception {
    Config.set("exporter.baseDirectory", args[0]);
    Config.set("exporter.csv.folder_per_run", "false");
    Config.set("exporter.csv.append_mode", "false");
    Config.set("exporter.csv.included_files", ""); Config.set("exporter.csv.excluded_files", "");
    Config.set("exporter.csv.max_lines_per_file", "0"); Config.set("exporter.years_of_history", "0");
    PayerManager.clear(); PayerManager.loadNoInsurance();
    Payer primary = new Payer("Scripted Primary", 701, new HashSet<>(List.of("*")), "PRIVATE");
    Payer secondary = new Payer("Scripted Secondary", 702, new HashSet<>(List.of("*")), "PRIVATE");
    InsurancePlan plan = plan(primary, 701), supplement = plan(secondary, 702);
    Provider org = new Provider(); org.uuid = "scripted-organization";
    org.name = " Hospital,Name "; org.address = " Road\r\nName "; org.city = "Boston";
    org.state = "MA"; org.zip = "02110"; org.phone = "123"; org.npi = "1234567893";
    org.addRevenue(1234.5);
    Clinician clinician = new Clinician(42L, new DefaultRandomNumberGenerator(42L), 123L, org);
    clinician.attributes.put(Clinician.NAME, " Doctor,Name "); clinician.attributes.put(Person.COORDINATE, new Point2D.Double(-71.0, 42.0));
    Clinician specialist = new Clinician(42L, new DefaultRandomNumberGenerator(43L), 124L, org);
    specialist.attributes.put(Clinician.NAME, "Specialist");
    specialist.attributes.put(Person.COORDINATE, new Point2D.Double(-71.0, 42.0));
    org.clinicianMap.put("GENERAL", new ArrayList<>(List.of(clinician)));
    org.clinicianMap.put("CARDIOLOGY", new ArrayList<>(List.of(specialist)));
    Provider.clear();
    Field registry = Provider.class.getDeclaredField("providerByUuid"); registry.setAccessible(true);
    ((Map<String, Provider>) registry.get(null)).put(org.uuid, org);
    Field payers = PayerManager.class.getDeclaredField("payers"); payers.setAccessible(true);
    ((Map<Integer, Payer>) payers.get(null)).put(701, primary);
    ((Map<Integer, Payer>) payers.get(null)).put(702, secondary);
    CSVExporter exporter = CSVExporter.getInstance();
    call(exporter, "init", new Class<?>[] {});
    for (int i = 0; i < 32; i++) {
      Person p = new Person(42L + i);
      p.attributes.put(Person.ID, "person-" + i); p.attributes.put(Person.BIRTHDATE, BIRTH);
      p.attributes.put(Person.FIRST_NAME, " First,Name "); p.attributes.put(Person.LAST_NAME, "Last\nName");
      p.attributes.put(Person.GENDER, i % 2 == 0 ? "F" : "M"); p.attributes.put(Person.INCOME, 45000 + i);
      p.attributes.put(Person.MARITAL_STATUS, "S"); p.attributes.put(Person.COORDINATE, new Point2D.Double(-71.0, 42.0));
      p.coverage.setPlanToNoInsurance(BIRTH);
      while (p.coverage.newEnrollmentPeriod(TIME)) {}
      p.coverage.setPlanAtTime(TIME, i % 4 == 0 ? PayerManager.getNoInsurancePlan() : plan,
          i % 4 == 2 ? supplement : PayerManager.getNoInsurancePlan());
      PlanRecord pr = p.coverage.getLastPlanRecord();
      pr.updateStopTime(TIME + 366L * 86400000L);
  
      pr.incrementOutOfPocketExpenses(d("12.34")); pr.incrementPrimaryCoverage(d("56.78"));
      for (String metric : new String[] {"QALY", "DALY", "QOLS"}) {
        Map<Integer, Double> values = new HashMap<>(); values.put(2000, 0.75); values.put(2004, 1.005);
        p.attributes.put(metric, values);
      }
      long eventTime = i % 8 == 0 ? -315619200000L : TIME;
      Encounter e = p.record.encounterStart(eventTime, EncounterType.values()[i % EncounterType.values().length]);
      entry(e, "enc", i); if (i % 3 != 0) { e.provider = org; e.clinician = clinician; }
      org.institutional = i % 2 == 0;
      org.incrementEncounters(EncounterType.WELLNESS, 2020);
      Entry c = p.record.conditionStart(eventTime, "condition"); entry(c, "condition", i);
      if (i % 2 == 0) { e.reason = c.codes.get(0); }
      Allergy a = p.record.allergyStart(eventTime, "allergy"); entry(a, "allergy", i);
      a.allergyType = "allergy"; a.category = "food";
      a.reactions = new HashMap<>();
      for (int j = 0; j < i % 4; j++) {
        a.reactions.put(code("reaction-" + j), ReactionSeverity.values()[j]);
      }
      Observation o = p.record.observation(eventTime, "observation", i % 2 == 0 ? 1.005 : "a,b\nc");
      o.codes.add(code("observation")); o.category = "vital-signs"; o.unit = "mg";
      Observation panel = p.record.observation(eventTime, "panel", null);
      panel.observations = new ArrayList<>();
      Observation child = p.record.new Observation(eventTime, "child", code("value"));
      child.codes.add(code("child")); panel.observations.add(child);
      Procedure proc = p.record.procedure(eventTime, "procedure"); entry(proc, "procedure", i);
      if (i % 2 == 0) { proc.reasons.add(code("reason")); }
      Medication med = p.record.medicationStart(eventTime, "medication", false); entry(med, "medication", i);
      med.prescriptionDetails = new com.google.gson.JsonObject();
      if (i % 3 == 0) { med.prescriptionDetails.addProperty("refills", i % 5); }
      else if (i % 3 == 1) {
        com.google.gson.JsonObject dur = new com.google.gson.JsonObject(); dur.addProperty("quantity", 2);
        dur.addProperty("unit", "days"); med.prescriptionDetails.add("duration", dur);
      }
      if (i % 2 == 0) { med.reasons.add(code("reason")); }
      Immunization imm = p.record.immunization(eventTime, "immunization"); entry(imm, "immunization", i);
      CarePlan care = p.record.careplanStart(eventTime, "care"); entry(care, "care", i);
      care.codes.set(0, new Code("SNOMED-CT", "care", "Care plan"));
      if (i % 2 == 0) { care.reasons.add(code("reason")); }
      ImagingStudy study = p.record.new ImagingStudy(p, eventTime, "image"); study.codes.add(code("image"));
      for (int j = 0; j < 2; j++) {
        ImagingStudy.Series series = study.new Series(); series.dicomUid = "series-" + j;
        series.bodySite = new Code("SNOMED-CT", "body", "Body"); series.modality = new Code("DICOM", "CT", "CT");
        series.instances = new ArrayList<>();
        for (int k = 0; k < 2; k++) {
          ImagingStudy.Instance inst = study.new Instance(); inst.dicomUid = "instance-" + k;
          inst.sopClass = new Code("DICOM", "sop", "SOP"); series.instances.add(inst);
        }
        study.series.add(series);
      }
      e.imagingStudies.add(study);
      Device dev = p.record.deviceImplant(eventTime, "device"); entry(dev, "device", i); dev.udi = "udi-123";
      p.record.useSupply(eventTime, code("supply"), i + 1);
      costs(e.claim, i); costs(med.claim, i);
      if (i % 5 == 0) { p.attributes.put(Person.DEATHDATE, TIME + 1L); }
      if (i == 0) { pr.updateStopTime(0L); }
      if (i % 4 == 0) { e.conditions.clear(); e.reason = null; }
      exporter.export(p, i % 3 == 0 ? TIME : TIME + 86400000L);
      // Split record exports must not duplicate patients.csv rows.
      call(exporter, "exportPatient", new Class<?>[] {Person.class, long.class}, p, TIME);
    }
    exporter.exportOrganizationsAndProviders();
    exporter.exportPayers();
    Field fm = CSVExporter.class.getDeclaredField("fileManager"); fm.setAccessible(true);
    for (String key : CSVConstants.HEADER_LINE_MAP.keySet()) {
      ((org.mitre.synthea.export.CSVFileManager) fm.get(exporter)).flushWriter(key);
    }
  }
}
