package org.synthea.parity.probes;

import com.google.gson.Gson;
import java.io.PrintWriter;
import java.nio.file.*;
import java.util.*;
import java.math.BigDecimal;
import org.mitre.synthea.helpers.ExpressionProcessor;
import org.mitre.synthea.world.concepts.GrowthChartEntry;

/** #66: actual Math.log and independent StrictMath.log over IEEE edge cases and seeded bits. */
public class DistributionLogProbe {
  public static void main(String[] args) throws Exception {
    Random random = new Random(66007L);Gson gson = new Gson();
    List<Double> values = new ArrayList<>(Arrays.asList(0.0,-0.0,-1.0,Double.NEGATIVE_INFINITY,
      Double.POSITIVE_INFINITY,Double.NaN,Double.MIN_VALUE,Double.MIN_NORMAL,Double.MAX_VALUE,
      1.0,Math.nextUp(1.0),Math.nextDown(1.0),0.9366031367366193,0.2152045477721394));
    for(int i=0;i<10000;i++)values.add(Double.longBitsToDouble(random.nextLong() & Long.MAX_VALUE));
    try(PrintWriter out=new PrintWriter(Files.newBufferedWriter(Path.of(args[0]).resolve("logs.jsonl")))) {
      for(double x:values){
        Map<String,String> row=new LinkedHashMap<>();
        row.put("bits",Long.toHexString(Double.doubleToLongBits(x)));
        row.put("math",Double.toString(Math.log(x)));
        row.put("strict",Double.toString(StrictMath.log(x)));
        row.put("growth",Double.toString(new GrowthChartEntry(0.0,1.0,0.2).zscoreForValue(x)));
        out.println(gson.toJson(row));
      }
    }
    ExpressionProcessor ln=new ExpressionProcessor("Ln(#{x})");
    ExpressionProcessor log2=new ExpressionProcessor("Log(#{x}, 2.0)");
    ExpressionProcessor logBase=new ExpressionProcessor("Log(#{x}, 1.23456789)");
    try(PrintWriter out=new PrintWriter(Files.newBufferedWriter(Path.of(args[0]).resolve("cql_logs.jsonl")))) {
      for(int i=0;i<1000;i++) {
        double x=Math.exp((i-500)*7919.0/100000000.0);
        Map<String,Object> params=Map.of("x",new BigDecimal(Double.toString(x)));
        Map<String,String> row=new LinkedHashMap<>();
        row.put("x",Double.toString(x));
        row.put("ln",ln.evaluate(params).toString());
        row.put("log2",log2.evaluate(params).toString());
        row.put("logBase",logBase.evaluate(params).toString());
        out.println(gson.toJson(row));
      }
    }
  }
}
