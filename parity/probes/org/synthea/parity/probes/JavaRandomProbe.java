package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;

/**
 * Reference probe (and the TEMPLATE for writing new probes).
 *
 * <p>Writes random.jsonl: one JSON object per line, so a Python test can stream it.
 * Every probe takes exactly one argument (the output directory), is deterministic, and
 * prints nothing that depends on the clock or the machine.
 */
public class JavaRandomProbe {
  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    long[] seeds = {0L, 1L, 42L, -1L, 123456789L, Long.MAX_VALUE, Long.MIN_VALUE, 1735689600000L};
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("random.jsonl"), StandardCharsets.UTF_8))) {
      for (long seed : seeds) {
        Random r = new Random(seed);
        for (int i = 0; i < 200; i++) {
          JsonObject o = new JsonObject();
          o.addProperty("seed", Long.toString(seed));
          o.addProperty("i", i);
          // the call made at step i depends on i, to exercise interleaving (esp. nextGaussian)
          switch (i % 7) {
            case 0: o.addProperty("op", "nextDouble"); o.addProperty("v", Double.toString(r.nextDouble())); break;
            case 1: o.addProperty("op", "nextInt"); o.addProperty("v", Integer.toString(r.nextInt())); break;
            case 2: { int b = 1 + (i * 7919) % 1000; o.addProperty("op", "nextInt(" + b + ")"); o.addProperty("v", Integer.toString(r.nextInt(b))); break; }
            case 3: o.addProperty("op", "nextLong"); o.addProperty("v", Long.toString(r.nextLong())); break;
            case 4: o.addProperty("op", "nextBoolean"); o.addProperty("v", Boolean.toString(r.nextBoolean())); break;
            case 5: o.addProperty("op", "nextGaussian"); o.addProperty("v", Double.toString(r.nextGaussian())); break;
            default: o.addProperty("op", "nextInt(1<<30)"); o.addProperty("v", Integer.toString(r.nextInt(1 << 30))); break;
          }
          w.println(o.toString());
        }
        DefaultRandomNumberGenerator d = new DefaultRandomNumberGenerator(seed);
        for (int i = 0; i < 5; i++) {
          JsonObject o = new JsonObject();
          o.addProperty("seed", Long.toString(seed));
          o.addProperty("i", i);
          o.addProperty("op", "randUUID");
          o.addProperty("v", d.randUUID().toString());
          w.println(o.toString());
        }
      }
    }
  }
}
