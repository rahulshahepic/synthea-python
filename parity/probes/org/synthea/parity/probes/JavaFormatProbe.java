package org.synthea.parity.probes;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.Random;

/**
 * Probe for the javacompat numerics port (T03): Double/Float.toString, String.format,
 * Math.round, double-to-int/long casts, the parse* methods and BigDecimal operations.
 *
 * <p>Writes format.jsonl: one JSON object per line. Doubles travel as raw bit patterns
 * (longs as strings) so the Python test reconstructs the exact input value; results are
 * the exact strings/values the JDK produced. Deterministic; prints nothing that depends
 * on the clock or the machine.
 */
public class JavaFormatProbe {

  private static JsonObject bitsLine(String op, double v) {
    JsonObject o = new JsonObject();
    o.addProperty("bits", Long.toString(Double.doubleToRawLongBits(v)));
    o.addProperty("op", op);
    return o;
  }

  private static void doubleToString(PrintWriter w, double d) {
    JsonObject o = bitsLine("doubleToString", d);
    o.addProperty("v", Double.toString(d));
    w.println(o.toString());
  }

  private static void floatToString(PrintWriter w, float f) {
    JsonObject o = new JsonObject();
    o.addProperty("fbits", Integer.toString(Float.floatToRawIntBits(f)));
    o.addProperty("op", "floatToString");
    o.addProperty("v", Float.toString(f));
    w.println(o.toString());
  }

  // ---- typed format arguments -------------------------------------------------

  private static JsonObject dArg(double v) {
    JsonObject a = new JsonObject();
    a.addProperty("t", "double");
    a.addProperty("bits", Long.toString(Double.doubleToRawLongBits(v)));
    return a;
  }

  private static JsonObject iArg(int v) {
    JsonObject a = new JsonObject();
    a.addProperty("t", "int");
    a.addProperty("v", Integer.toString(v));
    return a;
  }

  private static JsonObject lArg(long v) {
    JsonObject a = new JsonObject();
    a.addProperty("t", "long");
    a.addProperty("v", Long.toString(v));
    return a;
  }

  private static JsonObject sArg(String v) {
    JsonObject a = new JsonObject();
    if (v == null) {
      a.addProperty("t", "null");
    } else {
      a.addProperty("t", "string");
      a.addProperty("v", v);
    }
    return a;
  }

  private static JsonObject bArg(boolean v) {
    JsonObject a = new JsonObject();
    a.addProperty("t", "bool");
    a.addProperty("v", Boolean.toString(v));
    return a;
  }

  private static void format(PrintWriter w, String pattern, Object[] fmtArgs, JsonObject[] jsonArgs) {
    JsonObject o = new JsonObject();
    o.addProperty("op", "format");
    o.addProperty("pattern", pattern);
    JsonArray arr = new JsonArray();
    for (JsonObject a : jsonArgs) {
      arr.add(a);
    }
    o.add("args", arr);
    o.addProperty("v", String.format(Locale.US, pattern, fmtArgs));
    w.println(o.toString());
  }

  private static void formatD(PrintWriter w, String pattern, double... values) {
    for (double v : values) {
      format(w, pattern, new Object[] {v}, new JsonObject[] {dArg(v)});
    }
  }

  private static void formatI(PrintWriter w, String pattern, int... values) {
    for (int v : values) {
      format(w, pattern, new Object[] {v}, new JsonObject[] {iArg(v)});
    }
  }

  private static void formatL(PrintWriter w, String pattern, long... values) {
    for (long v : values) {
      format(w, pattern, new Object[] {v}, new JsonObject[] {lArg(v)});
    }
  }

  // ---- BigDecimal --------------------------------------------------------------

  private static void bdResult(PrintWriter w, JsonObject o, BigDecimal r) {
    o.addProperty("ts", r.toString());
    o.addProperty("ps", r.toPlainString());
    w.println(o.toString());
  }

  private static void bdError(PrintWriter w, JsonObject o) {
    o.addProperty("ts", "ERROR");
    o.addProperty("ps", "ERROR");
    w.println(o.toString());
  }

  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("format.jsonl"), StandardCharsets.UTF_8))) {

      // -- Double.toString: bulk from raw bit patterns (finite only) --------------
      long[] seeds = {42L, 8675309L, -987654321L};
      int bulk = 0;
      for (long seed : seeds) {
        Random r = new Random(seed);
        int perSeed = 0;
        while (perSeed < 7000) {
          double d = Double.longBitsToDouble(r.nextLong());
          if (Double.isNaN(d) || Double.isInfinite(d)) {
            continue;
          }
          doubleToString(w, d);
          perSeed++;
          bulk++;
        }
      }
      // -- Double.toString: curated edge cases -------------------------------------
      double[] curated = {
        0.0, -0.0, 0.125, 1.005, 2.675, 1e7, 9999999.0, 10000000.0, 1e-3, 0.001, 9.9e-4, 1e-4,
        Double.MIN_VALUE, Double.MAX_VALUE, 2.2250738585072014e-308, 2.225073858507201e-308,
        1.0 / 3.0, 2.0 / 3.0, Math.PI, 1e22, 123456.789, 0.002, 999999.5, 9999999.5,
        99999999.0, 0.000999, 0.1, 0.3, 2.5, -1.5, 100.0, 1234567.0, 12345678.0,
        Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY
      };
      for (double d : curated) {
        doubleToString(w, d);
      }
      for (int e = -320; e <= 308; e++) {
        doubleToString(w, Math.pow(10.0, e));
      }
      for (int k = 1; k <= 2000; k++) {
        doubleToString(w, k / 1000.0);
      }
      for (int k = -500; k <= 500; k++) {
        doubleToString(w, k / 7.0);
      }
      // smallest subnormals, to pin down the JDK's rendering at the bottom of the range
      for (long b = 1; b <= 40; b++) {
        doubleToString(w, Double.longBitsToDouble(b));
      }

      // -- Float.toString -----------------------------------------------------------
      Random fr = new Random(1234567L);
      int fbulk = 0;
      while (fbulk < 2000) {
        float f = Float.intBitsToFloat(fr.nextInt());
        if (Float.isNaN(f) || Float.isInfinite(f)) {
          continue;
        }
        floatToString(w, f);
        fbulk++;
      }
      float[] fcurated = {
        0.0f, -0.0f, (float) 0.1, 1.0f / 3.0f, Float.MIN_VALUE, Float.MAX_VALUE, 1e7f,
        9999999f, 0.001f, 0.0001f, 0.125f, 2.675f,
        Float.NaN, Float.POSITIVE_INFINITY, Float.NEGATIVE_INFINITY
      };
      for (float f : fcurated) {
        floatToString(w, f);
      }
      // smallest subnormals, to pin down the JDK's rendering at the bottom of the range
      for (int b = 1; b <= 40; b++) {
        floatToString(w, Float.intBitsToFloat(b));
      }

      // -- String.format ------------------------------------------------------------
      formatD(w, "%.2f", 0.125, 1.005, 2.675, -0.125, 0.0, -0.0, 1234567.891, 1e20, 0.0004999,
          9999999.999, -2.675);
      formatD(w, "%f", 1.5, -2.25, 0.0);
      formatD(w, "%,.2f", 1234567.891, -1234.5);
      formatD(w, "%10.3f", 3.14159, -3.14159);
      formatD(w, "%010.3f", 3.14159, -3.14159);
      formatD(w, "%-10.3f|", 3.14159);
      formatD(w, "%6.2f", 3.14159, 123.456);
      formatD(w, "%.0f", 2.5, 3.5, -2.5, 0.49999999999999994);
      formatD(w, "%e", 12345.678, 0.0, -0.00012345, 1e20);
      formatD(w, "%.3e", 12345.678, 9.9999e5);
      formatD(w, "%.0e", 12345.678, 9.6e5);
      formatD(w, "%(.2f", -1.5, 1.5);
      formatD(w, "%f", Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY, Double.NaN);
      formatI(w, "%d", 0, 42, -42, Integer.MAX_VALUE, Integer.MIN_VALUE);
      formatL(w, "%d", 1234567890123L, Long.MAX_VALUE, Long.MIN_VALUE);
      formatI(w, "%,d", 1234567, -1234567);
      formatL(w, "%,d", -1234567890123L);
      formatI(w, "%05d", -42, 42, 0);
      formatI(w, "%+d", 42, -42);
      formatI(w, "% d", 42, -42);
      formatI(w, "%(d", -42, 42);
      formatI(w, "%x", 255, -1, Integer.MIN_VALUE, 0, 16);
      // Long %x negatives render 64-bit in Java; the Python port infers the width
      // from the value range (see PORTING_NOTES), so only a long outside int range
      // (Long.MIN_VALUE) is reproducible from a bare Python int. -1L is omitted here
      // deliberately: as a Python int it is indistinguishable from Integer -1.
      formatL(w, "%x", Long.MIN_VALUE, 255L);
      formatI(w, "%#x", 255, 0);
      formatI(w, "%08x", 255, -1);
      format(w, "%s", new Object[] {"hello"}, new JsonObject[] {sArg("hello")});
      format(w, "%s", new Object[] {null}, new JsonObject[] {sArg(null)});
      format(w, "%s", new Object[] {1e7}, new JsonObject[] {dArg(1e7)});
      format(w, "%s", new Object[] {Boolean.TRUE}, new JsonObject[] {bArg(true)});
      format(w, "%s", new Object[] {Boolean.FALSE}, new JsonObject[] {bArg(false)});
      format(w, "%.3s", new Object[] {"abcdef"}, new JsonObject[] {sArg("abcdef")});
      format(w, "%-10s|", new Object[] {"hi"}, new JsonObject[] {sArg("hi")});
      format(w, "%2$s %1$s", new Object[] {"a", "b"},
          new JsonObject[] {sArg("a"), sArg("b")});
      format(w, "%s %<s", new Object[] {"x"}, new JsonObject[] {sArg("x")});
      format(w, "%n", new Object[] {}, new JsonObject[] {});
      format(w, "%%", new Object[] {}, new JsonObject[] {});
      format(w, "%d%%", new Object[] {95}, new JsonObject[] {iArg(95)});
      format(w, "value=%08.3f units=%s", new Object[] {3.14159, "mg"},
          new JsonObject[] {dArg(3.14159), sArg("mg")});

      // -- Math.round ---------------------------------------------------------------
      double[] roundCurated = {
        0.5, -0.5, 1.5, -1.5, 2.5, -2.5, Double.NaN, 1e30, -1e30,
        0.49999999999999994, -0.49999999999999994, 0.0, -0.0
      };
      for (double d : roundCurated) {
        JsonObject o = bitsLine("mathRound", d);
        o.addProperty("v", Long.toString(Math.round(d)));
        w.println(o.toString());
      }
      Random rr = new Random(777L);
      for (int i = 0; i < 3000; i++) {
        double d = Double.longBitsToDouble(rr.nextLong());
        if (Double.isNaN(d)) {
          continue;
        }
        JsonObject o = bitsLine("mathRound", d);
        o.addProperty("v", Long.toString(Math.round(d)));
        w.println(o.toString());
      }
      float[] roundFloatCurated = {0.5f, -0.5f, 1.5f, -1.5f, Float.NaN, 3e38f, -3e38f, 0.0f};
      for (float f : roundFloatCurated) {
        JsonObject o = new JsonObject();
        o.addProperty("fbits", Integer.toString(Float.floatToRawIntBits(f)));
        o.addProperty("op", "mathRoundFloat");
        o.addProperty("v", Integer.toString(Math.round(f)));
        w.println(o.toString());
      }
      for (int i = 0; i < 1000; i++) {
        float f = Float.intBitsToFloat(rr.nextInt());
        if (Float.isNaN(f)) {
          continue;
        }
        JsonObject o = new JsonObject();
        o.addProperty("fbits", Integer.toString(Float.floatToRawIntBits(f)));
        o.addProperty("op", "mathRoundFloat");
        o.addProperty("v", Integer.toString(Math.round(f)));
        w.println(o.toString());
      }

      // -- casts ----------------------------------------------------------------------
      double[] castCurated = {
        Double.NaN, 1e30, -1e30, 2147483647.9, 2147483648.0, -2147483648.9, 0.999, -0.999,
        Double.MAX_VALUE, -Double.MAX_VALUE, Double.MIN_VALUE, 9223372036854775807.0,
        -9223372036854775808.0, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY
      };
      for (double d : castCurated) {
        JsonObject oi = bitsLine("d2i", d);
        oi.addProperty("v", Integer.toString((int) d));
        w.println(oi.toString());
        JsonObject ol = bitsLine("d2l", d);
        ol.addProperty("v", Long.toString((long) d));
        w.println(ol.toString());
      }
      Random cr = new Random(31337L);
      for (int i = 0; i < 3000; i++) {
        double d = Double.longBitsToDouble(cr.nextLong());
        JsonObject oi = bitsLine("d2i", d);
        oi.addProperty("v", Integer.toString((int) d));
        w.println(oi.toString());
        JsonObject ol = bitsLine("d2l", d);
        ol.addProperty("v", Long.toString((long) d));
        w.println(ol.toString());
      }

      // -- parsing ----------------------------------------------------------------------
      String[] parseDoubles = {
        "1.5", " 2.5 ", "1d", "1.5f", "NaN", "-NaN", "+Infinity", "Infinity", "-Infinity",
        ".5", "1e3", "1.", "0", "-0.0", "1_000", "nan", "infinity", "1.2.3", "", "e5", "  "
      };
      for (String s : parseDoubles) {
        JsonObject o = new JsonObject();
        o.addProperty("op", "parseDouble");
        o.addProperty("s", s);
        try {
          double d = Double.parseDouble(s);
          o.addProperty("v", Long.toString(Double.doubleToRawLongBits(d)));
        } catch (NumberFormatException e) {
          o.addProperty("v", "ERROR");
        }
        w.println(o.toString());
      }
      String[] parseInts = {
        "42", "+42", "-2147483648", "2147483647", "2147483648", " 42", "0x10", "", "-0"
      };
      for (String s : parseInts) {
        JsonObject o = new JsonObject();
        o.addProperty("op", "parseInt");
        o.addProperty("s", s);
        try {
          o.addProperty("v", Integer.toString(Integer.parseInt(s)));
        } catch (NumberFormatException e) {
          o.addProperty("v", "ERROR");
        }
        w.println(o.toString());
      }
      String[] parseLongs = {
        "9223372036854775807", "-9223372036854775808", "9223372036854775808", "-1", "42"
      };
      for (String s : parseLongs) {
        JsonObject o = new JsonObject();
        o.addProperty("op", "parseLong");
        o.addProperty("s", s);
        try {
          o.addProperty("v", Long.toString(Long.parseLong(s)));
        } catch (NumberFormatException e) {
          o.addProperty("v", "ERROR");
        }
        w.println(o.toString());
      }

      // -- BigDecimal ---------------------------------------------------------------------
      double[] valueOfDoubles = {0.1, 1.005, 2.675, 1e7, 123456789.123456789, 0.0, -4.5};
      for (double d : valueOfDoubles) {
        JsonObject o = bitsLine("bdValueOf", d);
        bdResult(w, o, BigDecimal.valueOf(d));
      }
      double[] exactDoubles = {0.1, 0.5, 1.1};
      for (double d : exactDoubles) {
        JsonObject o = bitsLine("bdExactDouble", d);
        bdResult(w, o, new BigDecimal(d));
      }
      String[] bdStrings = {
        "1E+7", "1E-7", "1.00", "0.000", "0E-7", "123456789", "1.23E+8", "0.000001",
        "0.0000001", "-4.5E-9", "100", "1E+2", "0", "0.00", "-0.5"
      };
      for (String s : bdStrings) {
        JsonObject o = new JsonObject();
        o.addProperty("op", "bdFromString");
        o.addProperty("a", s);
        bdResult(w, o, new BigDecimal(s));
      }
      String[][] pairs = {
        {"1.0", "1.00"}, {"2", "3"}, {"1", "3"}, {"1", "8"}, {"10", "4"},
        {"0.1", "0.2"}, {"1E+7", "1"}, {"5.00", "2.5"}, {"-1.5", "0.5"},
        {"123.456", "789.012"}, {"22", "7"}, {"0", "0.00"}
      };
      for (String[] p : pairs) {
        BigDecimal a = new BigDecimal(p[0]);
        BigDecimal b = new BigDecimal(p[1]);
        JsonObject oAdd = new JsonObject();
        oAdd.addProperty("op", "bdAdd");
        oAdd.addProperty("a", p[0]);
        oAdd.addProperty("b", p[1]);
        bdResult(w, oAdd, a.add(b));
        JsonObject oSub = new JsonObject();
        oSub.addProperty("op", "bdSubtract");
        oSub.addProperty("a", p[0]);
        oSub.addProperty("b", p[1]);
        bdResult(w, oSub, a.subtract(b));
        JsonObject oMul = new JsonObject();
        oMul.addProperty("op", "bdMultiply");
        oMul.addProperty("a", p[0]);
        oMul.addProperty("b", p[1]);
        bdResult(w, oMul, a.multiply(b));
        JsonObject oCmp = new JsonObject();
        oCmp.addProperty("op", "bdCompareTo");
        oCmp.addProperty("a", p[0]);
        oCmp.addProperty("b", p[1]);
        oCmp.addProperty("v", Integer.toString(a.compareTo(b)));
        w.println(oCmp.toString());
      }
      String[][] divPairs = {{"1", "3"}, {"2", "3"}, {"1", "8"}, {"10", "4"}, {"22", "7"}};
      Object[][] scaleModes = {
        {10, RoundingMode.HALF_UP}, {0, RoundingMode.HALF_UP}, {2, RoundingMode.HALF_UP},
        {2, RoundingMode.HALF_EVEN}, {2, RoundingMode.DOWN}, {2, RoundingMode.CEILING},
        {2, RoundingMode.FLOOR}, {2, RoundingMode.HALF_DOWN}, {5, RoundingMode.HALF_EVEN}
      };
      for (String[] p : divPairs) {
        for (Object[] sm : scaleModes) {
          int scale = (Integer) sm[0];
          RoundingMode mode = (RoundingMode) sm[1];
          JsonObject o = new JsonObject();
          o.addProperty("op", "bdDivide");
          o.addProperty("a", p[0]);
          o.addProperty("b", p[1]);
          o.addProperty("scale", scale);
          o.addProperty("mode", mode.name());
          try {
            bdResult(w, o, new BigDecimal(p[0]).divide(new BigDecimal(p[1]), scale, mode));
          } catch (ArithmeticException e) {
            bdError(w, o);
          }
        }
      }
      String[] setScaleValues = {"12345", "1.005", "1.00", "999.5", "0"};
      Object[][] setScales = {
        {-2, RoundingMode.HALF_UP}, {2, RoundingMode.HALF_UP}, {0, RoundingMode.HALF_EVEN},
        {-1, RoundingMode.DOWN}, {3, RoundingMode.UNNECESSARY}, {0, RoundingMode.UNNECESSARY}
      };
      for (String s : setScaleValues) {
        for (Object[] sm : setScales) {
          int scale = (Integer) sm[0];
          RoundingMode mode = (RoundingMode) sm[1];
          JsonObject o = new JsonObject();
          o.addProperty("op", "bdSetScale");
          o.addProperty("a", s);
          o.addProperty("scale", scale);
          o.addProperty("mode", mode.name());
          try {
            bdResult(w, o, new BigDecimal(s).setScale(scale, mode));
          } catch (ArithmeticException e) {
            bdError(w, o);
          }
        }
      }
    }
  }
}
