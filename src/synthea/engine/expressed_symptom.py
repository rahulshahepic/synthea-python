"""Java: org.mitre.synthea.engine.ExpressedSymptom."""

from __future__ import annotations

from typing import ClassVar

from synthea.javacompat.collections import JavaConcurrentHashMap


class ExpressedSymptom:
    """Java: org.mitre.synthea.engine.ExpressedSymptom."""

    serialVersionUID: ClassVar[int] = 4322116644425686800

    def __init__(self, name: str) -> None:
        """Java: ExpressedSymptom#ExpressedSymptom(String)."""
        self.sources: JavaConcurrentHashMap[str, SymptomSource] = JavaConcurrentHashMap()
        self.name: str = name

    def clone(self) -> ExpressedSymptom:
        """Java: ExpressedSymptom#clone."""
        data = ExpressedSymptom(self.name)
        data.sources.update(self.sources)
        return data

    def get_sources(self) -> JavaConcurrentHashMap[str, SymptomSource]:
        """Java: ExpressedSymptom#getSources."""
        return self.sources

    def on_set(
        self, module: str, cause: str, time: int, value: int, addressed: bool | None
    ) -> None:
        """Java: ExpressedSymptom#onSet(String, String, long, int, Boolean)."""
        if module not in self.sources:
            source = SymptomSource(module)
            source.symptom = self
            self.sources[module] = source
        self.sources[module].add_info(cause, time, value, addressed)

    def get_symptom(self) -> int:
        """Java: ExpressedSymptom#getSymptom."""
        max_value = 0
        for module in self.sources:
            value = self.sources[module].get_current_value()
            is_resolved = self.sources[module].is_resolved()
            if value is not None and value > max_value and not is_resolved:
                max_value = value
        return max_value

    def get_source_with_high_value(self) -> str | None:
        """Java: ExpressedSymptom#getSourceWithHighValue."""
        result: str | None = None
        max_value = 0
        for module in self.sources:
            is_resolved = self.sources[module].is_resolved()
            value = self.sources[module].get_current_value()
            # Java has two branches here (first-unresolved-source, then
            # strictly-greater); they assign the same values, combined.
            if value is not None and not is_resolved and (result is None or value > max_value):
                result = module
                max_value = value
        return result

    def get_value_from_source(self, source: str | None) -> int | None:
        """Java: ExpressedSymptom#getValueFromSource(String)."""
        if source is None or source not in self.sources:
            return None
        return self.sources[source].get_current_value()

    def address_source(self, source: str | None) -> None:
        """Java: ExpressedSymptom#addressSource(String)."""
        if source is not None and source in self.sources:
            self.sources[source].resolve()

    def get_symptom_last_updated_time(self, module: str | None) -> int | None:
        """Java: ExpressedSymptom#getSymptomLastUpdatedTime(String)."""
        result: int | None = None
        if module is not None and module in self.sources:
            result = self.sources[module].get_last_update_time()
        return result


class SymptomInfo:
    """Java: org.mitre.synthea.engine.ExpressedSymptom.SymptomInfo."""

    serialVersionUID: ClassVar[int] = 4322116644425686801

    def __init__(self, cause: str, value: int | None, time: int | None) -> None:
        """Java: SymptomInfo#SymptomInfo(String, Integer, Long)."""
        self.cause: str = cause
        self.value: int | None = value
        self.time: int | None = time

    def clone(self) -> SymptomInfo:
        """Java: SymptomInfo#clone."""
        return SymptomInfo(self.cause, self.value, self.time)

    def get_cause(self) -> str:
        """Java: SymptomInfo#getCause."""
        return self.cause

    def get_value(self) -> int | None:
        """Java: SymptomInfo#getValue."""
        return self.value

    def get_time(self) -> int | None:
        """Java: SymptomInfo#getTime."""
        return self.time


class SymptomSource:
    """Java: org.mitre.synthea.engine.ExpressedSymptom.SymptomSource."""

    serialVersionUID: ClassVar[int] = 4322116644425686802

    def __init__(self, source: str) -> None:
        """Java: SymptomSource#SymptomSource(String)."""
        self.symptom: ExpressedSymptom | None = None
        self.source: str = source
        self.resolved: bool = False
        self.last_update_time: int | None = None
        self.time_infos: JavaConcurrentHashMap[int, SymptomInfo] = JavaConcurrentHashMap(
            key_type="long"
        )

    def clone(self) -> SymptomSource:
        """Java: SymptomSource#clone."""
        data = SymptomSource(self.source)
        data.symptom = self.symptom
        data.resolved = self.resolved
        data.last_update_time = self.last_update_time
        data.time_infos.update(self.time_infos)
        return data

    def is_resolved(self) -> bool:
        """Java: SymptomSource#isResolved."""
        return self.resolved

    def resolve(self) -> None:
        """Java: SymptomSource#resolve."""
        self.resolved = True

    def activate(self) -> None:
        """Java: SymptomSource#activate."""
        self.resolved = False

    def get_last_update_time(self) -> int | None:
        """Java: SymptomSource#getLastUpdateTime."""
        return self.last_update_time

    def get_source(self) -> str:
        """Java: SymptomSource#getSource."""
        return self.source

    def add_info(self, cause: str, time: int, value: int, addressed: bool | None) -> None:
        """Java: SymptomSource#addInfo(String, long, int, Boolean)."""
        if addressed is None:
            # Java unboxes the Boolean into the boolean field: NullPointerException.
            raise TypeError("Java NullPointerException: unboxing a null Boolean")
        info = SymptomInfo(cause, value, time)
        self.time_infos[time] = info
        self.last_update_time = time
        self.resolved = addressed

    def get_current_value(self) -> int | None:
        """Java: SymptomSource#getCurrentValue."""
        if self.last_update_time is not None and self.last_update_time in self.time_infos:
            return self.time_infos[self.last_update_time].get_value()
        return None

    def get_time_infos(self) -> JavaConcurrentHashMap[int, SymptomInfo]:
        """Java: SymptomSource#getTimeInfos."""
        return self.time_infos


setattr(ExpressedSymptom, "SymptomInfo", SymptomInfo)  # noqa: B010
setattr(ExpressedSymptom, "SymptomSource", SymptomSource)  # noqa: B010
