"""Java: org.mitre.synthea.engine.Transition (T18).

Transition represents all the transition types within the generic module
framework. This class is stateless, and calling ``follow`` on an instance must
not modify state as instances of Transition within States and Modules are
shared across the population.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, NamedTuple

from synthea.helpers.utilities import LongRange
from synthea.javacompat.hashing import list_hash_code

if TYPE_CHECKING:
    from synthea.engine.logic import Logic
    from synthea.world.agents.person import Person
    from synthea.world.concepts.telemedicine_config import TelemedicineConfig


class IntRange(NamedTuple):
    """Java: org.apache.commons.lang3.Range<Integer> (from ``Range.between``).

    An external library value type (not Components.Range); only the
    minimum/maximum pair is observable, and ``Range.between`` sorts its
    endpoints. Mirrors the ``LongRange`` pattern in helpers.utilities.
    """

    minimum: int
    maximum: int


def _range_contains(rng: IntRange | LongRange, value: int) -> bool:
    """Java: org.apache.commons.lang3.Range#contains (inclusive both ends)."""
    return rng.minimum <= value <= rng.maximum


def _range_contains_range(outer: IntRange | LongRange, inner: IntRange | LongRange) -> bool:
    """Java: org.apache.commons.lang3.Range#containsRange."""
    return outer.minimum <= inner.minimum and inner.maximum <= outer.maximum


def _range_to_string(rng: IntRange | LongRange) -> str:
    """Java: org.apache.commons.lang3.Range#toString: ``[minimum,maximum]``."""
    return f"[{rng.minimum},{rng.maximum}]"


def _java_boxed_equals(left: int, right: int) -> bool:
    """Java ``==`` on two boxed Integer/Long objects.

    Java compares references; values produced by ``valueOf``/autoboxing are
    the same object only inside the -128..127 cache range, so two distinct
    boxed values outside that range compare unequal even when numerically
    equal. Reproduced from LookupTableKey.equals (see porting notes T18).
    """
    return left == right and -128 <= left <= 127


class Transition(ABC):
    """Java: Transition — abstract base for every transition type."""

    def __init__(self) -> None:
        """Java: Transition#Transition (implicit default constructor)."""
        self.remarks: list[str] | None = None

    @abstractmethod
    def follow(self, person: Person, time: int) -> str:
        """Java: Transition#follow — abstract; subclasses implement it.

        Java overloads:
        (Person person, long time)
        """

    @staticmethod
    def pick_distributed_transition(
        transitions: list[DistributedTransitionOption], person: Person
    ) -> str:
        """Java: Transition#pickDistributedTransition.

        Java overloads:
        (List transitions, Person person)
        """
        p = person.rand()
        high = 0.0
        for option in transitions:
            Transition.process_distributed_transition(option)
            if option.numeric_distribution is not None:
                high += option.numeric_distribution
            else:
                nd = option.named_distribution
                assert nd is not None
                dist = nd.default_distribution
                if nd.attribute in person.attributes:
                    dist = float(person.attributes[nd.attribute])  # type: ignore[arg-type]
                high += dist
            if p < high:
                return option.transition
        # fallback, just return the last transition
        last = transitions[len(transitions) - 1]
        return last.transition

    @staticmethod
    def process_distributed_transition(option: DistributedTransitionOption) -> None:
        """Java: Transition#processDistributedTransition.

        Java overloads:
        (DistributedTransitionOption option)
        """
        if option.numeric_distribution is not None or option.named_distribution is not None:
            return
        if isinstance(option.distribution, float):
            option.numeric_distribution = option.distribution
        elif isinstance(option.distribution, int) and not isinstance(option.distribution, bool):
            # Gson materializes a JSON number for an Object field as a Double;
            # the test builders do the same, so an int here is treated as one.
            option.numeric_distribution = float(option.distribution)
        else:
            option.named_distribution = NamedDistribution(option.distribution)  # type: ignore[arg-type]


class DirectTransition(Transition):
    """Java: Transition.DirectTransition — transitions directly to a state."""

    def __init__(self, transition: str) -> None:
        """Java: DirectTransition#DirectTransition.

        Java overloads:
        (String transition)
        """
        super().__init__()
        self.transition: str = transition

    def follow(self, person: Person, time: int) -> str:
        """Java: DirectTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        return self.transition


class TransitionOption:
    """Java: Transition.TransitionOption — a single destination state."""

    def __init__(self) -> None:
        """Java: TransitionOption#TransitionOption (implicit constructor)."""
        self.transition: str = None  # type: ignore[assignment]


class DistributedTransitionOption(TransitionOption):
    """Java: Transition.DistributedTransitionOption."""

    def __init__(self, transition: str | None = None, probability: float | None = None) -> None:
        """Java: DistributedTransitionOption#DistributedTransitionOption.

        Java overloads:
        ()
        (String transition, double probability)
        """
        super().__init__()
        self.distribution: object = None
        self.numeric_distribution: float | None = None
        self.named_distribution: NamedDistribution | None = None
        if transition is not None:
            self.transition = transition
        if probability is not None:
            self.numeric_distribution = probability


class DistributedTransition(Transition):
    """Java: Transition.DistributedTransition."""

    def __init__(self, transitions: list[DistributedTransitionOption]) -> None:
        """Java: DistributedTransition#DistributedTransition.

        Java overloads:
        (List transitions)
        """
        super().__init__()
        self.transitions: list[DistributedTransitionOption] = transitions

    def follow(self, person: Person, time: int) -> str:
        """Java: DistributedTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        return Transition.pick_distributed_transition(self.transitions, person)


class TypeOfCareTransition(Transition):
    """Java: Transition.TypeOfCareTransition."""

    def __init__(self, options: TypeOfCareTransitionOptions) -> None:
        """Java: TypeOfCareTransition#TypeOfCareTransition.

        Java overloads:
        (TypeOfCareTransitionOptions options)
        """
        super().__init__()
        from synthea.world.concepts.telemedicine_config import TelemedicineConfig

        self.ambulatory: str = options.ambulatory
        self.emergency: str = options.emergency
        self.telemedicine: str = options.telemedicine
        self.config: TelemedicineConfig = TelemedicineConfig.from_json()

    def follow(self, person: Person, time: int) -> str:
        """Java: TypeOfCareTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        from synthea.world.agents.payer_manager import PayerManager
        from synthea.world.concepts.telemedicine_config import TelemedicineConfig

        current = person.coverage.get_plan_at_time(time)
        if current is not None:
            insurance_name = current.get_payer().get_name()
        else:
            insurance_name = PayerManager.NO_INSURANCE
        config = self.config
        high_use = config.get_high_emergency_use_insurance_names()
        assert high_use is not None
        if time < config.get_telemedicine_start_time():
            if insurance_name in high_use:
                distro = config.get_pre_telemed_high_emergency()
            else:
                distro = config.get_pre_telemed_typical_emergency()
        else:
            if insurance_name in high_use:
                distro = config.get_telemed_high_emergency()
            else:
                distro = config.get_telemed_typical_emergency()
        assert distro is not None
        # Java: synchronized (distro) { reseed; sample; } — single-threaded here.
        distro.reseed_random_generator(person.rand_long())
        selected_transition = distro.sample()
        if selected_transition == TelemedicineConfig.AMBULATORY:
            return self.ambulatory
        if selected_transition == TelemedicineConfig.EMERGENCY:
            return self.emergency
        if selected_transition == TelemedicineConfig.TELEMEDICINE:
            return self.telemedicine
        raise RuntimeError("Selected transition is not ambulatory, emergency or telemedicine.")


class TypeOfCareTransitionOptions:
    """Java: Transition.TypeOfCareTransitionOptions."""

    def __init__(self) -> None:
        """Java: TypeOfCareTransitionOptions#TypeOfCareTransitionOptions."""
        self.ambulatory: str = None  # type: ignore[assignment]
        self.telemedicine: str = None  # type: ignore[assignment]
        self.emergency: str = None  # type: ignore[assignment]


class LookupTableTransitionOption(TransitionOption):
    """Java: Transition.LookupTableTransitionOption."""

    def __init__(self) -> None:
        """Java: LookupTableTransitionOption#LookupTableTransitionOption."""
        super().__init__()
        self.lookup_table_name: str = None  # type: ignore[assignment]
        self.default_probability: float = 0.0


class LookupTableMap:
    """Java: HashMap<LookupTableKey, List<DistributedTransitionOption>>.

    A list-backed stand-in for the one Java HashMap in Transition. Two Java
    properties rule out both dict and javacompat's JavaHashMap here:

    * HashMap lookup calls the *lookup* key's ``equals`` against the stored
      key, and LookupTableKey.equals is asymmetric (a person key matches a
      row key while the row key does not match the person key). A Python
      dict compares in the stored-key direction and misses.
    * Every key hashes to its attributes list, so same-attribute rows share
      a bucket; with more than 8 in a bucket Java treeifies and tie-breaks
      by System.identityHashCode, which is not reproducible. The map is
      never iterated by Transition (only get/put), so that order is
      unobservable and a linear scan is faithful.
    """

    def __init__(self) -> None:
        """Java: HashMap#HashMap (implicit, via field initializer)."""
        self._entries: list[tuple[LookupTableKey, list[DistributedTransitionOption]]] = []

    def put(
        self, key: LookupTableKey, value: list[DistributedTransitionOption]
    ) -> list[DistributedTransitionOption] | None:
        """Java: HashMap#put — replaces when the *new* key equals a stored one."""
        for i, (stored, old) in enumerate(self._entries):
            if key.hash_code() == stored.hash_code() and key.equals(stored):
                self._entries[i] = (stored, value)
                return old
        self._entries.append((key, value))
        return None

    def get(self, key: LookupTableKey) -> list[DistributedTransitionOption] | None:
        """Java: HashMap#get — the *lookup* key's equals decides the match."""
        for stored, value in self._entries:
            if key.hash_code() == stored.hash_code() and key.equals(stored):
                return value
        return None

    def __len__(self) -> int:
        """Java: HashMap#size."""
        return len(self._entries)

    def keys(self) -> list[LookupTableKey]:
        """Java: HashMap#keySet — stored keys (diagnostics/tests only; the
        Java iteration order of this map is unobservable, see class doc)."""
        return [key for key, _ in self._entries]


class LookupTableTransition(Transition):
    """Java: Transition.LookupTableTransition."""

    # Java: private static HashMap<String, HashMap<LookupTableKey, List<...>>>
    lookupTables: ClassVar[dict[str, LookupTableMap]] = {}

    def __init__(self, lookup_table_transitions: list[LookupTableTransitionOption]) -> None:
        """Java: LookupTableTransition#LookupTableTransition.

        Java overloads:
        (List lookupTableTransitions)
        """
        super().__init__()
        self.transitions: list[LookupTableTransitionOption] = lookup_table_transitions
        self.attributes: list[str] | None = None
        self.default_transitions: list[DistributedTransitionOption] = (
            self.load_default_transitions()
        )
        self.lookup_table_name: str = lookup_table_transitions[0].lookup_table_name
        if self.lookup_table_name is None:
            raise RuntimeError("LOOKUP TABLE JSON ERROR: Table name cannot be null.")
        if self.lookup_table_name not in LookupTableTransition.lookupTables:
            self.load_lookup_table()

    def load_default_transitions(self) -> list[DistributedTransitionOption]:
        """Java: LookupTableTransition#loadDefaultTransitions.

        Java overloads:
        ()
        """
        default_transitions: list[DistributedTransitionOption] = []
        for transition_option in self.transitions:
            distributed = DistributedTransitionOption()
            distributed.transition = transition_option.transition
            distributed.numeric_distribution = transition_option.default_probability
            default_transitions.append(distributed)
        return default_transitions

    def load_lookup_table(self) -> None:
        """Java: LookupTableTransition#loadLookupTable.

        Java overloads:
        ()
        """
        from synthea.helpers.config import Config
        from synthea.helpers.simple_csv import SimpleCSV
        from synthea.helpers.utilities import Utilities

        print("Loading Lookup Table: " + self.lookup_table_name)
        new_table = LookupTableMap()

        file_name = str(Config.get("generate.lookup_tables")) + self.lookup_table_name
        csv = Utilities.read_resource(file_name, True, True)
        lookup_table = SimpleCSV.parse(csv)

        if lookup_table is None or len(lookup_table) == 0:
            raise RuntimeError("The lookup table is null or empty.")
        column_headers = list(lookup_table[0].keys())
        # Parse the list of attributes.
        self.attributes = column_headers[0 : len(column_headers) - len(self.transitions)]
        # Parse the list of states to transition to.
        transition_states = column_headers[
            len(column_headers) - len(self.transitions) : len(column_headers)
        ]

        for current_row in lookup_table:
            row_attributes = list(current_row.values())
            row_attributes = row_attributes[0 : len(self.attributes)]
            age_range: IntRange | None = None
            time_range: LongRange | None = None
            if "age" in self.attributes:
                age_index = self.attributes.index("age")
                value = row_attributes.pop(age_index)
                first_dash = value.find("-")
                if (
                    "-" not in value
                    or len(value[0:first_dash]) < 1
                    or len(value[first_dash + 1 :]) < 1
                ):
                    raise RuntimeError(
                        "LOOKUP TABLE '"
                        + file_name
                        + "' ERROR: Age Range must be in the form: 'ageLow-ageHigh'. Found '"
                        + value
                        + "'"
                    )
                low = int(value[0:first_dash])
                high = int(value[first_dash + 1 :])
                age_range = IntRange(min(low, high), max(low, high))
            if "time" in self.attributes:
                time_index = self.attributes.index("time")
                value = row_attributes.pop(time_index)
                time_range = Utilities.parse_date_range(value)
            attributes_lookup_key = LookupTableKey(row_attributes, age_range, time_range)
            transition_probabilities = self.create_distributed_transition_options(
                current_row, transition_states
            )
            new_table.put(attributes_lookup_key, transition_probabilities)

        LookupTableTransition.lookupTables[self.lookup_table_name] = new_table

    def create_distributed_transition_options(
        self, current_row: dict[str, str], transition_states: list[str]
    ) -> list[DistributedTransitionOption]:
        """Java: LookupTableTransition#createDistributedTransitionOptions.

        Java overloads:
        (Map currentRow, List transitionStates)
        """
        transition_probabilities: list[DistributedTransitionOption] = []
        for transition_name in transition_states:
            if transition_name in current_row and any(
                t.transition == transition_name for t in self.transitions
            ):
                current_option = DistributedTransitionOption()
                current_option.numeric_distribution = float(current_row[transition_name])
                current_option.transition = transition_name
                transition_probabilities.append(current_option)
            else:
                raise RuntimeError(
                    "LOOKUP TABLE ERROR: CSV column state name '"
                    + transition_name
                    + "' does not match a JSON state to transition to in CSV '"
                    + self.lookup_table_name
                    + "'"
                )
        return transition_probabilities

    def follow(self, person: Person, time: int) -> str:
        """Java: LookupTableTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        age: int | None = None
        persons_attributes: list[str] = []
        # Java quirk, reproduced: ``attributes`` is only set on the instance
        # that loaded the table; on any other instance it is null and this
        # loop throws (NullPointerException in Java, TypeError here).
        for current_attribute in self.attributes:  # type: ignore[union-attr]
            if current_attribute.lower() == "age":
                age = person.age_in_years(time)
            elif current_attribute.lower() == "time":
                # do nothing, we already have it
                pass
            else:
                if current_attribute not in person.attributes:
                    raise RuntimeError(
                        "LOOKUP TABLE ERROR: Attribute '"
                        + current_attribute
                        + "' in CSV table '"
                        + self.lookup_table_name
                        + "' does not exist as one of this person's attributes."
                    )
                persons_attribute = str(person.attributes[current_attribute])
                persons_attributes.append(persons_attribute)
        persons_key = LookupTableKey(persons_attributes, age, time)
        table = LookupTableTransition.lookupTables[self.lookup_table_name]
        matched = table.get(persons_key)
        if matched is not None:
            return Transition.pick_distributed_transition(matched, person)
        return Transition.pick_distributed_transition(self.default_transitions, person)


class LookupTableKey:
    """Java: Transition.LookupTableKey — key for lookup tables."""

    def __init__(
        self,
        attributes: list[str],
        age_or_range: int | IntRange | None,
        time_or_time_range: int | LongRange | None,
    ) -> None:
        """Java: LookupTableKey#LookupTableKey.

        Java overloads:
        (List attributes, Integer age, Long time)
        (List attributes, Range range, Range timeRange)
        """
        self.attributes: list[str] = attributes
        if isinstance(age_or_range, IntRange):
            self.age: int | None = None
            self.age_range: IntRange | None = age_or_range
        else:
            self.age = age_or_range
            self.age_range = None
        if isinstance(time_or_time_range, LongRange):
            self.time: int | None = None
            self.time_range: LongRange | None = time_or_time_range
        else:
            self.time = time_or_time_range
            self.time_range = None

    def hash_code(self) -> int:
        """Java: LookupTableKey#hashCode — the hash of the attributes list,
        forcing age ranges to collide.

        Java overloads:
        ()
        """
        return list_hash_code(self.attributes)

    def equals(self, obj: object) -> bool:
        """Java: LookupTableKey#equals.

        Java overloads:
        (Object obj)
        """
        if obj is None or type(obj) is not type(self):
            return False
        that = obj
        assert isinstance(that, LookupTableKey)

        ages_match = True
        times_match = True

        if self.age is not None:
            if that.age is not None:
                ages_match = _java_boxed_equals(self.age, that.age)
            elif that.age_range is not None:
                ages_match = _range_contains(that.age_range, self.age)
            else:
                ages_match = False
        elif that.age is not None:
            if self.age_range is not None:
                ages_match = _range_contains(self.age_range, that.age)
            else:
                ages_match = False
        elif self.age_range is not None:
            if that.age_range is not None:
                ages_match = _range_contains_range(self.age_range, that.age_range)
            else:
                ages_match = False
        elif that.age_range is not None:
            ages_match = False

        if self.time is not None:
            if that.time is not None:
                times_match = _java_boxed_equals(self.time, that.time)
            elif that.time_range is not None:
                times_match = _range_contains(that.time_range, self.time)
            else:
                # do nothing. Time will always be populated in one of them
                pass
        elif that.time is not None:
            if self.time_range is not None:
                times_match = _range_contains(self.time_range, that.time)
            else:
                times_match = False
        elif self.time_range is not None:
            if that.time_range is not None:
                times_match = _range_contains_range(self.time_range, that.time_range)
            else:
                times_match = False
        elif that.time_range is not None:
            times_match = False

        return ages_match and times_match and self.attributes == that.attributes

    def to_string(self) -> str:
        """Java: LookupTableKey#toString.

        Java overloads:
        ()
        """
        ending = ""
        if self.age is not None or self.age_range is not None:
            ending = _range_to_string(self.age_range) if self.age is None else str(self.age)  # type: ignore[arg-type]
        if self.time is not None or self.time_range is not None:
            ending = _range_to_string(self.time_range) if self.time is None else str(self.time)  # type: ignore[arg-type]
        return "[" + ", ".join(self.attributes) + "]" + " : " + ending

    __hash__ = hash_code
    __eq__ = equals
    __str__ = to_string
    __repr__ = to_string


class ConditionalTransitionOption(TransitionOption):
    """Java: Transition.ConditionalTransitionOption."""

    def __init__(self) -> None:
        """Java: ConditionalTransitionOption#ConditionalTransitionOption."""
        super().__init__()
        self.condition: Logic | None = None


class ConditionalTransition(Transition):
    """Java: Transition.ConditionalTransition."""

    def __init__(self, transitions: list[ConditionalTransitionOption]) -> None:
        """Java: ConditionalTransition#ConditionalTransition.

        Java overloads:
        (List transitions)
        """
        super().__init__()
        self.transitions: list[ConditionalTransitionOption] = transitions

    def follow(self, person: Person, time: int) -> str:
        """Java: ConditionalTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        for option in self.transitions:
            if option.condition is None or option.condition.test(person, time):
                return option.transition
        # fallback, just return the last transition
        last = self.transitions[len(self.transitions) - 1]
        return last.transition


class ComplexTransitionOption(TransitionOption):
    """Java: Transition.ComplexTransitionOption."""

    def __init__(self) -> None:
        """Java: ComplexTransitionOption#ComplexTransitionOption."""
        super().__init__()
        self.condition: Logic | None = None
        self.distributions: list[DistributedTransitionOption] | None = None


class ComplexTransition(Transition):
    """Java: Transition.ComplexTransition."""

    def __init__(self, transitions: list[ComplexTransitionOption]) -> None:
        """Java: ComplexTransition#ComplexTransition.

        Java overloads:
        (List transitions)
        """
        super().__init__()
        self.transitions: list[ComplexTransitionOption] = transitions

    def follow(
        self,
        person_or_option: Person | ComplexTransitionOption,
        time_or_person: int | Person,
    ) -> str:
        """Java: ComplexTransition#follow.

        Java overloads:
        (Person person, long time)
        (ComplexTransitionOption option, Person person)
        """
        if isinstance(person_or_option, ComplexTransitionOption):
            option = person_or_option
            person = time_or_person
            assert isinstance(person, object)
            if option.transition is not None:
                return option.transition
            if option.distributions is not None:
                return Transition.pick_distributed_transition(option.distributions, person)
            raise ValueError("Complex Transition must have either transition or distributions")
        person = person_or_option
        time = time_or_person
        assert isinstance(time, int)
        for option in self.transitions:
            if option.condition is None or option.condition.test(person, time):
                return self.follow(option, person)
        # fallback, just return the last transition
        last = self.transitions[len(self.transitions) - 1]
        return self.follow(last, person)


class NamedDistribution:
    """Java: Transition.NamedDistribution."""

    def __init__(self, definition: dict[str, object]) -> None:
        """Java: NamedDistribution#NamedDistribution.

        Java overloads:
        (JsonObject definition)
        (Map definition)
        """
        self.attribute: str = definition["attribute"]  # type: ignore[assignment]
        self.default_distribution: float = float(definition["default"])  # type: ignore[arg-type]


setattr(Transition, "DirectTransition", DirectTransition)  # noqa: B010
setattr(Transition, "TransitionOption", TransitionOption)  # noqa: B010
setattr(Transition, "DistributedTransitionOption", DistributedTransitionOption)  # noqa: B010
setattr(Transition, "DistributedTransition", DistributedTransition)  # noqa: B010
setattr(Transition, "TypeOfCareTransition", TypeOfCareTransition)  # noqa: B010
setattr(Transition, "TypeOfCareTransitionOptions", TypeOfCareTransitionOptions)  # noqa: B010
setattr(Transition, "LookupTableTransitionOption", LookupTableTransitionOption)  # noqa: B010
setattr(Transition, "LookupTableTransition", LookupTableTransition)  # noqa: B010
setattr(Transition, "LookupTableKey", LookupTableKey)  # noqa: B010
setattr(Transition, "ConditionalTransitionOption", ConditionalTransitionOption)  # noqa: B010
setattr(Transition, "ConditionalTransition", ConditionalTransition)  # noqa: B010
setattr(Transition, "ComplexTransitionOption", ComplexTransitionOption)  # noqa: B010
setattr(Transition, "ComplexTransition", ComplexTransition)  # noqa: B010
setattr(Transition, "NamedDistribution", NamedDistribution)  # noqa: B010
