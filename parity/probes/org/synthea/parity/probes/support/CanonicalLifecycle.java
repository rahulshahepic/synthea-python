package org.synthea.parity.probes.support;

import com.google.common.collect.Table;
import com.google.gson.*;
import java.awt.geom.Point2D;
import java.lang.reflect.*;
import java.util.*;
import org.mitre.synthea.helpers.ValueGenerator;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.*;
import org.mitre.synthea.world.geography.Location;

/** T21 snapshots: every attribute, each vital value and all generator fields, plus RNG count. */
public final class CanonicalLifecycle {
  private CanonicalLifecycle() {}
  public static JsonElement value(Object input) {
    if (input == null) return JsonNull.INSTANCE;
    if (input instanceof Boolean) return new JsonPrimitive((Boolean) input);
    if (input instanceof Number || input instanceof String || input instanceof Enum<?> || input instanceof java.time.LocalDate)
      return new JsonPrimitive(input.toString());
    if (input instanceof HealthRecord.Code) return Canonical.code((HealthRecord.Code) input);
    if (input instanceof Point2D) {
      JsonObject o = new JsonObject(); Point2D p = (Point2D) input;
      o.addProperty("x", Double.toString(p.getX())); o.addProperty("y", Double.toString(p.getY())); return o;
    }
    if (input instanceof Location) {
      Location loc = (Location) input; JsonObject o = new JsonObject();
      o.add("state", value(loc.state)); o.add("city", value(loc.city)); return o;
    }
    if (input instanceof Table<?, ?, ?>) return value(((Table<?, ?, ?>) input).rowMap());
    if (input instanceof Map<?, ?>) {
      TreeMap<String, Object> sorted = new TreeMap<>();
      ((Map<?, ?>) input).forEach((k, v) -> sorted.put(k.toString(), v));
      JsonObject o = new JsonObject(); sorted.forEach((k, v) -> o.add(k, value(v))); return o;
    }
    if (input instanceof Iterable<?>) {
      JsonArray a = new JsonArray(); for (Object item : (Iterable<?>) input) a.add(value(item)); return a;
    }
    if (input instanceof PediatricGrowthTrajectory || input instanceof PediatricGrowthTrajectory.Point
        || input instanceof NHANESSample || input instanceof Employment || input instanceof ValueGenerator) {
      TreeMap<String, Object> fields = new TreeMap<>();
      for (Class<?> type = input.getClass(); type != null; type = type.getSuperclass()) {
        for (Field f : type.getDeclaredFields()) {
          if (Modifier.isStatic(f.getModifiers()) || f.isSynthetic() || f.getName().equals("person")) continue;
          try { f.setAccessible(true); fields.put(f.getName().replaceAll("([a-z0-9])([A-Z])", "$1_$2").toLowerCase(Locale.ROOT), f.get(input)); }
          catch (IllegalAccessException ex) { throw new IllegalStateException(ex); }
        }
      }
      return value(fields);
    }
    throw new IllegalArgumentException("No Lifecycle encoder for " + input.getClass());
  }
  public static JsonObject person(Person person, long time) {
    JsonObject out = new JsonObject(), vitals = new JsonObject();
    for (VitalSign sign : VitalSign.values()) {
      if (person.vitalSigns.containsKey(sign)) {
        JsonObject vital = new JsonObject();
        vital.addProperty("value", Double.toString(person.getVitalSign(sign, time)));
        vital.add("generator", value(person.vitalSigns.get(sign)));
        vitals.add(sign.name(), vital);
      }
    }
    out.add("vitals", vitals);
    out.add("attributes", value(person.attributes));
    out.addProperty("rng_count", Long.toString(person.getCount()));
    out.addProperty("time", Long.toString(time));
    return out;
  }
}
