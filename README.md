# synthea-python

A Python port of [Synthea](https://github.com/synthetichealth/synthea), the synthetic patient
generator. It is **seed-for-seed equivalent** to the Java reference: given the same seed,
options and dates, it writes byte-identical CSV files.

The port covers the core simulation (every disease and lifecycle module, providers, payers,
costs, claims) and the CSV exporter. Other exporters are not ported yet; see
[What is not ported](#what-is-not-ported).

## Requirements

- Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).
- JDK 21, only if you want to run the Java reference to check parity yourself.

The port reads Synthea's own data (modules, demographics, providers, lookup tables) straight
from `java/src/main/resources`. Keep the `java/` directory when you clone or copy the repo.

## Install

```bash
git clone https://github.com/rahulshahepic/synthea-python.git
cd synthea-python
uv sync
```

## Generate patients

```bash
uv run run_synthea -c config/csv.properties -p 10 Massachusetts
```

This simulates 10 living people in Massachusetts from birth to today and writes their records
to `./output/csv/`. People who die during the simulation are written too and replaced, so
`patients.csv` can hold more than 10 rows.

> **Always pass `-c config/csv.properties`.** Synthea's own defaults turn on FHIR export (not
> ported) and turn off CSV, so without it the run finishes without writing any files.

### Common options

| Option | Meaning | Example |
|---|---|---|
| `state [city]` | Where people live (default Massachusetts) | `Texas`, `Alaska Juneau` |
| `-p N` | Number of living people to generate | `-p 100` |
| `-s SEED` | Population seed; the same seed gives the same people | `-s 42` |
| `-cs SEED` | Clinician seed | `-cs 42` |
| `-r YYYYMMDD` | Reference date (the "today" of the simulation) | `-r 20250101` |
| `-e YYYYMMDD` | End date of the simulation | `-e 20250101` |
| `-g M\|F` | Only one gender | `-g F` |
| `-a MIN-MAX` | Only this age range at the reference date | `-a 0-18` |
| `-c FILE` | Load a properties file of settings | `-c config/csv.properties` |
| `--key=value` | Override any setting in `java/src/main/resources/synthea.properties` | `--exporter.baseDirectory=./out/` |

`uv run run_synthea -h` prints the full list. Options and settings mean exactly what they mean
in Java Synthea, so the [Synthea wiki](https://github.com/synthetichealth/synthea/wiki) applies.
Where `-c` and `--key=value` set the same thing, the one given last wins.

### Reproducible runs

Fix the seeds and both dates to get the same output every time, on any machine:

```bash
uv run run_synthea -c config/csv.properties -s 42 -cs 42 -r 20250101 -e 20250101 -p 10 Massachusetts
```

Run the Java reference with the same options and the CSVs match byte for byte. See
[Check parity with Java](#check-parity-with-java).

### Output

`output/csv/` holds one file per record type: `patients`, `encounters`, `conditions`,
`medications`, `observations`, `procedures`, `immunizations`, `careplans`, `allergies`,
`devices`, `supplies`, `imaging_studies`, `claims`, `claims_transactions`, `payers`,
`payer_transitions`, `organizations` and `providers`. Synthea's
[CSV data dictionary](https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary)
describes every column. By default only the last 10 years of encounters are kept
(`exporter.years_of_history`); pass `--exporter.years_of_history=0` for whole lifetimes.

Speed: roughly 20–60 seconds per person on one core (10 people take about 4 minutes). The port
runs single-threaded and favours exact equivalence over speed, so plan for `-p 1000` to take
hours.

### Use from Python

```python
from synthea.cli import App

App.main(["-c", "config/csv.properties", "-s", "42", "-p", "5", "Massachusetts"])
```

## What is not ported

These options raise `NotImplementedError` with a message saying so, rather than silently
doing something different from Java:

- exporters other than CSV (FHIR, C-CDA, text, CPCDS, BFD and so on)
- population snapshots (`-i`, `-u`, `-t`), fixed records (`-f`), keep-patients modules (`-k`)
  and the flexporter
- the physiology simulation and growth-chart error editors
- custom exporter plugins

## Check parity with Java

Parity is checked at two levels. Probes in `parity/probes/` drive individual Java classes, and
Python tests compare against their output exactly. The scenarios in `parity/scenarios/` run the
whole Java app, and `tests/parity/test_e2e.py` runs the Python CLI with the same arguments and
requires every CSV to be byte-identical.

```bash
parity/gen_golden.sh                # needs JDK 21: builds java/, runs every probe and scenario
PARITY_REQUIRED=1 uv run pytest     # full suite; parity tests fail if goldens are missing
```

Without goldens, `uv run pytest` still runs the unit tests and skips the parity tests. CI runs
everything on every push.

To compare a run of your own, give both apps the same arguments and diff the folders:

```bash
JAR=$(parity/build_java.sh | tail -1)
ARGS="-s 7 -cs 7 -r 20250101 -e 20250101 -p 10 Texas"
(cd java && java -XX:+UnlockDiagnosticVMOptions -XX:DisableIntrinsic=_dlog -Duser.timezone=UTC \
   -Duser.language=en -Duser.country=US -Dfile.encoding=UTF-8 -cp "$JAR" App \
   -c ../config/csv.properties $ARGS --exporter.baseDirectory=/tmp/java-out/)
uv run run_synthea -c config/csv.properties $ARGS --exporter.baseDirectory=/tmp/py-out/
diff -r /tmp/java-out/csv /tmp/py-out/csv && echo identical
```

The JVM flags matter. They fix the time zone, locale and encoding the port assumes, and make
Java's `Math.log` deterministic (see `parity/gen_golden.sh`).

## Repository layout

| Path | What it is |
|---|---|
| `src/synthea/` | The Python port, laid out like the Java packages (`engine`, `modules`, `world`, `export`, `helpers`). `javacompat/` reproduces Java behaviour Python lacks: `java.util.Random`, `HashMap` iteration order, number formatting and so on. |
| `config/` | Ready-made settings files, such as `csv.properties`. |
| `java/` | Upstream Synthea, vendored **read-only** at the commit in `java/UPSTREAM.md`. It is both the specification and the source of the data files. |
| `parity/` | Java probes, end-to-end scenarios and the scripts that turn them into goldens. |
| `tests/` | `unit/` holds ordinary tests (including ported JUnit tests); `parity/` holds Java-vs-Python comparisons. |
| `docs/` | Porting guide, porting notes per task, migration plan and review process. |

## Contributing

The port was built task by task by AI agents under review. If you are an agent, read
[`AGENTS.md`](AGENTS.md) first; reviewers follow [`docs/REVIEW.md`](docs/REVIEW.md). For
anyone changing code: [`docs/PORTING_GUIDE.md`](docs/PORTING_GUIDE.md) explains how Java
behaviour is reproduced, and every change must keep `PARITY_REQUIRED=1 uv run pytest` green.

## License

Apache-2.0, like upstream Synthea. See `LICENSE` and `NOTICE`.
