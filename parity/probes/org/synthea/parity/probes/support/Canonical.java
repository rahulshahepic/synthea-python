package org.synthea.parity.probes.support;

import com.google.gson.*;
import java.lang.reflect.*;
import java.math.BigDecimal;
import java.util.*;
import java.util.function.Function;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.HealthRecord.*;

/**
 * Complete HealthRecord canonical schema; Python counterpart: tests/parity/canonical/__init__.py.
 *
 * <p>Includes nulls, inherited fields and the cached private cost without computing it.
 * Longs/doubles/UUIDs are strings; maps are ordered key/value pairs. Owner links are
 * implicit, Observation.report is a UUID backlink. Later tasks add CanonicalArea.java
 * and register external encoders here, never edit this file. Unregistered types fail
 * rather than silently omit their fields. Only HealthRecord nested types are reflected.
 */
public final class Canonical {
  private Canonical() { }
  private static final Map<Class<?>, Function<Object, JsonElement>> ENCODERS =
      new LinkedHashMap<>();

  public static <T> void register(Class<T> type, Function<T, JsonElement> encoder) {
    ENCODERS.put(type, value -> encoder.apply(type.cast(value)));
  }

  private static String snake(String value) {
    return value.replaceAll("([a-z0-9])([A-Z])", "$1_$2").toLowerCase(Locale.ROOT);
  }

  public static JsonElement code(Code value) {
    if (value == null) { return JsonNull.INSTANCE; }
    JsonObject out = new JsonObject();
    out.add("system", value(value.system));
    out.add("code", value(value.code));
    out.add("display", value(value.display));
    out.add("version", value(value.version));
    out.add("value_set", value(value.valueSet));
    return out;
  }

  public static JsonElement value(Object input) {
    if (input == null) { return JsonNull.INSTANCE; }
    if (input instanceof JsonElement) { return json((JsonElement) input); }
    if (input instanceof Code) { return code((Code) input); }
    if (input instanceof Entry) { return entry((Entry) input); }
    if (input instanceof String || input instanceof Character || input instanceof UUID
        || input instanceof Long || input instanceof Double || input instanceof Float
        || input instanceof BigDecimal) { return new JsonPrimitive(input.toString()); }
    if (input instanceof Boolean) { return new JsonPrimitive((Boolean) input); }
    if (input instanceof Number) { return new JsonPrimitive((Number) input); }
    if (input instanceof Enum<?>) { return new JsonPrimitive(((Enum<?>) input).name()); }
    if (input instanceof Map<?, ?>) {
      JsonArray result = new JsonArray();
      for (Map.Entry<?, ?> item : ((Map<?, ?>) input).entrySet()) {
        JsonObject pair = new JsonObject();
        pair.add("key", value(item.getKey()));
        pair.add("value", value(item.getValue()));
        result.add(pair);
      }
      return result;
    }
    if (input instanceof Iterable<?>) {
      JsonArray result = new JsonArray();
      for (Object item : (Iterable<?>) input) { result.add(value(item)); }
      return result;
    }
    if (input instanceof ImagingStudy.Series || input instanceof ImagingStudy.Instance) {
      return fields(input);
    }
    for (Map.Entry<Class<?>, Function<Object, JsonElement>> encoder : ENCODERS.entrySet()) {
      if (encoder.getKey().isInstance(input)) { return encoder.getValue().apply(input); }
    }
    throw new IllegalArgumentException("Register a canonical encoder for " + input.getClass());
  }

  public static JsonElement json(JsonElement input) {
    if (input.isJsonObject()) {
      JsonObject out = new JsonObject();
      for (Map.Entry<String, JsonElement> item : input.getAsJsonObject().entrySet()) {
        out.add(item.getKey(), json(item.getValue()));
      }
      return out;
    }
    if (input.isJsonArray()) {
      JsonArray out = new JsonArray();
      for (JsonElement item : input.getAsJsonArray()) { out.add(json(item)); }
      return out;
    }
    if (input.isJsonPrimitive() && input.getAsJsonPrimitive().isNumber()) {
      String text = input.getAsString();
      if (text.contains(".") || text.contains("e") || text.contains("E")) {
        return new JsonPrimitive(Double.toString(input.getAsDouble()));
      }
    }
    return input;
  }

  private static JsonObject fields(Object input) {
    TreeMap<String, JsonElement> sorted = new TreeMap<>();
    try {
      for (Class<?> type = input.getClass(); type != null; type = type.getSuperclass()) {
        for (Field field : type.getDeclaredFields()) {
          if (Modifier.isStatic(field.getModifiers()) || field.isSynthetic()
              || field.getName().equals("record")) { continue; }
          field.setAccessible(true);
          Object child = field.get(input);
          String name = snake(field.getName());
          if (name.equals("report")) {
            sorted.put(name, value(child == null ? null : ((Entry) child).uuid));
          } else {
            sorted.put(name, value(child));
          }
        }
      }
    } catch (IllegalAccessException ex) { throw new IllegalStateException(ex); }
    JsonObject result = new JsonObject();
    sorted.forEach(result::add);
    return result;
  }

  public static JsonObject entry(Entry input) {
    JsonObject result = new JsonObject();
    result.addProperty("entry_class", input.getClass().getSimpleName());
    for (Map.Entry<String, JsonElement> item : fields(input).entrySet()) {
      result.add(item.getKey(), item.getValue());
    }
    return result;
  }

  public static JsonObject record(HealthRecord input) {
    JsonObject result = new JsonObject();
    result.add("provider", value(input.provider));
    result.add("encounters", value(input.encounters));
    result.add("present", value(input.present));
    result.add("death", value(input.death));
    result.add("demographics_at_record_creation", value(input.demographicsAtRecordCreation));
    return result;
  }
}
