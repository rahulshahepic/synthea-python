"""Java API skeleton: State.java."""

from __future__ import annotations

from enum import StrEnum
from typing import IO, TYPE_CHECKING, ClassVar, Protocol

from synthea.world.concepts.health_record import Code

if TYPE_CHECKING:
    from synthea.engine.components import (
        Attachment,
        Exact,
        ExactWithUnit,
        Range,
        RangeWithUnit,
        SampledData,
    )
    from synthea.engine.distribution import Distribution
    from synthea.engine.logic import Logic
    from synthea.engine.module import Module
    from synthea.engine.reaction_probabilities import ReactionProbabilities
    from synthea.engine.transition import (
        ComplexTransitionOption,
        ConditionalTransitionOption,
        DistributedTransitionOption,
        LookupTableTransitionOption,
        Transition,
        TypeOfCareTransitionOptions,
    )
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code, Entry, Medication
    from synthea.world.concepts.health_record import Code as HealthRecordCode
    from synthea.world.concepts.health_record import Series as HealthRecordSeries
    from synthea.world.concepts.vital_sign import VitalSign as ConceptVitalSign

    class IoMapper(Protocol):
        """Java boundary type: IoMapper; external to the mapped Python port."""

    class PhysiologySimulator(Protocol):
        """Java boundary type: PhysiologySimulator; external to the mapped Python port."""

    class ThreadLocal(Protocol):
        """Java boundary type: ThreadLocal; external to the mapped Python port."""


class State:
    """Java: State; pending T19/T20."""

    ENABLE_PHYSIOLOGY_STATE: ClassVar[bool]  # Java initialization deferred to T19/T20.

    def __init__(self) -> None:
        """Java: State#State.

        Java overloads:
        ()
        """
        self.module: Module
        self.name: str
        self.entered: int
        self.entry: Entry
        self.exited: int
        self._transition: Transition
        self.direct_transition: str
        self.conditional_transition: list[ConditionalTransitionOption]
        self.distributed_transition: list[DistributedTransitionOption]
        self.complex_transition: list[ComplexTransitionOption]
        self.lookup_table_transition: list[LookupTableTransitionOption]
        self.type_of_care_transition: TypeOfCareTransitionOptions
        self.remarks: list[str]
        raise NotImplementedError("Java: State#State — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: State#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        raise NotImplementedError("Java: State#initialize — pending T19/T20")

    @staticmethod
    def build(module: Module, name: str, definition: dict[str, object]) -> State:
        """Java: State#build.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        raise NotImplementedError("Java: State#build — pending T19/T20")

    def clone(self) -> State:
        """Java: State#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: State#clone — pending T19/T20")

    def transition(self, person: Person, time: int) -> str:
        """Java: State#transition.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: State#transition — pending T19/T20")

    def get_transition(self) -> Transition:
        """Java: State#getTransition.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: State#getTransition — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: State#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: State#process — pending T19/T20")

    def run(self, person: Person, time: int, terminate_on_death: bool) -> bool:
        """Java: State#run.

        Java overloads:
        (Person person, long time, boolean terminateOnDeath)
        """
        raise NotImplementedError("Java: State#run — pending T19/T20")

    def to_string(self) -> str:
        """Java: State#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: State#toString — pending T19/T20")


class Initial(State):
    """Java: Initial; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Initial#Initial.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Initial#Initial — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Initial#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Initial#process — pending T19/T20")


class Simple(State):
    """Java: Simple; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Simple#Simple.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Simple#Simple — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Simple#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Simple#process — pending T19/T20")


class CallSubmodule(State):
    """Java: CallSubmodule; pending T19/T20."""

    def __init__(self) -> None:
        """Java: CallSubmodule#CallSubmodule.

        Java overloads:
        ()
        """
        self.submodule: str
        self.submodule_exited: int
        raise NotImplementedError("Java: CallSubmodule#CallSubmodule — pending T19/T20")

    def clone(self) -> CallSubmodule:
        """Java: CallSubmodule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CallSubmodule#clone — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: CallSubmodule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CallSubmodule#process — pending T19/T20")


class Physiology(State):
    """Java: Physiology; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Physiology#Physiology.

        Java overloads:
        ()
        """
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
        raise NotImplementedError("Java: Physiology#Physiology — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Physiology#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        raise NotImplementedError("Java: Physiology#initialize — pending T19/T20")

    def setup(self) -> None:
        """Java: Physiology#setup.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Physiology#setup — pending T19/T20")

    def clone(self) -> Physiology:
        """Java: Physiology#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Physiology#clone — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Physiology#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Physiology#process — pending T19/T20")

    def transition(self, person: Person, time: int) -> str:
        """Java: Physiology#transition.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Physiology#transition — pending T19/T20")


class Terminal(State):
    """Java: Terminal; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Terminal#Terminal.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Terminal#Terminal — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Terminal#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Terminal#process — pending T19/T20")


class Delayable(State):
    """Java: Delayable; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Delayable#Delayable.

        Java overloads:
        ()
        """
        self.next: int
        raise NotImplementedError("Java: Delayable#Delayable — pending T19/T20")

    def clone(self) -> Delayable:
        """Java: Delayable#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Delayable#clone — pending T19/T20")

    def end_of_delay(self, time: int, person: Person) -> int:
        """Java: Delayable#endOfDelay.

        Java overloads:
        (long time, Person person)
        """
        raise NotImplementedError("Java: Delayable#endOfDelay — pending T19/T20")

    def process_once(self, person: Person, time: int) -> None:
        """Java: Delayable#processOnce.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Delayable#processOnce — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Delayable#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Delayable#process — pending T19/T20")


class LegacyStateWithUnitlessRV(State):
    """Java: LegacyStateWithUnitlessRV; pending T19/T20."""

    def __init__(self) -> None:
        """Java: LegacyStateWithUnitlessRV#LegacyStateWithUnitlessRV.

        Java overloads:
        ()
        """
        self.range: Range
        self.exact: Exact
        raise NotImplementedError(
            "Java: LegacyStateWithUnitlessRV#LegacyStateWithUnitlessRV — pending T19/T20"
        )

    def clone(self) -> State:
        """Java: LegacyStateWithUnitlessRV#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LegacyStateWithUnitlessRV#clone — pending T19/T20")

    def is_legacy_gmf(self) -> bool:
        """Java: LegacyStateWithUnitlessRV#isLegacyGmf.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LegacyStateWithUnitlessRV#isLegacyGmf — pending T19/T20")


class Delay(Delayable):
    """Java: Delay; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Delay#Delay.

        Java overloads:
        ()
        """
        self.range: RangeWithUnit[float]
        self.exact: ExactWithUnit[float]
        self.distribution: Distribution
        self.unit: str
        raise NotImplementedError("Java: Delay#Delay — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Delay#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        raise NotImplementedError("Java: Delay#initialize — pending T19/T20")

    def clone(self) -> Delay:
        """Java: Delay#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Delay#clone — pending T19/T20")

    def end_of_delay(self, time: int, person: Person) -> int:
        """Java: Delay#endOfDelay.

        Java overloads:
        (long time, Person person)
        """
        raise NotImplementedError("Java: Delay#endOfDelay — pending T19/T20")

    def is_legacy_gmf(self) -> bool:
        """Java: Delay#isLegacyGmf.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Delay#isLegacyGmf — pending T19/T20")


class Guard(State):
    """Java: Guard; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Guard#Guard.

        Java overloads:
        ()
        """
        self.allow: Logic
        raise NotImplementedError("Java: Guard#Guard — pending T19/T20")

    def clone(self) -> Guard:
        """Java: Guard#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Guard#clone — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Guard#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Guard#process — pending T19/T20")


class SetAttribute(State):
    """Java: SetAttribute; pending T19/T20."""

    def __init__(self) -> None:
        """Java: SetAttribute#SetAttribute.

        Java overloads:
        ()
        """
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
        raise NotImplementedError("Java: SetAttribute#SetAttribute — pending T19/T20")

    def get_exp_processor(self) -> ThreadLocal:
        """Java: SetAttribute#getExpProcessor.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SetAttribute#getExpProcessor — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: SetAttribute#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        raise NotImplementedError("Java: SetAttribute#initialize — pending T19/T20")

    def clone(self) -> SetAttribute:
        """Java: SetAttribute#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SetAttribute#clone — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: SetAttribute#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: SetAttribute#process — pending T19/T20")


class Counter(State):
    """Java: Counter; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Counter#Counter.

        Java overloads:
        ()
        """
        self.attribute: str
        self.action: str
        self.increment: bool
        self.amount: int
        raise NotImplementedError("Java: Counter#Counter — pending T19/T20")

    def initialize(self, module: Module, name: str, definition: dict[str, object]) -> None:
        """Java: Counter#initialize.

        Java overloads:
        (Module module, String name, JsonObject definition)
        """
        raise NotImplementedError("Java: Counter#initialize — pending T19/T20")

    def clone(self) -> Counter:
        """Java: Counter#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Counter#clone — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Counter#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Counter#process — pending T19/T20")


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
        raise NotImplementedError("Java: Encounter#clone — pending T19/T20")

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
        raise NotImplementedError("Java: EncounterEnd#clone — pending T19/T20")

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
        raise NotImplementedError("Java: OnsetState#clone — pending T19/T20")

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
        raise NotImplementedError("Java: ConditionEnd#clone — pending T19/T20")

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
        raise NotImplementedError("Java: AllergyEnd#clone — pending T19/T20")

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
        raise NotImplementedError("Java: MedicationOrder#clone — pending T19/T20")

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
        raise NotImplementedError("Java: MedicationEnd#clone — pending T19/T20")

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
        raise NotImplementedError("Java: CarePlanStart#clone — pending T19/T20")

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
        raise NotImplementedError("Java: CarePlanEnd#clone — pending T19/T20")

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
        raise NotImplementedError("Java: Procedure#initialize — pending T19/T20")

    def clone(self) -> Procedure:
        """Java: Procedure#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Procedure#clone — pending T19/T20")

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
        raise NotImplementedError("Java: VitalSign#initialize — pending T19/T20")

    def get_exp_processor(self) -> ThreadLocal:
        """Java: VitalSign#getExpProcessor.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: VitalSign#getExpProcessor — pending T19/T20")

    def clone(self) -> VitalSign:
        """Java: VitalSign#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: VitalSign#clone — pending T19/T20")

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
        raise NotImplementedError("Java: Observation#initialize — pending T19/T20")

    def validate(self, module: Module, name: str) -> None:
        """Java: Observation#validate.

        Java overloads:
        (Module module, String name)
        """
        raise NotImplementedError("Java: Observation#validate — pending T19/T20")

    def get_exp_processor(self) -> ThreadLocal:
        """Java: Observation#getExpProcessor.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Observation#getExpProcessor — pending T19/T20")

    def clone(self) -> Observation:
        """Java: Observation#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Observation#clone — pending T19/T20")

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
        raise NotImplementedError("Java: ObservationGroup#initialize — pending T19/T20")

    def clone(self) -> ObservationGroup:
        """Java: ObservationGroup#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ObservationGroup#clone — pending T19/T20")


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
        raise NotImplementedError("Java: MultiObservation#clone — pending T19/T20")

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
        raise NotImplementedError("Java: ImagingStudy#clone — pending T19/T20")

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
        raise NotImplementedError("Java: Symptom#initialize — pending T19/T20")

    def clone(self) -> Symptom:
        """Java: Symptom#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Symptom#clone — pending T19/T20")

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
        raise NotImplementedError("Java: Device#clone — pending T19/T20")

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
        raise NotImplementedError("Java: DeviceEnd#clone — pending T19/T20")

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
        raise NotImplementedError("Java: SupplyList#clone — pending T19/T20")

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
    """Java: Death; pending T19/T20."""

    def __init__(self) -> None:
        """Java: Death#Death.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.condition_onset: str
        self.referenced_by_attribute: str
        self.range: RangeWithUnit[float]
        self.exact: ExactWithUnit[float]
        raise NotImplementedError("Java: Death#Death — pending T19/T20")

    def clone(self) -> Death:
        """Java: Death#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Death#clone — pending T19/T20")

    def process(self, person: Person, time: int) -> bool:
        """Java: Death#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Death#process — pending T19/T20")


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
        raise NotImplementedError("Java: Vaccine#clone — pending T19/T20")

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
