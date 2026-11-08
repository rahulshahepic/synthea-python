package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import org.mitre.synthea.engine.Generator;
import org.mitre.synthea.engine.Generator.GeneratorOptions;
import org.mitre.synthea.export.Exporter;
import org.mitre.synthea.helpers.*;
import org.mitre.synthea.world.agents.*;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.geography.*;
import org.synthea.parity.probes.support.*;

/** T27: real serial generator in three states plus demographics and criteria components. */
public class GeneratorProbe {
  static final Gson G=new GsonBuilder().serializeNulls().create();
  static final String[] STATES={"Massachusetts","California","Texas"};
  static final long[] SEEDS={42L,12345L,17L};
  static final long TIME=LocalDate.of(2025,1,1).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
  static Object field(Object target,String name)throws Exception {
    Field f=Generator.class.getDeclaredField(name);f.setAccessible(true);return f.get(target);
  }
  static void configure(){
    for(String key:Config.allPropertyNames())if(key.startsWith("exporter.")&&key.endsWith(".export"))Config.set(key,"false");
    Config.set("exporter.enable_custom_exporters","false");Config.set("exporter.years_of_history","0");Config.set("exporter.split_records","false");
    Config.set("generate.thread_pool_size","1");Config.set("generate.log_patients.detail","none");
    Config.set("generate.only_dead_patients","false");Config.set("generate.only_alive_patients","false");
    Config.set("generate.timestep","604800000");Config.set("generate.max_attempts_to_keep_patient","1000");
  }
  static GeneratorOptions options(int group){
    GeneratorOptions o=new GeneratorOptions();o.population=20;o.seed=SEEDS[group];o.clinicianSeed=100+SEEDS[group];
    o.referenceTime=TIME;o.endTime=TIME;o.threadPoolSize=1;o.state=STATES[group];
    o.ageSpecified=true;o.minAge=0;o.maxAge=3;o.enabledModules=List.of();return o;
  }
  static JsonObject values(Map<String,Object> map){
    JsonObject o=new JsonObject();new TreeMap<>(map).forEach((k,v)->o.addProperty(k,CanonicalPerson.renderValue(v)));return o;
  }
  static void demographics(Path out,int group)throws Exception {
    Provider.clear();PayerManager.clear();Generator g=new Generator(options(group));
    Method pick=Generator.class.getDeclaredMethod("pickDemographics",RandomNumberGenerator.class,Demographics.class);pick.setAccessible(true);
    Method birth=Generator.class.getDeclaredMethod("birthdateFromTargetAge",long.class,RandomNumberGenerator.class);birth.setAccessible(true);
    JsonArray rows=new JsonArray();
    for(int i=0;i<200;i++){
      g.options.ageSpecified=i%2==0;g.options.minAge=i%70;g.options.maxAge=70+i%30;
      g.options.gender=i%5==0?"F":i%5==1?"M":null;
      Field veteran=Generator.class.getDeclaredField("onlyVeterans");veteran.setAccessible(true);veteran.set(g,i%7==0);
      DefaultRandomNumberGenerator random=new DefaultRandomNumberGenerator(SEEDS[group]+i);
      JsonObject row=new JsonObject();row.add("attributes",values(g.randomDemographics(random)));
      row.addProperty("count",Long.toString(random.getCount()));
      JsonArray births=new JsonArray();for(long age:new long[]{0,1,18,35,85,100,140})births.add(Long.toString((Long)birth.invoke(g,age,random)));
      row.add("birthdates",births);row.addProperty("final_count",Long.toString(random.getCount()));rows.add(row);
    }
    Files.writeString(out.resolve("demographics_"+group+".json"),G.toJson(rows));
  }
  static JsonObject person(Person p)throws Exception {
    JsonObject row=new JsonObject();row.addProperty("person",CanonicalPerson.dump(p));
    row.add("enum_attributes",CanonicalGenerator.enumAttributes(p));
    row.add("record",Canonical.record(p.record));row.add("coverage",CanonicalCoverage.coverage(p.coverage));
    row.addProperty("last_updated",Long.toString(p.lastUpdated));row.addProperty("population_seed",Long.toString(p.populationSeed));
    List<VitalSign> orderedSigns=new ArrayList<>(p.vitalSigns.keySet());
    orderedSigns.sort(Comparator.comparing(VitalSign::name));
    JsonObject signs=new JsonObject();for(VitalSign sign:orderedSigns)signs.addProperty(sign.name(),Double.toString(p.getVitalSign(sign,p.lastUpdated)));
    row.add("vitals",signs);JsonArray modules=new JsonArray();for(org.mitre.synthea.engine.Module m:p.currentModules)modules.add(m.name);row.add("modules",modules);
    return row;
  }
  static void population(Path out,int group)throws Exception {
    Provider.clear();PayerManager.clear();Generator g=new Generator(options(group));
    Field store=Generator.class.getDeclaredField("internalStore");store.setAccessible(true);store.set(g,new LinkedList<Person>());
    g.run();JsonObject row=new JsonObject();JsonArray people=new JsonArray();
    for(Person p:(List<Person>)store.get(g))people.add(person(p));row.add("people",people);
    row.addProperty("alive",g.stats.get("alive").get());row.addProperty("dead",g.stats.get("dead").get());
    row.addProperty("total",g.totalGeneratedPopulation.get());row.addProperty("rng",Long.toString(g.getRandomizer().getCount()));
    row.addProperty("clinician_rng",Long.toString(((DefaultRandomNumberGenerator)field(g,"clinicianRandom")).getCount()));
    Files.writeString(out.resolve("population_"+group+".json"),G.toJson(row));
  }
  public static void main(String[] args)throws Exception {
    Path out=Path.of(args[0]);Files.createDirectories(out);configure();CanonicalGenerator.registerAll();
    for(int i=0;i<3;i++){demographics(out,i);population(out,i);}
  }
}
