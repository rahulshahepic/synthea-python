"""Java: org.mitre.synthea.engine.ExpressedConditionRecord."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from synthea.javacompat.collections import JavaConcurrentHashMap

if TYPE_CHECKING:
    from synthea.engine.expressed_symptom import SymptomSource
    from synthea.world.agents.person import Person


class ExpressedConditionRecord:
    """Java: org.mitre.synthea.engine.ExpressedConditionRecord."""

    serialVersionUID: ClassVar[int] = 4322116644425686900

    def __init__(self, person: Person) -> None:
        """Java: ExpressedConditionRecord#ExpressedConditionRecord(Person)."""
        self.sources: JavaConcurrentHashMap[str, ModuleConditions] = JavaConcurrentHashMap()
        self.person: Person = person

    def clone(self) -> ExpressedConditionRecord:
        """Java: ExpressedConditionRecord#clone."""
        data = ExpressedConditionRecord(self.person)
        data.sources.update(self.sources)
        return data

    def get_sources(self) -> JavaConcurrentHashMap[str, ModuleConditions]:
        """Java: ExpressedConditionRecord#getSources."""
        return self.sources

    def on_condition_onset(self, module: str, state: str, condition: str, time: int) -> None:
        """Java: ExpressedConditionRecord#onConditionOnset(String, String, String, long)."""
        if module not in self.sources:
            self.sources[module] = ModuleConditions(module)
        self.sources[module].onset_condition(condition, state, time)

    def get_condition_last_onset_time_from_module(self, module: str, condition: str) -> int | None:
        """Java: ExpressedConditionRecord#getConditionLastOnsetTimeFromModule(String, String)."""
        result: int | None = None
        if module in self.sources:
            result = self.sources[module].get_condition_last_onset_time(condition)
        return result

    def get_condition_last_end_time_from_module(self, module: str, condition: str) -> int | None:
        """Java: ExpressedConditionRecord#getConditionLastEndTimeFromModule(String, String)."""
        result: int | None = None
        if module in self.sources:
            result = self.sources[module].get_condition_last_end_time(condition)
        return result

    def get_condition_from_state(self, module: str, state: str) -> str | None:
        """Java: ExpressedConditionRecord#getConditionFromState(String, String)."""
        result: str | None = None
        if module in self.sources:
            result = self.sources[module].get_condition_from_state(state)
        return result

    def on_condition_end(self, module: str, condition: str, time: int) -> None:
        """Java: ExpressedConditionRecord#onConditionEnd(String, String, long)."""
        if module in self.sources:
            self.sources[module].end_condition(condition, time)

    def get_condition_symptoms(
        self,
    ) -> JavaConcurrentHashMap[int, list[ConditionWithSymptoms]]:
        """Java: ExpressedConditionRecord#getConditionSymptoms."""
        symptoms = self.person.get_expressed_symptoms()
        result: JavaConcurrentHashMap[int, list[ConditionWithSymptoms]] = JavaConcurrentHashMap(
            key_type="long"
        )
        for module in self.sources:
            module_conditions = self.sources[module]
            for condition in module_conditions.get_onset_conditions():
                infos = module_conditions.get_onset_conditions()[condition].get_time_infos()
                for entry in infos:
                    begin = entry.get_onset_time()
                    end = entry.get_end_time()
                    if begin is None:
                        # Java: ConcurrentHashMap.containsKey(null) below.
                        raise TypeError("Java NullPointerException: null onset time as map key")
                    if begin not in result:
                        result[begin] = []
                    condition_with_symptoms = ConditionWithSymptoms(condition, begin, end)
                    for type_name in symptoms:
                        expressed_symptom = symptoms[type_name]
                        if module in expressed_symptom.get_sources():
                            symptom_source = expressed_symptom.get_sources()[module]
                            condition_with_symptoms.add_symptoms(type_name, symptom_source)
                    result[begin].append(condition_with_symptoms)
        return result


class ConditionPeriod:
    """Java: org.mitre.synthea.engine.ExpressedConditionRecord.ConditionPeriod."""

    serialVersionUID: ClassVar[int] = 4322116644425686901

    def __init__(self, onset_time: int | None, end_time: int | None = None) -> None:
        """Java: ConditionPeriod#ConditionPeriod(Long) and #ConditionPeriod(Long, Long)."""
        self.end_time: int | None = end_time
        self.onset_time: int | None = onset_time

    def clone(self) -> ConditionPeriod:
        """Java: ConditionPeriod#clone."""
        return ConditionPeriod(self.onset_time, self.end_time)

    def get_end_time(self) -> int | None:
        """Java: ConditionPeriod#getEndTime."""
        return self.end_time

    def set_end_time(self, end_time: int | None) -> None:
        """Java: ConditionPeriod#setEndTime(Long)."""
        self.end_time = end_time

    def get_onset_time(self) -> int | None:
        """Java: ConditionPeriod#getOnsetTime."""
        return self.onset_time


class OnsetCondition:
    """Java: org.mitre.synthea.engine.ExpressedConditionRecord.OnsetCondition."""

    serialVersionUID: ClassVar[int] = 4322116644425686902

    def __init__(self, name: str) -> None:
        """Java: OnsetCondition#OnsetCondition(String)."""
        self.name: str = name
        self.time_infos: list[ConditionPeriod] = []

    def clone(self) -> OnsetCondition:
        """Java: OnsetCondition#clone."""
        data = OnsetCondition(self.name)
        data.time_infos.extend(self.time_infos)
        return data

    def get_name(self) -> str:
        """Java: OnsetCondition#getName."""
        return self.name

    def get_time_infos(self) -> list[ConditionPeriod]:
        """Java: OnsetCondition#getTimeInfos."""
        return self.time_infos

    def get_last_onset_time(self) -> int | None:
        """Java: OnsetCondition#getLastOnsetTime."""
        if not self.time_infos:
            return None
        return self.time_infos[-1].get_onset_time()

    def get_last_end_time(self) -> int | None:
        """Java: OnsetCondition#getLastEndTime."""
        if not self.time_infos:
            return None
        return self.time_infos[-1].get_end_time()

    def add_new_entry(self, onset_time: int) -> None:
        """Java: OnsetCondition#addNewEntry(long)."""
        self.time_infos.append(ConditionPeriod(onset_time, None))

    def end_last_entry(self, time: int) -> None:
        """Java: OnsetCondition#endLastEntry(long)."""
        if len(self.time_infos) > 0:
            self.time_infos[-1].set_end_time(time)


class ModuleConditions:
    """Java: org.mitre.synthea.engine.ExpressedConditionRecord.ModuleConditions."""

    serialVersionUID: ClassVar[int] = 4322116644425686903

    def __init__(self, source: str) -> None:
        """Java: ModuleConditions#ModuleConditions(String)."""
        self.source: str = source
        self.onset_conditions: JavaConcurrentHashMap[str, OnsetCondition] = JavaConcurrentHashMap()
        self.state2condition_mapping: JavaConcurrentHashMap[str, str] = JavaConcurrentHashMap()

    def clone(self) -> ModuleConditions:
        """Java: ModuleConditions#clone."""
        data = ModuleConditions(self.source)
        data.state2condition_mapping.update(self.state2condition_mapping)
        data.onset_conditions.update(self.onset_conditions)
        return data

    def onset_condition(self, condition: str, state: str, time: int) -> None:
        """Java: ModuleConditions#onsetCondition(String, String, long)."""
        if condition not in self.onset_conditions:
            self.onset_conditions[condition] = OnsetCondition(condition)
        self.onset_conditions[condition].add_new_entry(time)
        self.state2condition_mapping[state] = condition

    def end_condition(self, condition: str, time: int) -> None:
        """Java: ModuleConditions#endCondition(String, long)."""
        if condition in self.onset_conditions:
            self.onset_conditions[condition].end_last_entry(time)

    def get_condition_last_onset_time(self, condition: str) -> int | None:
        """Java: ModuleConditions#getConditionLastOnsetTime(String)."""
        if condition in self.onset_conditions:
            return self.onset_conditions[condition].get_last_onset_time()
        return None

    def get_condition_last_end_time(self, condition: str) -> int | None:
        """Java: ModuleConditions#getConditionLastEndTime(String)."""
        if condition in self.onset_conditions:
            return self.onset_conditions[condition].get_last_end_time()
        return None

    def get_condition_from_state(self, state: str) -> str | None:
        """Java: ModuleConditions#getConditionFromState(String)."""
        if state in self.state2condition_mapping:
            return self.state2condition_mapping[state]
        return None

    def get_onset_conditions(self) -> JavaConcurrentHashMap[str, OnsetCondition]:
        """Java: ModuleConditions#getOnsetConditions."""
        return self.onset_conditions


class ConditionWithSymptoms:
    """Java: org.mitre.synthea.engine.ExpressedConditionRecord.ConditionWithSymptoms."""

    serialVersionUID: ClassVar[int] = 4322116644425686904

    def __init__(self, name: str, onset_time: int | None, end_time: int | None) -> None:
        """Java: ConditionWithSymptoms#ConditionWithSymptoms(String, Long, Long)."""
        self.condition_name: str = name
        self.onset_time: int | None = onset_time
        self.end_time: int | None = end_time
        self.symptoms: JavaConcurrentHashMap[str, list[int | None]] = JavaConcurrentHashMap()

    def clone(self) -> ConditionWithSymptoms:
        """Java: ConditionWithSymptoms#clone."""
        data = ConditionWithSymptoms(self.condition_name, self.onset_time, self.end_time)
        data.symptoms.update(self.symptoms)
        return data

    def add_symptoms(self, name: str, symptom_source: SymptomSource) -> None:
        """Java: ConditionWithSymptoms#addSymptoms(String, SymptomSource)."""
        timed_typed_symptoms = symptom_source.get_time_infos()
        all_times: list[int] = []
        for time in timed_typed_symptoms:
            if self.onset_time is None:
                # Java unboxes onsetTime for the comparison: NullPointerException.
                raise TypeError("Java NullPointerException: unboxing a null Long")
            greater_than_begin = time >= self.onset_time
            lower_than_end = (self.end_time is not None and time <= self.end_time) or (
                self.end_time is None
            )
            if greater_than_begin and lower_than_end:
                all_times.append(time)
        if len(all_times) > 0:
            all_times.sort()
            if name not in self.symptoms:
                self.symptoms[name] = []
            for time in all_times:
                value = timed_typed_symptoms[time].get_value()
                self.symptoms[name].append(value)

    def get_onset_time(self) -> int | None:
        """Java: ConditionWithSymptoms#getOnsetTime."""
        return self.onset_time

    def get_end_time(self) -> int | None:
        """Java: ConditionWithSymptoms#getEndTime."""
        return self.end_time

    def get_condition_name(self) -> str:
        """Java: ConditionWithSymptoms#getConditionName."""
        return self.condition_name

    def get_symptoms(self) -> JavaConcurrentHashMap[str, list[int | None]]:
        """Java: ConditionWithSymptoms#getSymptoms."""
        return self.symptoms


setattr(ExpressedConditionRecord, "ConditionPeriod", ConditionPeriod)  # noqa: B010
setattr(ExpressedConditionRecord, "OnsetCondition", OnsetCondition)  # noqa: B010
setattr(ExpressedConditionRecord, "ModuleConditions", ModuleConditions)  # noqa: B010
setattr(ExpressedConditionRecord, "ConditionWithSymptoms", ConditionWithSymptoms)  # noqa: B010
