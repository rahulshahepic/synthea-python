"""Java: static constants and enum data in the T04 API skeleton."""

from __future__ import annotations

import importlib
import json
from collections.abc import Callable, Mapping
from decimal import Decimal
from pathlib import Path

import pytest

# Person inherits RandomNumberGenerator's default rand(...) overloads (incl. rand(String...)), so
# its single declared rand() is not the full Python signature. Java: Person implements RNG.
INHERITED_RNG_OVERLOADS = {("org.mitre.synthea.world.agents.Person", "rand")}

DATA_CLASSES = {
    "org.mitre.synthea.world.agents.Person": "synthea.world.agents.person",
    "org.mitre.synthea.world.concepts.ClinicianSpecialty": (
        "synthea.world.concepts.clinician_specialty"
    ),
    "org.mitre.synthea.world.concepts.HealthRecord": "synthea.world.concepts.health_record",
    "org.mitre.synthea.world.concepts.RaceAndEthnicity": (
        "synthea.world.concepts.race_and_ethnicity"
    ),
    "org.mitre.synthea.world.concepts.Claim": "synthea.world.concepts.claim",
    "org.mitre.synthea.helpers.Telemedicine": "synthea.helpers.telemedicine",
    "org.mitre.synthea.engine.ReactionProbabilities": "synthea.engine.reaction_probabilities",
    "org.mitre.synthea.modules.calculators.ASCVD": "synthea.modules.calculators.ascvd",
    "org.mitre.synthea.modules.calculators.Framingham": "synthea.modules.calculators.framingham",
    "org.mitre.synthea.export.CSVConstants": "synthea.export.csv_constants",
}


def _canonical(value: object) -> object:
    """Java: SkeletonProbe#canonical; exact decimal scale and recursive containers."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_canonical(item) for item in value]
    return value


@pytest.mark.parity
def test_skeleton_static_data(golden: Callable[[str], Path]) -> None:
    """Compare every static field of the selected Java data classes exactly."""
    expected = json.loads((golden("SkeletonProbe") / "constants.json").read_text())
    for java, module_name in DATA_CLASSES.items():
        module = importlib.import_module(module_name)
        cls = getattr(module, java.rsplit(".", 1)[1])
        assert expected[java], java
        actual = {name: _canonical(getattr(cls, name)) for name in expected[java]}
        assert actual == expected[java], java


@pytest.mark.parity
def test_skeleton_enum_data(golden: Callable[[str], Path]) -> None:
    """Java enum constructor values and annotation text are data, not behavior."""
    from synthea.world.concepts.health_record import (
        ENUM_CONSTRUCTOR_ARGUMENTS,
        EncounterType,
        ReactionSeverity,
    )
    from synthea.world.concepts.vital_sign import VITAL_SIGN_DISPLAY_NAMES, VitalSign

    expected = json.loads((golden("SkeletonProbe") / "constants.json").read_text())
    for enum_cls, fields in [(EncounterType, ["code"]), (ReactionSeverity, ["code", "display"])]:
        actual = {
            member.name: dict(
                zip(fields, ENUM_CONSTRUCTOR_ARGUMENTS[enum_cls.__name__][member.name], strict=True)
            )
            for member in enum_cls
        }
        assert (
            actual == expected["org.mitre.synthea.world.concepts.HealthRecord$" + enum_cls.__name__]
        )
    assert {member.name: {"name": VITAL_SIGN_DISPLAY_NAMES[member]} for member in VitalSign} == (
        expected["org.mitre.synthea.world.concepts.VitalSign"]
    )


@pytest.mark.parity
def test_skeleton_java_declared_signatures(golden: Callable[[str], Path]) -> None:
    """Java reflection checks direct class ownership, overload arities, and static dispatch."""
    import ast
    import re
    import tomllib
    from inspect import Parameter, signature

    root = Path(__file__).resolve().parents[2]
    entries = tomllib.loads((root / "docs/port_map.toml").read_text())["module"]
    modules = {
        entry["java"].removeprefix("java/src/main/java/").removesuffix(".java").replace("/", "."): (
            entry["python"].removeprefix("src/").removesuffix(".py").replace("/", ".")
        )
        for entry in entries
        if entry["java"] and not set(entry["owners"]) & {"T01", "T02", "T03"}
    }
    expected = json.loads((golden("SkeletonProbe") / "api.json").read_text())
    assert set(modules) <= set(expected)
    for java, api in expected.items():
        top = java.split("$", 1)[0]
        module = importlib.import_module(modules[top])
        name = java.rsplit("$", 1)[-1].rsplit(".", 1)[-1]
        cls = getattr(module, name)
        if api["interface"]:
            assert cls._is_protocol, java
        grouped: dict[str, list[dict[str, object]]] = {}
        for method, sig in api["methods"].items():
            grouped.setdefault(method.split("/", 1)[0], []).append(sig)
        if api["constructors"]:
            grouped["__init__"] = [
                {"arity": arity, "static": False} for arity in api["constructors"]
            ]
        for method, overloads in grouped.items():
            python_name = re.sub(
                r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", method
            ).lower()
            assert python_name in vars(cls), f"{java}#{method}: missing own method"
            descriptor = vars(cls)[python_name]
            is_static = isinstance(descriptor, staticmethod)
            assert all(is_static == item["static"] for item in overloads), f"{java}#{method}"
            fn = descriptor.__func__ if is_static else descriptor
            params = list(signature(fn).parameters.values())
            if not is_static:
                params = params[1:]
            required = sum(p.default is Parameter.empty for p in params)
            arities = [int(item["arity"]) for item in overloads]
            assert required == min(arities), f"{java}#{method}: minimum arity"
            if (java, method) not in INHERITED_RNG_OVERLOADS:
                assert len(params) == max(arities), f"{java}#{method}: maximum arity"
        # No variadic catch-all signatures can masquerade as a faithful declaration.
        source = Path(module.__file__).read_text()
        tree = ast.parse(source)
        assert not any(
            isinstance(node, ast.FunctionDef)
            and (node.args.vararg or node.args.kwarg)
            and (java, node.name) not in INHERITED_RNG_OVERLOADS
            for node in ast.walk(tree)
        ), java
