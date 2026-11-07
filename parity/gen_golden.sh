#!/usr/bin/env bash
# Regenerate every golden under parity/golden/ from the Java reference.
#
#   parity/gen_golden.sh                       # all probes + all scenarios
#   parity/gen_golden.sh JavaRandomProbe       # just one probe (or scenario name)
#   parity/gen_golden.sh --verify-determinism  # run scenarios twice and require identical output
#
# Probes:    every class parity/probes/org/synthea/parity/probes/*Probe.java is run as
#            `java <Class> <outdir>` and must write its files into parity/golden/<Class>/.
# Scenarios: every parity/scenarios/<name>.args is passed to Synthea's App with
#            --exporter.baseDirectory=parity/golden/scenarios/<name>/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERIFY=0
ONLY=""
for arg in "$@"; do
  case "$arg" in
    --verify-determinism) VERIFY=1 ;;
    *) ONLY="$arg" ;;
  esac
done

JAR="$("$ROOT/parity/build_java.sh" | tail -1)"
CP="$JAR:$ROOT/parity/build/probes"
# Fixed JVM environment: UTC, en-US, UTF-8. The Python port assumes exactly this.
# Math.log is a JIT intrinsic whose result differs from StrictMath (fdlibm) by CPU and execution tier. Disable ONLY the
# log intrinsic so Math.log == StrictMath.log. Do not use -XX:DisableIntrinsic=_dlog: it also changes pow/exp, which T12 matches
# against the default VM.
JAVA=(java -XX:+UnlockDiagnosticVMOptions -XX:DisableIntrinsic=_dlog -Duser.timezone=UTC -Duser.language=en -Duser.country=US -Dfile.encoding=UTF-8 -Xmx4g)
GOLDEN="$ROOT/parity/golden"
mkdir -p "$GOLDEN"

for src in $(find "$ROOT/parity/probes" -name '*Probe.java' | sort); do
  cls="$(basename "$src" .java)"
  [[ -n "$ONLY" && "$ONLY" != "$cls" ]] && continue
  echo "== probe $cls"
  rm -rf "${GOLDEN:?}/$cls" && mkdir -p "$GOLDEN/$cls"
  (cd "$ROOT/java" && "${JAVA[@]}" -cp "$CP" "org.synthea.parity.probes.$cls" "$GOLDEN/$cls")
done

run_scenario() { # name outdir
  local name="$1" out="$2"
  rm -rf "$out" && mkdir -p "$out"
  mapfile -t ARGS < <(grep -v '^\s*#' "$ROOT/parity/scenarios/$name.args" | grep -v '^\s*$')
  (cd "$ROOT/java" && "${JAVA[@]}" -cp "$JAR" App "${ARGS[@]}" "--exporter.baseDirectory=$out/") \
    > "$out.log" 2>&1 || { cat "$out.log"; return 1; }
}

for f in $(find "$ROOT/parity/scenarios" -name '*.args' | sort); do
  name="$(basename "$f" .args)"
  [[ -n "$ONLY" && "$ONLY" != "$name" ]] && continue
  echo "== scenario $name"
  run_scenario "$name" "$GOLDEN/scenarios/$name"
  if [[ "$VERIFY" == "1" ]]; then
    tmp="$(mktemp -d)"
    run_scenario "$name" "$tmp/$name"
    diff -r "$GOLDEN/scenarios/$name" "$tmp/$name" \
      || { echo "Java reference is NOT deterministic for scenario $name"; exit 1; }
    rm -rf "$tmp"
  fi
done
echo "goldens written to $GOLDEN"
