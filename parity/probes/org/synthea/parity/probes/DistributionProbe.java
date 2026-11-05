package org.synthea.parity.probes;

import com.google.gson.Gson;
import java.io.PrintWriter;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.math.BigDecimal;
import org.apache.commons.math3.util.Pair;
import org.mitre.synthea.engine.Distribution;
import org.mitre.synthea.helpers.ConstantValueGenerator;
import org.mitre.synthea.helpers.ExpressionProcessor;
import org.mitre.synthea.helpers.RandomCollection;
import org.mitre.synthea.helpers.RandomValueGenerator;
import org.mitre.synthea.helpers.SyncedEnumeratedDistro;
import org.mitre.synthea.helpers.TrendingValueGenerator;
import org.mitre.synthea.world.agents.Person;

/** Java-generated oracle for T07. No expected values are embedded in this probe. */
public class DistributionProbe {
  private static final long[] SEEDS = {0L, 1L, -1L, 42L, 987654321L};
  private static final Gson GSON = new Gson();

  private static Distribution distribution(String name) {
    Distribution d = new Distribution();
    String kind = name.split("_")[0];
    d.kind = Distribution.Kind.valueOf(kind);
    d.round = name.endsWith("rounded");
    d.parameters = new HashMap<>();
    switch (d.kind) {
      case EXACT: d.parameters.put("value", -2.5); break;
      case UNIFORM:
        d.parameters.put("low", -100.25); d.parameters.put("high", 350.75); break;
      case GAUSSIAN:
        d.parameters.put("mean", 10.0); d.parameters.put("standardDeviation", 6.0);
        if (name.contains("clamped")) {
          d.parameters.put("min", 7.0); d.parameters.put("max", 12.0);
        }
        break;
      case EXPONENTIAL: d.parameters.put("mean", 5.3); break;
      case TRIANGULAR:
        d.parameters.put("min", -10.0); d.parameters.put("mode", 3.5);
        d.parameters.put("max", 30.0); break;
      default: throw new IllegalArgumentException(name);
    }
    return d;
  }

  private static void row(PrintWriter out, String area, String scenario, long seed,
      List<?> values, Person person) {
    Map<String,Object> r = new LinkedHashMap<>();
    r.put("area", area); r.put("scenario", scenario); r.put("seed", Long.toString(seed));
    r.put("values", values); r.put("count", Long.toString(person.getCount()));
    out.println(GSON.toJson(r));
  }

  private static void samples(PrintWriter out) {
    for (long seed : SEEDS) {
      for (String name : new String[] {"EXACT", "EXACT_rounded", "UNIFORM", "UNIFORM_rounded",
          "GAUSSIAN", "GAUSSIAN_clamped", "GAUSSIAN_clamped_rounded", "EXPONENTIAL",
          "EXPONENTIAL_rounded", "TRIANGULAR", "TRIANGULAR_rounded"}) {
        Person person = new Person(seed);
        Distribution d = distribution(name);
        List<String> values = new ArrayList<>();
        for (int i = 0; i < 240; i++) { values.add(Double.toString(d.generate(person))); }
        row(out, "distribution", name, seed, values, person);
      }
      Person person = new Person(seed);
      RandomCollection<String> rc = new RandomCollection<>();
      rc.add(0, "never"); rc.add(-2, "never"); rc.add(0.1, "a"); rc.add(0.2, "b");
      RandomCollection<String> more = new RandomCollection<>();
      more.add(0.3, "c"); more.add(1.5, "d"); rc.addAll(more);
      List<String> picks = new ArrayList<>();
      for (int i = 0; i < 240; i++) { picks.add(rc.next(person)); }
      row(out, "collection", "add_all", seed, picks, person);
      person = new Person(seed);
      List<Pair<String,Double>> pmf = new ArrayList<>();
      pmf.add(new Pair<>("never", 0.0)); pmf.add(new Pair<>("a", 0.1));
      pmf.add(new Pair<>("b", 0.2)); pmf.add(new Pair<>("a", 0.3));
      pmf.add(new Pair<>("c", 1.5));
      SyncedEnumeratedDistro<String> enumerated = new SyncedEnumeratedDistro<>(pmf);
      picks = new ArrayList<>();
      for (int i = 0; i < 240; i++) { picks.add(enumerated.syncedReseededSample(person)); }
      row(out, "enumerated", "duplicates_zero", seed, picks, person);
      for (String name : new String[] {"constant", "range", "distribution", "trend",
          "trend_min", "trend_max", "trend_bounded"}) {
        person = new Person(seed);
        ConstantValueGenerator constant = new ConstantValueGenerator(person, -12.75);
        RandomValueGenerator range = new RandomValueGenerator(person, -4.5, 19.25);
        RandomValueGenerator fromDistribution = new RandomValueGenerator(person,
            distribution("GAUSSIAN_clamped"));
        TrendingValueGenerator trend = new TrendingValueGenerator(person, 4.5,
            8.0, 14.0, 100L, 300L,
            name.equals("trend_min") || name.equals("trend_bounded") ? 7.0 : null,
            name.equals("trend_max") || name.equals("trend_bounded") ? 15.0 : null);
        List<String> values = new ArrayList<>();
        for (int i = 0; i < 240; i++) {
          long time = i * 2L;
          double value;
          switch (name) {
            case "constant": value = constant.getValue(time); break;
            case "range": value = range.getValue(time); break;
            case "distribution": value = fromDistribution.getValue(time); break;
            default: value = trend.getValue(time);
          }
          values.add(Double.toString(value));
        }
        row(out, "generator", name, seed, values, person);
      }
    }
  }

  private static void expressions(PrintWriter out) {
    String[] expressions = {"10 + 3", "25 / 2",
        "2 * (10 + 6) + 4 + 3 * ((10 / 2) * (9 / 3))",
        "#{x} / 2 + 7", "#{x} * (#{y} + 3.0) + Max(#l{xs})",
        "Sum(#l{xs})", "Min(#l{xs})", "Avg(#l{xs})", "Count(#l{xs})",
        "if #s{sex} = 'male' then 1.0 else #d{x} * 2.0",
        "if #b{flag} then #{x} else #{y}", "#{var one} * (#{y} + 3.0)",
        "define offset: 2.0\n#{x} + offset", "#{x} > #{y}",
        "Round(#{x} / 7, 3)", "Abs(-#{x})", "Power(#{x}, 2.0)",
        "if null then 1.0 else 2.0", "Coalesce(null, #{x})",
        "#{x} / 3", "0.1 + 0.2", "null = null", "true and null",
        "false and null", "true or null", "false or null"};
    for (String expression : expressions) {
      ExpressionProcessor processor = new ExpressionProcessor(expression);
      for (int i = 0; i < 6; i++) {
        Map<String,Object> params = new HashMap<>();
        for (String name : processor.getParamNames()) {
          Object value;
          switch (name) {
            case "xs": value = List.of(new BigDecimal("3"), new BigDecimal("1.2342"),
                new BigDecimal("5.25512"), new BigDecimal("12")); break;
            case "sex": value = i % 2 == 0 ? "male" : "female"; break;
            case "flag": value = i % 2 == 0; break;
            case "y": value = new BigDecimal("3"); break;
            default: value = new BigDecimal(i).add(new BigDecimal("2.125"));
          }
          params.put(name, value);
        }
        Object value = processor.evaluate(params);
        Map<String,Object> r = new LinkedHashMap<>();
        r.put("expression", expression); r.put("iteration", i);
        r.put("params", params); r.put("names", processor.getParamNames());
        r.put("types", processor.getParamTypes());
        r.put("result", value == null ? "null" : value.toString());
        r.put("type", value == null ? "null" : value.getClass().getSimpleName());
        out.println(GSON.toJson(r));
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Path dir = Path.of(args[0]); Files.createDirectories(dir);
    try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(dir.resolve("samples.jsonl"),
        StandardCharsets.UTF_8))) { samples(out); }
    try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(dir.resolve("expressions.jsonl"),
        StandardCharsets.UTF_8))) { expressions(out); }
  }
}
