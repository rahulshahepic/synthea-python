"""Java: RandomCollectionTest, DistributionTest, ExpressionProcessorTest and T07 edges."""

from __future__ import annotations

import math
from collections import Counter
from decimal import Decimal
from itertools import cycle

import pytest

from synthea.engine.distribution import Distribution, Kind
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.expression_processor import ExpressionProcessor
from synthea.helpers.random_collection import RandomCollection
from synthea.helpers.synced_enumerated_distro import SyncedEnumeratedDistro
from synthea.helpers.trending_value_generator import TrendingValueGenerator
from synthea.javacompat.bigdecimal import from_double_exact
from synthea.world.concepts.vital_sign import VitalSign


class Fixed(DefaultRandomNumberGenerator):
    """Java: RandomCollectionTest.Fixed, deterministic boundary RNG."""

    def __init__(self) -> None:
        super().__init__(0)
        self.values = cycle([0.0, 0.5, 0.999])

    def _rand(self) -> float:
        return next(self.values)


class PersonValues:
    """Java: Person subset for ExpressionProcessorTest, independent of T09."""

    def __init__(self) -> None:
        self.attributes: dict[str, object] = {
            "age_attr": 26,
            "decimal": 0.1,
            "flag": True,
            "text": "male",
            "bad": [],
        }
        self.vitals = {VitalSign.BMI: 23.1, VitalSign.SYSTOLIC_BLOOD_PRESSURE: 123.4}

    def age_in_decimal_years(self, time: int) -> float:
        return 26.1

    def get_vital_sign(self, vital_sign: VitalSign, time: int) -> float:
        return self.vitals[vital_sign]


def test_random_collection_zero_weights() -> None:
    """Java: RandomCollectionTest#testZeroWeights."""
    rc = RandomCollection[str]()
    rc.add(0, "white")
    rc.add(1, "black")
    rc.add(0, "asian")
    rc.add(-1, "never")
    assert [rc.next(DefaultRandomNumberGenerator(i)) for i in range(10)] == ["black"] * 10


def test_random_collection_fixed() -> None:
    """Java: RandomCollectionTest#testFixed and #testFixedCounts."""
    fixed = Fixed()
    assert [fixed.rand() for _ in range(9)] == [0.0, 0.5, 0.999] * 3
    rc = RandomCollection[str]()
    for name in ("white", "black", "asian"):
        rc.add(0.33, name)
    assert Counter(rc.next(fixed) for _ in range(9)) == {"white": 3, "black": 3, "asian": 3}


def test_collection_exact_boundary_and_add_all() -> None:
    rc = RandomCollection[str]()
    other = RandomCollection[str]()
    rc.add(1, "a")
    other.add(2, "b")
    other.add(3, "c")
    rc.add_all(other)
    assert [rc.next(v) for v in (-1.0, 0.0, 1.0, 3.0, 6.0, 10.0)] == ["a", "a", "b", "c", "c", "c"]


@pytest.mark.parametrize(
    ("kind", "parameters"),
    [
        (Kind.EXACT, {"value": 1.0}),
        (Kind.UNIFORM, {"low": 1.0, "high": 10.0}),
        (Kind.GAUSSIAN, {"mean": 1.0, "standardDeviation": 2.0}),
        (Kind.EXPONENTIAL, {"mean": 5.3}),
        (Kind.TRIANGULAR, {"min": 0.0, "mode": 0.5, "max": 1.0}),
    ],
)
def test_distribution_validate(kind: Kind, parameters: dict[str, float]) -> None:
    """Java: DistributionTest#testValidate and #testValidateExponential, all kinds."""
    d = Distribution()
    d.kind = kind
    assert not d.validate()
    d.parameters = parameters
    assert d.validate()
    for key in parameters:
        d.parameters = {k: v for k, v in parameters.items() if k != key}
        assert not d.validate()


def test_distribution_rounding() -> None:
    """Java: DistributionTest#testRounding and Math.round edge regressions."""
    d = Distribution()
    d.kind, d.round, d.parameters = Kind.UNIFORM, True, {"low": 1.0, "high": 10.0}
    rng = DefaultRandomNumberGenerator(0)
    assert all(d.generate(rng).is_integer() for _ in range(10))
    d.kind = Kind.EXACT
    for value, expected in [
        (math.nextafter(0.5, 0), 0),
        (-1.5, -1),
        (math.nan, 0),
        (math.inf, 2**63 - 1),
        (-math.inf, -(2**63)),
    ]:
        d.parameters = {"value": value}
        assert d.generate(rng) == float(expected)


def test_distribution_degenerate_parameters() -> None:
    d = Distribution()
    d.kind = Kind.TRIANGULAR
    d.parameters = {"min": 2.0, "mode": 2.0, "max": 2.0}
    assert d.generate(DefaultRandomNumberGenerator(0)) == 2.0
    d.kind, d.parameters = Kind.EXPONENTIAL, {"mean": 0.0}
    assert d.generate(DefaultRandomNumberGenerator(0)) == 1.0


@pytest.mark.parametrize(
    "weights", [[], [("x", 0.0)], [("x", -1.0)], [("x", math.nan)], [("x", math.inf)]]
)
def test_enumerated_invalid_pmf(weights: list[tuple[str, float]]) -> None:
    with pytest.raises(ValueError):
        SyncedEnumeratedDistro(weights)


def test_trending_contract() -> None:
    rng = DefaultRandomNumberGenerator(0)
    trend = TrendingValueGenerator(rng, 0, 1, 3, 100, 300, None, None)
    assert trend.get_begin_time() == 100 and trend.get_end_time() == 300
    assert [trend.get_value(t) for t in (0, 100, 200, 300, 400)] == [1, 1, 2, 3, 3]
    assert rng.get_count() == 5  # zero standard deviation still consumes Gaussian draws
    assert trend.to_string() == (
        "TrendingValueGenerator {standardDeviation=0.0, beginMean=1.0, "
        "endMean=3.0, beginTime=100, endTime=300, "
        "minimumValue=null, maximumValue=null}"
    )
    equal_time = TrendingValueGenerator(rng, 0, 1, 3, 100, 100, None, None)
    assert math.isnan(equal_time.get_value(100))
    for sd, low, high in [(-1, None, None), (math.nan, None, None), (1, 2, 1), (1, math.nan, 1)]:
        with pytest.raises(ValueError):
            TrendingValueGenerator(rng, sd, 1, 2, 0, 1, low, high)


def test_expression_basic() -> None:
    """Java: ExpressionProcessorTest#testBasic."""
    assert ExpressionProcessor("10 + 3").evaluate(None, 0) == 13
    assert ExpressionProcessor("25 / 2").evaluate(None, 0) == Decimal("12.5")
    assert (
        ExpressionProcessor("2 * (10 + 6) + 4 + 3 * ((10 / 2) * (9 / 3))").evaluate(None, 0) == 81
    )


def test_expression_person_attributes() -> None:
    """Java: ExpressionProcessorTest#testWithPersonAttributes and lookup errors."""
    person = PersonValues()
    assert ExpressionProcessor("#{age_attr} / 2 + 7").evaluate(person, 0) == 20
    assert ExpressionProcessor.get_person_value("age", person, 0) == from_double_exact(26.1)
    assert ExpressionProcessor.get_person_value("BMI", person, 0) == from_double_exact(23.1)
    assert ExpressionProcessor.get_person_value(
        "systolic blood pressure", person, 0
    ) == from_double_exact(123.4)
    assert ExpressionProcessor.get_person_value("decimal", person, 0) == Decimal("0.1")
    assert ExpressionProcessor.get_person_value("flag", person, 0) is True
    assert ExpressionProcessor.get_person_value("text", person, 0) == "male"
    with pytest.raises(ValueError, match="Invalid person attribute or vital sign"):
        ExpressionProcessor("#{missing} + 1").evaluate(person, 0)
    with pytest.raises(ValueError, match="Unsupported type"):
        ExpressionProcessor.get_person_value("bad", person, 0, "test")


def test_expression_instance_and_spaces() -> None:
    """Java: ExpressionProcessorTest#testInstance and #testWithSpaces."""
    types = {"var_one": "Decimal", "var_two": "Decimal", "var_three": "List<Decimal>"}
    params = {
        "var_one": Decimal(2),
        "var_two": Decimal(3),
        "var_three": [from_double_exact(v) for v in (3.0, 1.2342, 5.25512, 12.0)],
    }
    processor = ExpressionProcessor("#{var_one} * (#{var_two} + 3.0) + Max(#{var_three})", types)
    assert processor.evaluate_numeric(params) == 24
    spaced = ExpressionProcessor(
        "#{var one} * (#{var two} + 3.0)", {"var one": "Decimal", "var two": "Decimal"}
    )
    assert spaced.evaluate_numeric({"var one": Decimal(2), "var two": Decimal(3)}) == 12
    assert processor.get_expression().startswith("#{var_one}")
    assert processor.get_param_names() == set(params)
    assert processor.get_param_types() is types


def test_expression_strings_and_lists() -> None:
    """Java: ExpressionProcessorTest#testStringInput and #testListInput."""
    processor = ExpressionProcessor("if #s{var_two} = 'male' then 1.0 else #d{var_one}*2.0")
    for sex, expected in [("male", 1), ("female", 4)]:
        assert processor.evaluate_numeric({"var_one": Decimal(2), "var_two": sex}) == expected
    assert (
        ExpressionProcessor("Sum(#l{list_var})").evaluate_numeric(
            {"list_var": [Decimal(x) for x in (3, 1, 2, 12)]}
        )
        == 18
    )


def test_expression_errors_and_reuse(caplog: pytest.LogCaptureFixture) -> None:
    processor = ExpressionProcessor("#{x} + 1")
    with pytest.raises(ValueError, match="Missing parameter"):
        processor.evaluate({})
    assert processor.evaluate({"x": Decimal(2), "unused": False}) == 3
    assert "unused parameter" in caplog.text
    assert processor.evaluate({"x": Decimal(5)}) == 6
    with pytest.raises(ValueError):
        ExpressionProcessor("#{a b} + #{a_b}")
    for invalid in ("10 +", "unresolved + 1", "Unknown(1)", "__import__(1)", "null = null"):
        with pytest.raises(ValueError):
            ExpressionProcessor(invalid)
    with pytest.raises(TypeError):
        ExpressionProcessor("10 + 3").evaluate_numeric({})
    with pytest.raises(NotImplementedError, match="out of scope"):
        processor.evaluate_from_sim_results(object(), 0)


def test_expression_decimal_precision_and_nulls() -> None:
    assert ExpressionProcessor("-1.0 / 3").evaluate({}) == Decimal("-0.33333334")
    assert ExpressionProcessor("Round(-1.5)").evaluate({}) == -1
    assert ExpressionProcessor("1.0 / 0.0").evaluate({}) is None
    assert ExpressionProcessor("false and null").evaluate({}) is False
    assert ExpressionProcessor("true and null").evaluate({}) is None
    assert ExpressionProcessor("true or null").evaluate({}) is True
    assert ExpressionProcessor("false or null").evaluate({}) is None
    assert ExpressionProcessor("define offset: 2.0\n#{x} + offset").evaluate({"x": Decimal(3)}) == 5
