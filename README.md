# synthea-python

A Python port of [Synthea](https://github.com/synthetichealth/synthea). It is meant to be
**seed-for-seed equivalent** to the Java reference: given the same seed, config and reference
date, it produces byte-identical CSV output.

| Path | What it is |
|---|---|
| `java/` | Upstream Synthea, vendored **read-only** at the commit pinned in `java/UPSTREAM.md`. It is the specification. |
| `src/synthea/` | The Python port. |
| `parity/` | Java "probes" and scenarios that generate golden outputs. The Python tests compare against these. |
| `tests/` | `unit/` holds ordinary tests. `parity/` holds Java-vs-Python comparisons. |
| `docs/` | Migration plan, porting guide and review process. |

**Agents: read [`AGENTS.md`](AGENTS.md) before doing anything.**

## Quick start

```bash
uv sync
uv run pytest            # parity tests skip locally if goldens are missing
parity/gen_golden.sh     # needs JDK 21; builds java/ and writes parity/golden/
PARITY_REQUIRED=1 uv run pytest
```

Scope (phase 1): the core simulation plus the CSV exporter. FHIR, C-CDA and the other
exporters, physiology simulation, fixed-record identity, and the Epic Chronicles/Caboodle
importers come later.

Licensed under Apache-2.0, like upstream; see `NOTICE`.
