package org.synthea.parity.probes;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;

/** Java 21 reference for T02: boxed hashing, UTF-16 comparison and mutable collection order. */
public class JavaCollectionsProbe {
  private static final Gson GSON = new GsonBuilder().serializeNulls().create();
  private static final String[] TYPES = {
    "string", "integer", "long", "double", "boolean", "character", "custom"
  };
  private static final String[] KINDS = {
    "HashMap", "HashSet", "ConcurrentHashMap", "LinkedHashMap", "TreeMap"
  };

  /** A stable hash with genuine Comparable ordering, including large collision trees. */
  public static final class ProbeKey implements Comparable<ProbeKey> {
    final int value;
    ProbeKey(int value) { this.value = value; }
    @Override public int hashCode() { return value % 7; }
    @Override public boolean equals(Object other) {
      return other instanceof ProbeKey key && value == key.value;
    }
    @Override public int compareTo(ProbeKey other) { return Integer.compare(value, other.value); }
  }

  private static List<Integer> units(String text) {
    List<Integer> result = new ArrayList<>();
    for (int i = 0; i < text.length(); i++) { result.add((int) text.charAt(i)); }
    return result;
  }

  private static String randomString(Random random) {
    String[] atoms = {"Aa", "BB", "\u0000", "\u00df", "\u0130", "\u0131", "\u03c2",
        "\ud801\udc00", "\ud801\udc28", "\ud83d\ude80", "\ue000", "\ud800", "\udc00"};
    StringBuilder text = new StringBuilder();
    for (int i = random.nextInt(20); i > 0; i--) {
      if (random.nextBoolean()) { text.append(atoms[random.nextInt(atoms.length)]); }
      else { text.append((char) random.nextInt(65536)); }
    }
    return text.toString();
  }

  private static Object encoded(Object key) {
    if (key instanceof String text) { return units(text); }
    if (key instanceof Long value) { return value.toString(); }
    if (key instanceof Double value) {
      return Long.toUnsignedString(Double.doubleToLongBits(value), 16);
    }
    if (key instanceof Character value) { return (int) value.charValue(); }
    if (key instanceof ProbeKey value) { return value.value; }
    return key;
  }

  private static void hashing(Path out) throws Exception {
    Random random = new Random(0x21C011EC710L);
    long[] longEdges = {Long.MIN_VALUE, Long.MAX_VALUE, -1L, 0L, 1L, 1L << 32};
    long[] doubleEdges = {0L, Long.MIN_VALUE, 0x7ff8000000000000L, 0xfff0000000000001L,
        0x7ff0000000000000L, 0xfff0000000000000L, 1L, 0x000fffffffffffffL};
    try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(
        out.resolve("hashes.jsonl"), StandardCharsets.UTF_8))) {
      for (int i = 0; i < 1500; i++) {
        String text = randomString(random), other = randomString(random);
        int integer = i == 0 ? Integer.MIN_VALUE : i == 1 ? Integer.MAX_VALUE : random.nextInt();
        long wide = i < longEdges.length ? longEdges[i] : random.nextLong();
        double decimal = Double.longBitsToDouble(
            i < doubleEdges.length ? doubleEdges[i] : random.nextLong());
        boolean flag = random.nextBoolean();
        char character = (char) random.nextInt(65536);
        Object[] objects = {text, integer, wide, decimal, flag, character, null};
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("string", units(text)); row.put("other", units(other));
        row.put("integer", integer); row.put("long", Long.toString(wide));
        row.put("double", encoded(decimal)); row.put("boolean", flag);
        row.put("character", (int) character);
        row.put("hashes", Arrays.asList(text.hashCode(), Integer.hashCode(integer),
            Long.hashCode(wide), Double.hashCode(decimal), Boolean.hashCode(flag),
            Character.hashCode(character)));
        row.put("objectsHash", Objects.hash(objects));
        row.put("arrayHash", Arrays.hashCode(objects));
        row.put("listHash", Arrays.asList(objects).hashCode());
        row.put("longArrayHash", Arrays.hashCode(new long[] {wide, -1L, Long.MIN_VALUE}));
        row.put("doubleArrayHash", Arrays.hashCode(new double[] {decimal, -0.0, Double.NaN}));
        row.put("booleanArrayHash", Arrays.hashCode(new boolean[] {flag, true, false}));
        row.put("compare", text.compareTo(other));
        row.put("compareIgnoreCase", text.compareToIgnoreCase(other));
        writer.println(GSON.toJson(row));
      }
    }
    try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(
        out.resolve("case-mappings.jsonl"), StandardCharsets.UTF_8))) {
      for (int cp = 0; cp <= Character.MAX_CODE_POINT; cp++) {
        int upper = Character.toUpperCase(cp), lower = Character.toLowerCase(cp);
        if (upper != cp || lower != cp) {
          writer.println(GSON.toJson(Arrays.asList(cp, upper, lower)));
        }
      }
    }
  }

  private static String collision(int index) {
    StringBuilder text = new StringBuilder();
    for (int bit = 0; bit < 6; bit++) { text.append((index & (1 << bit)) == 0 ? "Aa" : "BB"); }
    return text.toString();
  }

  private static Object key(String type, int index, Random random) {
    switch (type) {
      case "string":
        return index < 64 ? collision(index) : "k" + index + "-" + random.nextInt(100000);
      case "integer": return index < 50 ? (index << 16) | index : random.nextInt();
      case "long": return index == 0 ? Long.MIN_VALUE : index == 1 ? Long.MAX_VALUE
          : (long) index << 32 | (random.nextInt() & 0xffffffffL);
      case "double": return index == 0 ? -0.0 : index == 1 ? 0.0 : index == 2 ? Double.NaN
          : Double.longBitsToDouble(random.nextLong());
      case "boolean": return random.nextBoolean();
      case "character": return (char) random.nextInt(65536);
      case "custom": return new ProbeKey(index);
      default: throw new IllegalArgumentException(type);
    }
  }

  @SuppressWarnings({"unchecked", "rawtypes"})
  private static Map<Object, Integer> map(String kind, int ctor, int capacity,
      float loadFactor, int concurrency, boolean accessOrder, Map<Object, Integer> source) {
    switch (kind) {
      case "HashMap":
        return ctor == 0 ? new HashMap<>() : ctor == 1 ? new HashMap<>(capacity)
            : ctor == 2 ? new HashMap<>(source) : new HashMap<>(capacity, loadFactor);
      case "ConcurrentHashMap":
        return ctor == 0 ? new ConcurrentHashMap<>() : ctor == 1
            ? new ConcurrentHashMap<>(capacity) : ctor == 2 ? new ConcurrentHashMap<>(source)
            : new ConcurrentHashMap<>(capacity, loadFactor, concurrency);
      case "LinkedHashMap":
        return ctor == 0 ? new LinkedHashMap<>() : ctor == 1 ? new LinkedHashMap<>(capacity)
            : ctor == 2 ? new LinkedHashMap<>(source)
            : new LinkedHashMap<>(capacity, loadFactor, accessOrder);
      case "TreeMap":
        return ctor == 2 ? new TreeMap<>(source) : ctor == 3
            ? new TreeMap(Collections.reverseOrder()) : new TreeMap<>();
      default: throw new IllegalArgumentException(kind);
    }
  }

  private static List<Object> snapshot(Map<Object, Integer> map, HashSet<Object> set) {
    List<Object> result = new ArrayList<>();
    if (set != null) {
      for (Object key : set) { result.add(Arrays.asList(encoded(key), 1)); }
    } else {
      for (Map.Entry<Object, Integer> item : map.entrySet()) {
        result.add(Arrays.asList(encoded(item.getKey()), item.getValue()));
      }
    }
    return result;
  }

  private static void collections(Path out) throws Exception {
    try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(
        out.resolve("collections.jsonl"), StandardCharsets.UTF_8))) {
      for (String kind : KINDS) {
        for (int scenario = 0; scenario < 240; scenario++) {
          Random random = new Random(0xC011EC700L + scenario * 7919L);
          String type = TYPES[scenario % TYPES.length];
          int size = scenario == 0 ? 0 : scenario % 37 == 0 ? 5000 : random.nextInt(220);
          int ctor = scenario % 4;
          int capacity = new int[] {0, 1, 2, 3, 12, 16, 32, 64, 128, 1024}[scenario % 10];
          float loadFactor = new float[] {0.5f, 0.75f, 1.0f, 1.5f}[scenario / 4 % 4];
          int concurrency = new int[] {1, 8, 32}[scenario % 3];
          boolean accessOrder = scenario % 2 != 0;
          List<Object> keys = new ArrayList<>();
          for (int i = 0; i < Math.max(size, 20); i++) { keys.add(key(type, i, random)); }
          Collections.shuffle(keys, random);
          List<Object> initialKeys = ctor == 2 ? new ArrayList<>(keys.subList(0, size / 3))
              : new ArrayList<>();
          Map<Object, Integer> source = new LinkedHashMap<>();
          for (int i = 0; i < initialKeys.size(); i++) { source.put(initialKeys.get(i), i % 17); }
          Map<Object, Integer> map = kind.equals("HashSet") ? null
              : map(kind, ctor, capacity, loadFactor, concurrency, accessOrder, source);
          HashSet<Object> set = !kind.equals("HashSet") ? null : ctor == 0 ? new HashSet<>()
              : ctor == 1 ? new HashSet<>(capacity) : ctor == 2 ? new HashSet<>(initialKeys)
              : new HashSet<>(capacity, loadFactor);
          Map<String, Object> row = new LinkedHashMap<>();
          row.put("kind", kind); row.put("id", scenario); row.put("keyType", type);
          row.put("ctor", ctor); row.put("capacity", capacity); row.put("loadFactor", loadFactor);
          row.put("concurrency", concurrency); row.put("accessOrder", accessOrder);
          List<Object> initial = new ArrayList<>();
          if (set != null) {
            for (Object k : initialKeys) { initial.add(Arrays.asList(encoded(k), 1)); }
          } else {
            for (Map.Entry<Object, Integer> e : source.entrySet()) {
              initial.add(Arrays.asList(encoded(e.getKey()), e.getValue()));
            }
          }
          row.put("initial", initial);
          List<Object> operations = new ArrayList<>(), returns = new ArrayList<>();
          Map<Integer, Object> snapshots = new TreeMap<>();
          snapshots.put(0, snapshot(map, set));
          for (int i = 0; i < size; i++) {
            Object k = keys.get(i);
            Integer value = map instanceof ConcurrentHashMap || i % 17 != 0 ? i % 101 : null;
            operations.add(Arrays.asList("put", encoded(k), value));
            returns.add(set == null ? map.put(k, value) : set.add(k));
            if (i == 7 || i == 8 || i == 9 || i == 11 || i == 15 || i == 31 || i == 63) {
              snapshots.put(operations.size(), snapshot(map, set));
            }
          }
          snapshots.put(operations.size(), snapshot(map, set));
          for (int i = 0; i < 120; i++) {
            Object k = keys.get(random.nextInt(keys.size()));
            int op = random.nextInt(6), value = random.nextInt(100);
            if (i == 60 && scenario % 17 == 0) {
              operations.add(List.of("clear"));
              if (set == null) { map.clear(); } else { set.clear(); }
              returns.add(null);
            } else if (set != null) {
              String name = op < 3 ? "put" : op < 5 ? "remove" : "get";
              operations.add(Arrays.asList(name, encoded(k), value));
              returns.add(op < 3 ? set.add(k) : op < 5 ? set.remove(k) : set.contains(k));
            } else if (op == 0) {
              operations.add(Arrays.asList("put", encoded(k), value)); returns.add(map.put(k, value));
            } else if (op == 1) {
              operations.add(Arrays.asList("remove", encoded(k))); returns.add(map.remove(k));
            } else if (op == 2) {
              operations.add(Arrays.asList("putIfAbsent", encoded(k), value));
              returns.add(map.putIfAbsent(k, value));
            } else if (op == 3) {
              Integer computed = i % 7 == 0 ? null : value;
              operations.add(Arrays.asList("compute", encoded(k), computed));
              returns.add(map.computeIfAbsent(k, ignored -> computed));
            } else if (op == 4) {
              boolean drop = i % 7 == 0;
              operations.add(Arrays.asList("merge", encoded(k), value, drop));
              returns.add(map.merge(k, value, (a, b) -> drop ? null : a + b));
            } else {
              operations.add(Arrays.asList("get", encoded(k))); returns.add(map.get(k));
            }
            if (i % 30 == 29 || scenario == 0) { snapshots.put(operations.size(), snapshot(map, set)); }
          }
          row.put("operations", operations); row.put("returns", returns);
          row.put("snapshots", snapshots);
          writer.println(GSON.toJson(row));
        }
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Path out = Path.of(args[0]);
    Files.createDirectories(out);
    hashing(out);
    collections(out);
  }
}
