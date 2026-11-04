package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;

/** Deterministic parity coverage for RandomNumberGenerator default overloads. */
public class RandomNumberGeneratorProbe {
  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    long[] seeds = {0L, 1L, 42L, -1L, 123456789L, Long.MAX_VALUE,
        Long.MIN_VALUE, 1735689600000L};
    try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(
        out.resolve("generator.jsonl"), StandardCharsets.UTF_8))) {
      for (long seed : seeds) {
        DefaultRandomNumberGenerator rng = new DefaultRandomNumberGenerator(seed);
        for (int i = 0; i < 1200; i++) {
          JsonObject obj = new JsonObject();
          obj.addProperty("seed", Long.toString(seed));
          obj.addProperty("i", i);
          int op = i % 12;
          switch (op) {
            case 0:
              obj.addProperty("op", "rand");
              obj.addProperty("v", Double.toString(rng.rand()));
              break;
            case 1:
              obj.addProperty("op", "randRange");
              obj.addProperty("v", Double.toString(rng.rand(-7.25, 21.5)));
              break;
            case 2:
              obj.addProperty("op", "randRound");
              obj.addProperty("v", Double.toString(rng.rand(-7.25, 21.5, 2)));
              break;
            case 3:
              obj.addProperty("op", "randDoubleArray");
              obj.addProperty("v", Double.toString(rng.rand(new double[] {-2.5, 6.25})));
              break;
            case 4:
              obj.addProperty("op", "randIntArray");
              obj.addProperty("v", Double.toString(rng.rand(new int[] {-3, 7})));
              break;
            case 5:
              obj.addProperty("op", "randChoices");
              obj.addProperty("v", rng.rand("alpha", "beta", "gamma", "delta"));
              break;
            case 6:
              obj.addProperty("op", "randBoolean");
              obj.addProperty("v", Boolean.toString(rng.randBoolean()));
              break;
            case 7:
              obj.addProperty("op", "randGaussian");
              obj.addProperty("v", Double.toString(rng.randGaussian()));
              break;
            case 8:
              obj.addProperty("op", "randInt");
              obj.addProperty("v", Integer.toString(rng.randInt()));
              break;
            case 9:
              obj.addProperty("op", "randIntBound");
              obj.addProperty("v", Integer.toString(rng.randInt(1 + (i * 7919) % 1000)));
              break;
            case 10:
              obj.addProperty("op", "randLong");
              obj.addProperty("v", Long.toString(rng.randLong()));
              break;
            default:
              obj.addProperty("op", "randUUID");
              obj.addProperty("v", rng.randUUID().toString());
              break;
          }
          obj.addProperty("count", Long.toString(rng.getCount()));
          writer.println(obj);
        }
      }
    }
  }
}
