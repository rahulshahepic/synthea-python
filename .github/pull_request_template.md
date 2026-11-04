<!-- Title: "#<issue> <issue title>". Read AGENTS.md. Keep this body updated as you work. -->
Closes #<issue>
Agent: <muse|chatgpt>
Task: T<nn>

## Checklist (tick as you go; this is your resume point after an interruption)
- [ ] Claimed (branch `task/<issue>` pushed, issue labelled + commented)
- [ ] Probe(s) written: `parity/probes/.../<Area>Probe.java`
- [ ] Goldens generated (locally or in CI)
- [ ] Python port of every Java file in scope
- [ ] Parity tests `tests/parity/test_<area>.py` pass exactly
- [ ] Upstream JUnit tests ported to `tests/unit/` (list skipped ones below with reasons)
- [ ] `uv run python scripts/check_port_map.py --task T<nn> --no-stubs` passes
- [ ] lint / typecheck / tests green in CI
- [ ] Every acceptance criterion in the issue is met (one line each below)

## Acceptance criteria evidence
1. …

## Deviations / Java quirks reproduced (also appended to docs/PORTING_NOTES.md)
none

## Problems found (bugs in other tasks, ambiguous spec, suspected non-determinism)
none

## Skipped upstream tests (with reason)
none
