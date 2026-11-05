"""Port of the upstream JUnit test ExpressedSymptomTest (T09).

Java: java/src/test/java/org/mitre/synthea/engine/ExpressedSymptomTest.java.
Every assertion mirrors the Java test one for one.
"""

from __future__ import annotations

from synthea.engine.expressed_symptom import ExpressedSymptom, SymptomInfo, SymptomSource


def _source(symptom: ExpressedSymptom, name: str) -> SymptomSource:
    """Java: symptom.new SymptomSource(name) (binds the enclosing symptom)."""
    source = SymptomSource(name)
    source.symptom = symptom
    return source


def test_symptom_info() -> None:
    """Java: ExpressedSymptomTest#testSymptomInfo."""
    symptom = ExpressedSymptom("pain")
    info = SymptomInfo("test", 100, 0)
    assert info.get_cause() == "test"
    assert info.get_value() == 100
    assert info.get_time() == 0

    clone = info.clone()
    assert clone.get_cause() == info.get_cause()
    assert clone.get_value() == info.get_value()
    assert clone.get_time() == info.get_time()


def test_symptom_source() -> None:
    """Java: ExpressedSymptomTest#testSymptomSource."""
    symptom = ExpressedSymptom("pain")
    source = _source(symptom, "unit_test")
    assert source.get_source() == "unit_test"
    assert source.get_current_value() is None
    assert source.get_last_update_time() is None
    assert not source.is_resolved()
    assert len(source.get_time_infos()) == 0

    source.resolve()
    assert source.is_resolved()

    source.activate()
    assert not source.is_resolved()

    source.add_info("foo", 0, 100, False)
    assert source.get_current_value() == 100
    assert source.get_last_update_time() == 0
    assert not source.is_resolved()
    assert len(source.get_time_infos()) != 0
    assert source.get_time_infos()[0].get_value() == 100

    source.add_info("bar", 1, 200, True)
    assert source.get_current_value() == 200
    assert source.get_last_update_time() == 1
    assert source.is_resolved()
    assert len(source.get_time_infos()) != 0
    assert source.get_time_infos()[1].get_value() == 200
    assert source.get_time_infos()[0].get_value() == 100


def test_expressed_symptom() -> None:
    """Java: ExpressedSymptomTest#testExpressedSymtpom."""
    symptom = ExpressedSymptom("pain")
    assert len(symptom.get_sources()) == 0
    assert symptom.get_symptom() == 0
    assert symptom.get_source_with_high_value() is None
    assert symptom.get_value_from_source(None) is None
    assert symptom.get_symptom_last_updated_time(None) is None
    symptom.address_source(None)

    module = "testModule"
    cause = "testCause"
    assert symptom.get_source_with_high_value() is None
    assert symptom.get_value_from_source(module) is None
    assert symptom.get_symptom_last_updated_time(module) is None
    symptom.address_source(module)

    for l_value in range(3):
        symptom.on_set(module, cause, l_value, 100 * l_value, False)
        assert symptom.get_source_with_high_value() == module
        assert symptom.get_value_from_source(module) == 100 * l_value
        assert symptom.get_symptom() == 100 * l_value
        assert symptom.get_symptom_last_updated_time(module) == l_value

    another_module = "anotherModule"
    for l_value in range(3):
        symptom.on_set(another_module, cause, l_value, 10 * l_value, False)
        assert symptom.get_source_with_high_value() == module
        assert symptom.get_value_from_source(another_module) == 10 * l_value
        assert symptom.get_symptom() == 200
        assert symptom.get_symptom_last_updated_time(another_module) == l_value

    symptom.address_source(module)
    assert symptom.get_source_with_high_value() == another_module
    assert symptom.get_symptom() == 20
    assert symptom.get_value_from_source(another_module) == 20

    symptom.address_source(another_module)
    assert symptom.get_symptom() == 0
    assert symptom.get_source_with_high_value() is None
