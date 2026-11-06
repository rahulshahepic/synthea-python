package org.synthea.parity.probes;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.math3.distribution.EnumeratedDistribution;
import org.apache.commons.math3.util.Pair;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.*;
import org.yaml.snakeyaml.Yaml;

/** Calls every T11 public method; names consume 1000 draws per gender/language/seed. */
public class ConceptsProbe {
  private static final Gson GSON = new GsonBuilder().serializeNulls().create();
  private static final long[] SEEDS = {0L, 1L, 42L, -1L, 123456789L, Long.MIN_VALUE, Long.MAX_VALUE};

  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    if (args.length == 1) {
      for (String flag : new String[]{"false", "true"}) {
        Process process = new ProcessBuilder(Path.of(System.getProperty("java.home"), "bin", "java").toString(),
            "-Duser.timezone=UTC", "-Duser.language=en", "-Duser.country=US", "-Dfile.encoding=UTF-8",
            "-cp", System.getProperty("java.class.path"), ConceptsProbe.class.getName(), out.toString(), flag)
            .inheritIO().start();
        if (process.waitFor() != 0) { throw new IllegalStateException("name subprocess failed"); }
      }
      return;
    }
    boolean append = Boolean.parseBoolean(args[1]);
    Config.set("generate.append_numbers_to_person_names", args[1]);
    try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(out.resolve("concepts-" + append + ".jsonl")))) {
      for (long seed : SEEDS) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("seed", Long.toString(seed));
        result.put("append", Names.appendNumbersToNames);
        List<Object> combos = new ArrayList<>();
        for (String language : new String[]{"english", "spanish", "SPANISH", "french", "ſpanish", null}) {
          for (String gender : new String[]{"M", "F"}) {
            Person person = new Person(seed);
            List<Object> draws = new ArrayList<>();
            for (int i = 0; i < 1000; i++) {
              draws.add(List.of(Names.fakeFirstName(gender, language, person),
                  Names.fakeLastName(language, person)));
            }
            combos.add(java.util.Arrays.asList(language, gender, draws, Long.toString(person.randLong())));
          }
        }
        result.put("names", combos);
        Person person = new Person(seed);
        List<String> addresses = new ArrayList<>();
        for (int i = 0; i < 1000; i++) { addresses.add(Names.fakeAddress(i % 2 == 0, person)); }
        result.put("addresses", addresses);
        result.put("addressNext", Long.toString(person.randLong()));
        List<Object> hashes = new ArrayList<>();
        for (String name : new String[]{"", "John", "Smith", "García", "José", "😀", "polygenelubricants"}) {
          hashes.add(List.of(name, Names.addHash(name)));
        }
        result.put("hashes", hashes);
        result.put("race", entries(RaceAndEthnicity.LOOK_UP_CDC_RACE));
        result.put("ethnicityCode", entries(RaceAndEthnicity.LOOK_UP_CDC_ETHNICITY_CODE));
        result.put("ethnicityDisplay", entries(RaceAndEthnicity.LOOK_UP_CDC_ETHNICITY_DISPLAY));
        List<Object> specialties = new ArrayList<>();
        for (String specialty : ClinicianSpecialty.getSpecialties()) {
          specialties.add(List.of(specialty, ClinicianSpecialty.getCMSProviderSpecialtyCode(specialty)));
        }
        specialties.add(List.of("unrecognized", ClinicianSpecialty.getCMSProviderSpecialtyCode("unrecognized")));
        result.put("specialties", specialties);
        List<Object> vitals = new ArrayList<>();
        for (VitalSign sign : VitalSign.values()) {
          vitals.add(List.of(sign.name(), sign.toString(), VitalSign.fromString(sign.toString()).name(),
              VitalSign.fromString(sign.toString().toLowerCase(java.util.Locale.ROOT)).name(),
              VitalSign.fromString(sign.name()).name()));
        }
        result.put("vitals", vitals);
        result.put("unicodeVital", VitalSign.fromString("Weİght").name());
        Map<String,Object> biometrics = new LinkedHashMap<>();
        Map<?,?> yaml = new Yaml().load(Utilities.readResource("biometrics.yml"));
        biometrics(yaml, "", biometrics);
        biometrics.put("missing", BiometricsConfig.get("absent"));
        biometrics.put("default", BiometricsConfig.get("absent", "fallback"));
        result.put("biometrics", biometrics);
        List<Object> bmis = new ArrayList<>();
        for (int i = 0; i < 200; i++) {
          double height = person.rand(1.0, 300.0), weight = person.rand(0.0, 1000.0);
          bmis.add(List.of(Double.toString(height), Double.toString(weight),
              Double.toString(BMI.calculate(height, weight)), Double.toString(BMI.weightForHeightAndBMI(height, weight))));
        }
        for (double height : new double[]{0.0, -0.0, -180.0, Double.POSITIVE_INFINITY, Double.NaN, Double.MIN_VALUE}) {
          for (double weight : new double[]{0.0, -0.0, 70.0, -70.0, Double.POSITIVE_INFINITY, Double.NaN}) {
            bmis.add(List.of(Double.toString(height), Double.toString(weight), Double.toString(BMI.calculate(height, weight)),
                Double.toString(BMI.weightForHeightAndBMI(height, weight))));
          }
        }
        result.put("bmi", bmis);
        TelemedicineConfig config = TelemedicineConfig.fromJSON();
        result.put("telemedicineStart", Long.toString(config.getTelemedicineStartTime()));
        result.put("insurance", config.getHighEmergencyUseInsuranceNames());
        List<Object> distributions = new ArrayList<>();
        for (EnumeratedDistribution<String> distribution : List.of(config.getPreTelemedHighEmergency(),
            config.getPreTelemedTypicalEmergency(), config.getTelemedHighEmergency(), config.getTelemedTypicalEmergency(),
            new TelemedicineConfig.TelemedicineProbabilities(Map.of("ambulatory", 2.0, "emergency", 1.0)).toEnumeratedDistribution(),
            new TelemedicineConfig.TelemedicineProbabilities(Map.of("ambulatory", 0.0, "emergency", 1.0, "telemedicine", 3.0)).toEnumeratedDistribution())) {
          List<Object> pmf = new ArrayList<>();
          for (Pair<String,Double> pair : distribution.getPmf()) { pmf.add(List.of(pair.getFirst(), Double.toString(pair.getSecond()))); }
          distribution.reseedRandomGenerator(seed);
          List<String> samples = new ArrayList<>();
          for (int i=0; i<1000; i++) { samples.add(distribution.sample()); }
          distributions.add(List.of(pmf, samples));
        }
        result.put("distributions", distributions);
        List<Object> boundaries = new ArrayList<>();
        for (double draw : new double[]{0.0, Math.nextDown(0.25), 0.25, Math.nextUp(0.25), 0.5, 0.75, Math.nextDown(1.0)}) {
          org.apache.commons.math3.random.Well19937c fixed = new org.apache.commons.math3.random.Well19937c(seed) {
            @Override public double nextDouble() { return draw; }
          };
          EnumeratedDistribution<String> distribution = new EnumeratedDistribution<>(fixed, List.of(
              new Pair<>("a", 0.25), new Pair<>("b", 0.25), new Pair<>("c", 0.25), new Pair<>("d", 0.25)));
          boundaries.add(List.of(Double.toString(draw), distribution.sample()));
        }
        result.put("boundaries", boundaries);
        writer.println(GSON.toJson(result));
      }
    }
  }
  private static List<Object> entries(Map<String,String> map) {
    List<Object> result = new ArrayList<>();
    for (Map.Entry<String,String> entry : map.entrySet()) { result.add(List.of(entry.getKey(), entry.getValue())); }
    return result;
  }
  private static void biometrics(Map<?,?> map, String prefix, Map<String,Object> output) {
    for (Map.Entry<?,?> entry : map.entrySet()) {
      String path = prefix + entry.getKey();
      Object value = BiometricsConfig.get(path);
      output.put(path, value);
      if (value instanceof Map) { biometrics((Map<?,?>)value, path + ".", output); }
      if (value instanceof List) {
        List<?> values = (List<?>)value;
        if (values.stream().allMatch(v -> v instanceof Number)) { output.put(path+"#doubles", BiometricsConfig.doubles(path)); }
        if (values.stream().allMatch(v -> v instanceof Integer)) { output.put(path+"#ints", BiometricsConfig.ints(path)); }
      }
    }
  }
}
