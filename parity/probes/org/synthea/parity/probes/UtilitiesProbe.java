package org.synthea.parity.probes;

import com.google.gson.JsonArray;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import org.apache.commons.lang3.Range;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;
import org.mitre.synthea.helpers.Telemedicine;
import org.mitre.synthea.helpers.TimeSeriesData;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.HealthRecord.Code;

/**
 * Probe for T06: Utilities, TimeSeriesData and Telemedicine. Writes a
 * single utilities.jsonl into the output directory; every row carries a
 * "kind" and the exact inputs, so the Python parity test recomputes each
 * field and compares the whole record. Doubles are written with
 * Double.toString and longs as strings. It also writes a small directory
 * tree under walktree/ and a free file freefile.txt, which the
 * walkAllModules / readResourceOrPath rows refer to.
 */
public class UtilitiesProbe {

  private static String err(Throwable e) {
    return "ERR:" + e.getClass().getSimpleName();
  }

  private interface Call<T> {
    T run() throws Exception;
  }

  private static <T> String orErr(Call<T> call, java.util.function.Function<T, String> fmt) {
    try {
      return fmt.apply(call.run());
    } catch (Throwable e) {
      return err(e);
    }
  }

  private static final String[] UNITS = {
    "hours", "minutes", "seconds", "days", "weeks", "months", "years", "fortnights", ""
  };

  private static final String[] OPS = {
    "<", "<=", "==", ">=", ">", "!=", "is nil", "is not nil", "~="
  };

  public static void main(String[] args) throws Exception {
    Path outdir = Paths.get(args[0]);
    Files.createDirectories(outdir);
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(outdir.resolve("utilities.jsonl"), StandardCharsets.UTF_8))) {
      writeConvertTime(w);
      writeCalendar(w);
      writeLocalDates(w);
      writePrimitive(w);
      writeRisk(w);
      writeCompare(w);
      writeParseRange(w);
      writeResources(w, outdir);
      writeDicom(w);
      writeStrToObject(w);
      writeCleanMap(w);
      writeWalk(w, outdir);
      writeTimeSeries(w);
      writeTelemedicine(w);
    }
  }

  // ------------------------------------------------------------ convertTime

  private static void writeConvertTime(PrintWriter w) {
    Random rng = new Random(123456789L);
    List<Long> longs = new ArrayList<>(List.of(
        0L, 1L, -1L, 2L, -2L, 7L, 30L, 365L, 1000L, -1000L,
        2147483647L, -2147483648L, 4294967295L, 9007199254740993L,
        Long.MAX_VALUE, Long.MIN_VALUE, Long.MAX_VALUE - 1, Long.MIN_VALUE + 1,
        2562047788015215L, -2562047788015215L));
    for (int i = 0; i < 140; i++) {
      longs.add(rng.nextLong());
    }
    for (int i = 0; i < 20; i++) {
      longs.add((long) (rng.nextInt(2000000) - 1000000));
    }
    for (String unit : UNITS) {
      for (long v : longs) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "ctLong");
        o.addProperty("units", unit);
        o.addProperty("value", Long.toString(v));
        o.addProperty("result", orErr(() -> Utilities.convertTime(unit, v), r -> Long.toString(r)));
        w.println(o.toString());
      }
    }
    List<Double> doubles = new ArrayList<>(List.of(
        0.0, -0.0, 0.5, -0.5, 1.5, -1.5, 2.25, 0.1, 1.0e-3, 365.25,
        1.0e15, -1.0e15, 1.0e300, -1.0e300,
        Double.MAX_VALUE, -Double.MAX_VALUE, Double.NaN,
        Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY, 4.9e-324));
    for (int i = 0; i < 140; i++) {
      doubles.add(rng.nextDouble() * 2000.0 - 1000.0);
    }
    for (int i = 0; i < 20; i++) {
      doubles.add((rng.nextDouble() - 0.5) * 2.0e18);
    }
    for (String unit : UNITS) {
      for (double v : doubles) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "ctDouble");
        o.addProperty("units", unit);
        o.addProperty("value", Double.toString(v));
        o.addProperty("result",
            orErr(() -> Utilities.convertTime(unit, v), r -> Long.toString(r)));
        w.println(o.toString());
      }
    }
  }

  // --------------------------------------------------------------- calendar

  private static void writeCalendar(PrintWriter w) {
    for (int year = -2000; year <= 3000; year++) {
      JsonObject o = new JsonObject();
      o.addProperty("kind", "calYears");
      o.addProperty("year", year);
      o.addProperty("result",
          orErr(() -> Utilities.convertCalendarYearsToTime(year), r -> Long.toString(r)));
      w.println(o.toString());
    }
    // getYear / getMonth over Jan 1 and mid-year (day 182) of every year in
    // the same range, plus day-boundary timestamps around the epoch and the
    // 1582 cutover.
    List<Long> times = new ArrayList<>();
    for (int year = -2000; year <= 3000; year++) {
      long jan1 = Utilities.convertCalendarYearsToTime(year);
      times.add(jan1);
      times.add(jan1 + 182L * 86400000L + 43200123L);
    }
    times.addAll(List.of(
        0L, -1L, 1L, -86400000L, 86399999L, -86400001L,
        -141428L * 86400000L, -141427L * 86400000L,
        -141428L * 86400000L - 1L, -141427L * 86400000L - 1L,
        1504783221000L, 1234567890000L, Long.MAX_VALUE, Long.MIN_VALUE));
    for (long t : times) {
      JsonObject o = new JsonObject();
      o.addProperty("kind", "yearMonth");
      o.addProperty("time", Long.toString(t));
      o.addProperty("year", orErr(() -> Utilities.getYear(t), Object::toString));
      o.addProperty("month", orErr(() -> Utilities.getMonth(t), Object::toString));
      w.println(o.toString());
    }
    // getAnniversary: seeded random base times x anniversary offsets, plus
    // the Feb 29 series.
    Random rng = new Random(777L);
    int[] annivs = {-100, -10, -4, -1, 0, 1, 4, 10, 100};
    for (int i = 0; i < 260; i++) {
      long base = (long) ((rng.nextDouble() - 0.5) * 6.0e12);
      for (int a : annivs) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "anniversary");
        o.addProperty("time", Long.toString(base));
        o.addProperty("anniversary", a);
        o.addProperty("result",
            orErr(() -> Utilities.getAnniversary(base, a), r -> Long.toString(r)));
        w.println(o.toString());
      }
    }
    long feb29 = Utilities.localDateToTimestamp(LocalDate.of(2020, 2, 29)) + 37800000L;
    for (int a = -8; a <= 8; a++) {
      JsonObject o = new JsonObject();
      o.addProperty("kind", "anniversary");
      o.addProperty("time", Long.toString(feb29));
      o.addProperty("anniversary", a);
      o.addProperty("result",
          orErr(() -> Utilities.getAnniversary(feb29, a), r -> Long.toString(r)));
      w.println(o.toString());
    }
  }

  private static void writeLocalDates(PrintWriter w) {
    List<LocalDate> dates = new ArrayList<>();
    for (long day = -719528L; day <= 2932896L; day += 733) {
      dates.add(LocalDate.ofEpochDay(day));
    }
    for (int y = 2019; y <= 2021; y++) {
      for (int doy = 1; doy <= 366; doy++) {
        try {
          dates.add(LocalDate.ofYearDay(y, doy));
        } catch (RuntimeException ignored) {
          // 2021 is not a leap year; day 366 does not exist
        }
      }
    }
    dates.addAll(List.of(
        LocalDate.of(1582, 10, 4), LocalDate.of(1582, 10, 15),
        LocalDate.of(1, 1, 1), LocalDate.of(9999, 12, 31),
        LocalDate.of(1970, 1, 1), LocalDate.of(1969, 12, 31)));
    for (LocalDate d : dates) {
      JsonObject o = new JsonObject();
      o.addProperty("kind", "localDate");
      o.addProperty("date", d.toString());
      long ts = Utilities.localDateToTimestamp(d);
      o.addProperty("ts", Long.toString(ts));
      o.addProperty("roundtrip", Utilities.timestampToLocalDate(ts).toString());
      w.println(o.toString());
    }
    // timestampToLocalDate over raw timestamps (mid-day and negative).
    Random rng = new Random(31337L);
    for (int i = 0; i < 1200; i++) {
      long t = (long) ((rng.nextDouble() - 0.5) * 2.0e13) + rng.nextInt(86400000);
      JsonObject o = new JsonObject();
      o.addProperty("kind", "tsToDate");
      o.addProperty("time", Long.toString(t));
      o.addProperty("date", Utilities.timestampToLocalDate(t).toString());
      w.println(o.toString());
    }
  }

  // -------------------------------------------------------------- primitive

  private static JsonObject primRow(String inputKind, Object value) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "primitive");
    o.addProperty("inputKind", inputKind);
    if (value == null) {
      o.add("value", JsonNull.INSTANCE);
    } else {
      o.addProperty("value", String.valueOf(value));
    }
    try {
      Object result = Utilities.primitive(value == null ? null : primOf(inputKind, value));
      if (result == null) {
        o.add("result", JsonNull.INSTANCE);
        o.addProperty("resultClass", "null");
      } else {
        o.addProperty("result", String.valueOf(result));
        o.addProperty("resultClass", result.getClass().getSimpleName());
      }
    } catch (Throwable e) {
      o.addProperty("result", err(e));
      o.addProperty("resultClass", "ERR");
    }
    return o;
  }

  private static JsonPrimitive primOf(String inputKind, Object value) {
    return switch (inputKind) {
      case "bool" -> new JsonPrimitive(Boolean.valueOf((String) value));
      case "string" -> new JsonPrimitive((String) value);
      case "char" -> new JsonPrimitive(((String) value).charAt(0));
      case "double" -> new JsonPrimitive(Double.valueOf((String) value));
      case "int" -> new JsonPrimitive(Integer.valueOf((String) value));
      case "long" -> new JsonPrimitive(Long.valueOf((String) value));
      case "float" -> new JsonPrimitive(Float.valueOf((String) value));
      default -> throw new IllegalStateException(inputKind);
    };
  }

  private static void writePrimitive(PrintWriter w) {
    w.println(primRow("bool", "true").toString());
    w.println(primRow("bool", "false").toString());
    for (String s : List.of("Foo", "", "1.5", "true")) {
      w.println(primRow("string", s).toString());
    }
    w.println(primRow("char", "x").toString());
    w.println(primRow("null", null).toString());
    Random rng = new Random(4242L);
    for (int i = 0; i < 500; i++) {
      w.println(primRow("double", Double.toString(rng.nextDouble() * 4000 - 2000)).toString());
    }
    for (double d : new double[] {
        1.2, 1.5, 1.501, 1.7, -0.5, 0.0, -0.0, 2147483647.0, 2147483648.0,
        -2147483648.0, -2147483649.0, 1.0e300, -1.0e300, Double.NaN,
        Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY}) {
      w.println(primRow("double", Double.toString(d)).toString());
    }
    for (int i = 0; i < 250; i++) {
      w.println(primRow("int", Integer.toString(rng.nextInt())).toString());
    }
    for (long v : new long[] {3000000000L, -3000000000L, 5L, Long.MAX_VALUE, Long.MIN_VALUE}) {
      w.println(primRow("long", Long.toString(v)).toString());
    }
    for (int i = 0; i < 250; i++) {
      long v = rng.nextLong();
      w.println(primRow("long", Long.toString(v)).toString());
    }
    for (float f : new float[] {1.5f, 2.0f, -3.25f, 1.0e30f}) {
      w.println(primRow("float", Float.toString(f)).toString());
    }
  }

  // ------------------------------------------------------------------- risk

  private static void writeRisk(PrintWriter w) {
    Random rng = new Random(99L);
    double[] periods = {1000.0, 86400000.0, 604800000.0, 31557600000.0, 1.0};
    double[] steps = {0.0, 500.0, 1000.0, 604800000.0, 1209600000.0, 31557600000.0};
    for (int i = 0; i < 200; i++) {
      double risk = rng.nextDouble();
      double period = periods[i % periods.length];
      double step = steps[i % steps.length];
      JsonObject o = new JsonObject();
      o.addProperty("kind", "risk3");
      o.addProperty("risk", Double.toString(risk));
      o.addProperty("period", Double.toString(period));
      o.addProperty("step", Double.toString(step));
      o.addProperty("result", Double.toString(Utilities.convertRiskToTimestep(risk, period, step)));
      w.println(o.toString());
    }
    // risk grid: 25 risks x 5 periods x 6 steps with boundary risks
    double[] risks = {0.0, 1.0, 0.5, -0.5, 2.0};
    for (double risk : risks) {
      for (double period : periods) {
        for (double step : steps) {
          JsonObject o = new JsonObject();
          o.addProperty("kind", "risk3");
          o.addProperty("risk", Double.toString(risk));
          o.addProperty("period", Double.toString(period));
          o.addProperty("step", Double.toString(step));
          o.addProperty("result",
              Double.toString(Utilities.convertRiskToTimestep(risk, period, step)));
          w.println(o.toString());
        }
      }
    }
    for (int i = 0; i < 200; i++) {
      double risk = rng.nextDouble();
      double period = periods[i % periods.length];
      JsonObject o = new JsonObject();
      o.addProperty("kind", "risk2");
      o.addProperty("risk", Double.toString(risk));
      o.addProperty("period", Double.toString(period));
      o.addProperty("result", Double.toString(Utilities.convertRiskToTimestep(risk, period)));
      w.println(o.toString());
    }
  }

  // ---------------------------------------------------------------- compare

  private static JsonObject typedVal(String type, String value) {
    JsonObject o = new JsonObject();
    o.addProperty("t", type);
    if (value == null) {
      o.add("v", JsonNull.INSTANCE);
    } else {
      o.addProperty("v", value);
    }
    return o;
  }

  private static Object fromTyped(JsonObject o) {
    String type = o.get("t").getAsString();
    if (o.get("v").isJsonNull()) {
      return null;
    }
    String v = o.get("v").getAsString();
    return switch (type) {
      case "double" -> Double.valueOf(v);
      case "int" -> Integer.valueOf(v);
      case "long" -> Long.valueOf(v);
      case "bool" -> Boolean.valueOf(v);
      case "string" -> v;
      case "code" -> {
        String[] parts = v.split("\\|", -1);
        yield new Code(parts[0], parts[1], parts[2]);
      }
      default -> throw new IllegalStateException(type);
    };
  }

  private static void compareRow(PrintWriter w, String overload,
      JsonObject lhs, JsonObject rhs, String op) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "compare");
    o.addProperty("overload", overload);
    o.add("lhs", lhs);
    o.add("rhs", rhs);
    o.addProperty("op", op);
    Object l = fromTyped(lhs);
    Object r = fromTyped(rhs);
    String result = switch (overload) {
      case "object" -> orErr(() -> Utilities.compare(l, r, op), Object::toString);
      case "double" -> orErr(() -> Utilities.compare((Double) l, (Double) r, op), Object::toString);
      case "boolean" -> orErr(() -> Utilities.compare((Boolean) l, (Boolean) r, op),
          Object::toString);
      case "string" -> orErr(() -> Utilities.compare((String) l, (String) r, op), Object::toString);
      case "integer" -> orErr(() -> Utilities.compare((Integer) l, (Integer) r, op),
          Object::toString);
      case "code" -> orErr(() -> Utilities.compare((Code) l, (Code) r, op), Object::toString);
      default -> throw new IllegalStateException(overload);
    };
    o.addProperty("result", result);
    w.println(o.toString());
  }

  private static void writeCompare(PrintWriter w) {
    double[] dvals = {
      1.2, 1.8, 1.2, 0.0, -0.0, -1.5, 100.0, Double.NaN,
      Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY, 4.9e-324, -4.9e-324};
    for (double a : dvals) {
      for (double b : dvals) {
        for (String op : OPS) {
          compareRow(w, "double",
              typedVal("double", Double.toString(a)), typedVal("double", Double.toString(b)), op);
        }
      }
    }
    for (boolean a : new boolean[] {false, true}) {
      for (boolean b : new boolean[] {false, true}) {
        for (String op : OPS) {
          compareRow(w, "boolean",
              typedVal("bool", Boolean.toString(a)), typedVal("bool", Boolean.toString(b)), op);
        }
      }
    }
    String[] svals = {"A", "Z", "foo", "foobar", "", "a", "Z", "é", "aa", "aB"};
    for (String a : svals) {
      for (String b : svals) {
        for (String op : OPS) {
          compareRow(w, "string", typedVal("string", a), typedVal("string", b), op);
        }
      }
    }
    int[] ivals = {-1, 0, 1, 42, -42, Integer.MAX_VALUE, Integer.MIN_VALUE};
    for (int a : ivals) {
      for (int b : ivals) {
        for (String op : OPS) {
          compareRow(w, "integer",
              typedVal("int", Integer.toString(a)), typedVal("int", Integer.toString(b)), op);
        }
      }
    }
    // Object overload: same-type dispatch, mixed Numbers (compared as
    // doubles), mismatched types, and nulls.
    for (String op : OPS) {
      compareRow(w, "object", typedVal("double", "1.5"), typedVal("int", "2"), op);
      compareRow(w, "object", typedVal("int", "2"), typedVal("double", "1.5"), op);
      compareRow(w, "object", typedVal("long", "3000000000"), typedVal("int", "3"), op);
      compareRow(w, "object", typedVal("bool", "true"), typedVal("string", "Z"), op);
      compareRow(w, "object", typedVal("string", "foo"), typedVal("double", "1.0"), op);
      compareRow(w, "object", typedVal("string", "foo"), typedVal("string", "foobar"), op);
      compareRow(w, "object", typedVal("null", null), typedVal("string", "x"), op);
      compareRow(w, "object", typedVal("null", null), typedVal("null", null), op);
      compareRow(w, "object", typedVal("string", "x"), typedVal("null", null), op);
    }
    // Codes via the Object and Code overloads; display is not part of equals.
    String[][] codes = {
      {"SNOMED", "123", "Display A"}, {"SNOMED", "123", "Display B"},
      {"SNOMED", "124", "Display A"}, {"LOINC", "123", "Display A"}};
    for (String[] a : codes) {
      for (String[] b : codes) {
        for (String op : OPS) {
          compareRow(w, "code",
              typedVal("code", String.join("|", a)), typedVal("code", String.join("|", b)), op);
          compareRow(w, "object",
              typedVal("code", String.join("|", a)), typedVal("code", String.join("|", b)), op);
        }
      }
    }
    // Typed overloads with a null lhs agree with the Object overload on the
    // nil operators and on unsupported operators (both return false there);
    // those rows are included. (Supported-operator rows with a null lhs are
    // excluded on purpose: the statically typed Java overloads throw NPE
    // where the Object overload returns false — see T06 porting notes.)
    for (String op : new String[] {"is nil", "is not nil", "~="}) {
      compareRow(w, "double", typedVal("double", null), typedVal("double", null), op);
      compareRow(w, "boolean", typedVal("bool", null), typedVal("bool", null), op);
      compareRow(w, "string", typedVal("string", null), typedVal("string", null), op);
      compareRow(w, "integer", typedVal("int", null), typedVal("int", null), op);
    }
  }

  // ------------------------------------------------------------ parse range

  private static void rangeRow(PrintWriter w, String input) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "parseRange");
    o.addProperty("input", input);
    try {
      Range<Long> r = Utilities.parseDateRange(input);
      o.addProperty("min", Long.toString(r.getMinimum()));
      o.addProperty("max", Long.toString(r.getMaximum()));
    } catch (Throwable e) {
      o.addProperty("result", err(e));
    }
    w.println(o.toString());
  }

  private static void writeParseRange(PrintWriter w) {
    LocalDate base = LocalDate.of(2019, 1, 1);
    for (int i = 0; i < 400; i++) {
      LocalDate start = base.plusDays(i * 3L);
      LocalDate end = start.plusDays(i % 97);
      rangeRow(w, start + "-" + end);
    }
    for (int i = 0; i < 200; i++) {
      LocalDate start = base.plusDays(i * 5L);
      LocalDate end = start.minusDays(i % 50); // reversed: Range.between sorts
      rangeRow(w, start + "-" + end);
    }
    Random rng = new Random(8080L);
    for (int i = 0; i < 500; i++) {
      long a = (long) (rng.nextDouble() * 2.0e12);
      long b = a + (long) (rng.nextDouble() * 1.0e10);
      rangeRow(w, a + "-" + b);
    }
    for (String bad : List.of(
        "silliness", "", "-", "123-", "2020-09-05-2021-08-03", "1599264000000-1628035199999",
        "2020-13-01-2021-01-01", "2020-02-30-2021-01-01", "123-456-789", "1-2",
        "2021-08-03-2020-09-05", "1628035199999-1599264000000", "abc-def", " 1-2")) {
      rangeRow(w, bad);
    }
  }

  // -------------------------------------------------------------- resources

  private static String sha256(String text) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    byte[] hash = digest.digest(text.getBytes(StandardCharsets.UTF_8));
    StringBuilder hex = new StringBuilder();
    for (byte b : hash) {
      hex.append(String.format("%02x", b));
    }
    return hex.toString();
  }

  private static void resourceRow(PrintWriter w, String mode, String name, Call<String> call) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "resource");
    o.addProperty("mode", mode);
    o.addProperty("name", name);
    try {
      String content = call.run();
      o.addProperty("length", content.length());
      o.addProperty("sha256", sha256(content));
      if (content.length() <= 200) {
        o.addProperty("content", content);
      }
    } catch (Throwable e) {
      o.addProperty("result", err(e));
    }
    w.println(o.toString());
  }

  private static void writeResources(PrintWriter w, Path outdir) throws Exception {
    for (String name : List.of(
        "synthea.properties", "names.yml", "biometrics.yml", "version.txt",
        "no/such-file.txt", "modules/allergic_rhinitis.json")) {
      resourceRow(w, "plain", name, () -> Utilities.readResource(name));
      resourceRow(w, "stripBOM", name, () -> Utilities.readResourceAndStripBOM(name));
    }
    // A free file outside the classpath, with a BOM and non-ASCII content.
    String freeContent = "\ufeffFree file content — café\nsecond line\n";
    Path free = outdir.resolve("freefile.txt");
    Files.writeString(free, freeContent, StandardCharsets.UTF_8);
    String freePath = free.toAbsolutePath().toString();
    JsonObject meta = new JsonObject();
    meta.addProperty("kind", "freefile");
    meta.addProperty("content", freeContent);
    w.println(meta.toString());
    resourceRow(w, "orPath", freePath, () -> Utilities.readResourceOrPath(freePath));
    resourceRow(w, "freeStrip", freePath, () -> Utilities.readResource(freePath, true, true));
    resourceRow(w, "freeNoStrip", freePath, () -> Utilities.readResource(freePath, false, true));
    resourceRow(w, "orPathMissing", freePath + ".missing",
        () -> Utilities.readResourceOrPath(freePath + ".missing"));
    resourceRow(w, "classpathOnlyFree", freePath, () -> Utilities.readResource(freePath));
  }

  // ----------------------------------------------------------------- dicom

  private static void writeDicom(PrintWriter w) {
    long[] times = {0L, -1L, 1L, Long.MAX_VALUE, Long.MIN_VALUE, 1234567890000L, -1234567890000L};
    int[][] seriesInstance = {{0, 0}, {-1, -1}, {2, 3}, {Integer.MAX_VALUE, Integer.MAX_VALUE}, {1, 0}};
    for (int seed = 0; seed < 40; seed++) {
      for (long t : times) {
        for (int[] si : seriesInstance) {
          JsonObject o = new JsonObject();
          o.addProperty("kind", "dicom");
          o.addProperty("seed", seed);
          o.addProperty("time", Long.toString(t));
          o.addProperty("series", si[0]);
          o.addProperty("instance", si[1]);
          DefaultRandomNumberGenerator rng = new DefaultRandomNumberGenerator(seed);
          o.addProperty("uid", Utilities.randomDicomUid(rng, t, si[0], si[1]));
          w.println(o.toString());
        }
      }
    }
    // A stream from one generator: consecutive salts from one RNG.
    DefaultRandomNumberGenerator rng = new DefaultRandomNumberGenerator(2024L);
    for (int i = 0; i < 60; i++) {
      JsonObject o = new JsonObject();
      o.addProperty("kind", "dicomStream");
      o.addProperty("seed", 2024);
      o.addProperty("uid", Utilities.randomDicomUid(rng, 1000L * i, i, i + 1));
      w.println(o.toString());
    }
  }

  // ------------------------------------------------------------ strToObject

  private static void strRow(PrintWriter w, String clazzName, Class<?> clazz, String value) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "strToObject");
    o.addProperty("clazz", clazzName);
    o.addProperty("value", value);
    o.addProperty("result", orErr(() -> Utilities.strToObject(clazz, value), v -> {
      if (v instanceof Float f) {
        return "Float:" + Float.toString(f);
      }
      if (v instanceof Double d) {
        return "Double:" + Double.toString(d);
      }
      return v.getClass().getSimpleName() + ":" + v;
    }));
    w.println(o.toString());
  }

  private static void writeStrToObject(PrintWriter w) {
    Map<String, Class<?>> classes = new LinkedHashMap<>();
    classes.put("Boolean", Boolean.class);
    classes.put("boolean", Boolean.TYPE);
    classes.put("Byte", Byte.class);
    classes.put("byte", Byte.TYPE);
    classes.put("Short", Short.class);
    classes.put("short", Short.TYPE);
    classes.put("Integer", Integer.class);
    classes.put("int", Integer.TYPE);
    classes.put("Long", Long.class);
    classes.put("long", Long.TYPE);
    classes.put("Float", Float.class);
    classes.put("float", Float.TYPE);
    classes.put("Double", Double.class);
    classes.put("double", Double.TYPE);
    List<String> values = new ArrayList<>(List.of(
        "true", "false", "TRUE", "yes", "0", "1", "-1", "2", "5", "7", "127", "128", "-128",
        "-129", "32767", "32768", "-32768", "2147483647", "2147483648", "-2147483648",
        "9223372036854775807", "9223372036854775808", "-9223372036854775808",
        "2.5", "4.8", "-0.0", "1e3", "1.5f", "NaN", "Infinity", "-Infinity", "abc", "",
        " 5", "5 ", "+5", "--5", "0x10", "1_000"));
    Random rng = new Random(60606L);
    for (int i = 0; i < 50; i++) {
      values.add(Integer.toString(rng.nextInt()));
    }
    for (int i = 0; i < 20; i++) {
      values.add(Double.toString(rng.nextDouble() * 1e6 - 5e5));
    }
    for (Map.Entry<String, Class<?>> e : classes.entrySet()) {
      for (String v : values) {
        strRow(w, e.getKey(), e.getValue(), v);
      }
    }
    strRow(w, "Date", java.util.Date.class, "oops");
    strRow(w, "String", String.class, "hello");
  }

  // -------------------------------------------------------------- clean map

  private static void writeCleanMap(PrintWriter w) {
    Random rng = new Random(111213L);
    for (int i = 0; i < 120; i++) {
      LinkedHashMap<String, Object> map = new LinkedHashMap<>();
      JsonArray input = new JsonArray();
      int n = rng.nextInt(8);
      for (int j = 0; j < n; j++) {
        String key = "k" + j;
        JsonObject entry = new JsonObject();
        entry.addProperty("k", key);
        if (rng.nextInt(3) == 0) {
          map.put(key, null);
          entry.add("v", JsonNull.INSTANCE);
        } else {
          String val = "v" + rng.nextInt(100);
          map.put(key, val);
          entry.addProperty("v", val);
        }
        input.add(entry);
      }
      JsonObject o = new JsonObject();
      o.addProperty("kind", "cleanMap");
      o.add("input", input);
      Utilities.cleanMap(map);
      JsonArray cleaned = new JsonArray();
      for (Map.Entry<String, Object> e : map.entrySet()) {
        JsonObject entry = new JsonObject();
        entry.addProperty("k", e.getKey());
        entry.addProperty("v", String.valueOf(e.getValue()));
        cleaned.add(entry);
      }
      o.add("cleaned", cleaned);
      w.println(o.toString());
    }
  }

  // ------------------------------------------------------------------ walk

  private static void writeWalk(PrintWriter w, Path outdir) throws Exception {
    Path tree = outdir.resolve("walktree");
    Files.createDirectories(tree.resolve("sub/deep"));
    Files.createDirectories(tree.resolve("empty"));
    Files.writeString(tree.resolve("a.json"), "{}");
    Files.writeString(tree.resolve("b.txt"), "x");
    Files.writeString(tree.resolve("sub/c.json"), "{}");
    Files.writeString(tree.resolve("sub/d.json.bak"), "{}");
    Files.writeString(tree.resolve("sub/deep/e.json"), "{}");
    Files.writeString(tree.resolve("sub/deep/f.JSON"), "{}");
    List<String> found = new ArrayList<>();
    Utilities.walkAllModules(tree, p -> found.add(tree.relativize(p).toString()));
    found.sort(String::compareTo);
    JsonObject o = new JsonObject();
    o.addProperty("kind", "walk");
    JsonArray arr = new JsonArray();
    for (String f : found) {
      arr.add(f.replace('\\', '/'));
    }
    o.add("files", arr);
    w.println(o.toString());
  }

  // ------------------------------------------------------------ time series

  private static void writeTimeSeries(PrintWriter w) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "timeSeries");
    TimeSeriesData ts = new TimeSeriesData(2.5);
    Random rng = new Random(2718L);
    JsonArray vals = new JsonArray();
    for (int i = 0; i < 1000; i++) {
      double v = rng.nextDouble() * 100 - 50;
      ts.addValue(v);
      vals.add(Double.toString(v));
    }
    o.addProperty("period", Double.toString(ts.getPeriod()));
    o.add("values", vals);
    o.addProperty("size", ts.getValues().size());
    w.println(o.toString());

    // List constructor keeps the reference: an external add is visible.
    List<Double> backing = new ArrayList<>(List.of(1.0, 2.0, 3.0));
    TimeSeriesData ts2 = new TimeSeriesData(backing, 0.5);
    backing.add(4.0);
    JsonObject o2 = new JsonObject();
    o2.addProperty("kind", "timeSeriesList");
    o2.addProperty("period", Double.toString(ts2.getPeriod()));
    JsonArray vals2 = new JsonArray();
    for (double v : ts2.getValues()) {
      vals2.add(Double.toString(v));
    }
    o2.add("values", vals2);
    w.println(o2.toString());

    for (int cap : new int[] {0, 5, 100, -1, Integer.MIN_VALUE}) {
      JsonObject oc = new JsonObject();
      oc.addProperty("kind", "timeSeriesCapacity");
      oc.addProperty("capacity", cap);
      oc.addProperty("result", orErr(() -> {
        TimeSeriesData t = new TimeSeriesData(cap, 1.25);
        return t.getValues().size() + ":" + Double.toString(t.getPeriod());
      }, Object::toString));
      w.println(oc.toString());
    }

    TimeSeriesData ts3 = new TimeSeriesData(1.0);
    ts3.setPeriod(9.75);
    ts3.setValues(new ArrayList<>(List.of(7.0, 8.0)));
    boolean added = ts3.addValue(9.0);
    JsonObject o3 = new JsonObject();
    o3.addProperty("kind", "timeSeriesSetters");
    o3.addProperty("period", Double.toString(ts3.getPeriod()));
    o3.addProperty("added", added);
    JsonArray vals3 = new JsonArray();
    for (double v : ts3.getValues()) {
      vals3.add(Double.toString(v));
    }
    o3.add("values", vals3);
    w.println(o3.toString());
  }

  // ------------------------------------------------------------ telemedicine

  private static void writeTelemedicine(PrintWriter w) {
    JsonObject constants = new JsonObject();
    constants.addProperty("kind", "telemedicineConstants");
    constants.addProperty("current", Double.toString(Telemedicine.CURRENT_CHANCE));
    constants.addProperty("prepandemic", Double.toString(Telemedicine.PREPANDEMIC_CHANCE));
    constants.addProperty("start", Long.toString(Telemedicine.TELEMEDICINE_START_DATE));
    constants.addProperty("uptake", Long.toString(Telemedicine.TELEMEDICINE_UPTAKE_DATE));
    w.println(constants.toString());

    long[] times = {
      1420070400000L, // 2015-01-01 12:00 UTC (before start)
      Telemedicine.TELEMEDICINE_START_DATE - 1,
      Telemedicine.TELEMEDICINE_START_DATE,
      1520000000000L, // pre-pandemic era
      Telemedicine.TELEMEDICINE_UPTAKE_DATE - 1,
      Telemedicine.TELEMEDICINE_UPTAKE_DATE,
      1609459200000L, // 2021-01-01 (post-uptake)
      1700000000000L};
    for (long time : times) {
      for (int seed = 0; seed < 150; seed++) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "telemedicine");
        o.addProperty("seed", seed);
        o.addProperty("time", Long.toString(time));
        o.addProperty("result", Telemedicine.shouldEncounterBeVirtual(new Person(seed), time));
        w.println(o.toString());
      }
    }
    // One person, repeated post-uptake calls: the RNG stream advances.
    Person person = new Person(8456L);
    JsonArray stream = new JsonArray();
    for (int i = 0; i < 50; i++) {
      stream.add(Telemedicine.shouldEncounterBeVirtual(person, 1609459200000L));
    }
    JsonObject o = new JsonObject();
    o.addProperty("kind", "telemedicineStream");
    o.addProperty("seed", 8456);
    o.add("results", stream);
    w.println(o.toString());
  }
}
