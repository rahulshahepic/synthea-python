"""Exact Math.pow parity, including the cases where StrictMath.pow differs."""

import json
import math
import struct
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.world.concepts.growth_chart_entry import _java_pow


@pytest.mark.parity
def test_growth_pow_matches_actual_jdk(golden: Callable[[str], Path]) -> None:
    """Java: Math#pow; compare all binary64 bits and canonicalize only NaN payloads."""
    rows = (golden("GrowthPowProbe") / "pow.jsonl").read_text().splitlines()
    assert len(rows) == 12156
    for i, line in enumerate(rows):
        row = json.loads(line)
        x = struct.unpack(">d", int(row["x"], 16).to_bytes(8, "big"))[0]
        y = struct.unpack(">d", int(row["y"], 16).to_bytes(8, "big"))[0]
        actual = _java_pow(x, y)
        actual_bits = (
            0x7FF8000000000000
            if math.isnan(actual)
            else struct.unpack(">Q", struct.pack(">d", actual))[0]
        )
        assert actual_bits == int(row["math"], 16), (
            f"row={i}, x={x.hex()}, y={y.hex()}, actual={actual.hex()}, "
            f"Math={row['math']}, StrictMath={row['strict']}"
        )
