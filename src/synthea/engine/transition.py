"""Java API skeleton: Transition.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.engine.components import Range
    from synthea.engine.logic import Logic
    from synthea.world.agents.person import Person
    from synthea.world.concepts.telemedicine_config import TelemedicineConfig


class Transition:
    """Java: Transition; pending T18."""

    def __init__(self) -> None:
        """Java: Transition#Transition.

        Java overloads:
        ()
        """
        self.remarks: list[str]
        raise NotImplementedError("Java: Transition#Transition — pending T18")

    def follow(self, person: Person, time: int) -> str:
        """Java: Transition#follow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Transition#follow — pending T18")

    @staticmethod
    def pick_distributed_transition(
        transitions: list[DistributedTransitionOption], person: Person
    ) -> str:
        """Java: Transition#pickDistributedTransition.

        Java overloads:
        (List transitions, Person person)
        """
        raise NotImplementedError("Java: Transition#pickDistributedTransition — pending T18")

    @staticmethod
    def process_distributed_transition(option: DistributedTransitionOption) -> None:
        """Java: Transition#processDistributedTransition.

        Java overloads:
        (DistributedTransitionOption option)
        """
        raise NotImplementedError("Java: Transition#processDistributedTransition — pending T18")


class DirectTransition(Transition):
    """Java: DirectTransition; pending T18."""

    def __init__(self, transition: str) -> None:
        """Java: DirectTransition#DirectTransition.

        Java overloads:
        (String transition)
        """
        self.transition: str
        raise NotImplementedError("Java: DirectTransition#DirectTransition — pending T18")

    def follow(self, person: Person, time: int) -> str:
        """Java: DirectTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: DirectTransition#follow — pending T18")


class TransitionOption:
    """Java: TransitionOption; pending T18."""

    def __init__(self) -> None:
        """Java: TransitionOption#TransitionOption.

        Java overloads:
        ()
        """
        self.transition: str
        raise NotImplementedError("Java: TransitionOption#TransitionOption — pending T18")


class DistributedTransitionOption(TransitionOption):
    """Java: DistributedTransitionOption; pending T18."""

    def __init__(self, transition: str | None = None, probability: float | None = None) -> None:
        """Java: DistributedTransitionOption#DistributedTransitionOption.

        Java overloads:
        ()
        (String transition, double probability)
        """
        self.distribution: object
        self.numeric_distribution: float
        self.named_distribution: NamedDistribution
        raise NotImplementedError(
            "Java: DistributedTransitionOption#DistributedTransitionOption — pending T18"
        )


class DistributedTransition(Transition):
    """Java: DistributedTransition; pending T18."""

    def __init__(self, transitions: list[DistributedTransitionOption]) -> None:
        """Java: DistributedTransition#DistributedTransition.

        Java overloads:
        (List transitions)
        """
        self.transitions: list[DistributedTransitionOption]
        raise NotImplementedError("Java: DistributedTransition#DistributedTransition — pending T18")

    def follow(self, person: Person, time: int) -> str:
        """Java: DistributedTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: DistributedTransition#follow — pending T18")


class TypeOfCareTransition(Transition):
    """Java: TypeOfCareTransition; pending T18."""

    def __init__(self, options: TypeOfCareTransitionOptions) -> None:
        """Java: TypeOfCareTransition#TypeOfCareTransition.

        Java overloads:
        (TypeOfCareTransitionOptions options)
        """
        self.ambulatory: str
        self.telemedicine: str
        self.emergency: str
        self.config: TelemedicineConfig
        raise NotImplementedError("Java: TypeOfCareTransition#TypeOfCareTransition — pending T18")

    def follow(self, person: Person, time: int) -> str:
        """Java: TypeOfCareTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: TypeOfCareTransition#follow — pending T18")


class TypeOfCareTransitionOptions:
    """Java: TypeOfCareTransitionOptions; pending T18."""

    def __init__(self) -> None:
        """Java: TypeOfCareTransitionOptions#TypeOfCareTransitionOptions.

        Java overloads:
        ()
        """
        self.ambulatory: str
        self.telemedicine: str
        self.emergency: str
        raise NotImplementedError(
            "Java: TypeOfCareTransitionOptions#TypeOfCareTransitionOptions — pending T18"
        )


class LookupTableTransitionOption(TransitionOption):
    """Java: LookupTableTransitionOption; pending T18."""

    def __init__(self) -> None:
        """Java: LookupTableTransitionOption#LookupTableTransitionOption.

        Java overloads:
        ()
        """
        self.lookup_table_name: str
        self.default_probability: float
        raise NotImplementedError(
            "Java: LookupTableTransitionOption#LookupTableTransitionOption — pending T18"
        )


class LookupTableTransition(Transition):
    """Java: LookupTableTransition; pending T18."""

    lookupTables: ClassVar[dict[str, dict[LookupTableKey, list[DistributedTransitionOption]]]] = {}

    def __init__(self, lookup_table_transitions: list[LookupTableTransitionOption]) -> None:
        """Java: LookupTableTransition#LookupTableTransition.

        Java overloads:
        (List lookupTableTransitions)
        """
        self.transitions: list[LookupTableTransitionOption]
        self.attributes: list[str]
        self.default_transitions: list[DistributedTransitionOption]
        self.lookup_table_name: str
        raise NotImplementedError("Java: LookupTableTransition#LookupTableTransition — pending T18")

    def load_default_transitions(self) -> list[DistributedTransitionOption]:
        """Java: LookupTableTransition#loadDefaultTransitions.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: LookupTableTransition#loadDefaultTransitions — pending T18"
        )

    def load_lookup_table(self) -> None:
        """Java: LookupTableTransition#loadLookupTable.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LookupTableTransition#loadLookupTable — pending T18")

    def create_distributed_transition_options(
        self, current_row: dict[str, str], transition_states: list[str]
    ) -> list[DistributedTransitionOption]:
        """Java: LookupTableTransition#createDistributedTransitionOptions.

        Java overloads:
        (Map currentRow, List transitionStates)
        """
        raise NotImplementedError(
            "Java: LookupTableTransition#createDistributedTransitionOptions — pending T18"
        )

    def follow(self, person: Person, time: int) -> str:
        """Java: LookupTableTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LookupTableTransition#follow — pending T18")


class LookupTableKey:
    """Java: LookupTableKey; pending T18."""

    def __init__(
        self,
        attributes: list[str],
        age_or_range: int | Range[int],
        time_or_time_range: int | Range[int],
    ) -> None:
        """Java: LookupTableKey#LookupTableKey.

        Java overloads:
        (List attributes, Integer age, Long time)
        (List attributes, Range range, Range timeRange)
        """
        self.attributes: list[str]
        self.age: int
        self.age_range: Range[int]
        self.time: int
        self.time_range: Range[int]
        raise NotImplementedError("Java: LookupTableKey#LookupTableKey — pending T18")

    def hash_code(self) -> int:
        """Java: LookupTableKey#hashCode.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LookupTableKey#hashCode — pending T18")

    def equals(self, obj: object) -> bool:
        """Java: LookupTableKey#equals.

        Java overloads:
        (Object obj)
        """
        raise NotImplementedError("Java: LookupTableKey#equals — pending T18")

    def to_string(self) -> str:
        """Java: LookupTableKey#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LookupTableKey#toString — pending T18")


class ConditionalTransitionOption(TransitionOption):
    """Java: ConditionalTransitionOption; pending T18."""

    def __init__(self) -> None:
        """Java: ConditionalTransitionOption#ConditionalTransitionOption.

        Java overloads:
        ()
        """
        self.condition: Logic
        raise NotImplementedError(
            "Java: ConditionalTransitionOption#ConditionalTransitionOption — pending T18"
        )


class ConditionalTransition(Transition):
    """Java: ConditionalTransition; pending T18."""

    def __init__(self, transitions: list[ConditionalTransitionOption]) -> None:
        """Java: ConditionalTransition#ConditionalTransition.

        Java overloads:
        (List transitions)
        """
        self.transitions: list[ConditionalTransitionOption]
        raise NotImplementedError("Java: ConditionalTransition#ConditionalTransition — pending T18")

    def follow(self, person: Person, time: int) -> str:
        """Java: ConditionalTransition#follow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: ConditionalTransition#follow — pending T18")


class ComplexTransitionOption(TransitionOption):
    """Java: ComplexTransitionOption; pending T18."""

    def __init__(self) -> None:
        """Java: ComplexTransitionOption#ComplexTransitionOption.

        Java overloads:
        ()
        """
        self.condition: Logic
        self.distributions: list[DistributedTransitionOption]
        raise NotImplementedError(
            "Java: ComplexTransitionOption#ComplexTransitionOption — pending T18"
        )


class ComplexTransition(Transition):
    """Java: ComplexTransition; pending T18."""

    def __init__(self, transitions: list[ComplexTransitionOption]) -> None:
        """Java: ComplexTransition#ComplexTransition.

        Java overloads:
        (List transitions)
        """
        self.transitions: list[ComplexTransitionOption]
        raise NotImplementedError("Java: ComplexTransition#ComplexTransition — pending T18")

    def follow(
        self, person_or_option: Person | ComplexTransitionOption, time_or_person: int | Person
    ) -> str:
        """Java: ComplexTransition#follow.

        Java overloads:
        (Person person, long time)
        (ComplexTransitionOption option, Person person)
        """
        raise NotImplementedError("Java: ComplexTransition#follow — pending T18")


class NamedDistribution:
    """Java: NamedDistribution; pending T18."""

    def __init__(self, definition: dict[str, object]) -> None:
        """Java: NamedDistribution#NamedDistribution.

        Java overloads:
        (JsonObject definition)
        (Map definition)
        """
        self.attribute: str
        self.default_distribution: float
        raise NotImplementedError("Java: NamedDistribution#NamedDistribution — pending T18")


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
