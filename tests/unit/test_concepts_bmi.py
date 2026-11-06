"""Java: BMI#calculate and BMI#weightForHeightAndBMI."""

import math

from synthea.world.concepts.bmi import BMI


def test_bmi_operation_order_and_ieee_edges() -> None:
    assert BMI.calculate(200.0, 80.0) == 20.0
    assert BMI.weight_for_height_and_bmi(200.0, 20.0) == 80.0
    assert math.isinf(BMI.calculate(0.0, 80.0))
    assert math.isnan(BMI.calculate(0.0, 0.0))
    assert BMI.calculate(0.0, -80.0) == -math.inf
