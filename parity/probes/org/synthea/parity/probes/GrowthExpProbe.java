package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

/** Direct warmed Math.exp/StrictMath.exp evidence including subnormal and overflow boundaries. */
public class GrowthExpProbe {
  private static volatile double warmupSink;

  private static void emit(PrintWriter out, double x) {
    JsonObject row = new JsonObject();
    row.addProperty("x", Long.toHexString(Double.doubleToRawLongBits(x)));
    row.addProperty("math", Long.toHexString(Double.doubleToLongBits(Math.exp(x))));
    row.addProperty("strict", Long.toHexString(Double.doubleToLongBits(StrictMath.exp(x))));
    out.println(row);
  }

  public static void main(String[] args) throws Exception {
    for (int i = 0; i < 30000; i++) {
      warmupSink = Math.exp(((i % 6001) - 3000) / 1000.0);
    }
    double[] special = {Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY, Double.NaN,
        0.0, -0.0, Double.MAX_VALUE, -Double.MAX_VALUE, Double.MIN_VALUE, -Double.MIN_VALUE,
        -750, -745.1332191019411, -744, 709.782712893384, 710, -1};
    Random rng = new Random(11991L);
    try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(
        Path.of(args[0]).resolve("exp.jsonl"), StandardCharsets.UTF_8))) {
      for (double x : special) {
        emit(out, x);
      }
      for (int i = 0; i < 10000; i++) {
        emit(out, -750 + 1460 * rng.nextDouble());
      }
      for (int i = 0; i < 10000; i++) {
        emit(out, -3 + 6 * rng.nextDouble());
      }
      for (int i = 0; i < 10000; i++) {
        emit(out, Double.longBitsToDouble(rng.nextLong()));
      }
    }
    JsonObject platform = new JsonObject();
    platform.addProperty("java", System.getProperty("java.runtime.version"));
    platform.addProperty("architecture", System.getProperty("os.arch"));
    platform.addProperty("warmupCallsPerFunction", 30000);
    Files.writeString(Path.of(args[0]).resolve("platform.json"), platform.toString(),
        StandardCharsets.UTF_8);
  }
}
