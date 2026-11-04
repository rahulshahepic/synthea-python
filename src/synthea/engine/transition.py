"""Java API skeleton for transition.py.
Java: org.mitre.synthea.engine.Transition.
"""

from __future__ import annotations


class Transition:
    """Java: Transition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Transition constructor; pending T18."""
        self.remarks: list[object] = []
        raise NotImplementedError("Java: Transition — pending T18")

    def follow(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#follow."""
        raise NotImplementedError("Java: follow — pending T18")

    def load_default_transitions(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#loadDefaultTransitions."""
        raise NotImplementedError("Java: loadDefaultTransitions — pending T18")

    def load_lookup_table(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#loadLookupTable."""
        raise NotImplementedError("Java: loadLookupTable — pending T18")

    def create_distributed_transition_options(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#createDistributedTransitionOptions."""
        raise NotImplementedError("Java: createDistributedTransitionOptions — pending T18")

    def hash_code(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#hashCode."""
        raise NotImplementedError("Java: hashCode — pending T18")

    def equals(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#equals."""
        raise NotImplementedError("Java: equals — pending T18")

    def to_string(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#toString."""
        raise NotImplementedError("Java: toString — pending T18")

    def pick_distributed_transition(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#pickDistributedTransition."""
        raise NotImplementedError("Java: pickDistributedTransition — pending T18")

    def process_distributed_transition(self, *args: object, **kwargs: object) -> object:
        """Java: Transition#processDistributedTransition."""
        raise NotImplementedError("Java: processDistributedTransition — pending T18")


class DirectTransition:
    """Java: DirectTransition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: DirectTransition constructor; pending T18."""
        self.transition: str | None = None
        raise NotImplementedError("Java: DirectTransition — pending T18")


class TransitionOption:
    """Java: TransitionOption; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: TransitionOption constructor; pending T18."""
        self.transition: str | None = None
        raise NotImplementedError("Java: TransitionOption — pending T18")


class DistributedTransitionOption:
    """Java: DistributedTransitionOption; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: DistributedTransitionOption constructor; pending T18."""
        self.distribution: object | None = None
        self.numericDistribution: object | None = None
        self.namedDistribution: object | None = None
        raise NotImplementedError("Java: DistributedTransitionOption — pending T18")


class DistributedTransition:
    """Java: DistributedTransition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: DistributedTransition constructor; pending T18."""
        self.transitions: list[object] = []
        raise NotImplementedError("Java: DistributedTransition — pending T18")


class TypeOfCareTransition:
    """Java: TypeOfCareTransition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: TypeOfCareTransition constructor; pending T18."""
        self.ambulatory: str | None = None
        self.telemedicine: str | None = None
        self.emergency: str | None = None
        self.config: object | None = None
        raise NotImplementedError("Java: TypeOfCareTransition — pending T18")


class TypeOfCareTransitionOptions:
    """Java: TypeOfCareTransitionOptions; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: TypeOfCareTransitionOptions constructor; pending T18."""
        self.ambulatory: str | None = None
        self.telemedicine: str | None = None
        self.emergency: str | None = None
        raise NotImplementedError("Java: TypeOfCareTransitionOptions — pending T18")


class LookupTableTransitionOption:
    """Java: LookupTableTransitionOption; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: LookupTableTransitionOption constructor; pending T18."""
        self.lookupTableName: str | None = None
        self.defaultProbability: float = 0.0
        raise NotImplementedError("Java: LookupTableTransitionOption — pending T18")


class LookupTableTransition:
    """Java: LookupTableTransition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: LookupTableTransition constructor; pending T18."""
        self.transitions: list[object] = []
        self.attributes: list[object] = []
        self.defaultTransitions: list[object] = []
        self.lookupTableName: str | None = None
        raise NotImplementedError("Java: LookupTableTransition — pending T18")


class LookupTableKey:
    """Java: LookupTableKey; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: LookupTableKey constructor; pending T18."""
        self.attributes: list[object] = []
        self.age: object | None = None
        self.ageRange: object | None = None
        self.time: object | None = None
        self.timeRange: object | None = None
        raise NotImplementedError("Java: LookupTableKey — pending T18")


class ConditionalTransitionOption:
    """Java: ConditionalTransitionOption; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ConditionalTransitionOption constructor; pending T18."""
        self.condition: object | None = None
        raise NotImplementedError("Java: ConditionalTransitionOption — pending T18")


class ConditionalTransition:
    """Java: ConditionalTransition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ConditionalTransition constructor; pending T18."""
        self.transitions: list[object] = []
        raise NotImplementedError("Java: ConditionalTransition — pending T18")


class ComplexTransitionOption:
    """Java: ComplexTransitionOption; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ComplexTransitionOption constructor; pending T18."""
        self.condition: object | None = None
        self.distributions: list[object] = []
        raise NotImplementedError("Java: ComplexTransitionOption — pending T18")


class ComplexTransition:
    """Java: ComplexTransition; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ComplexTransition constructor; pending T18."""
        self.transitions: list[object] = []
        raise NotImplementedError("Java: ComplexTransition — pending T18")


class NamedDistribution:
    """Java: NamedDistribution; pending T18."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: NamedDistribution constructor; pending T18."""
        self.attribute: str | None = None
        self.defaultDistribution: float = 0.0
        raise NotImplementedError("Java: NamedDistribution — pending T18")
