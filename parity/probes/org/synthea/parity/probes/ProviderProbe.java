package org.synthea.parity.probes;

import com.google.gson.JsonObject;
import java.awt.geom.Point2D;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.mitre.synthea.helpers.DefaultRandomNumberGenerator;
import org.mitre.synthea.world.agents.Clinician;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.agents.Provider;
import org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderNearest;
import org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderNearestMedicare;
import org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderRandom;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;
import org.mitre.synthea.world.geography.Location;
import org.synthea.parity.probes.support.CanonicalProvider;

/**
 * T13 probe: loads providers for three states with two clinician seeds and
 * dumps every provider and clinician canonically, then runs 500 queries per
 * provider finder (nearest / nearest-Medicare / random) plus a subset of
 * Provider.findService / findServiceNewProvider calls.
 *
 * <p>The Python mirror is tests/parity/test_provider.py. Provider.clear() is
 * called before every load so each case starts from the same static state.
 */
public class ProviderProbe {

  private static final String[] STATES = {"Massachusetts", "California", "Texas"};
  private static final long[] SEEDS = {42L, 12345L};

  private static void emit(PrintWriter w, String kase, String out) {
    JsonObject o = new JsonObject();
    o.addProperty("case", kase);
    o.addProperty("out", out);
    w.println(o.toString());
  }

  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(out.resolve("provider.jsonl"), StandardCharsets.UTF_8))) {
      for (String state : STATES) {
        for (long seed : SEEDS) {
          loadCase(w, state, seed);
          opsCase(w, state, seed);
        }
      }
      for (String state : STATES) {
        finderCase(w, state);
      }
    }
  }

  private static void loadCase(PrintWriter w, String state, long seed) {
    Provider.clear();
    Location location = new Location(state, null);
    Provider.loadProviders(location, new DefaultRandomNumberGenerator(seed));
    List<Provider> providers = Provider.getProviderList();
    StringBuilder sb = new StringBuilder();
    sb.append("state=").append(state).append(" seed=").append(seed);
    sb.append("\nloaded=").append(Provider.getProviderList().size());
    for (Provider provider : providers) {
      sb.append("\n---\n").append(CanonicalProvider.dump(provider));
    }
    emit(w, "load:" + state + ":" + seed, sb.toString());
  }

  private static void opsCase(PrintWriter w, String state, long seed) {
    // Continues on the load performed by loadCase for the same state/seed.
    List<Provider> providers = Provider.getProviderList();
    Provider first = providers.get(0);
    StringBuilder sb = new StringBuilder();
    DefaultRandomNumberGenerator chooseRand = new DefaultRandomNumberGenerator(99L);
    Clinician chosen = first.chooseClinicianList("GENERAL PRACTICE", chooseRand);
    sb.append("choose1=").append(chosen.uuid)
        .append(" encountersAfter=").append(chosen.getEncounterCount());
    Clinician chosenAgain = first.chooseClinicianList("GENERAL PRACTICE", chooseRand);
    sb.append("\nchoose2=").append(chosenAgain.uuid)
        .append(" encountersAfter=").append(chosenAgain.getEncounterCount());
    DefaultRandomNumberGenerator fallbackRand = new DefaultRandomNumberGenerator(100L);
    Clinician fallback = first.chooseClinicianList("CARDIOLOGY", fallbackRand);
    sb.append("\nchooseFallback=").append(fallback.uuid)
        .append(" encountersAfter=").append(fallback.getEncounterCount());
    sb.append("\nchooseRandCount=").append(chooseRand.getCount());
    first.incrementEncounters(EncounterType.WELLNESS, 2020);
    first.incrementEncounters(EncounterType.WELLNESS, 2020);
    first.incrementProcedures(2020);
    first.incrementLabs(2021);
    first.incrementPrescriptions(2021);
    first.addRevenue(123.45);
    first.addRevenue(0.05);
    EncounterType[] types = EncounterType.values();
    for (int i = 0; i < 25; i++) {
      Provider target = providers.get(i);
      Person person = new Person(6000L + i);
      person.attributes.put(Person.COORDINATE,
          new Point2D.Double(target.getLonLat().getX(), target.getLonLat().getY()));
      EncounterType service = types[i % types.length];
      Provider found = Provider.findService(person, service, 0L);
      sb.append("\nfindService").append(i).append(" ").append(service.name())
          .append(" -> ").append(found == null ? "null" : found.uuid)
          .append(" count=").append(person.getCount());
    }
    List<String> taken = new ArrayList<>();
    taken.add(providers.get(0).uuid);
    taken.add(providers.get(1).uuid);
    for (int i = 0; i < 10; i++) {
      Provider target = providers.get(i);
      Person person = new Person(7000L + i);
      person.attributes.put(Person.COORDINATE,
          new Point2D.Double(target.getLonLat().getX(), target.getLonLat().getY()));
      EncounterType service = types[(i * 3) % types.length];
      Provider found = Provider.findServiceNewProvider(person, service, 0L, taken);
      sb.append("\nfindNew").append(i).append(" ").append(service.name())
          .append(" -> ").append(found == null ? "null" : found.uuid)
          .append(" count=").append(person.getCount());
    }
    sb.append("\n---\n").append(CanonicalProvider.dump(first));
    emit(w, "ops:" + state + ":" + seed, sb.toString());
  }

  private static void finderCase(PrintWriter w, String state) {
    Provider.clear();
    Location location = new Location(state, null);
    Provider.loadProviders(location, new DefaultRandomNumberGenerator(42L));
    List<Provider> providers = Provider.getProviderList();
    EncounterType[] types = EncounterType.values();
    StringBuilder sb = new StringBuilder();
    sb.append("state=").append(state).append(" providers=").append(providers.size());
    runFinderQueries(sb, "nearest", providers, types);
    runFinderQueries(sb, "medicare", providers, types);
    runFinderQueries(sb, "random", providers, types);
    emit(w, "finders:" + state, sb.toString());
  }

  private static void runFinderQueries(StringBuilder sb, String finderName,
      List<Provider> providers, EncounterType[] types) {
    sb.append("\nfinder=").append(finderName);
    for (int i = 0; i < 500; i++) {
      Provider target = providers.get((i * 37) % providers.size());
      Person person = new Person(5000L + i);
      double x = target.getLonLat().getX() + ((i % 7) - 3) * 0.01;
      double y = target.getLonLat().getY() + ((i % 5) - 2) * 0.01;
      person.attributes.put(Person.COORDINATE, new Point2D.Double(x, y));
      if (i % 11 == 0) {
        person.attributes.put(Person.VETERAN, "vietnam");
      }
      if (i % 13 == 0) {
        person.attributes.put(Person.RACE, "native");
      } else if (i % 7 == 0) {
        person.attributes.put(Person.RACE, "white");
      }
      EncounterType service = (i % 6 == 5) ? null : types[i % types.length];
      Provider found;
      switch (finderName) {
        case "nearest":
          found = new ProviderFinderNearest().find(providers, person, service, 0L);
          break;
        case "medicare":
          found = new ProviderFinderNearestMedicare().find(providers, person, service, 0L);
          break;
        default:
          found = new ProviderFinderRandom().find(providers, person, service, 0L);
          break;
      }
      sb.append("\nq").append(i)
          .append(" service=").append(service == null ? "null" : service.name())
          .append(" -> ").append(found == null ? "null" : found.uuid)
          .append(" count=").append(person.getCount());
    }
  }
}
