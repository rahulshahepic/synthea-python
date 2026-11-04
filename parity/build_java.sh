#!/usr/bin/env bash
# Build the vendored Java reference (java/) and compile the parity probes.
# Requires JDK 21 (goldens are defined as the output of JDK 21; do not use 17).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/java/build/libs/synthea-with-dependencies.jar"
OUT="$ROOT/parity/build/probes"

if [[ ! -f "$JAR" || "${FORCE_JAVA_BUILD:-0}" == "1" ]]; then
  (cd "$ROOT/java" && ./gradlew --no-daemon -q shadowJar -x test -x javadoc -x checkstyleMain -x checkstyleTest)
fi

rm -rf "$OUT" && mkdir -p "$OUT"
mapfile -t SOURCES < <(find "$ROOT/parity/probes" -name '*.java' | sort)
if [[ ${#SOURCES[@]} -gt 0 ]]; then
  javac -encoding UTF-8 -cp "$JAR" -d "$OUT" "${SOURCES[@]}"
fi
echo "$JAR"
