package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import org.mitre.synthea.helpers.*;
import org.mitre.synthea.modules.*;
import org.mitre.synthea.modules.calculators.*;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.concepts.HealthRecord.*;
import org.synthea.parity.probes.support.*;

/** T23: forty-two adult years for fifty seeds plus direct calculator boundary cases. */
public class ChronicModulesProbe {
  static final Gson G = new GsonBuilder().serializeNulls().create();
  static final long WEEK = 604800000L;
  static long date(int y) { return LocalDate.of(y,1,1).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli(); }
  static Person person(int i, long birth) {
    Person p = new Person(230000L+i);
    p.attributes.put(Person.BIRTHDATE,birth); p.attributes.put(Person.GENDER,i%2==0?"F":"M");
    p.attributes.put(Person.RACE,i%3==0?"black":"white"); p.attributes.put(Person.INCOME,100000);
    p.attributes.put(Person.SMOKER,i%3==1); p.attributes.put("diabetes",i%4==0);
    p.attributes.put("hypertension",i%5==0); p.attributes.put("blood_pressure_controlled",i%3==0);
    p.attributes.put("left_ventricular_hypertrophy",i%11==0);
    p.attributes.put("coronary_heart_disease",i%7==0);
    if(i%13==0) p.attributes.put("atrial_fibrillation",false);
    return p;
  }
  static void vitals(Person p, int i) {
    p.setVitalSign(VitalSign.SYSTOLIC_BLOOD_PRESSURE,95+(i*17)%115);
    p.setVitalSign(VitalSign.DIASTOLIC_BLOOD_PRESSURE,55+(i*13)%65);
    p.setVitalSign(VitalSign.TOTAL_CHOLESTEROL,110+(i*23)%240);
    p.setVitalSign(VitalSign.HDL,25+(i*7)%65);
    p.setVitalSign(VitalSign.HEIGHT,160+(i%30));
    p.setVitalSign(VitalSign.WEIGHT,75+(i%65));
    p.setVitalSign(VitalSign.BMI,BMI.calculate(160+(i%30),75+(i%65)));
  }
  static void condition(HealthRecord record,long time,int years,String code) {
    Encounter e = record.new Encounter(time,"wellness"); record.encounters.add(e);
    Entry c = record.new Entry(time,code); c.codes.add(new Code("SNOMED-CT",code,"Fixture condition"));
    if(years>0)c.stop=time+Utilities.convertTime("years",years); e.conditions.add(c);
  }
  static JsonObject snapshot(Person p,long time) {
    JsonObject row=new JsonObject(); JsonObject attrs=new JsonObject();
    for(String key:new TreeSet<>(p.attributes.keySet()))attrs.addProperty(key,CanonicalPerson.renderValue(p.attributes.get(key)));
    row.add("attributes",attrs); row.addProperty("rng_count",Long.toString(p.getCount()));
    JsonObject vs=new JsonObject(); for(VitalSign sign:p.vitalSigns.keySet())vs.addProperty(sign.name(),Double.toString(p.getVitalSign(sign,time)));
    row.add("vitals",vs); row.add("record",Canonical.record(p.defaultRecord));
    row.add("loss_record",p.lossOfCareRecord==null?JsonNull.INSTANCE:Canonical.record(p.lossOfCareRecord));
    JsonObject order=new JsonObject();
    for(String key:new String[]{"QALY","DALY","QOLS"})if(p.attributes.containsKey(key)){
      JsonArray years=new JsonArray(); for(Object year:((Map)p.attributes.get(key)).keySet())years.add(year.toString()); order.add(key,years);
    }
    row.add("year_order",order); return row;
  }
  static void lifetime(Path out,int i) throws Exception {
    Config.set("generate.payers.loss_of_care",Boolean.toString(i%3==0));
    long birth=date(1920+i),start=date(1940+i),end=date(1982+i);
    Person p=person(i,birth); vitals(p,i);
    p.coverage.setPlanToNoInsurance(birth);p.coverage.getLastPlanRecord().updateStopTime(end+WEEK);
    condition(p.defaultRecord,start,0,"44054006");
    condition(p.defaultRecord,start,15,"195967001");
    condition(p.defaultRecord,start,5,"192127007");
    if(p.lossOfCareEnabled)condition(p.lossOfCareRecord,start,0,"44054006");
    CardiovascularDiseaseModule cardio=new CardiovascularDiseaseModule();
    QualityOfLifeModule qol=new QualityOfLifeModule();WeightLossModule weight=new WeightLossModule();
    Field use=CardiovascularDiseaseModule.class.getDeclaredField("useFramingham");use.setAccessible(true);use.set(null,i%2==1);
    JsonArray rows=new JsonArray();int year=-1;
    for(long t=start;t<end;t+=WEEK){
      if(Utilities.getYear(t)!=year){
        year=Utilities.getYear(t);
        if((year-(1940+i))%9==0)p.attributes.put(WeightLossModule.TRIGGER_WEIGHT_LOSS,true);
      }
      cardio.process(p,t);qol.process(p,t);weight.process(p,t);
      if(t+WEEK>=end || Utilities.getYear(t+WEEK)!=year)rows.add(snapshot(p,t));
    }
    p.recordDeath(end,new Code("SNOMED-CT","12345","Fixture death"));
    JsonObject last=snapshot(p,end);last.addProperty("cardio_stopped",cardio.process(p,end));
    last.addProperty("weight_stopped",weight.process(p,end));qol.process(p,end);last.add("dead_qol",G.toJsonTree(QualityOfLifeModule.calculate(p,end)));rows.add(last);
    Files.writeString(out.resolve("adult_"+i+".json"),G.toJson(rows));
  }
  static void risks(Path out)throws Exception {
    try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(out.resolve("risks.jsonl")))){
      for(int i=0;i<2400;i++){
        int age=15+i%86;long time=date(2020);Person p=person(i,date(2020-age));vitals(p,i);
        JsonArray values=new JsonArray();
        for(boolean per:new boolean[]{false,true}){
          values.add(Double.toString(ASCVD.ascvd10Year(p,time,per)));
          values.add(Double.toString(Framingham.chd10Year(p,time,per)));
          values.add(Double.toString(Framingham.cvd10Year(p,time,per)));
          values.add(Double.toString(Framingham.atrialFibrillation10Year(p,time,per)));
          values.add(Double.toString(Framingham.stroke10Year(p,time,per)));
        }
        w.println(G.toJson(values));
      }
    }
  }
  static JsonArray trajectory(PediatricGrowthTrajectory pgt)throws Exception {
    Field f=PediatricGrowthTrajectory.class.getDeclaredField("trajectory");f.setAccessible(true);
    JsonArray values=new JsonArray();
    for(PediatricGrowthTrajectory.Point p:(List<PediatricGrowthTrajectory.Point>)f.get(pgt)){
      JsonArray point=new JsonArray();point.add(p.ageInMonths);point.add(Long.toString(p.timeInSimulation));point.add(Double.toString(p.bmi));values.add(point);
    } return values;
  }
  static void pediatric(Path out)throws Exception {
    GrowthChart chart=GrowthChart.loadCharts().get(GrowthChart.ChartType.BMI);
    WeightLossModule m=new WeightLossModule();JsonArray cases=new JsonArray();
    for(int i=0;i<50;i++){
      for(int action=0;action<5;action++){
        long birth=date(1990),start=date(1998+i%11);Person p=person(i,birth);
        String gender=(String)p.attributes.get(Person.GENDER);
        p.attributes.put(WeightLossModule.WEIGHT_MANAGEMENT_START,start);
        p.attributes.put(WeightLossModule.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE,0.01+(i%5)*0.005);
        p.setVitalSign(VitalSign.HEIGHT_PERCENTILE,0.75);
        PediatricGrowthTrajectory pgt=new PediatricGrowthTrajectory(i,birth);
        long before=start-Utilities.convertTime("months",6),after=start+Utilities.convertTime("months",1);
        int beforeAge=p.ageInMonths(before),afterAge=p.ageInMonths(after);
        pgt.addPoint(beforeAge,before,chart.lookUp(beforeAge,gender,0.90));
        pgt.addPoint(afterAge,after,chart.lookUp(afterAge,gender,0.90));
        p.attributes.put(Person.GROWTH_TRAJECTORY,pgt);JsonObject row=new JsonObject();
        if(action==0){m.adjustBMIVectorForSuccessfulManagement(p);row.add("first",trajectory(pgt));m.adjustBMIVectorForSuccessfulManagement(p);}
        if(action==1)m.maintainBMIPercentile(p,after+Utilities.convertTime("months",1));
        if(action==2){m.adjustBMIVectorForSuccessfulManagement(p);m.pediatricRegression(p,start+Utilities.convertTime("years",2));}
        if(action==3){for(int y=1993;y<2010;y++)pgt.currentBMI(p,date(y));row.addProperty("weight",Double.toString(m.transitionRegression(p,date(2010))));}
        if(action==4){p.attributes.put(WeightLossModule.ACTIVE_WEIGHT_MANAGEMENT,true);p.attributes.put(WeightLossModule.WEIGHT_LOSS_ADHERENCE,true);p.attributes.put(WeightLossModule.LONG_TERM_WEIGHT_LOSS,true);m.process(p,start+Utilities.convertTime("months",2));}
        row.add("trajectory",trajectory(pgt));row.addProperty("rng",Long.toString(p.getCount()));cases.add(row);
      }
    }
    Files.writeString(out.resolve("pediatric.json"),G.toJson(cases));
  }
  static void upstream(Path out)throws Exception {
    JsonObject row=new JsonObject(); WeightLossModule m=new WeightLossModule();
    GrowthChart chart=GrowthChart.loadCharts().get(GrowthChart.ChartType.BMI);
    long birth=date(1990),start=date(2000);Person p=new Person(0L);
    p.attributes.put(Person.BIRTHDATE,birth);p.attributes.put(Person.GENDER,"M");
    p.attributes.put(WeightLossModule.WEIGHT_MANAGEMENT_START,start);
    p.attributes.put(WeightLossModule.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE,0.01);
    PediatricGrowthTrajectory pgt=new PediatricGrowthTrajectory(0L,birth);
    for(LocalDate d:new LocalDate[]{LocalDate.of(1999,7,2),LocalDate.of(2000,2,1)}){
      long t=d.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();int age=p.ageInMonths(t);
      pgt.addPoint(age,t,chart.lookUp(age,"M",0.9));
    }
    int low=pgt.tail().ageInMonths+12;
    pgt.addPoint(low,pgt.tail().timeInSimulation+WeightLossModule.ONE_YEAR,chart.lookUp(low,"M",0.89));
    p.attributes.put(Person.GROWTH_TRAJECTORY,pgt);
    long regression=LocalDate.of(2002,3,1).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
    m.pediatricRegression(p,regression);row.addProperty("regression_bmi",Double.toString(pgt.tail().bmi));
    p=new Person(0L);p.attributes.put(Person.BIRTHDATE,birth);p.attributes.put(Person.GENDER,"M");
    p.attributes.put(WeightLossModule.WEIGHT_MANAGEMENT_START,LocalDate.of(2003,12,2).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli());
    p.attributes.put(WeightLossModule.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE,0.01);p.setVitalSign(VitalSign.HEIGHT_PERCENTILE,0.75);
    pgt=new PediatricGrowthTrajectory(0L,birth);for(int y=1993;y<2010;y++)pgt.currentBMI(p,date(y));
    p.attributes.put(Person.GROWTH_TRAJECTORY,pgt);row.addProperty("transition_weight",Double.toString(m.transitionRegression(p,date(2010))));
    Files.writeString(out.resolve("upstream.json"),G.toJson(row));
  }
  public static void main(String[] args)throws Exception {
    CanonicalChronic.registerAll();Path out=Path.of(args[0]);Files.createDirectories(out);PayerManager.loadNoInsurance();
    Config.set("generate.timestep",Long.toString(WEEK));risks(out);
    for(int i=0;i<50;i++)lifetime(out,i);pediatric(out);upstream(out);
    Map<String,Attributes.Inventory> inventory=new TreeMap<>();ASCVD.inventoryAttributes(inventory);Framingham.inventoryAttributes(inventory);CardiovascularDiseaseModule.inventoryAttributes(inventory);QualityOfLifeModule.inventoryAttributes(inventory);
    Files.writeString(out.resolve("inventory.json"),G.toJson(inventory));
  }
}
