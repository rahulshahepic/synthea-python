# Porting notes

Notes live in **one file per task**: `docs/porting_notes/T<nn>.md`. Only the task that owns a
file writes to it, so parallel PRs never conflict. Do **not** add entries to this file.

Record intentional deviations, reproduced Java quirks and suspected precision issues, in this format:

```
# T<nn> (#<issue>) <Class/area> (agent: <name>)
- <what and why>
```

Index: see `docs/porting_notes/`.
