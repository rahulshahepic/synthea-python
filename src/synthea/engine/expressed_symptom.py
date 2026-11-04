"""Java API skeleton: ExpressedSymptom.java."""

from __future__ import annotations

from typing import ClassVar


class ExpressedSymptom:
    """Java: ExpressedSymptom; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686800

    def __init__(self, name: str) -> None:
        """Java: ExpressedSymptom#ExpressedSymptom.

        Java overloads:
        (String name)
        """
        self.sources: dict[str, SymptomSource]
        self.name: str
        raise NotImplementedError("Java: ExpressedSymptom#ExpressedSymptom — pending T09")

    def clone(self) -> ExpressedSymptom:
        """Java: ExpressedSymptom#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressedSymptom#clone — pending T09")

    def get_sources(self) -> dict[str, SymptomSource]:
        """Java: ExpressedSymptom#getSources.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressedSymptom#getSources — pending T09")

    def on_set(self, module: str, cause: str, time: int, value: int, addressed: bool) -> None:
        """Java: ExpressedSymptom#onSet.

        Java overloads:
        (String module, String cause, long time, int value, Boolean addressed)
        """
        raise NotImplementedError("Java: ExpressedSymptom#onSet — pending T09")

    def get_symptom(self) -> int:
        """Java: ExpressedSymptom#getSymptom.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressedSymptom#getSymptom — pending T09")

    def get_source_with_high_value(self) -> str:
        """Java: ExpressedSymptom#getSourceWithHighValue.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressedSymptom#getSourceWithHighValue — pending T09")

    def get_value_from_source(self, source: str) -> int:
        """Java: ExpressedSymptom#getValueFromSource.

        Java overloads:
        (String source)
        """
        raise NotImplementedError("Java: ExpressedSymptom#getValueFromSource — pending T09")

    def address_source(self, source: str) -> None:
        """Java: ExpressedSymptom#addressSource.

        Java overloads:
        (String source)
        """
        raise NotImplementedError("Java: ExpressedSymptom#addressSource — pending T09")

    def get_symptom_last_updated_time(self, module: str) -> int:
        """Java: ExpressedSymptom#getSymptomLastUpdatedTime.

        Java overloads:
        (String module)
        """
        raise NotImplementedError("Java: ExpressedSymptom#getSymptomLastUpdatedTime — pending T09")


class SymptomInfo:
    """Java: SymptomInfo; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686801

    def __init__(self, cause: str, value: int, time: int) -> None:
        """Java: SymptomInfo#SymptomInfo.

        Java overloads:
        (String cause, Integer value, Long time)
        """
        self.cause: str
        self.value: int
        self.time: int
        raise NotImplementedError("Java: SymptomInfo#SymptomInfo — pending T09")

    def clone(self) -> SymptomInfo:
        """Java: SymptomInfo#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomInfo#clone — pending T09")

    def get_cause(self) -> str:
        """Java: SymptomInfo#getCause.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomInfo#getCause — pending T09")

    def get_value(self) -> int:
        """Java: SymptomInfo#getValue.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomInfo#getValue — pending T09")

    def get_time(self) -> int:
        """Java: SymptomInfo#getTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomInfo#getTime — pending T09")


class SymptomSource:
    """Java: SymptomSource; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686802

    def __init__(self, source: str) -> None:
        """Java: SymptomSource#SymptomSource.

        Java overloads:
        (String source)
        """
        self.symptom: ExpressedSymptom
        self.source: str
        self.resolved: bool
        self.last_update_time: int
        self.time_infos: dict[int, SymptomInfo]
        raise NotImplementedError("Java: SymptomSource#SymptomSource — pending T09")

    def clone(self) -> SymptomSource:
        """Java: SymptomSource#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#clone — pending T09")

    def is_resolved(self) -> bool:
        """Java: SymptomSource#isResolved.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#isResolved — pending T09")

    def resolve(self) -> None:
        """Java: SymptomSource#resolve.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#resolve — pending T09")

    def activate(self) -> None:
        """Java: SymptomSource#activate.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#activate — pending T09")

    def get_last_update_time(self) -> int:
        """Java: SymptomSource#getLastUpdateTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#getLastUpdateTime — pending T09")

    def get_source(self) -> str:
        """Java: SymptomSource#getSource.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#getSource — pending T09")

    def add_info(self, cause: str, time: int, value: int, addressed: bool) -> None:
        """Java: SymptomSource#addInfo.

        Java overloads:
        (String cause, long time, int value, Boolean addressed)
        """
        raise NotImplementedError("Java: SymptomSource#addInfo — pending T09")

    def get_current_value(self) -> int:
        """Java: SymptomSource#getCurrentValue.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#getCurrentValue — pending T09")

    def get_time_infos(self) -> dict[int, SymptomInfo]:
        """Java: SymptomSource#getTimeInfos.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SymptomSource#getTimeInfos — pending T09")


setattr(ExpressedSymptom, "SymptomInfo", SymptomInfo)  # noqa: B010
setattr(ExpressedSymptom, "SymptomSource", SymptomSource)  # noqa: B010
