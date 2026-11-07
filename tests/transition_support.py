"""Shared support for the T18 Transition tests.

``build_transition`` mirrors the Java construction in State (direct /
distributed / conditional / complex / lookup-table / type-of-care, in that
priority order) and the Gson field filling behind it: LOWER_CASE_WITH_
UNDERSCORES keys, JSON numbers for Object-typed fields becoming float,
``default_probability`` parsed from either a JSON number or a numeric
string, and Logic conditions built by tests.logic_support.build_logic
(the real Gson analogue is out of scope; see T06's Utilities.get_gson).

``scripted_person`` / ``script_definition_attributes`` duplicate the
TransitionProbe scripting exactly; keep them in sync with the probe.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from synthea.engine.transition import (
    ComplexTransition,
    ComplexTransitionOption,
    ConditionalTransition,
    ConditionalTransitionOption,
    DirectTransition,
    DistributedTransition,
    DistributedTransitionOption,
    LookupTableTransition,
    LookupTableTransitionOption,
    Transition,
    TypeOfCareTransition,
    TypeOfCareTransitionOptions,
)
from synthea.world.agents.person import Person
from tests.logic_support import build_logic

TIME = 1609459200000  # 2021-01-01T00:00:00Z
PRE_TIME = 1546300800000  # 2019-01-01T00:00:00Z
SEEDS = 25


def _epoch_millis(year: int, month: int, day: int) -> int:
    return int(datetime(year, month, day, tzinfo=UTC).timestamp() * 1000)


def scripted_person(seed: int) -> Person:
    """Mirror of TransitionProbe.scriptedPerson — identical script."""
    person = Person(seed)
    person.attributes[Person.BIRTHDATE] = _epoch_millis(2021 - (1 + (seed % 80)), 1, 1)
    person.attributes[Person.GENDER] = "M" if seed % 2 == 0 else "F"
    person.attributes["race"] = "White"
    person.attributes[Person.INCOME] = 10000 * (seed % 12)
    return person


def _script_distribution(person: Person, seed: int, option: dict[str, object]) -> None:
    distribution = option.get("distribution")
    if isinstance(distribution, dict):
        person.attributes[cast(str, distribution["attribute"])] = (seed % 10) / 10.0


def _script_condition_attributes(person: Person, seed: int, condition: dict[str, object]) -> None:
    if condition.get("condition_type") == "Attribute" and seed % 3 == 0 and "value" in condition:
        value = condition["value"]
        converted: object = None
        if isinstance(value, bool):
            converted = value
        elif isinstance(value, (int, float)):
            converted = float(value)
        elif isinstance(value, str):
            converted = value
        if converted is not None:
            person.attributes[cast(str, condition["attribute"])] = converted
    for value in condition.values():
        if isinstance(value, dict):
            _script_condition_attributes(person, seed, value)
        elif isinstance(value, list):
            for element in value:
                if isinstance(element, dict):
                    _script_condition_attributes(person, seed, element)


def script_definition_attributes(person: Person, seed: int, state: dict[str, object]) -> None:
    """Mirror of TransitionProbe.scriptDefinitionAttributes."""
    for key in ("distributed_transition", "complex_transition"):
        options = state.get(key)
        if isinstance(options, list):
            for option in options:
                distributions = option.get("distributions")
                if isinstance(distributions, list):
                    for distribution in distributions:
                        _script_distribution(person, seed, distribution)
                else:
                    _script_distribution(person, seed, option)
                condition = option.get("condition")
                if isinstance(condition, dict):
                    _script_condition_attributes(person, seed, condition)
    for key in ("conditional_transition", "complex_transition"):
        options = state.get(key)
        if isinstance(options, list):
            for option in options:
                condition = option.get("condition")
                if isinstance(condition, dict):
                    _script_condition_attributes(person, seed, condition)


def transition_kind(state: dict[str, object]) -> str | None:
    """The State priority order for picking a state's transition kind."""
    if "direct_transition" in state:
        return "direct"
    if "distributed_transition" in state:
        return "distributed"
    if "conditional_transition" in state:
        return "conditional"
    if "complex_transition" in state:
        return "complex"
    if "lookup_table_transition" in state:
        return "lookup_table"
    if "type_of_care_transition" in state:
        return "type_of_care"
    return None


def _gson_string_codes(value: object) -> object:
    """Gson fills Code.code (a String field) from a JSON number by taking
    its literal text; mirror that before build_logic sees a condition."""
    if isinstance(value, dict):
        result = {k: _gson_string_codes(v) for k, v in value.items()}
        codes = result.get("codes")
        if isinstance(codes, list):
            for entry in codes:
                if isinstance(entry, dict) and isinstance(entry.get("code"), (int, float)):
                    entry["code"] = str(int(cast(float, entry["code"])))
        return result
    if isinstance(value, list):
        return [_gson_string_codes(v) for v in value]
    return value


def _distributed_option(definition: dict[str, object]) -> DistributedTransitionOption:
    option = DistributedTransitionOption()
    option.transition = cast(str, definition["transition"])
    if "distribution" in definition:
        distribution = definition["distribution"]
        if isinstance(distribution, dict):
            # Gson materializes the JSON object as a Map with Double values.
            option.distribution = {
                "attribute": cast(str, distribution["attribute"]),
                "default": float(cast(float, distribution["default"])),
            }
        else:
            option.distribution = float(cast(float, distribution))
    return option


def build_transition(kind: str, state: dict[str, object]) -> Transition:
    """Build the Transition for a module-JSON state, mirroring State+Gson."""
    if kind == "direct":
        return DirectTransition(cast(str, state["direct_transition"]))
    if kind == "distributed":
        options = [
            _distributed_option(cast(dict[str, object], o))
            for o in cast(list[object], state["distributed_transition"])
        ]
        return DistributedTransition(options)
    if kind == "conditional":
        options = []
        for definition in cast(list[dict[str, object]], state["conditional_transition"]):
            option = ConditionalTransitionOption()
            option.transition = cast(str, definition["transition"])
            condition = definition.get("condition")
            if isinstance(condition, dict):
                option.condition = build_logic(
                    cast(dict[str, object], _gson_string_codes(condition))
                )
            options.append(option)
        return ConditionalTransition(options)
    if kind == "complex":
        options = []
        for definition in cast(list[dict[str, object]], state["complex_transition"]):
            option = ComplexTransitionOption()
            if "transition" in definition:
                option.transition = cast(str, definition["transition"])
            condition = definition.get("condition")
            if isinstance(condition, dict):
                option.condition = build_logic(
                    cast(dict[str, object], _gson_string_codes(condition))
                )
            distributions = definition.get("distributions")
            if isinstance(distributions, list):
                option.distributions = [
                    _distributed_option(cast(dict[str, object], d)) for d in distributions
                ]
            options.append(option)
        return ComplexTransition(options)
    if kind == "lookup_table":
        options = []
        for definition in cast(list[dict[str, object]], state["lookup_table_transition"]):
            option = LookupTableTransitionOption()
            option.transition = cast(str, definition["transition"])
            option.lookup_table_name = cast(str, definition.get("lookup_table_name"))
            option.default_probability = float(
                cast(float, definition.get("default_probability", 0.0))
            )
            options.append(option)
        return LookupTableTransition(options)
    if kind == "type_of_care":
        definition = cast(dict[str, object], state["type_of_care_transition"])
        options = TypeOfCareTransitionOptions()
        options.ambulatory = cast(str, definition.get("ambulatory"))
        options.telemedicine = cast(str, definition.get("telemedicine"))
        options.emergency = cast(str, definition.get("emergency"))
        return TypeOfCareTransition(options)
    raise ValueError(f"unknown transition kind {kind}")
