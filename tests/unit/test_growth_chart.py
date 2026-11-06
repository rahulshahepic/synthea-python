"""Java: org.mitre.synthea.world.concepts.GrowthChartTest."""

import math

import pytest

from synthea.world.concepts.growth_chart import ChartType, GrowthChart


def test_growth_chart_lookup_high_percentile() -> None:
    """Java: GrowthChartTest#testLookUp; high-tail BMI stays finite."""
    charts = GrowthChart.load_charts()
    bmi = charts[ChartType.BMI].look_up(240, "F", 0.997394309960757)
    assert not math.isnan(bmi)
    # Preserve the upstream JUnit assertion and its explicit absolute tolerance.
    # The independent probe parity tests require exact Java output equality.
    assert charts[ChartType.BMI].look_up(240, "F", 0.5) == pytest.approx(
        21.71699934, abs=0.01, rel=0.0
    )
