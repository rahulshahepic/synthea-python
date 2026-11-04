# Parity harness

The Java code in `java/` is the specification. "Correct" means **the Python port produces
exactly what the Java produces**, and the comparison is always made against output that the
Java itself generated. Nobody writes goldens by hand.

```
parity/
  build_java.sh     builds java/ (gradle shadowJar) and compiles probes/ against the jar
  gen_golden.sh     runs every probe and scenario and writes parity/golden/ (git-ignored)
  probes/           Java programs that call Synthea classes and dump results as JSON/CSV
  scenarios/        end-to-end CLI argument files for Synthea's App (CSV export)
  golden/           generated output; never committed, never edited by hand
```

## Writing a probe (each porting task adds one or more)

1. Copy `probes/org/synthea/parity/probes/JavaRandomProbe.java`. Name the copy `<Area>Probe.java`.
2. `main(String[] args)` gets one argument, the output directory. Write `.jsonl`, `.json` or `.csv`
   files there.
3. Exercise the ported code broadly: many seeds, edge cases, and all branches you can reach.
   Prefer 100s of cases over a handful.
4. Output must be deterministic. Format doubles with `Double.toString(x)` (exact, round-trippable)
   and longs as strings.
5. Only the jar's classes are available (Synthea plus its dependencies, including Gson). The
   working directory is `java/`, so `Config` and resource loading behave as in a normal run.
6. Run `parity/gen_golden.sh <Area>Probe`, then write `tests/parity/test_<area>.py`. Use the
   `golden("<Area>Probe")` fixture to get the directory.

Probes may call `public` Synthea API, or use reflection for private members when necessary.
They must not modify anything under `java/`.

## CI

The `java-golden` job builds `java/`, runs `gen_golden.sh --verify-determinism` and uploads
`parity/golden` as an artifact. The result is cached, keyed on the hash of `java/**` and
`parity/**`. The `test` job downloads it and runs pytest with `PARITY_REQUIRED=1`, so a missing
golden there is a failure, not a skip.
