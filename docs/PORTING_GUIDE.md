# Porting guide: Java → Python, seed-for-seed

Goal: for the same seed, config and reference date, the Python port makes the **same random
draws in the same order** and therefore produces **byte-identical CSV output**. Everything
here serves that goal.

## 1. Golden rules

1. **Translate, don't redesign.** Keep the Java control flow, branch order, loop order and
   method boundaries. Pythonic refactors that reorder anything (iteration, short-circuiting,
   evaluation order) break parity. Idiomatic naming (`snake_case`) is fine. Restructuring is not.
2. **Every RNG call must match.** Same method (`rand()` vs `randInt(n)` vs `randGaussian()`),
   same arguments, same order, same count, including draws whose results Java ignores.
3. **The Java is the spec, bugs included.** If the Java has an off-by-one or a quirky
   rounding, reproduce it, and note it in `docs/porting_notes/T<nn>.md`.
4. **Iteration order is part of the behaviour.** See §3.
5. **Number formatting is part of the behaviour.** See §4.

## 2. Package layout (mirror the Java packages)

| Java | Python |
|---|---|
| `java.util.Random`, `HashMap` order, `String.hashCode`, `Double.toString`, `String.format`, `Math.round`, int/long overflow, `BigDecimal` | `synthea.javacompat.*` |
| `org.mitre.synthea.helpers` | `synthea.helpers` |
| `org.mitre.synthea.engine` | `synthea.engine` |
| `org.mitre.synthea.world.{agents,concepts,geography}` | `synthea.world.{agents,concepts,geography}` |
| `org.mitre.synthea.modules` | `synthea.modules` |
| `org.mitre.synthea.export` | `synthea.export` |
| `App` | `synthea.cli` |

Module naming: one Python module per Java class, in snake_case (`HealthRecord.java` →
`health_record.py`). Nested classes stay nested, or sit next to their parent in the same module.

Resources are **never copied**. Load them through `synthea.resources.resource_path(...)`,
which points at `java/src/main/resources`.

## 3. Collections and iteration order

| Java | Python |
|---|---|
| `ArrayList`, `LinkedList`, arrays | `list` |
| `LinkedHashMap` / `LinkedHashSet` | `dict` / dict-as-ordered-set |
| `TreeMap` / `TreeSet` | sort keys at iteration time with the same comparator (Java `String.compareTo` compares UTF-16 code units; see `javacompat`) |
| `HashMap` / `HashSet` / `ConcurrentHashMap` | **`synthea.javacompat` hash-order collections** whenever the code iterates them (`for`, `keySet()`, `values()`, `entrySet()`, `stream()`), or passes them to something that does. A plain `dict` is fine only for pure lookup. |
| Gson `JsonObject` (module JSON) | `dict` from `json.load` (insertion order matches Gson's `LinkedTreeMap`) |

If you iterate a Java `HashMap` and draw random numbers inside the loop, a plain `dict` will
silently diverge. When in doubt, use the javacompat collection.

`Collections.sort` / `List.sort` are stable, and so is Python's `sort`. Port the `Comparator`
exactly. Beware comparators that are inconsistent or return non-zero for equal elements.

## 4. Numbers

* `int` is 32-bit and `long` is 64-bit, both two's complement **with silent overflow**.
  Use `javacompat` helpers (`to_int32`, `to_int64`) wherever Java arithmetic can overflow:
  hash codes, seed arithmetic, `* 31` loops.
* Integer division and `%` truncate toward zero in Java. Python's `//` and `%` floor. Use
  `javacompat.idiv` / `javacompat.irem`.
* `(int) x` truncates toward zero, and saturates for out-of-range doubles. NaN becomes 0.
* `Math.round(x)` is `floor(x + 0.5)` (as a `long`), **not** banker's rounding. Never use
  Python's `round()` for a Java `Math.round`.
* `Math.floor`, `Math.ceil`, `Math.sqrt`, `Math.abs`, `Math.min/max` map directly (mind NaN
  and -0.0 in `min`/`max`). `Math.pow`, `Math.exp`, `Math.log` map to `math.*`. Rare 1-ulp
  libm differences are a known risk. If you suspect one, note it under "Problems found"
  instead of hacking around it.
* `BigDecimal` (costs and claims) maps to `decimal.Decimal`, with the **same scale and
  RoundingMode** at each step. Use the `javacompat` helpers.
* `float` in Java (32-bit) is rare in Synthea. If you meet one, round through
  `struct.pack('f', …)`.

### String formatting

* `Double.toString(d)` / string concatenation of a double has its own format (`1.0E10`,
  `1.0E-5`, `100.0`). Use `javacompat.double_to_string`, never `str()` or `repr()`.
* `String.format("%.2f", x)` rounds **HALF_UP on the decimal digits of the shortest
  representation**, so `0.125` gives `"0.13"` and `1.005` gives `"1.01"`. Python's `f"{x:.2f}"`
  gives `"0.12"` and `"1.00"`. Use `javacompat.format`.
* `Integer.toString`, `Long.toString` and `Boolean.toString` (`true`/`false`, lowercase) all need care.

## 5. Randomness

* All randomness comes from `synthea.javacompat.random.JavaRandom` (a bit-exact port of
  `java.util.Random`, including `nextGaussian`'s cached second value), wrapped by
  `synthea.helpers.random_number_generator` (Java: `DefaultRandomNumberGenerator` and the
  default methods of `RandomNumberGenerator`).
* Never use Python's `random`, `uuid.uuid4`, `secrets`, `time.time()` or `datetime.now()`
  in simulation code.
* UUIDs: `new UUID(seed, randLong())`, formatted the way Java's `UUID.toString` does.

## 6. Time

* Synthea represents time as `long` epoch **milliseconds, UTC**. Keep it that way (Python `int`).
* The goldens run with `-Duser.timezone=UTC`. Wherever Java uses the default time zone,
  Python uses UTC.
* Port `java.time` / `Calendar` / `SimpleDateFormat` usages carefully. Write probes for
  edge cases: leap years, year boundaries, negative epochs (people born before 1970).

## 7. Hash codes

`String.hashCode` (`s[0]*31^(n-1) + …` over **UTF-16 code units**, int32 overflow),
`Long.hashCode`, `Integer.hashCode`, `Double.hashCode`, `Boolean.hashCode` (1231/1237) and
`Objects.hash` are all deterministic, and `javacompat` provides them. `Object.hashCode` (identity)
and `Enum.hashCode` are **not** deterministic across JVM runs. If Java iterates a `HashMap`
keyed by those and the order matters, the Java itself is non-deterministic: raise a
`❓ QUESTION` instead of guessing.

## 8. Out of scope (phase 1). Port as a stub that raises `NotImplementedError` if enabled

Physiology simulation (`physiology.*` = false), growth-data error editors (`growtherrors` =
false), the terminology server (`RandomCodeGenerator` network calls), fixed records / identity
(`-f`), population snapshots (`-i`/`-u`), keep-patients filters (`-k`), FHIR/C-CDA/CPCDS/BFD
and other non-CSV exporters, the flexporter, Graphviz, ChartRenderer.

When a config flag that is off by default enables one of these, the Python code checks it
and raises `NotImplementedError("<feature> not ported yet")`. It must never silently ignore it.

## 9. Porting notes

Write one file per task, `docs/porting_notes/T<nn>.md`, with an entry for every intentional
deviation, Java quirk you reproduced, or suspected libm/precision issue:

```
# T<nn> (#<issue>) <Class/area> (agent: <name>)
- <what and why>
```

Never edit another task's notes file. One file per task means parallel PRs can't conflict.
