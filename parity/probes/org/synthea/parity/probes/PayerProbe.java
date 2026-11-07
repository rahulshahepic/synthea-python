package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.PrintWriter;
import java.math.BigDecimal;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.mitre.synthea.helpers.*;
import org.mitre.synthea.modules.HealthInsuranceModule;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.agents.behaviors.payeradjustment.*;
import org.mitre.synthea.world.agents.behaviors.planfinder.*;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.concepts.healthinsurance.*;
import org.mitre.synthea.world.geography.Location;

/** T15 component boundaries: real CSV loading; GENERIC-only strategy calls. */
public class PayerProbe {
  static final long TIME = 1582934400000L; // leap day 2020
  static final Gson GSON = new GsonBuilder().serializeNulls().create();
  static final String[] STATES = {"Massachusetts", "Texas", "Wisconsin"};
  static InsurancePlan plan(int id, Payer payer, BigDecimal premium, boolean income,
                            int priority, int start, int end, String services) {
    InsurancePlan p = new InsurancePlan(id,payer,new HashSet<>(Arrays.asList(services.split(","))),
      new BigDecimal("123.40"),new BigDecimal("0.80"),new BigDecimal("25.00"),premium,
      new BigDecimal("8700.00"),false,false,income,start,end,priority,"GENERIC");
    payer.addPlan(p);return p;
  }
  static Person person(long seed, int i) {
    Person p=new Person(seed);p.attributes.put(Person.INCOME,(i%6)*20000);
    p.attributes.put(Person.OCCUPATION_LEVEL,(i%3)*0.25);
    p.attributes.put(Person.BIRTHDATE,0L);
    if(i%2==0){p.hasMultipleRecords=true;p.records=new java.util.concurrent.ConcurrentHashMap<>();
      p.records.put("a",p.defaultRecord);}
    // Existing record objects, encounter state only. No claims or coverage invoked.
    Person owner = new Person(0L); owner.attributes.put(Person.BIRTHDATE,TIME);
    owner.coverage.setPlanToNoInsurance(TIME);
    for(int j=0;j<i%9;j++) {
      HealthRecord.Encounter e=owner.defaultRecord.new Encounter(TIME,"ambulatory");
      e.start=TIME-j*90L*86400000;
      p.defaultRecord.encounters.add(0,e);
    }
    return p;
  }
  static JsonObject dumpPayer(Payer payer) throws Exception {
    JsonObject o=new JsonObject();o.addProperty("id",payer.getPlanLinkId());
    o.addProperty("name",payer.getName());o.addProperty("uuid",payer.uuid);
    o.addProperty("ownership",payer.getOwnership());o.add("attributes",GSON.toJsonTree(payer.getAttributes()));
    o.addProperty("hash",payer.hashCode());JsonArray plans=new JsonArray();
    for(InsurancePlan p:payer.getPlans()){
      JsonObject q=new JsonObject();q.addProperty("id",p.id);q.addProperty("status",p.getInsuranceStatus());
      q.addProperty("deductible",p.getDeductible().toString());
      q.addProperty("premium",p.getMonthlyPremium(120000).toString());
      q.addProperty("yearly",p.getYearlyCost(120000).toString());
      q.addProperty("payerCoinsurance",p.getPayerCoinsurance().toString());
      q.addProperty("patientCoinsurance",p.getPatientCoinsurance().toString());
      q.addProperty("max",p.getMaxOop().toString());q.addProperty("priority",p.getPriority());
      q.addProperty("supplement",p.isMedicareSupplementPlan());q.addProperty("copayBased",p.isCopayBased());
      q.addProperty("maySupplement",p.mayPurchaseSupplement());
      q.addProperty("atZero",p.isActive(0L));q.addProperty("atTime",p.isActive(TIME));
      q.addProperty("copay",p.determineCopay("ambulatory",TIME).toString());
      q.addProperty("wellness",p.determineCopay("WELLNESS",TIME).toString());
      q.addProperty("coversNull",p.coversService(null));plans.add(q);
    }o.add("plans",plans);return o;
  }
  static void stateLoading(Path out) throws Exception {
    try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(out.resolve("states.jsonl")))) {
      for(String state:STATES){PayerManager.clear();PayerManager.loadPayers(new Location(state,null));
        JsonObject o=new JsonObject();o.addProperty("state",state);JsonArray payers=new JsonArray();
        for(Payer payer:PayerManager.getAllPayers())payers.add(dumpPayer(payer));
        o.add("payers",payers);o.add("none",dumpPayer(PayerManager.getNoInsurancePlan().getPayer()));
        w.println(GSON.toJson(o));}
    }
  }
  static void strategies(Path out) throws Exception {
    PayerManager.loadNoInsurance();
    try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(out.resolve("strategies.jsonl")))) {
      for(int i=0;i<600;i++){
        long seed=i*7919L-1000000L;JsonObject o=new JsonObject();o.addProperty("i",i);
        List<InsurancePlan> plans=new ArrayList<>();
        for(int k=0;k<4;k++){
          Payer payer=new Payer("Component "+k,k,new HashSet<>(List.of("*")),k==3?"GOVERNMENT":"PRIVATE");
          plans.add(plan(k,payer,new BigDecimal(k==2?"0.075":""+(100+50*((k+i)%4))),k==2,k%2,0,Integer.MAX_VALUE,k==1?"emergency":"*"));
        }
        IPlanFinder[] finders={new PlanFinderRandom(),new PlanFinderPriority(),new PlanFinderBestRates()};
        JsonArray selected=new JsonArray();
        for(IPlanFinder finder:finders){Person person=person(seed,i);
          List<InsurancePlan> options=i%13==0?List.of():i%11==0?plans.subList(0,1):plans;
          InsurancePlan p=finder.find(options,person,null,i%5==0?0L:TIME);
          JsonArray a=new JsonArray();a.add(p.id);a.add(Long.toString(person.getCount()));
          a.add(Long.toString(person.randLong()));selected.add(a);}
        o.add("selected",selected);
        JsonArray adjusted=new JsonArray();double[] rates={-0.5,0.0,0.05,0.5,1.0,1.5};
        IPayerAdjustment[] adjustments={new PayerAdjustmentNone(),new PayerAdjustmentFixed(rates[i%6]),new PayerAdjustmentRandom(rates[i%6])};
        for(IPayerAdjustment adjustment:adjustments){Person person=person(seed,i);
          Person owner = new Person(0L); owner.attributes.put(Person.BIRTHDATE,TIME);
          owner.coverage.setPlanToNoInsurance(TIME);
          HealthRecord.Encounter entry=owner.defaultRecord.new Encounter(TIME,"ambulatory");
          Claim.ClaimEntry ce=new Claim(entry, owner).mainEntry;ce.cost=new BigDecimal(i+".125");
          ce.adjustment=new BigDecimal("7.77");
          JsonArray a=new JsonArray();a.add(adjustment.adjustClaim(ce,person).toString());
          a.add(ce.adjustment.toString());a.add(Long.toString(person.getCount()));
          a.add(Long.toString(person.randLong()));adjusted.add(a);}
        o.add("adjusted",adjusted);
        InsurancePlan money=plans.get(i%4);int income=100001+i;
        JsonArray costs=new JsonArray();costs.add(money.getMonthlyPremium(income).toString());
        costs.add(money.getYearlyCost(income).toString());
        costs.add(money.payMonthlyPremium(i%2,income).toString());
        costs.add(money.getPayer().getRevenue().toString());
        for(long t:new long[]{HealthInsuranceModule.mandateTime-1,HealthInsuranceModule.mandateTime,HealthInsuranceModule.mandateTime+1})
          costs.add(money.determineCopay("wellness",t).toString());
        o.add("money",costs);w.println(GSON.toJson(o));
      }
    }
  }
  static void integration(Path out) throws Exception {
    try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(out.resolve("integration.jsonl")))) {
      for(String state:STATES){PayerManager.clear();PayerManager.loadPayers(new Location(state,null));
        List<InsurancePlan> plans=PayerManager.getActivePlans(PayerManager.getAllPayers(),TIME);
        for(int i=0;i<40;i++){
          Person p=person(i+20,i);p.attributes.put(Person.GENDER,"M");
          JsonObject o=new JsonObject();o.addProperty("state",state);o.addProperty("i",i);
          JsonArray a=new JsonArray();
          for(InsurancePlan plan:plans)a.add(plan.accepts(p,TIME));
          o.add("accepts",a);w.println(GSON.toJson(o));
        }
      }
    }
  }
  public static void main(String[] args) throws Exception {
    Path out=Path.of(args[0]);Config.set("generate.payers.selection_behavior","random");
    stateLoading(out);strategies(out);integration(out);
  }
}
