package org.synthea.parity.probes;

import com.google.gson.*;
import java.io.PrintWriter;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.*;

/** Public growth APIs across 1200 reproducible seeds, both sexes and ages zero through twenty. */
public class GrowthProbe {
  static JsonArray point(PediatricGrowthTrajectory.Point p) {
    if (p == null) return null;
    JsonArray a = new JsonArray(); a.add(p.ageInMonths); a.add(Long.toString(p.timeInSimulation));
    a.add(Double.toString(p.bmi)); a.add(p.toString()); return a;
  }
  static void number(JsonObject o, String k, double v) { o.addProperty(k, Double.toString(v)); }
  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    Map<GrowthChart.ChartType,GrowthChart> charts = GrowthChart.loadCharts();
    Field sampleField = PediatricGrowthTrajectory.class.getDeclaredField("initialSample");
    sampleField.setAccessible(true);
    Method getSample = PediatricGrowthTrajectory.class.getDeclaredMethod("getSample",long.class,String.class);
    getSample.setAccessible(true);
    Method cdf = PediatricGrowthTrajectory.class.getDeclaredMethod("cumulativeProbability",double.class);
    Method ppf = PediatricGrowthTrajectory.class.getDeclaredMethod("inverseCumulativeProbability",double.class);
    cdf.setAccessible(true); ppf.setAccessible(true);
    List<NHANESSample> samples = NHANESSample.loadSamples();
    try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out.resolve("growth.jsonl")));
         PrintWriter r = new PrintWriter(Files.newBufferedWriter(out.resolve("reverse.jsonl")))) {
      for (int i=0;i<1200;i++) {
        long seed = i * 7919L - 4000000L; Random rng = new Random(seed);
        String sex = i%2==0 ? "M":"F";
        int age = i%241; double percentile = rng.nextDouble();
        JsonObject o = new JsonObject(); o.addProperty("i",i); o.addProperty("seed",Long.toString(seed));
        o.addProperty("sex",sex); o.addProperty("age",age); number(o,"percentile",percentile);
        number(o,"z",GrowthChart.calculateZScore(percentile));
        number(o,"cdf",GrowthChart.zscoreToPercentile(GrowthChart.calculateZScore(percentile)));
        number(o,"privateCdf",(double)cdf.invoke(null,percentile*16-8));
        number(o,"privatePpf",(double)ppf.invoke(null,percentile));
        JsonArray chartResults = new JsonArray();
        for (GrowthChart.ChartType type: GrowthChart.ChartType.values()) {
          int months = type==GrowthChart.ChartType.HEAD ? age%37 : age;
          if (type==GrowthChart.ChartType.BMI) months=24+age%217;
          GrowthChart chart=charts.get(type); double v=chart.lookUp(months,sex,percentile);
          JsonArray row=new JsonArray();row.add(type.toString());row.add(months);row.add(Double.toString(v));
          row.add(Double.toString(chart.percentileFor(months,sex,v)));chartResults.add(row);
        }
        o.add("charts",chartResults);
        GrowthChartEntry entry = new GrowthChartEntry(i%3==0 ? 0:0.5,10+percentile,0.2);
        number(o,"entryValue",entry.lookUp(percentile));
        number(o,"entryZ",entry.zscoreForValue(9+percentile));
        number(o,"entryPercentile",entry.percentileForValue(9+percentile));
        o.addProperty("sampleRow",samples.get(i%samples.size()).toString());
        for (int code=0;code<3;code++) {
          var dist = code==0?NHANESSample.loadDistribution():NHANESSample.loadDistributionBySex(code);
          dist.reseedRandomGenerator(seed);o.addProperty("distribution"+code,dist.sample().toString());
        }
        var fallback=NHANESSample.loadDistributionBySex(99);fallback.reseedRandomGenerator(seed);
        o.addProperty("distributionFallback",fallback.sample().toString());
        long birth=-631152000000L;
        PediatricGrowthTrajectory trajectory=new PediatricGrowthTrajectory(seed,birth,sex);
        PediatricGrowthTrajectory legacy=new PediatricGrowthTrajectory(seed,birth);
        o.add("initial",point(trajectory.tail()));o.add("legacy",point(legacy.tail()));
        o.addProperty("selected",getSample.invoke(null,seed,sex).toString());
        long t=trajectory.tail().timeInSimulation;
        o.addProperty("before",trajectory.beforeInitialSample(t-1));
        o.addProperty("equalBefore",trajectory.beforeInitialSample(t));
        o.add("noBefore",point(trajectory.justBefore(t)));o.add("noAfter",point(trajectory.justAfter(t)));
        int months=24+age%205;
        double sigma=PediatricGrowthTrajectory.sigma(sex,age/12d);
        number(o,"sigma",sigma);
        double bmi=PediatricGrowthTrajectory.percentileToBMI(percentile,months,sex,sigma);
        number(o,"bmi",bmi);number(o,"extended",PediatricGrowthTrajectory.extendedZScore(bmi,months,sex,sigma));
        trajectory.addPoint(trajectory.tail().ageInMonths+12,t+31536000000L,18+percentile);
        o.add("beforePoint",point(trajectory.justBefore(t+1)));o.add("afterPoint",point(trajectory.justAfter(t+1)));
        Person person=new Person(seed);person.attributes.put(Person.BIRTHDATE,birth);person.attributes.put(Person.GENDER,sex);
        number(o,"interpolated",trajectory.currentBMI(person,t+15768000000L));
        trajectory.addPointFromPercentile(60,t+2*31536000000L,percentile,sex);o.add("percentilePoint",point(trajectory.tail()));
        boolean invalid=false;try { trajectory.addPoint(1,t,1); } catch(IllegalArgumentException e) { invalid=true; }
        o.addProperty("invalid",invalid);
        PediatricGrowthTrajectory generated=new PediatricGrowthTrajectory(seed,birth,sex);
        generated.generateNextYearBMI(person,generated.tail().timeInSimulation+31536000000L-1);o.add("generated",point(generated.tail()));
        PediatricGrowthTrajectory current=new PediatricGrowthTrajectory(seed,birth,sex);
        number(o,"currentGenerated",current.currentBMI(person,current.tail().timeInSimulation+31536000000L-1));
        current.addPoint(240,t+20*31536000000L,23);number(o,"adult",current.currentBMI(person,t+21*31536000000L));
        o.addProperty("correlations",PediatricGrowthTrajectory.loadCorrelations().size());
        Person mother=new Person(seed);mother.attributes.put(Person.GENDER,i%7==0?"M":"F");
        mother.attributes.put(Person.ETHNICITY,i%3==0?"HiSpAnIc":"nonhispanic");mother.attributes.put("pregnant",i%5!=0);
        if(i%4==0) mother.attributes.put(BirthStatistics.BIRTH_SEX,"F");
        BirthStatistics.setBirthStatistics(mother,birth);JsonObject attrs=new JsonObject();
        for(String key:List.of(BirthStatistics.BIRTH_WEEK,BirthStatistics.BIRTH_DATE,BirthStatistics.BIRTH_WEIGHT,BirthStatistics.BIRTH_HEIGHT,BirthStatistics.BIRTH_SEX)) {
          Object value=mother.attributes.get(key);if(value!=null)attrs.addProperty(key,value.toString());
        }
        o.add("birth",attrs);BirthStatistics.clearBirthStatistics(mother);
        o.addProperty("cleared",!mother.attributes.containsKey(BirthStatistics.BIRTH_SEX));
        o.addProperty("motherDraws",mother.getCount());
        JsonObject reverse=new JsonObject();reverse.addProperty("seed",Long.toString(seed));reverse.addProperty("sex",sex);
        number(reverse,"percentile",percentile);number(reverse,"value",new PediatricGrowthTrajectory(seed,birth,sex).reverseWeightPercentile(sex,percentile));r.println(reverse);
        w.println(o);
      }
    }
  }
}
