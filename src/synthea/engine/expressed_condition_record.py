"""Java API skeleton: ExpressedConditionRecord.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.engine.expressed_symptom import SymptomSource
    from synthea.world.agents.person import Person


class ExpressedConditionRecord:
    """Java: ExpressedConditionRecord; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686900

    def __init__(self, person: Person) -> None:
        """Java: ExpressedConditionRecord#ExpressedConditionRecord.

        Java overloads:
        (Person person)
        """
        self.sources: dict[str, ModuleConditions]
        self.person: Person
        raise NotImplementedError(
            "Java: ExpressedConditionRecord#ExpressedConditionRecord — pending T09"
        )

    def clone(self) -> ExpressedConditionRecord:
        """Java: ExpressedConditionRecord#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressedConditionRecord#clone — pending T09")

    def get_sources(self) -> dict[str, ModuleConditions]:
        """Java: ExpressedConditionRecord#getSources.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressedConditionRecord#getSources — pending T09")

    def on_condition_onset(self, module: str, state: str, condition: str, time: int) -> None:
        """Java: ExpressedConditionRecord#onConditionOnset.

        Java overloads:
        (String module, String state, String condition, long time)
        """
        raise NotImplementedError("Java: ExpressedConditionRecord#onConditionOnset — pending T09")

    def get_condition_last_onset_time_from_module(self, module: str, condition: str) -> int:
        """Java: ExpressedConditionRecord#getConditionLastOnsetTimeFromModule.

        Java overloads:
        (String module, String condition)
        """
        raise NotImplementedError(
            "Java: ExpressedConditionRecord#getConditionLastOnsetTimeFromModule — pending T09"
        )

    def get_condition_last_end_time_from_module(self, module: str, condition: str) -> int:
        """Java: ExpressedConditionRecord#getConditionLastEndTimeFromModule.

        Java overloads:
        (String module, String condition)
        """
        raise NotImplementedError(
            "Java: ExpressedConditionRecord#getConditionLastEndTimeFromModule — pending T09"
        )

    def get_condition_from_state(self, module: str, state: str) -> str:
        """Java: ExpressedConditionRecord#getConditionFromState.

        Java overloads:
        (String module, String state)
        """
        raise NotImplementedError(
            "Java: ExpressedConditionRecord#getConditionFromState — pending T09"
        )

    def on_condition_end(self, module: str, condition: str, time: int) -> None:
        """Java: ExpressedConditionRecord#onConditionEnd.

        Java overloads:
        (String module, String condition, long time)
        """
        raise NotImplementedError("Java: ExpressedConditionRecord#onConditionEnd — pending T09")

    def get_condition_symptoms(self) -> dict[int, list[ConditionWithSymptoms]]:
        """Java: ExpressedConditionRecord#getConditionSymptoms.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: ExpressedConditionRecord#getConditionSymptoms — pending T09"
        )


class ConditionPeriod:
    """Java: ConditionPeriod; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686901

    def __init__(self, onset_time: int, end_time: int | None = None) -> None:
        """Java: ConditionPeriod#ConditionPeriod.

        Java overloads:
        (Long onsetTime)
        (Long onsetTime, Long endTime)
        """
        self.end_time: int
        self.onset_time: int
        raise NotImplementedError("Java: ConditionPeriod#ConditionPeriod — pending T09")

    def clone(self) -> ConditionPeriod:
        """Java: ConditionPeriod#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionPeriod#clone — pending T09")

    def get_end_time(self) -> int:
        """Java: ConditionPeriod#getEndTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionPeriod#getEndTime — pending T09")

    def set_end_time(self, end_time: int) -> None:
        """Java: ConditionPeriod#setEndTime.

        Java overloads:
        (Long endTime)
        """
        raise NotImplementedError("Java: ConditionPeriod#setEndTime — pending T09")

    def get_onset_time(self) -> int:
        """Java: ConditionPeriod#getOnsetTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionPeriod#getOnsetTime — pending T09")


class OnsetCondition:
    """Java: OnsetCondition; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686902

    def __init__(self, name: str) -> None:
        """Java: OnsetCondition#OnsetCondition.

        Java overloads:
        (String name)
        """
        self.name: str
        self.time_infos: list[ConditionPeriod]
        raise NotImplementedError("Java: OnsetCondition#OnsetCondition — pending T09")

    def clone(self) -> OnsetCondition:
        """Java: OnsetCondition#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: OnsetCondition#clone — pending T09")

    def get_name(self) -> str:
        """Java: OnsetCondition#getName.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: OnsetCondition#getName — pending T09")

    def get_time_infos(self) -> list[ConditionPeriod]:
        """Java: OnsetCondition#getTimeInfos.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: OnsetCondition#getTimeInfos — pending T09")

    def get_last_onset_time(self) -> int:
        """Java: OnsetCondition#getLastOnsetTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: OnsetCondition#getLastOnsetTime — pending T09")

    def get_last_end_time(self) -> int:
        """Java: OnsetCondition#getLastEndTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: OnsetCondition#getLastEndTime — pending T09")

    def add_new_entry(self, onset_time: int) -> None:
        """Java: OnsetCondition#addNewEntry.

        Java overloads:
        (long onsetTime)
        """
        raise NotImplementedError("Java: OnsetCondition#addNewEntry — pending T09")

    def end_last_entry(self, time: int) -> None:
        """Java: OnsetCondition#endLastEntry.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: OnsetCondition#endLastEntry — pending T09")


class ModuleConditions:
    """Java: ModuleConditions; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686903

    def __init__(self, source: str) -> None:
        """Java: ModuleConditions#ModuleConditions.

        Java overloads:
        (String source)
        """
        self.source: str
        self.onset_conditions: dict[str, OnsetCondition]
        self.state2condition_mapping: dict[str, str]
        raise NotImplementedError("Java: ModuleConditions#ModuleConditions — pending T09")

    def clone(self) -> ModuleConditions:
        """Java: ModuleConditions#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ModuleConditions#clone — pending T09")

    def onset_condition(self, condition: str, state: str, time: int) -> None:
        """Java: ModuleConditions#onsetCondition.

        Java overloads:
        (String condition, String state, long time)
        """
        raise NotImplementedError("Java: ModuleConditions#onsetCondition — pending T09")

    def end_condition(self, condition: str, time: int) -> None:
        """Java: ModuleConditions#endCondition.

        Java overloads:
        (String condition, long time)
        """
        raise NotImplementedError("Java: ModuleConditions#endCondition — pending T09")

    def get_condition_last_onset_time(self, condition: str) -> int:
        """Java: ModuleConditions#getConditionLastOnsetTime.

        Java overloads:
        (String condition)
        """
        raise NotImplementedError("Java: ModuleConditions#getConditionLastOnsetTime — pending T09")

    def get_condition_last_end_time(self, condition: str) -> int:
        """Java: ModuleConditions#getConditionLastEndTime.

        Java overloads:
        (String condition)
        """
        raise NotImplementedError("Java: ModuleConditions#getConditionLastEndTime — pending T09")

    def get_condition_from_state(self, state: str) -> str:
        """Java: ModuleConditions#getConditionFromState.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: ModuleConditions#getConditionFromState — pending T09")

    def get_onset_conditions(self) -> dict[str, OnsetCondition]:
        """Java: ModuleConditions#getOnsetConditions.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ModuleConditions#getOnsetConditions — pending T09")


class ConditionWithSymptoms:
    """Java: ConditionWithSymptoms; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686904

    def __init__(self, name: str, onset_time: int, end_time: int) -> None:
        """Java: ConditionWithSymptoms#ConditionWithSymptoms.

        Java overloads:
        (String name, Long onsetTime, Long endTime)
        """
        self.condition_name: str
        self.onset_time: int
        self.end_time: int
        self.symptoms: dict[str, list[int]]
        raise NotImplementedError("Java: ConditionWithSymptoms#ConditionWithSymptoms — pending T09")

    def clone(self) -> ConditionWithSymptoms:
        """Java: ConditionWithSymptoms#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionWithSymptoms#clone — pending T09")

    def add_symptoms(self, name: str, symptom_source: SymptomSource) -> None:
        """Java: ConditionWithSymptoms#addSymptoms.

        Java overloads:
        (String name, SymptomSource symptomSource)
        """
        raise NotImplementedError("Java: ConditionWithSymptoms#addSymptoms — pending T09")

    def get_onset_time(self) -> int:
        """Java: ConditionWithSymptoms#getOnsetTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionWithSymptoms#getOnsetTime — pending T09")

    def get_end_time(self) -> int:
        """Java: ConditionWithSymptoms#getEndTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionWithSymptoms#getEndTime — pending T09")

    def get_condition_name(self) -> str:
        """Java: ConditionWithSymptoms#getConditionName.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionWithSymptoms#getConditionName — pending T09")

    def get_symptoms(self) -> dict[str, list[int]]:
        """Java: ConditionWithSymptoms#getSymptoms.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ConditionWithSymptoms#getSymptoms — pending T09")


setattr(ExpressedConditionRecord, "ConditionPeriod", ConditionPeriod)  # noqa: B010
setattr(ExpressedConditionRecord, "OnsetCondition", OnsetCondition)  # noqa: B010
setattr(ExpressedConditionRecord, "ModuleConditions", ModuleConditions)  # noqa: B010
setattr(ExpressedConditionRecord, "ConditionWithSymptoms", ConditionWithSymptoms)  # noqa: B010
