"""Java: DistributionProbe exact values and RNG-call counts for T07."""

from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

import pytest

from synthea.engine.distribution import Distribution, Kind
from synthea.helpers.constant_value_generator import ConstantValueGenerator
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.expression_processor import ExpressionProcessor
from synthea.helpers.random_collection import RandomCollection
from synthea.helpers.random_value_generator import RandomValueGenerator
from synthea.helpers.synced_enumerated_distro import SyncedEnumeratedDistro
from synthea.helpers.trending_value_generator import TrendingValueGenerator
from synthea.javacompat.bigdecimal import to_string
from synthea.javacompat.numbers import double_to_string


def make_distribution(name: str) -> Distribution:
    """Java: DistributionProbe#distribution."""
    d = Distribution()
    d.kind = Kind(name.split("_")[0])
    d.round = name.endswith("rounded")
    d.parameters = {
        Kind.EXACT: {"value": -2.5},
        Kind.UNIFORM: {"low": -100.25, "high": 350.75},
        Kind.GAUSSIAN: {"mean": 10.0, "standardDeviation": 6.0},
        Kind.EXPONENTIAL: {"mean": 5.3},
        Kind.TRIANGULAR: {"min": -10.0, "mode": 3.5, "max": 30.0},
    }[d.kind]
    if "clamped" in name:
        d.parameters.update(min=7.0, max=12.0)
    return d


@pytest.mark.parity
def test_distribution_samples(golden: Callable[[str], Path]) -> None:
    """Java: DistributionProbe#samples; 5 seeds x 240 draws for every scenario."""
    rows = [
        json.loads(line)
        for line in (golden("DistributionProbe") / "samples.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 100
    for row in rows:
        rng = DefaultRandomNumberGenerator(int(row["seed"]))
        scenario, area = row["scenario"], row["area"]
        actual: list[str]
        if area == "distribution":
            distribution = make_distribution(scenario)
            actual = [double_to_string(distribution.generate(rng)) for _ in range(240)]
        elif area == "collection":
            collection = RandomCollection[str]()
            for weight, value in [(0, "never"), (-2, "never"), (0.1, "a"), (0.2, "b")]:
                collection.add(weight, value)
            other = RandomCollection[str]()
            other.add(0.3, "c")
            other.add(1.5, "d")
            collection.add_all(other)
            actual = [collection.next(rng) for _ in range(240)]
        elif area == "enumerated":
            enumerated = SyncedEnumeratedDistro(
                [("never", 0.0), ("a", 0.1), ("b", 0.2), ("a", 0.3), ("c", 1.5)]
            )
            actual = [enumerated.synced_reseeded_sample(rng) for _ in range(240)]
        else:
            if scenario == "constant":
                generator = ConstantValueGenerator(rng, -12.75)
            elif scenario == "range":
                generator = RandomValueGenerator(rng, -4.5, 19.25)
            elif scenario == "distribution":
                generator = RandomValueGenerator(rng, make_distribution("GAUSSIAN_clamped"))
            else:
                generator = TrendingValueGenerator(
                    rng,
                    4.5,
                    8.0,
                    14.0,
                    100,
                    300,
                    7.0 if scenario in ("trend_min", "trend_bounded") else None,
                    15.0 if scenario in ("trend_max", "trend_bounded") else None,
                )
            actual = [double_to_string(generator.get_value(i * 2)) for i in range(240)]
        assert actual == row["values"], (area, scenario, row["seed"])
        assert str(rng.get_count()) == row["count"], (area, scenario, row["seed"])


@pytest.mark.parity
def test_distribution_expressions(golden: Callable[[str], Path]) -> None:
    """Java: DistributionProbe#expressions; values, runtime types, parameter metadata."""
    rows = [
        json.loads(line, parse_float=Decimal)
        for line in (golden("DistributionProbe") / "expressions.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 340
    assert len({row["expression"] for row in rows}) == 60
    for row in rows:
        if "error" in row:
            with pytest.raises(ValueError):
                ExpressionProcessor(row["expression"])
            continue
        processor = ExpressionProcessor(row["expression"])
        params = {
            key: Decimal(value) if type(value) is int else value
            for key, value in row["params"].items()
        }
        result = processor.evaluate(params)
        if isinstance(result, Decimal):
            actual, type_name = to_string(result), "BigDecimal"
        elif isinstance(result, bool):
            actual, type_name = str(result).lower(), "Boolean"
        elif result is None:
            actual, type_name = "null", "null"
        else:
            actual, type_name = str(result), "Integer" if isinstance(result, int) else "String"
        assert (actual, type_name) == (row["result"], row["type"]), row["expression"]
        assert processor.get_param_names() == set(row["names"])
        assert processor.get_param_types() == row["types"]


@pytest.mark.parity
def test_distribution_fdlibm_log(golden: Callable[[str], Path]) -> None:
    """#66: the reference disables only _dlog; actual Math.log must match fdlibm exactly."""
    import struct

    from synthea.engine.distribution import _java_log
    from synthea.world.concepts.growth_chart_entry import GrowthChartEntry

    rows = [
        json.loads(line)
        for line in (golden("DistributionLogProbe") / "logs.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 10014
    for row in rows:
        value = struct.unpack(">d", int(row["bits"], 16).to_bytes(8, "big"))[0]
        actual = double_to_string(_java_log(value))
        assert actual == row["strict"], row
        assert actual == row["math"], "Reference Math.log must disable _dlog; see issue #66"
        assert (
            double_to_string(GrowthChartEntry(0.0, 1.0, 0.2).zscore_for_value(value))
            == row["growth"]
        )


@pytest.mark.parity
def test_distribution_cql_logs(golden: Callable[[str], Path]) -> None:
    """Real Java CQL Ln/Log paths: 1,000 inputs x three expressions under the corrected VM."""
    processors = {
        "ln": ExpressionProcessor("Ln(#{x})"),
        "log2": ExpressionProcessor("Log(#{x}, 2.0)"),
        "logBase": ExpressionProcessor("Log(#{x}, 1.23456789)"),
    }
    rows = [
        json.loads(line)
        for line in (golden("DistributionLogProbe") / "cql_logs.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 1000
    for row in rows:
        for key, processor in processors.items():
            actual = processor.evaluate({"x": Decimal(row["x"])})
            assert isinstance(actual, Decimal)
            assert to_string(actual) == row[key], (key, row["x"])
