package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

/** Direct actual Math.pow and StrictMath.pow evidence for T12's private compatibility helper. */
public class GrowthPowProbe {
  private static void emit(PrintWriter out, double x, double y) {
    JsonObject row = new JsonObject();
    row.addProperty("x", Long.toHexString(Double.doubleToRawLongBits(x)));
    row.addProperty("y", Long.toHexString(Double.doubleToRawLongBits(y)));
    row.addProperty("math", Long.toHexString(Double.doubleToLongBits(Math.pow(x, y))));
    row.addProperty("strict", Long.toHexString(Double.doubleToLongBits(StrictMath.pow(x, y))));
    out.println(row);
  }

  public static void main(String[] args) throws Exception {
    double[] bases = {0.0, -0.0, 1.0, -1.0, 2.0, -2.0, Double.MIN_VALUE,
        Double.MAX_VALUE, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY, Double.NaN, 0.5};
    double[] powers = {Double.NEGATIVE_INFINITY, -3, -2, -0.5, -0.0, 0.0,
        0.5, 1, 2, 3, Double.POSITIVE_INFINITY, Double.NaN, 10};
    Random rng = new Random(9917L);
    try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(
        Path.of(args[0]).resolve("pow.jsonl"), StandardCharsets.UTF_8))) {
      for (double x : bases) {
        for (double y : powers) {
          emit(out, x, y);
        }
      }
      for (int i = 0; i < 10000; i++) {
        double x = Math.exp(-8 + 16 * rng.nextDouble());
        double y = i % 7 == 0 ? 0.5 : i % 7 == 1 ? 2.0 : -20 + 40 * rng.nextDouble();
        emit(out, x, y);
      }
      for (int i = 0; i < 1000; i++) {
        double x = Double.longBitsToDouble(rng.nextLong() & Long.MAX_VALUE);
        emit(out, x, -40 + 80 * rng.nextDouble());
      }
      for (int i = 0; i < 1000; i++) {
        double x = 1 + (rng.nextDouble() - 0.5) * 0x1.0p-40;
        double y = (rng.nextBoolean() ? 1 : -1) * rng.nextDouble() * 0x1.0p55;
        emit(out, x, y);
      }
    }
  }
}
