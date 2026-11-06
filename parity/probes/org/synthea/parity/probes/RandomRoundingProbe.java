package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;

/** Java BigDecimal rounding of negative values to positive zero, with RNG continuation. */
public class RandomRoundingProbe {
  public static void main(String[] args) throws Exception {
    long[] seeds = {0L, 1L, 42L, -1L, 123456789L, Long.MAX_VALUE,
        Long.MIN_VALUE, 1735689600000L};
    int[] scales = {-1, 0, 2, 6};
    try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(
        Path.of(args[0]).resolve("rounding.jsonl"), StandardCharsets.UTF_8))) {
      for (long seed : seeds) {
        DefaultRandomNumberGenerator rng = new DefaultRandomNumberGenerator(seed);
        for (int decimals : scales) {
          for (int i = 0; i < 100; i++) {
            JsonObject row = new JsonObject();
            row.addProperty("seed", Long.toString(seed));
            row.addProperty("decimals", decimals);
            row.addProperty("value", Double.toString(rng.rand(-1e-12, -1e-13, decimals)));
            row.addProperty("count", Long.toString(rng.getCount()));
            row.addProperty("nextLong", Long.toString(rng.randLong()));
            out.println(row);
          }
        }
      }
    }
  }
}
