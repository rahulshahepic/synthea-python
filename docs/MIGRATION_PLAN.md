# Migration plan: Synthea (Java) → Python, seed-for-seed

## Goal and definition of "equivalent"

With the same seed (`-s`), clinician seed (`-cs`), reference/end dates (`-r`/`-e`), population
(`-p`), location and config, `run_synthea` (Python) writes **byte-identical CSV files** to
Java Synthea at the pinned commit (`java/UPSTREAM.md`). The environment is fixed: JDK 21, UTC,
`en-US`, `generate.thread_pool_size=1`.

Phase-1 scope: the core simulation (all JSON disease modules plus the Java modules) and the
**CSV exporter**. Later: other exporters, then importers into Epic Chronicles and Caboodle (they
consume the CSV/FHIR output, so they need no simulation changes).

## Why seed parity is feasible, and the known risks

| Concern | Resolution |
|---|---|
| `java.util.Random` | A 48-bit LCG that is fully specified, so a bit-exact port is easy (T01). |
| Multithreading | Each person has an independent seeded RNG, and goldens are generated single-threaded. |
| `HashMap`/`ConcurrentHashMap` iteration order (≈56 loops iterate hash collections) | Emulate Java's bucket order for String/Integer/Long keys (T02). |
| Number formatting (`Double.toString`, `String.format` HALF_UP, `BigDecimal`) | Dedicated javacompat helpers, verified against 20k+ cases (T03). |
| `Math.log/exp/pow` 1-ulp differences between the JVM and glibc | **Residual risk.** Rare, and it can only flip a threshold comparison. If the e2e parity tests (T28) hit one, we port the specific function (fdlibm), document it, and move on. |
| Identity-hash ordering (enum/object keys in HashMaps) | Non-deterministic in Java itself. CI runs every scenario twice (`--verify-determinism`), so this would surface immediately. |

## Workflow

* `AGENTS.md`: the protocol agents follow (claim → work → review → merge).
* `docs/REVIEW.md`: the reviewer's routine and the labels.
* `docs/PORTING_GUIDE.md`: how to translate Java so the output is identical.
* `docs/port_map.toml`: which task owns which Python file. This is the overlap guard.
* `parity/`: Java probes produce goldens, and Python tests compare against them exactly.

### How parallel work stays conflict-free

1. **Atomic claims**: a task is claimed by creating the branch `task/<issue#>`. Only one agent
   can create it.
2. **File ownership**: each Python module has exactly one owner task (`docs/port_map.toml`).
   Agents may edit only their own modules, tests and probes.
3. **Skeleton first** (T04): every class is stubbed with its full signature early on. Because
   Java's import cycles are pre-broken, later tasks can proceed in parallel and depend on
   *interfaces* instead of finished code.
4. **Dependencies**: an issue is `status:ready` only when every issue it depends on is merged.

## Phases and tasks

Phases 1–2 are foundations, 3–4 the world model, 5 the engine, 6 the Java modules,
7 export, and 8 generation plus end-to-end parity.

| Task | Issue | Phase | Title | Depends on |
|---|---|---|---|---|
| T01 | #1 | 1 | javacompat: java.util.Random, UUID, RandomNumberGenerator | — |
| T02 | #2 | 1 | javacompat: hashCode, String.compareTo, HashMap/HashSet/ConcurrentHashMap iteration order | — |
| T03 | #3 | 1 | javacompat: numerics, Double.toString, String.format, BigDecimal | — |
| T04 | #4 | 1 | Port skeleton: stub every in-scope class with signatures | — |
| T05 | #5 | 2 | helpers: Config, SimpleCSV, SimpleYML | T03, T04 |
| T06 | #6 | 2 | helpers: Utilities, TimeSeriesData, Telemedicine | T01, T03, T05 |
| T07 | #7 | 2 | helpers/engine: RandomCollection, Distribution, ValueGenerators, RandomCodeGenerator, ExpressionProcessor | T01, T02, T06 |
| T08 | #8 | 3 | world/concepts: HealthRecord data model | T06, T07 |
| T09 | #9 | 3 | world/agents: Person, ExpressedSymptom, ExpressedConditionRecord | T08 |
| T10 | #10 | 3 | world/geography: Place, Location, Demographics, CMS state codes, QuadTree, Employment | T05, T07, T09 |
| T11 | #11 | 3 | world/concepts: names, race/ethnicity, specialties, vitals, biometrics, BMI, telemedicine config | T05, T07, T09 |
| T12 | #12 | 3 | world/concepts: birth statistics, growth charts, NHANES, pediatric growth | T05, T07, T09 |
| T13 | #13 | 3 | world/agents: Clinician, Provider, provider finders | T10, T11 |
| T14 | #14 | 4 | world/concepts: Costs and Claim | T03, T09, T10 |
| T15 | #15 | 4 | insurance I: Payer, PayerManager, InsurancePlan, payer adjustments, plan finders | T14 |
| T16 | #16 | 4 | insurance II: PlanRecord, CoverageRecord, plan eligibility, HealthInsuranceModule | T15 |
| T17 | #17 | 5 | engine: Components and Logic (conditions) | T09 |
| T18 | #18 | 5 | engine: Transition | T15, T17 |
| T19 | #19 | 5 | engine: Module loading/processing + control-flow States | T18 |
| T20 | #20 | 5 | engine: clinical States (Encounter, Condition, Medication, Procedure, Observation, …) | T13, T14, T19 |
| T21 | #21 | 6 | modules: LifecycleModule, BloodPressureValueGenerator | T10, T11, T12, T19 |
| T22 | #22 | 6 | modules: EncounterModule, DeathModule, Immunizations | T13, T20 |
| T23 | #23 | 6 | modules: CardiovascularDisease, ASCVD, Framingham, QualityOfLife, WeightLoss | T20, T21 |
| T24 | #24 | 6 | modules: COVID-19 immunization | T22 |
| T25 | #25 | 7 | export core: Exporter (CSV path), ExportHelper, CSVFileManager, CSVConstants | T08, T09 |
| T26 | #26 | 7 | export: CSVExporter | T16, T25 |
| T27 | #27 | 8 | engine: Generator | T16, T21, T22, T23, T24 |
| T28 | #28 | 8 | CLI (run_synthea) and end-to-end CSV parity | T26, T27 |

### Critical path

T03 → T05 → T06 → T07 → T08 → T09 → T10 → T13 → T14 → T15 → T16 → T26 → T28, with
T17 → T18 → T19 → T20 → T22 → T24 → T27 running in parallel. Up to 3–4 tasks are
claimable at once in most phases.

### After phase 1 (not yet ticketed)

* More e2e scenarios (several states, `-p 1000`, age/gender filters, different years).
* Performance work, once parity holds and is guarded by the e2e tests.
* FHIR R4 exporter, then the Epic Chronicles / Caboodle importers.
