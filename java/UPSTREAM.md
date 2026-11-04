# Vendored upstream

- Source: https://github.com/synthetichealth/synthea
- Branch: master
- Commit: bd8a52ba0a54ad8c6a1004b74787a14d8c25dbcc (2026-10-21)
- Imported unmodified except that `.git` was dropped. **Read-only**: never edit anything under `java/`.

To move to a newer upstream later: replace this directory wholesale in a dedicated PR, update
this file, and let CI regenerate every golden. Any diff in parity tests is then upstream drift
that has to be ported.
