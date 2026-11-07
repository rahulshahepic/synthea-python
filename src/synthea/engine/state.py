"""Java: org.mitre.synthea.engine.State (T19 base + control-flow states; T20 clinical states).

Construction mirrors ``Utilities.getGson()`` (LOWER_CASE_WITH_UNDERSCORES
field naming, ``InnerClassTypeAdapterFactory`` on the State ``type`` field
and the Logic ``condition_type`` field): ``State.build`` creates the state
without user code running (Java field defaults first), fills its fields
from the module JSON, then calls ``initialize`` — exactly Gson's order.
The real Gson analogue is out of scope for the port (see T06's
``Utilities.get_gson``); this module carries the State-specific mirror.
"""

from __future__ import annotations

import copy
from abc import abstractmethod
from enum import StrEnum
from typing import IO, TYPE_CHECKING, ClassVar, Protocol, cast

from synthea.engine import logic as _logic_module
from synthea.engine.components import (
    Attachment,
    Exact,
    ExactWithUnit,
    Range,
    RangeWithUnit,
    SampledData,
)
from synthea.engine.distribution import Distribution
from synthea.engine.distribution import Kind as _DistributionKind
from synthea.engine.logic import Logic
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
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import parse_double
from synthea.world.concepts.health_record import Code
from synthea.world.concepts.vital_sign import VITAL_SIGN_DISPLAY_NAMES

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.engine.reaction_probabilities import ReactionProbabilities
    from synthea.helpers.expression_processor import ExpressionPerson
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code as HealthRecordCode
    from synthea.world.concepts.health_record import Entry, Medication
    from synthea.world.concepts.health_record import Series as HealthRecordSeries
    from synthea.world.concepts.vital_sign import VitalSign as ConceptVitalSign

    class IoMapper(Protocol):
        """Java boundary type: IoMapper; external to the mapped Python port."""

    class PhysiologySimulator(Protocol):
        """Java boundary type: PhysiologySimulator; external to the mapped Python port."""

    class ThreadLocal(Protocol):
        """Java boundary type: ThreadLocal; external to the mapped Python port."""


class _ThreadLocalShim:
    """Single-threaded stand-in for Java ``ThreadLocal<ExpressionProcessor>``."""

    def __init__(self) -> None:
        """Java: ThreadLocal#ThreadLocal (single-threaded stand-in)."""
        self._value: object = None

    def get(self) -> object:
        """Java: ThreadLocal#get."""
        return self._value

    def set(self, value: object) -> None:
        """Java: ThreadLocal#set."""
        self._value = value


# Java field defaults per State subclass, keyed by class name then field
# name (object fields -> None, int/long -> 0, double -> 0.0, boolean ->
# False), with three corrections to the T04 skeleton's annotations:
# State.entered/exited and Delayable.next are Java Long (nullable), and
# Symptom.probability is a Java Double (nullable; initialize defaults it).
_FIELD_DEFAULTS: dict[str, dict[str, object]] = {
    "State": {
        "module": None,
        "name": None,
        "entered": None,
        "entry": None,
        "exited": None,
        "_transition": None,
        "direct_transition": None,
        "conditional_transition": None,
        "distributed_transition": None,
        "complex_transition": None,
        "lookup_table_transition": None,
        "type_of_care_transition": None,
        "remarks": None,
    },
    "CallSubmodule": {"submodule": None, "submodule_exited": 0},
    "Physiology": {
        "model": None,
        "solver": None,
        "step_size": 0.0,
        "sim_duration": 0.0,
        "lead_time": 0.0,
        "alt_direct_transition": None,
        "inputs": None,
        "outputs": None,
        "alt_transition": None,
        "simulator": None,
        "param_types": None,
    },
    "Delayable": {"next": None},
    "LegacyStateWithUnitlessRV": {"range": None, "exact": None},
    "Delay": {"range": None, "exact": None, "distribution": None, "unit": None},
    "Guard": {"allow": None},
    "SetAttribute": {
        "attribute": None,
        "value": None,
        "value_code": None,
        "value_attribute": None,
        "range": None,
        "expression": None,
        "thread_exp_processor": None,
        "series_data": None,
        "period": 0.0,
        "distribution": None,
    },
    "Counter": {
        "attribute": None,
        "action": None,
        "increment": False,
        "amount": 0,
    },
    "Encounter": {
        "wellness": False,
        "encounter_class": None,
        "codes": None,
        "reason": None,
        "telemedicine_possibility": None,
    },
    "EncounterEnd": {"discharge_disposition": None},
    "AttributeAssignableState": {"assign_to_attribute": None},
    "OnsetState": {"diagnosed": False, "codes": None, "target_encounter": None},
    "ConditionEnd": {
        "codes": None,
        "condition_onset": None,
        "referenced_by_attribute": None,
    },
    "AllergyOnset": {"allergy_type": None, "category": None, "reactions": None},
    "AllergyEnd": {
        "codes": None,
        "allergy_onset": None,
        "referenced_by_attribute": None,
    },
    "MedicationOrder": {
        "codes": None,
        "reason": None,
        "prescription": None,
        "administration": False,
        "chronic": False,
    },
    "MedicationEnd": {
        "codes": None,
        "medication_order": None,
        "referenced_by_attribute": None,
    },
    "CarePlanStart": {
        "codes": None,
        "activities": None,
        "goals": None,
        "reason": None,
    },
    "CarePlanEnd": {
        "codes": None,
        "careplan": None,
        "referenced_by_attribute": None,
    },
    "Procedure": {
        "codes": None,
        "reason": None,
        "duration": None,
        "assign_to_attribute": None,
        "stop": 0,
        "distribution": None,
        "unit": None,
    },
    "VitalSign": {
        "vital_sign": None,
        "unit": None,
        "expression": None,
        "distribution": None,
        "thread_exp_processor": None,
    },
    "Observation": {
        "codes": None,
        "value_code": None,
        "attribute": None,
        "vital_sign": None,
        "sampled_data": None,
        "attachment": None,
        "category": None,
        "unit": None,
        "expression": None,
        "distribution": None,
        "thread_exp_processor": None,
    },
    "ObservationGroup": {"codes": None, "observations": None},
    "MultiObservation": {"category": None},
    "ImagingStudy": {
        "procedure_code": None,
        "series": None,
        "min_number_series": 0,
        "max_number_series": 0,
    },
    "Symptom": {
        "symptom": None,
        "cause": None,
        "probability": None,
        "addressed": False,
        "distribution": None,
    },
    "Device": {"code": None, "manufacturer": None, "model": None},
    "DeviceEnd": {
        "codes": None,
        "device": None,
        "referenced_by_attribute": None,
    },
    "SupplyList": {"supplies": None},
    "SupplyComponent": {"code": None, "quantity": 0},
    "Death": {
        "codes": None,
        "condition_onset": None,
        "referenced_by_attribute": None,
        "range": None,
        "exact": None,
    },
    "Vaccine": {"series": 0, "codes": None},
}


def _init_state_fields(state: State) -> None:
    """Set every Java field of ``state`` to its Java default value."""
    for klass in reversed(type(state).__mro__):
        defaults = _FIELD_DEFAULTS.get(klass.__name__)
        if defaults:
            for field, default in defaults.items():
                setattr(state, field, default)


def _gson_string_codes(value: object) -> object:
    """Gson fills Code.code (a String field) from a JSON number by taking
    its literal text; mirror that before building nested objects."""
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


def _build_code(definition: dict[str, object]) -> Code:
    """Java: Gson construction of a HealthRecord.Code."""
    raw_code = definition["code"]
    if isinstance(raw_code, (int, float)) and not isinstance(raw_code, bool):
        code_text = str(int(raw_code)) if float(raw_code).is_integer() else str(raw_code)
    else:
        code_text = cast(str, raw_code)
    code = Code(
        cast(str, definition["system"]),
        code_text,
        cast("str | None", definition.get("display")),
    )
    if definition.get("version") is not None:
        code.version = cast(str, definition["version"])
    return code


def _gson_object_value(value: object) -> object:
    """Gson deserialization of an Object-typed field: numbers become Double."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    return value


_LOGIC_INT_FIELDS = {"year", "month", "minimum", "maximum"}
_LOGIC_FLOAT_FIELDS = {"quantity", "value"}
_VITAL_SIGNS_BY_DISPLAY = {display: vs for vs, display in VITAL_SIGN_DISPLAY_NAMES.items()}


def _convert_logic_field(logic: Logic, key: str, value: object) -> object:
    """Java: Gson field conversion for one Logic field (mirror of the
    test-side builder in tests/logic_support.py, which T17 validated)."""
    from synthea.engine.components import DateInput

    if key == "codes":
        return [_build_code(cast("dict[str, object]", c)) for c in cast(list, value)]
    if key == "value_code":
        return _build_code(cast("dict[str, object]", value))
    if key == "conditions":
        return [_build_logic(cast("dict[str, object]", c)) for c in cast(list, value)]
    if key == "condition":
        return _build_logic(cast("dict[str, object]", value))
    if key == "date":
        raw = cast("dict[str, object]", value)
        date = DateInput()
        for field in ("year", "month", "day", "hour", "minute", "second", "millisecond"):
            if raw.get(field) is not None:
                setattr(date, field, int(cast(float, raw[field])))
        return date
    if key == "within":
        raw = cast("dict[str, object]", value)
        within: ExactWithUnit[float] = ExactWithUnit()
        within.quantity = float(cast(float, raw["quantity"]))
        within.unit = cast(str, raw["unit"])
        return within
    if key == "vital_sign":
        return _VITAL_SIGNS_BY_DISPLAY[cast(str, value)]
    if key == "value" and type(logic).__name__ in ("Observation", "Attribute"):
        return _gson_object_value(value)
    if key in _LOGIC_INT_FIELDS:
        return int(cast(float, value))
    if key in _LOGIC_FLOAT_FIELDS:
        return float(cast(float, value))
    return value


def _build_logic(definition: dict[str, object]) -> Logic:
    """Java: Gson construction of a Logic object (``condition_type``
    selects the subclass, per InnerClassTypeAdapterFactory)."""
    definition = cast("dict[str, object]", _gson_string_codes(definition))
    type_name = cast(str, definition["condition_type"]).replace(" ", "")
    cls = getattr(_logic_module, type_name)
    logic: Logic = cls()
    for key, value in definition.items():
        if key == "condition_type":
            continue
        setattr(logic, key, _convert_logic_field(logic, key, value))
    return logic


def _build_distribution(definition: dict[str, object]) -> Distribution:
    """Java: Gson construction of a Distribution."""
    distribution = Distribution()
    kind = definition.get("kind")
    if kind is not None:
        distribution.kind = _DistributionKind(cast(str, kind))
    if definition.get("round") is not None:
        distribution.round = bool(definition["round"])
    parameters = definition.get("parameters")
    if isinstance(parameters, dict):
        distribution.parameters = {str(k): float(cast(float, v)) for k, v in parameters.items()}
    return distribution


def _build_range(definition: dict[str, object], with_unit: bool) -> Range:
    """Java: Gson construction of a Components.Range / RangeWithUnit."""
    rng: Range = RangeWithUnit() if with_unit else Range()
    if definition.get("low") is not None:
        rng.low = float(cast(float, definition["low"]))
    if definition.get("high") is not None:
        rng.high = float(cast(float, definition["high"]))
    if definition.get("decimals") is not None:
        rng.decimals = int(cast(float, definition["decimals"]))
    if with_unit:
        cast(RangeWithUnit, rng).unit = cast("str | None", definition.get("unit"))
    return rng


def _build_exact(definition: dict[str, object], with_unit: bool) -> Exact:
    """Java: Gson construction of a Components.Exact / ExactWithUnit."""
    exact: Exact = ExactWithUnit() if with_unit else Exact()
    quantity = definition.get("quantity")
    if isinstance(quantity, (int, float)) and not isinstance(quantity, bool):
        exact.quantity = float(quantity)
    else:
        exact.quantity = quantity
    if with_unit:
        cast(ExactWithUnit, exact).unit = cast("str | None", definition.get("unit"))
    return exact


def _distributed_option(definition: dict[str, object]) -> DistributedTransitionOption:
    """Java: Gson construction of a DistributedTransitionOption."""
    option = DistributedTransitionOption()
    option.transition = cast(str, definition["transition"])
    if "distribution" in definition:
        distribution = definition["distribution"]
        if isinstance(distribution, dict):
            # Gson materializes the JSON object as a Map; NamedDistribution
            # reads exactly these two entries (see T18's builder).
            option.distribution = {
                "attribute": cast(str, distribution["attribute"]),
                "default": float(cast(float, distribution["default"])),
            }
        else:
            option.distribution = float(cast(float, distribution))
    return option


def _fill_state_from_json(state: State, definition: dict[str, object]) -> None:
    """Fill ``state``'s fields from its module-JSON definition, mirroring
    Gson with LOWER_CASE_WITH_UNDERSCORES naming."""
    defaults: dict[str, object] = {}
    for klass in reversed(type(state).__mro__):
        defaults.update(_FIELD_DEFAULTS.get(klass.__name__, {}))
    for key, raw in definition.items():
        if key == "type":
            continue
        value: object = raw
        if key == "direct_transition":
            value = cast(str, raw)
        elif key == "distributed_transition":
            value = [_distributed_option(cast("dict[str, object]", o)) for o in cast(list, raw)]
        elif key == "conditional_transition":
            conditional_options = []
            for opt_def in cast("list[dict[str, object]]", raw):
                option = ConditionalTransitionOption()
                option.transition = cast(str, opt_def["transition"])
                condition = opt_def.get("condition")
                if isinstance(condition, dict):
                    option.condition = _build_logic(condition)
                conditional_options.append(option)
            value = conditional_options
        elif key == "complex_transition":
            complex_options = []
            for opt_def in cast("list[dict[str, object]]", raw):
                x_option = ComplexTransitionOption()
                if "transition" in opt_def:
                    x_option.transition = cast(str, opt_def["transition"])
                condition = opt_def.get("condition")
                if isinstance(condition, dict):
                    x_option.condition = _build_logic(condition)
                distributions = opt_def.get("distributions")
                if isinstance(distributions, list):
                    x_option.distributions = [
                        _distributed_option(cast("dict[str, object]", d)) for d in distributions
                    ]
                complex_options.append(x_option)
            value = complex_options
        elif key == "lookup_table_transition":
            lookup_options = []
            for opt_def in cast("list[dict[str, object]]", raw):
                l_option = LookupTableTransitionOption()
                l_option.transition = cast(str, opt_def["transition"])
                l_option.lookup_table_name = cast(str, opt_def.get("lookup_table_name"))
                l_option.default_probability = float(
                    cast(float, opt_def.get("default_probability", 0.0))
                )
                lookup_options.append(l_option)
            value = lookup_options
        elif key == "type_of_care_transition":
            toc_def = cast("dict[str, object]", raw)
            toc_options = TypeOfCareTransitionOptions()
            toc_options.ambulatory = cast(str, toc_def.get("ambulatory"))
            toc_options.telemedicine = cast(str, toc_def.get("telemedicine"))
            toc_options.emergency = cast(str, toc_def.get("emergency"))
            value = toc_options
        elif key in ("allow", "condition"):
            value = _build_logic(cast("dict[str, object]", raw))
        elif key == "codes" and isinstance(raw, list):
            value = [_build_code(cast("dict[str, object]", c)) for c in raw]
        elif key in ("value_code", "code", "procedure_code") and isinstance(raw, dict):
            value = _build_code(cast("dict[str, object]", raw))
        elif key == "distribution" and isinstance(raw, dict):
            value = _build_distribution(cast("dict[str, object]", raw))
        elif key == "range" and isinstance(raw, dict):
            value = _build_range(
                cast("dict[str, object]", raw),
                "unit" in raw or type(state).__name__ in ("Delay", "Death"),
            )
        elif key == "exact" and isinstance(raw, dict):
            value = _build_exact(
                cast("dict[str, object]", raw),
                "unit" in raw or type(state).__name__ in ("Delay", "Death"),
            )
        elif key == "duration" and isinstance(raw, dict):
            value = _build_range(cast("dict[str, object]", raw), "unit" in raw)
        elif key == "observations" and isinstance(raw, list):
            observations = []
            for obs_def in cast("list[dict[str, object]]", raw):
                observation = Observation.__new__(Observation)
                _init_state_fields(observation)
                _fill_state_from_json(observation, obs_def)
                observations.append(observation)
            value = observations
        elif key == "attachment" and isinstance(raw, dict):
            attachment = Attachment()
            for a_key, a_value in cast("dict[str, object]", raw).items():
                setattr(attachment, a_key, a_value)
            value = attachment
        elif key == "sampled_data" and isinstance(raw, dict):
            sampled = SampledData()
            for s_key, s_value in cast("dict[str, object]", raw).items():
                setattr(sampled, s_key, s_value)
            value = sampled
        elif key == "value" and type(state).__name__ == "SetAttribute":
            value = _gson_object_value(raw)
        elif key == "probability" and isinstance(raw, (int, float)):
            value = float(raw)
        else:
            default = defaults.get(key)
            if isinstance(default, bool):
                value = bool(raw)
            elif isinstance(default, int) and isinstance(raw, (int, float)):
                value = int(raw)
            elif isinstance(default, float) and isinstance(raw, (int, float)):
                value = float(raw)
        setattr(state, key, value)


class State:
    """Java: State — base class for every generic-module state."""

    ENABLE_PHYSIOLOGY_STATE: ClassVar[bool] = Config.get_as_boolean(
        "physiology.state.enabled", False
    )

    def __init__(self) -> None:
        """Java: State#State (implicit default constructor; fields take
        Java defaults, then Gson fills them in ``build``)."""
        _init_state_fields(self)
        self.module: Module | None = None
        self.name: str | None = None
        self.entered: int | None = None
        self.entry: Entry | None = None
        self.exited: int | None = None
        self._transition: Transition | None = None
        self.direct_transition: str | None = None
        self.conditional_transition: list[ConditionalTransitionOption] | None = None
        self.distributed_transition: list[DistributedTransitionOption] | None = None
        self.complex_transition: list[ComplexTransitionOption] | None = None
        self.lookup_table_transition: list[LookupTableTransitionOption] | None = None
        self.type_of_care_transition: TypeOfCareTransitionOptions | None = None
        self.remarks: list[str] | None = None

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: State#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        self.module = module
        self.name = name
        if self.direct_transition is not None:
            self._transition = DirectTransition(self.direct_transition)
        elif self.distributed_transition is not None:
            self._transition = DistributedTransition(self.distributed_transition)
        elif self.conditional_transition is not None:
            self._transition = ConditionalTransition(self.conditional_transition)
        elif self.complex_transition is not None:
            self._transition = ComplexTransition(self.complex_transition)
        elif self.lookup_table_transition is not None:
            self._transition = LookupTableTransition(self.lookup_table_transition)
        elif self.type_of_care_transition is not None:
            self._transition = TypeOfCareTransition(self.type_of_care_transition)
        elif not isinstance(self, Terminal):
            raise RuntimeError("State `" + name + "` has no transition.\n")

    @staticmethod
    def build(module: Module, name: str, definition: dict[str, object]) -> State:
        """Java: State#build.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        type_name = cast(str, definition["type"])
        cls = globals().get(type_name)
        if not (isinstance(cls, type) and issubclass(cls, State)):
            raise RuntimeError(f"State type `{type_name}` does not exist")
        state = cls.__new__(cls)
        _init_state_fields(state)
        _fill_state_from_json(state, definition)
        state.initialize(module, name, definition)
        return state

    def clone(self) -> State:
        """Java: State#clone.

        Java overloads:
        ()
        """
        clone = copy.copy(self)
        clone.entered = None
        clone.exited = None
        clone.entry = None
        return clone

    def transition(self, person: Person, time: int) -> str:
        """Java: State#transition.

        Java overloads:
        (Person person, long time)
        """
        assert self._transition is not None
        return self._transition.follow(person, time)

    def get_transition(self) -> Transition:
        """Java: State#getTransition.

        Java overloads:
        ()
        """
        assert self._transition is not None
        return self._transition

    @abstractmethod
    def process(self, person: Person, time: int) -> bool:
        """Java: State#process — abstract in Java; every concrete
        subclass implements it.

        Java overloads:
        (Person person, long time)
        """

    def run(self, person: Person, time: int, terminate_on_death: bool) -> bool:
        """Java: State#run.

        Java overloads:
        (Person person, long time, boolean terminateOnDeath)
        """
        if terminate_on_death and not person.alive(time):
            return False
        if self.entered is None:
            self.entered = time
        exit_state = self.process(person, time)
        if exit_state:
            if isinstance(self, Delayable):
                self.exited = self.next
            elif isinstance(self, CallSubmodule):
                self.exited = self.submodule_exited
            else:
                self.exited = time
        elif isinstance(self, Terminal):
            self.exited = time
        return exit_state

    def to_string(self) -> str:
        """Java: State#toString.

        Java overloads:
        ()
        """
        return type(self).__name__ + " '" + str(self.name) + "'"

    __str__ = to_string


class Initial(State):
    """Java: Initial — the first state processed in a generic module."""

    def __init__(self) -> None:
        """Java: Initial#Initial.

        Java overloads:
        ()
        """
        super().__init__()

    def process(self, person: Person, time: int) -> bool:
        """Java: Initial#process.

        Java overloads:
        (Person person, long time)
        """
        return True


class Simple(State):
    """Java: Simple — a state that performs no action and transitions on."""

    def __init__(self) -> None:
        """Java: Simple#Simple.

        Java overloads:
        ()
        """
        super().__init__()

    def process(self, person: Person, time: int) -> bool:
        """Java: Simple#process.

        Java overloads:
        (Person person, long time)
        """
        return True


class CallSubmodule(State):
    """Java: CallSubmodule — processes a reusable submodule inline."""

    def __init__(self) -> None:
        """Java: CallSubmodule#CallSubmodule.

        Java overloads:
        ()
        """
        super().__init__()
        self.submodule: str
        self.submodule_exited: int

    def clone(self) -> CallSubmodule:
        """Java: CallSubmodule#clone.

        Java overloads:
        ()
        """
        return cast(CallSubmodule, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: CallSubmodule#process.

        Java overloads:
        (Person person, long time)
        """
        from synthea.engine.module import Module

        # e.g. "submodule": "medications/otc_antihistamine"
        module_history = person.history
        submod = Module.get_module_by_path(self.submodule)
        if submod is None:
            raise RuntimeError("Unknown submodule: " + self.submodule)
        # set the submodule name to have the same name as this parent
        # module, that way the submodule is empowered (and vice versa)
        # to act on encounters created using the same name.
        assert self.module is not None
        submod.name = self.module.name
        completed = submod.process(person, time)

        if completed:
            # keep track of when the submodule exited,
            # in case it was "rewinding time" when it completed
            assert person.history is not None
            first_state = person.history[0]
            if first_state.exited is None:
                # this happens when the patient dies in the submodule,
                # so processing is going to stop anyway
                # but just to be safe and not crash,
                # we'll assume we exited at the current timestep
                self.submodule_exited = time
            else:
                self.submodule_exited = first_state.exited

            # add the history from the submodule to this module's history,
            # at the front
            if module_history is not person.history:
                # if the submodule is a java module, it didn't create its
                # own history
                assert module_history is not None
                module_history[0:0] = person.history
            # clear the submodule history
            assert submod.submodule_name is not None
            person.attributes.pop(submod.submodule_name, None)
            # reset person.history to this module's history
            person.history = module_history
            # add this state to history to indicate we returned to this
            # module
            person.history.insert(0, self)
            return True
        else:
            # reset person.history to this module's history
            person.history = module_history
            # the submodule is still processing
            # next time we call this state it should pick up where it left
            # off
            return False


class Physiology(State):
    """Java: Physiology — physiology simulation state (disabled by
    default; the simulation itself is out of scope, PORTING_GUIDE §8)."""

    def __init__(self) -> None:
        """Java: Physiology#Physiology.

        Java overloads:
        ()
        """
        super().__init__()
        self.model: str
        self.solver: str
        self.step_size: float
        self.sim_duration: float
        self.lead_time: float
        self.alt_direct_transition: str
        self.inputs: list[IoMapper]
        self.outputs: list[IoMapper]
        self.alt_transition: Transition
        self.simulator: PhysiologySimulator
        self.param_types: dict[str, str]

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Physiology#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        if not self.alt_direct_transition:
            raise RuntimeError(
                "All Physiology States MUST have an alt_direct_transition"
                " defined in the event that Physiology States are disabled."
            )
        self.alt_transition = DirectTransition(self.alt_direct_transition)
        if self.lead_time > self.sim_duration:
            raise ValueError("Simulation lead time cannot be greater than sim duration!")
        if State.ENABLE_PHYSIOLOGY_STATE:
            self.setup()

    def setup(self) -> None:
        """Java: Physiology#setup — the physiology simulation is out of
        scope for the Python port (PORTING_GUIDE §8)."""
        raise NotImplementedError("physiology simulation is out of scope for the Python port")

    def clone(self) -> Physiology:
        """Java: Physiology#clone.

        Java overloads:
        ()
        """
        clone = cast(Physiology, super().clone())
        clone.inputs = [copy.copy(mapper) for mapper in self.inputs]
        clone.outputs = [copy.copy(mapper) for mapper in self.outputs]
        if State.ENABLE_PHYSIOLOGY_STATE:
            clone.setup()
        return clone

    def process(self, person: Person, time: int) -> bool:
        """Java: Physiology#process.

        Java overloads:
        (Person person, long time)
        """
        if not State.ENABLE_PHYSIOLOGY_STATE:
            return True
        raise NotImplementedError("physiology simulation is out of scope for the Python port")

    def transition(self, person: Person, time: int) -> str:
        """Java: Physiology#transition.

        Java overloads:
        (Person person, long time)
        """
        if State.ENABLE_PHYSIOLOGY_STATE:
            return super().transition(person, time)
        return self.alt_transition.follow(person, time)


class Terminal(State):
    """Java: Terminal — the end of a module's progression."""

    def __init__(self) -> None:
        """Java: Terminal#Terminal.

        Java overloads:
        ()
        """
        super().__init__()

    def process(self, person: Person, time: int) -> bool:
        """Java: Terminal#process.

        Java overloads:
        (Person person, long time)
        """
        assert self.module is not None
        module = self.module
        if (
            person.has_current_encounter()
            and not module.submodule  # only auto-close for top-level modules
            and person.get_current_encounter_module() == module.name
        ):
            # End any encounter this module is accidentally leaving open
            assert person.record is not None
            encounter = person.record.current_encounter(time)
            if encounter is not None:
                from synthea.world.concepts.health_record import EncounterType

                encounter_type = EncounterType.from_string(encounter.type)
                person.record.encounter_end(time, encounter_type)
            # reset current provider hash
            assert module.name is not None
            person.remove_current_provider(module.name)
            person.release_current_encounter(time, module.name)
        return False


class Delayable(State):
    """Java: Delayable — a state that can be delayed."""

    def __init__(self) -> None:
        """Java: Delayable#Delayable.

        Java overloads:
        ()
        """
        super().__init__()
        self.next: int | None

    def clone(self) -> Delayable:
        """Java: Delayable#clone.

        Java overloads:
        ()
        """
        clone = cast(Delayable, super().clone())
        clone.next = None
        return clone

    @abstractmethod
    def end_of_delay(self, time: int, person: Person) -> int:
        """Java: Delayable#endOfDelay — abstract in Java.

        Java overloads:
        (long time, Person person)
        """

    def process_once(self, person: Person, time: int) -> None:
        """Java: Delayable#processOnce.

        Java overloads:
        (Person person, long time)
        """
        # do nothing. allow subclasses to override
        return None

    def process(self, person: Person, time: int) -> bool:
        """Java: Delayable#process.

        Java overloads:
        (Person person, long time)
        """
        if self.next is None:
            self.process_once(person, time)
            self.next = self.end_of_delay(time, person)
            if self.next < time:
                # Don't allow a negative delay
                self.next = time
        return (time >= self.next) and person.alive(self.next)


class LegacyStateWithUnitlessRV(State):
    """Java: LegacyStateWithUnitlessRV — base for GMF 1.0 states whose
    random variable is a unitless range or exact value."""

    def __init__(self) -> None:
        """Java: LegacyStateWithUnitlessRV#LegacyStateWithUnitlessRV.

        Java overloads:
        ()
        """
        super().__init__()
        self.range: Range
        self.exact: Exact

    def clone(self) -> State:
        """Java: LegacyStateWithUnitlessRV#clone.

        Java overloads:
        ()
        """
        # Java re-assigns range/exact to themselves (shared references).
        return super().clone()

    def is_legacy_gmf(self) -> bool:
        """Java: LegacyStateWithUnitlessRV#isLegacyGmf.

        Java overloads:
        ()
        """
        return self.exact is not None or self.range is not None


class Delay(Delayable):
    """Java: Delay — a pre-configured temporal delay in the timeline."""

    def __init__(self) -> None:
        """Java: Delay#Delay.

        Java overloads:
        ()
        """
        super().__init__()
        self.range: RangeWithUnit[float]
        self.exact: ExactWithUnit[float]
        self.distribution: Distribution
        self.unit: str

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Delay#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        if self.distribution is not None and not self.distribution.validate():
            raise RuntimeError(f"State {self.name} contains an invalid distribution")

    def clone(self) -> Delay:
        """Java: Delay#clone.

        Java overloads:
        ()
        """
        return cast(Delay, super().clone())

    def end_of_delay(self, time: int, person: Person) -> int:
        """Java: Delay#endOfDelay.

        Java overloads:
        (long time, Person person)
        """
        if self.is_legacy_gmf():
            if self.exact is not None:
                # use an exact quantity
                return time + Utilities.convert_time(
                    cast(str, self.exact.unit), cast(float, self.exact.quantity)
                )
            elif self.range is not None:
                # use a range
                return time + Utilities.convert_time(
                    cast(str, self.range.unit),
                    person.rand(cast(float, self.range.low), cast(float, self.range.high)),
                )
        else:
            if self.distribution is not None:
                return time + Utilities.convert_time(
                    self.unit, int(self.distribution.generate(person))
                )
        raise RuntimeError("Delay state has no distribution properties: " + str(self))

    def is_legacy_gmf(self) -> bool:
        """Java: Delay#isLegacyGmf.

        Java overloads:
        ()
        """
        return self.exact is not None or self.range is not None


class Guard(State):
    """Java: Guard — passes only when its ``allow`` logic is met."""

    def __init__(self) -> None:
        """Java: Guard#Guard.

        Java overloads:
        ()
        """
        super().__init__()
        self.allow: Logic

    def clone(self) -> Guard:
        """Java: Guard#clone.

        Java overloads:
        ()
        """
        return cast(Guard, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Guard#process.

        Java overloads:
        (Person person, long time)
        """
        exit_state = self.allow.test(person, time)
        if exit_state:
            self.exited = time
        return exit_state


class SetAttribute(State):
    """Java: SetAttribute — sets (or clears) a person attribute."""

    def __init__(self) -> None:
        """Java: SetAttribute#SetAttribute.

        Java overloads:
        ()
        """
        super().__init__()
        self.attribute: str
        self.value: object
        self.value_code: Code
        self.value_attribute: str
        self.range: Range[float]
        self.expression: str
        self.thread_exp_processor: ThreadLocal
        self.series_data: str
        self.period: float
        self.distribution: Distribution

    def get_exp_processor(self) -> ThreadLocal:
        """Java: SetAttribute#getExpProcessor.

        Java overloads:
        ()
        """
        # If the ThreadLocal instance hasn't been created yet, create it now
        if self.thread_exp_processor is None:
            self.thread_exp_processor = cast("ThreadLocal", _ThreadLocalShim())
        # If there's an expression, create the processor for it
        shim = cast(_ThreadLocalShim, self.thread_exp_processor)
        if self.expression is not None and shim.get() is None:
            from synthea.helpers.expression_processor import ExpressionProcessor

            shim.set(ExpressionProcessor(self.expression))
        return self.thread_exp_processor

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: SetAttribute#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        # special handling for integers
        if isinstance(self.value, float):
            double_val = self.value
            if double_val.is_integer():  # Java: doubleVal == Math.rint(doubleVal)
                self.value = int(double_val)
        # Series data default period is 1.0s
        if self.period <= 0.0:
            self.period = 1.0
        if self.distribution is not None and not self.distribution.validate():
            raise RuntimeError(f"State {self.name} contains an invalid distribution")

    def clone(self) -> SetAttribute:
        """Java: SetAttribute#clone.

        Java overloads:
        ()
        """
        return cast(SetAttribute, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: SetAttribute#process.

        Java overloads:
        (Person person, long time)
        """
        from synthea.helpers.expression_processor import ExpressionProcessor
        from synthea.helpers.time_series_data import TimeSeriesData

        exp_processor = cast(_ThreadLocalShim, self.get_exp_processor())
        processor = exp_processor.get()
        if processor is not None:
            self.value = cast(ExpressionProcessor, processor).evaluate(
                cast("ExpressionPerson", person), time
            )
        elif self.range is not None:
            self.value = person.rand(
                cast(float, self.range.low),
                cast(float, self.range.high),
                self.range.decimals,
            )
        elif self.series_data is not None:
            items = self.series_data.split(" ")
            data = TimeSeriesData(len(items), self.period)
            for item in items:
                try:
                    data.add_value(parse_double(item))
                except ValueError:
                    raise RuntimeError(
                        'unable to parse "'
                        + item
                        + '" in SetAttribute state for "'
                        + self.attribute
                        + '"'
                    ) from None
            self.value = data
        elif self.distribution is not None:
            self.value = self.distribution.generate(person)
        elif self.value_code is not None:
            self.value = self.value_code
        elif self.value_attribute is not None and self.value_attribute in person.attributes:
            # the module is setting an attribute to be the value of an
            # existing attribute
            self.value = person.attributes.get(self.value_attribute)

        if self.value is not None:
            person.attributes[self.attribute] = self.value
        elif self.attribute in person.attributes:
            # intentionally clear out the variable
            person.attributes.pop(self.attribute, None)

        return True


class Counter(State):
    """Java: Counter — increments or decrements a numeric attribute."""

    def __init__(self) -> None:
        """Java: Counter#Counter.

        Java overloads:
        ()
        """
        super().__init__()
        self.attribute: str
        self.action: str
        self.increment: bool
        self.amount: int

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Counter#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        self.increment = self.action == "increment"
        if self.amount == 0:
            # default to 1 for legacy compatibility
            self.amount = 1

    def clone(self) -> Counter:
        """Java: Counter#clone.

        Java overloads:
        ()
        """
        return cast(Counter, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Counter#process.

        Java overloads:
        (Person person, long time)
        """
        counter = 0.0
        if self.attribute in person.attributes:
            # this parse as double from the string form is to handle cases
            # where the attribute is either a Double or an Integer
            counter = parse_double(str(person.attributes.get(self.attribute)))
        counter = counter + self.amount if self.increment else counter - self.amount
        person.attributes[self.attribute] = counter
        return True


class TelemedicinePossibility(StrEnum):
    """Java: TelemedicinePossibility; pending T19/T20."""

    NONE = "NONE"
    POSSIBLE = "POSSIBLE"
    ALWAYS = "ALWAYS"


class Encounter(State):
    """Java: Encounter; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Encounter#Encounter.

        Java overloads:
        ()
        """
        self.wellness: bool
        self.encounter_class: str
        self.codes: list[Code]
        self.reason: str
        self.telemedicine_possibility: str
        raise NotImplementedError("Java: Encounter#Encounter — pending T19/T20")

    def clone(self) -> Encounter:
        """Java: Encounter#clone.

        Java overloads:
        ()
        """
        return cast(Encounter, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Encounter#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Encounter#process — pending T19/T20")

    def diagnose_past_conditions(self, person: Person, time: int) -> None:
        """Java: Encounter#diagnosePastConditions.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Encounter#diagnosePastConditions — pending T19/T20")

    def renew_chronic_medications_at_wellness(self, person: Person, time: int) -> None:
        """Java: Encounter#renewChronicMedicationsAtWellness.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: Encounter#renewChronicMedicationsAtWellness — pending T19/T20"
        )

    def is_wellness(self) -> bool:
        """Java: Encounter#isWellness.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Encounter#isWellness — pending T19/T20")


class EncounterEnd(State):
    """Java: EncounterEnd; pending T19/T20."""

    def __init__(self) -> None:
        """Java: EncounterEnd#EncounterEnd.

        Java overloads:
        ()
        """
        self.discharge_disposition: Code
        raise NotImplementedError("Java: EncounterEnd#EncounterEnd — pending T19/T20")

    def clone(self) -> EncounterEnd:
        """Java: EncounterEnd#clone.

        Java overloads:
        ()
        """
        return cast(EncounterEnd, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: EncounterEnd#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: EncounterEnd#process — pending T19/T20")


class AttributeAssignableState(State):
    """Java: AttributeAssignableState; pending T19/T20."""

    def __init__(self) -> None:
        """Java: AttributeAssignableState#AttributeAssignableState.

        Java overloads:
        ()
        """
        self.assign_to_attribute: str
        raise NotImplementedError(
            "Java: AttributeAssignableState#AttributeAssignableState — pending T19/T20"
        )

    def should_assign_attribute(self) -> bool:
        """Java: AttributeAssignableState#shouldAssignAttribute.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: AttributeAssignableState#shouldAssignAttribute — pending T19/T20"
        )


class OnsetState(AttributeAssignableState):
    """Java: OnsetState; pending T19/T20."""

    def __init__(self) -> None:
        """Java: OnsetState#OnsetState.

        Java overloads:
        ()
        """
        self.diagnosed: bool
        self.codes: list[Code]
        self.target_encounter: str
        raise NotImplementedError("Java: OnsetState#OnsetState — pending T19/T20")

    def clone(self) -> OnsetState:
        """Java: OnsetState#clone.

        Java overloads:
        ()
        """
        return cast(OnsetState, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: OnsetState#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: OnsetState#process — pending T19/T20")

    def update_onset_info(self, person: Person, time: int) -> None:
        """Java: OnsetState#updateOnsetInfo.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: OnsetState#updateOnsetInfo — pending T19/T20")

    def diagnose(self, person: Person, time: int) -> None:
        """Java: OnsetState#diagnose.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: OnsetState#diagnose — pending T19/T20")


class ConditionOnset(OnsetState):
    """Java: ConditionOnset; pending T19/T20."""

    def __init__(self) -> None:
        """Java: ConditionOnset#ConditionOnset.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionOnset#ConditionOnset — pending T19/T20")

    def update_onset_info(self, person: Person, time: int) -> None:
        """Java: ConditionOnset#updateOnsetInfo.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: ConditionOnset#updateOnsetInfo — pending T19/T20")

    def diagnose(self, person: Person, time: int) -> None:
        """Java: ConditionOnset#diagnose.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: ConditionOnset#diagnose — pending T19/T20")


class ConditionEnd(State):
    """Java: ConditionEnd; pending T19/T20."""

    def __init__(self) -> None:
        """Java: ConditionEnd#ConditionEnd.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.condition_onset: str
        self.referenced_by_attribute: str
        raise NotImplementedError("Java: ConditionEnd#ConditionEnd — pending T19/T20")

    def clone(self) -> ConditionEnd:
        """Java: ConditionEnd#clone.

        Java overloads:
        ()
        """
        return cast(ConditionEnd, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: ConditionEnd#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: ConditionEnd#process — pending T19/T20")


class AllergyOnset(OnsetState):
    """Java: AllergyOnset; pending T19/T20."""

    def __init__(self) -> None:
        """Java: AllergyOnset#AllergyOnset.

        Java overloads:
        ()
        """
        self.allergy_type: str
        self.category: str
        self.reactions: list[ReactionProbabilities]
        raise NotImplementedError("Java: AllergyOnset#AllergyOnset — pending T19/T20")

    def diagnose(self, person: Person, time: int) -> None:
        """Java: AllergyOnset#diagnose.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: AllergyOnset#diagnose — pending T19/T20")


class AllergyEnd(State):
    """Java: AllergyEnd; pending T19/T20."""

    def __init__(self) -> None:
        """Java: AllergyEnd#AllergyEnd.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.allergy_onset: str
        self.referenced_by_attribute: str
        raise NotImplementedError("Java: AllergyEnd#AllergyEnd — pending T19/T20")

    def clone(self) -> AllergyEnd:
        """Java: AllergyEnd#clone.

        Java overloads:
        ()
        """
        return cast(AllergyEnd, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: AllergyEnd#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: AllergyEnd#process — pending T19/T20")


class MedicationOrder(AttributeAssignableState):
    """Java: MedicationOrder; pending T19/T20."""

    def __init__(self) -> None:
        """Java: MedicationOrder#MedicationOrder.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.reason: str
        self.prescription: dict[str, object]
        self.administration: bool
        self.chronic: bool
        raise NotImplementedError("Java: MedicationOrder#MedicationOrder — pending T19/T20")

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: MedicationOrder#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java: MedicationOrder#writeObject — pending T19/T20")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: MedicationOrder#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java: MedicationOrder#readObject — pending T19/T20")

    def clone(self) -> MedicationOrder:
        """Java: MedicationOrder#clone.

        Java overloads:
        ()
        """
        return cast(MedicationOrder, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: MedicationOrder#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: MedicationOrder#process — pending T19/T20")

    def apply_features(self, person: Person, medication: Medication) -> None:
        """Java: MedicationOrder#applyFeatures.

        Java overloads:
        (Person person, Medication medication)
        """
        raise NotImplementedError("Java: MedicationOrder#applyFeatures — pending T19/T20")


class MedicationEnd(State):
    """Java: MedicationEnd; pending T19/T20."""

    EXPIRED: ClassVar[Code]  # Java initialization deferred to T19/T20.

    def __init__(self) -> None:
        """Java: MedicationEnd#MedicationEnd.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.medication_order: str
        self.referenced_by_attribute: str
        raise NotImplementedError("Java: MedicationEnd#MedicationEnd — pending T19/T20")

    def clone(self) -> MedicationEnd:
        """Java: MedicationEnd#clone.

        Java overloads:
        ()
        """
        return cast(MedicationEnd, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: MedicationEnd#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: MedicationEnd#process — pending T19/T20")


class CarePlanStart(AttributeAssignableState):
    """Java: CarePlanStart; pending T19/T20."""

    def __init__(self) -> None:
        """Java: CarePlanStart#CarePlanStart.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.activities: list[Code]
        self.goals: list[dict[str, object]]
        self.reason: str
        raise NotImplementedError("Java: CarePlanStart#CarePlanStart — pending T19/T20")

    def clone(self) -> CarePlanStart:
        """Java: CarePlanStart#clone.

        Java overloads:
        ()
        """
        return cast(CarePlanStart, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: CarePlanStart#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CarePlanStart#process — pending T19/T20")


class CarePlanEnd(State):
    """Java: CarePlanEnd; pending T19/T20."""

    FINISHED: ClassVar[Code]  # Java initialization deferred to T19/T20.

    def __init__(self) -> None:
        """Java: CarePlanEnd#CarePlanEnd.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.careplan: str
        self.referenced_by_attribute: str
        raise NotImplementedError("Java: CarePlanEnd#CarePlanEnd — pending T19/T20")

    def clone(self) -> CarePlanEnd:
        """Java: CarePlanEnd#clone.

        Java overloads:
        ()
        """
        return cast(CarePlanEnd, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: CarePlanEnd#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CarePlanEnd#process — pending T19/T20")


class Procedure(Delayable):
    """Java: Procedure; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Procedure#Procedure.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.reason: str
        self.duration: RangeWithUnit[int]
        self.assign_to_attribute: str
        self.stop: int
        self.distribution: Distribution
        self.unit: str
        raise NotImplementedError("Java: Procedure#Procedure — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Procedure#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        if self.distribution is not None and not self.distribution.validate():
            raise RuntimeError(f"State {self.name} contains an invalid distribution")

    def clone(self) -> Procedure:
        """Java: Procedure#clone.

        Java overloads:
        ()
        """
        return cast(Procedure, super().clone())

    def end_of_delay(self, time: int, person: Person) -> int:
        """Java: Procedure#endOfDelay.

        Java overloads:
        (long time, Person person)
        """
        raise NotImplementedError("Java: Procedure#endOfDelay — pending T19/T20")

    def process_once(self, person: Person, time: int) -> None:
        """Java: Procedure#processOnce.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Procedure#processOnce — pending T19/T20")


class VitalSign(LegacyStateWithUnitlessRV):
    """Java: VitalSign; pending T19/T20."""

    def __init__(self) -> None:
        """Java: VitalSign#VitalSign.

        Java overloads:
        ()
        """
        self.vital_sign: ConceptVitalSign
        self.unit: str
        self.expression: str
        self.distribution: Distribution
        self.thread_exp_processor: ThreadLocal
        raise NotImplementedError("Java: VitalSign#VitalSign — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: VitalSign#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        if self.distribution is not None and not self.distribution.validate():
            raise RuntimeError(f"State {self.name} contains an invalid distribution")

    def get_exp_processor(self) -> ThreadLocal:
        """Java: VitalSign#getExpProcessor.

        Java overloads:
        ()
        """
        if self.thread_exp_processor is None:
            self.thread_exp_processor = cast("ThreadLocal", _ThreadLocalShim())
        shim = cast(_ThreadLocalShim, self.thread_exp_processor)
        if self.expression is not None and shim.get() is None:
            from synthea.helpers.expression_processor import ExpressionProcessor

            shim.set(ExpressionProcessor(self.expression))
        return self.thread_exp_processor

    def clone(self) -> VitalSign:
        """Java: VitalSign#clone.

        Java overloads:
        ()
        """
        return cast(VitalSign, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: VitalSign#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: VitalSign#process — pending T19/T20")


class Observation(LegacyStateWithUnitlessRV):
    """Java: Observation; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Observation#Observation.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.value_code: Code
        self.attribute: str
        self.vital_sign: ConceptVitalSign
        self.sampled_data: SampledData
        self.attachment: Attachment
        self.category: str
        self.unit: str
        self.expression: str
        self.distribution: Distribution
        self.thread_exp_processor: ThreadLocal
        raise NotImplementedError("Java: Observation#Observation — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Observation#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        self.validate(module, name)

    def validate(self, module: Module, name: str) -> None:
        """Java: Observation#validate.

        Java overloads:
        (Module module, String name)
        """
        # units are required when a numeric quantity is given
        if (self.exact is not None or self.range is not None) and (
            self.unit is None or self.unit.strip() == ""
        ):
            raise RuntimeError(
                "Observations with numeric quantities must contain non-blank units. "
                + 'Module "'
                + str(module.name)
                + '": State "'
                + name
                + '": Unit is missing, empty, or all whitespace'
            )
        if self.distribution is not None and not self.distribution.validate():
            raise RuntimeError(f"State {self.name} contains an invalid distribution")

    def get_exp_processor(self) -> ThreadLocal:
        """Java: Observation#getExpProcessor.

        Java overloads:
        ()
        """
        if self.thread_exp_processor is None:
            self.thread_exp_processor = cast("ThreadLocal", _ThreadLocalShim())
        shim = cast(_ThreadLocalShim, self.thread_exp_processor)
        if self.expression is not None and shim.get() is None:
            from synthea.helpers.expression_processor import ExpressionProcessor

            shim.set(ExpressionProcessor(self.expression))
        if self.attachment is not None:
            self.attachment.validate()
        return self.thread_exp_processor

    def clone(self) -> Observation:
        """Java: Observation#clone.

        Java overloads:
        ()
        """
        return cast(Observation, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Observation#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Observation#process — pending T19/T20")


class ObservationGroup(State):
    """Java: ObservationGroup; pending T19/T20."""

    def __init__(self) -> None:
        """Java: ObservationGroup#ObservationGroup.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.observations: list[Observation]
        raise NotImplementedError("Java: ObservationGroup#ObservationGroup — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: ObservationGroup#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        for observation in self.observations:
            observation.validate(module, name)

    def clone(self) -> ObservationGroup:
        """Java: ObservationGroup#clone.

        Java overloads:
        ()
        """
        clone = cast(ObservationGroup, super().clone())
        # IMPORTANT: because each observation gets process()ed when the
        # state gets processed, deep-clone the observations list (Java
        # ObservationGroup#clone).
        clone.observations = [o.clone() for o in self.observations]
        return clone


class MultiObservation(ObservationGroup):
    """Java: MultiObservation; pending T19/T20."""

    def __init__(self) -> None:
        """Java: MultiObservation#MultiObservation.

        Java overloads:
        ()
        """
        self.category: str
        raise NotImplementedError("Java: MultiObservation#MultiObservation — pending T19/T20")

    def clone(self) -> MultiObservation:
        """Java: MultiObservation#clone.

        Java overloads:
        ()
        """
        return cast(MultiObservation, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: MultiObservation#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: MultiObservation#process — pending T19/T20")


class DiagnosticReport(ObservationGroup):
    """Java: DiagnosticReport; pending T19/T20."""

    def __init__(self) -> None:
        """Java: DiagnosticReport#DiagnosticReport.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: DiagnosticReport#DiagnosticReport — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: DiagnosticReport#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: DiagnosticReport#process — pending T19/T20")

    def panel_already_recorded_at_this_time(self, person: Person, time: int) -> bool:
        """Java: DiagnosticReport#panelAlreadyRecordedAtThisTime.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: DiagnosticReport#panelAlreadyRecordedAtThisTime — pending T19/T20"
        )


class ImagingStudy(State):
    """Java: ImagingStudy; pending T19/T20."""

    def __init__(self) -> None:
        """Java: ImagingStudy#ImagingStudy.

        Java overloads:
        ()
        """
        self.procedure_code: Code
        self.series: list[HealthRecordSeries]
        self.min_number_series: int
        self.max_number_series: int
        raise NotImplementedError("Java: ImagingStudy#ImagingStudy — pending T19/T20")

    def clone(self) -> ImagingStudy:
        """Java: ImagingStudy#clone.

        Java overloads:
        ()
        """
        return cast(ImagingStudy, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: ImagingStudy#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: ImagingStudy#process — pending T19/T20")

    def duplicate_series(
        self, random: RandomNumberGenerator, time: int
    ) -> list[HealthRecordSeries]:
        """Java: ImagingStudy#duplicateSeries.

        Java overloads:
        (RandomNumberGenerator random, long time)
        """
        raise NotImplementedError("Java: ImagingStudy#duplicateSeries — pending T19/T20")

    def duplicate_instances(
        self, random: RandomNumberGenerator, time: int, my_series: list[HealthRecordSeries]
    ) -> None:
        """Java: ImagingStudy#duplicateInstances.

        Java overloads:
        (RandomNumberGenerator random, long time, List mySeries)
        """
        raise NotImplementedError("Java: ImagingStudy#duplicateInstances — pending T19/T20")


class Symptom(LegacyStateWithUnitlessRV):
    """Java: Symptom; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Symptom#Symptom.

        Java overloads:
        ()
        """
        self.symptom: str
        self.cause: str
        self.probability: float
        self.addressed: bool
        self.distribution: Distribution
        raise NotImplementedError("Java: Symptom#Symptom — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Symptom#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        super().initialize(module, name, definition)
        if self.cause is None:
            self.cause = module.name
        if self.probability is None or self.probability > 1 or self.probability < 0:
            self.probability = 1.0
        self.addressed = False
        if self.distribution is not None and not self.distribution.validate():
            raise RuntimeError(f"State {self.name} contains an invalid distribution")

    def clone(self) -> Symptom:
        """Java: Symptom#clone.

        Java overloads:
        ()
        """
        return cast(Symptom, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Symptom#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Symptom#process — pending T19/T20")


class Device(AttributeAssignableState):
    """Java: Device; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Device#Device.

        Java overloads:
        ()
        """
        self.code: Code
        self.manufacturer: str
        self.model: str
        raise NotImplementedError("Java: Device#Device — pending T19/T20")

    def clone(self) -> Device:
        """Java: Device#clone.

        Java overloads:
        ()
        """
        return cast(Device, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Device#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Device#process — pending T19/T20")


class DeviceEnd(State):
    """Java: DeviceEnd; pending T19/T20."""

    def __init__(self) -> None:
        """Java: DeviceEnd#DeviceEnd.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.device: str
        self.referenced_by_attribute: str
        raise NotImplementedError("Java: DeviceEnd#DeviceEnd — pending T19/T20")

    def clone(self) -> DeviceEnd:
        """Java: DeviceEnd#clone.

        Java overloads:
        ()
        """
        return cast(DeviceEnd, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: DeviceEnd#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: DeviceEnd#process — pending T19/T20")


class SupplyList(State):
    """Java: SupplyList; pending T19/T20."""

    def __init__(self) -> None:
        """Java: SupplyList#SupplyList.

        Java overloads:
        ()
        """
        self.supplies: list[SupplyComponent]
        raise NotImplementedError("Java: SupplyList#SupplyList — pending T19/T20")

    def clone(self) -> SupplyList:
        """Java: SupplyList#clone.

        Java overloads:
        ()
        """
        return cast(SupplyList, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: SupplyList#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: SupplyList#process — pending T19/T20")


class SupplyComponent:
    """Java: SupplyComponent; pending T19/T20."""

    def __init__(self) -> None:
        """Java: SupplyComponent#SupplyComponent.

        Java overloads:
        ()
        """
        self.code: HealthRecordCode
        self.quantity: int
        raise NotImplementedError("Java: SupplyComponent#SupplyComponent — pending T19/T20")


class Death(State):
    """Java: Death — records the person's death."""

    def __init__(self) -> None:
        """Java: Death#Death.

        Java overloads:
        ()
        """
        super().__init__()
        self.codes: list[Code]
        self.condition_onset: str
        self.referenced_by_attribute: str
        self.range: RangeWithUnit[float]
        self.exact: ExactWithUnit[float]

    def clone(self) -> Death:
        """Java: Death#clone.

        Java overloads:
        ()
        """
        return cast(Death, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Death#process.

        Java overloads:
        (Person person, long time)
        """
        reason: Code | None = None
        if self.codes is not None:
            reason = self.codes[0]
        elif self.condition_onset is not None:
            if person.had_prior_state(self.condition_onset):
                # loop through the present conditions, the condition
                # "name" will match the name of the ConditionOnset state
                # (aka "reason")
                assert person.record is not None
                for entry in person.record.present.values():
                    if entry.name is not None and entry.name == self.condition_onset:
                        reason = entry.codes[0]
            elif self.condition_onset in self.module.get_state_names():
                state = self.module.get_state(self.condition_onset)
                if state is not None and isinstance(state, ConditionOnset):
                    reason = state.codes[0]
        elif self.referenced_by_attribute is not None:
            entry = cast("Entry | None", person.attributes.get(self.referenced_by_attribute))
            if entry is None:
                # condition referenced but not yet diagnosed
                raise RuntimeError(
                    "Attribute '"
                    + self.referenced_by_attribute
                    + "' was referenced by state '"
                    + str(self.name)
                    + "' but not set"
                )
            reason = entry.codes[0]
        if self.exact is not None:
            time_of_death = time + Utilities.convert_time(
                cast(str, self.exact.unit), cast(float, self.exact.quantity)
            )
            person.record_death(time_of_death, reason)
            return True
        elif self.range is not None:
            duration = person.rand(cast(float, self.range.low), cast(float, self.range.high))
            time_of_death = time + Utilities.convert_time(cast(str, self.range.unit), duration)
            person.record_death(time_of_death, reason)
            return True
        else:
            person.record_death(time, reason)
            return True


class Vaccine(State):
    """Java: Vaccine; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Vaccine#Vaccine.

        Java overloads:
        ()
        """
        self.series: int
        self.codes: list[Code]
        raise NotImplementedError("Java: Vaccine#Vaccine — pending T19/T20")

    def clone(self) -> Vaccine:
        """Java: Vaccine#clone.

        Java overloads:
        ()
        """
        return cast(Vaccine, super().clone())

    def process(self, person: Person, time: int) -> bool:
        """Java: Vaccine#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Vaccine#process — pending T19/T20")


setattr(State, "Initial", Initial)  # noqa: B010
setattr(State, "Simple", Simple)  # noqa: B010
setattr(State, "CallSubmodule", CallSubmodule)  # noqa: B010
setattr(State, "Physiology", Physiology)  # noqa: B010
setattr(State, "Terminal", Terminal)  # noqa: B010
setattr(State, "Delayable", Delayable)  # noqa: B010
setattr(State, "LegacyStateWithUnitlessRV", LegacyStateWithUnitlessRV)  # noqa: B010
setattr(State, "Delay", Delay)  # noqa: B010
setattr(State, "Guard", Guard)  # noqa: B010
setattr(State, "SetAttribute", SetAttribute)  # noqa: B010
setattr(State, "Counter", Counter)  # noqa: B010
setattr(State, "TelemedicinePossibility", TelemedicinePossibility)  # noqa: B010
setattr(State, "Encounter", Encounter)  # noqa: B010
setattr(State, "EncounterEnd", EncounterEnd)  # noqa: B010
setattr(State, "AttributeAssignableState", AttributeAssignableState)  # noqa: B010
setattr(State, "OnsetState", OnsetState)  # noqa: B010
setattr(State, "ConditionOnset", ConditionOnset)  # noqa: B010
setattr(State, "ConditionEnd", ConditionEnd)  # noqa: B010
setattr(State, "AllergyOnset", AllergyOnset)  # noqa: B010
setattr(State, "AllergyEnd", AllergyEnd)  # noqa: B010
setattr(State, "MedicationOrder", MedicationOrder)  # noqa: B010
setattr(State, "MedicationEnd", MedicationEnd)  # noqa: B010
setattr(State, "CarePlanStart", CarePlanStart)  # noqa: B010
setattr(State, "CarePlanEnd", CarePlanEnd)  # noqa: B010
setattr(State, "Procedure", Procedure)  # noqa: B010
setattr(State, "VitalSign", VitalSign)  # noqa: B010
setattr(State, "Observation", Observation)  # noqa: B010
setattr(State, "ObservationGroup", ObservationGroup)  # noqa: B010
setattr(State, "MultiObservation", MultiObservation)  # noqa: B010
setattr(State, "DiagnosticReport", DiagnosticReport)  # noqa: B010
setattr(State, "ImagingStudy", ImagingStudy)  # noqa: B010
setattr(State, "Symptom", Symptom)  # noqa: B010
setattr(State, "Device", Device)  # noqa: B010
setattr(State, "DeviceEnd", DeviceEnd)  # noqa: B010
setattr(State, "SupplyList", SupplyList)  # noqa: B010
setattr(State, "Death", Death)  # noqa: B010
setattr(State, "Vaccine", Vaccine)  # noqa: B010
setattr(SupplyList, "SupplyComponent", SupplyComponent)  # noqa: B010

# Java static data initialization; constructors remain stubs.
MedicationEnd.EXPIRED = object.__new__(Code)
MedicationEnd.EXPIRED.system = "SNOMED-CT"
MedicationEnd.EXPIRED.code = "182840001"
MedicationEnd.EXPIRED.display = "Drug treatment stopped - medical advice"
MedicationEnd.EXPIRED.version = None
MedicationEnd.EXPIRED.value_set = None
CarePlanEnd.FINISHED = object.__new__(Code)
CarePlanEnd.FINISHED.system = "SNOMED-CT"
CarePlanEnd.FINISHED.code = "385658003"
CarePlanEnd.FINISHED.display = "Done"
CarePlanEnd.FINISHED.version = None
CarePlanEnd.FINISHED.value_set = None
