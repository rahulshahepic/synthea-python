package org.synthea.parity.probes;

import com.google.gson.Gson;
import java.awt.geom.Point2D;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;
import org.mitre.synthea.helpers.Utilities;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.Employment;
import org.mitre.synthea.world.geography.CMSStateCodeMapper;
import org.mitre.synthea.world.geography.Demographics;
import org.mitre.synthea.world.geography.Location;
import org.mitre.synthea.world.geography.Place;
import org.mitre.synthea.world.geography.quadtree.QuadTree;

/** Public geography APIs with real Person objects and the pinned upstream resources. */
public final class GeographyProbe {
  private static final Gson GSON = new Gson();

  public static void main(String[] args) throws Exception {
    Path output = Path.of(args[0]);
    Files.createDirectories(output);
    CMSStateCodeMapper cms = new CMSStateCodeMapper();
    try (BufferedWriter writer = Files.newBufferedWriter(output.resolve("draws.jsonl"),
        StandardCharsets.UTF_8)) {
      for (String state : new String[] {"Massachusetts", "California", "Texas", "Ohio", "Hawaii"}) {
        Location location = new Location(state, null);
        for (int seed = 0; seed < 500; seed++) {
          DefaultRandomNumberGenerator rng = new DefaultRandomNumberGenerator(seed);
          Person person = new Person(seed);
          Map<String, Object> row = new LinkedHashMap<>();
          row.put("state", state);
          row.put("seed", seed);
          Demographics d = location.randomCity(rng);
          row.put("id", d.id);
          row.put("city", d.city);
          row.put("county", d.county);
          row.put("population", Long.toString(d.population));
          row.put("age", d.pickAge(rng));
          row.put("gender", d.pickGender(rng));
          String race = d.pickRace(rng);
          String ethnicity = d.pickEthnicity(rng);
          row.put("race", race);
          row.put("ethnicity", ethnicity);
          row.put("language", d.languageFromRaceAndEthnicity(race, ethnicity, rng));
          int income = d.pickIncome(rng);
          row.put("income", income);
          double incomeLevel = d.incomeLevel(income);
          row.put("incomeLevel", incomeLevel);
          row.put("povertyRatio", d.povertyRatio(income));
          String education = d.pickEducation(rng);
          row.put("education", education);
          double educationLevel = d.educationLevel(education, rng);
          row.put("educationLevel", educationLevel);
          double score = d.socioeconomicScore(incomeLevel, educationLevel, rng.rand());
          row.put("score", score);
          row.put("category", d.socioeconomicCategory(score));
          String zip = location.getZipCode(d.city, rng);
          row.put("zip", zip);
          row.put("zips", location.getZipCodes(d.city));
          row.put("fips", Location.getFipsCodeByZipCode(zip));
          row.put("ssa", cms.zipToCountyCode(zip));
          row.put("countyCode", cms.stateCountyNameToCountyCode(state,
              seed % 2 == 0 ? d.county : "Missing County", rng));
          row.put("birthplace", location.randomBirthplaceByLanguage(rng,
              seed % 2 == 0 ? "spanish" : "unknown-language"));
          String pointCity = seed % 4 == 0 ? null : seed % 4 == 1 ? "Missing City" : d.city;
          if (seed % 4 == 3) {
            person.attributes.put(Person.ZIP, zip);
          }
          location.assignPoint(person, pointCity);
          Point2D.Double point = person.getLonLat();
          row.put("x", point.x);
          row.put("y", point.y);
          if (seed % 2 == 0) {
            person.attributes.put(Person.COUNTY, d.county);
          }
          location.setSocialDeterminants(person);
          Map<String, Object> determinants = new LinkedHashMap<>();
          for (String key : new String[] {Person.FOOD_INSECURITY,
              Person.SEVERE_HOUSING_COST_BURDEN, Person.UNEMPLOYED,
              Person.NO_VEHICLE_ACCESS, Person.UNINSURED}) {
            determinants.put(key, person.attributes.get(key));
          }
          row.put("sdoh", determinants);
          Employment employment = new Employment(0.35);
          List<Object> employmentStates = new ArrayList<>();
          long interval = Utilities.convertTime("months", 6);
          for (int i = 0; i < 24; i++) {
            employment.checkEmployment(person, i * interval);
            employmentStates.add(person.attributes.get(Person.UNEMPLOYED));
            employment.checkEmployment(person, i * interval + 1);
            employmentStates.add(person.attributes.get(Person.UNEMPLOYED));
          }
          row.put("employment", employmentStates);
          row.put("rngCount", rng.getCount());
          row.put("personCount", person.getCount());
          row.put("nextRand", rng.rand());
          row.put("nextPersonRand", person.rand());
          writer.write(GSON.toJson(row));
          writer.newLine();
        }
      }
    }
    QuadTree tree = new QuadTree();
    List<Place> points = new ArrayList<>();
    for (int i = 0; i < 200; i++) {
      Map<String, String> row = new LinkedHashMap<>();
      row.put("USPS", "Test"); row.put("ST", "TS");
      row.put("NAME", Integer.toString(i)); row.put("ZCTA5", "00000");
      row.put("LON", Double.toString((i * 37) % 400 - 200.0));
      row.put("LAT", Double.toString((i * 19) % 400 - 200.0));
      Place point = new Place(row);
      points.add(point);
      tree.insert(point);
    }
    try (BufferedWriter writer = Files.newBufferedWriter(output.resolve("quadtree.jsonl"),
        StandardCharsets.UTF_8)) {
      for (int i = 0; i < points.size(); i++) {
        Place point = points.get(i);
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("index", i);
        row.put("bounds", tree.hasBoundsAround(point));
        row.put("errorBounds", tree.hasBoundsAround(point, 50));
        row.put("distance", point.distance(points.get((i + 1) % points.size())));
        List<String> names = new ArrayList<>();
        for (var found : tree.query(point, i % 3 == 0 ? 0 : 75)) {
          names.add(((Place) found).name);
        }
        row.put("query", names);
        row.put("size", tree.size());
        row.put("description", tree.toString());
        writer.write(GSON.toJson(row)); writer.newLine();
      }
    }
  }
}
