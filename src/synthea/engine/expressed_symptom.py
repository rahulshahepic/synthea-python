"""Java port skeleton: java/src/main/java/org/mitre/synthea/engine/ExpressedSymptom.java."""

from __future__ import annotations


class ExpressedSymptom:
    """Java: ExpressedSymptom; pending T09."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ExpressedSymptom constructor; pending T09."""
        self.sources: dict[object, object] = {}
        self.name: str | None = None
        raise NotImplementedError("Java: ExpressedSymptom#constructor — pending T09")

    def clone(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#clone; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#clone — pending T09")

    def get_cause(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getCause; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getCause — pending T09")

    def get_value(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getValue; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getValue — pending T09")

    def get_time(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getTime; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getTime — pending T09")

    def is_resolved(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#isResolved; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#isResolved — pending T09")

    def resolve(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#resolve; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#resolve — pending T09")

    def activate(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#activate; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#activate — pending T09")

    def get_last_update_time(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getLastUpdateTime; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getLastUpdateTime — pending T09")

    def get_source(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getSource; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getSource — pending T09")

    def add_info(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#addInfo; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#addInfo — pending T09")

    def get_current_value(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getCurrentValue; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getCurrentValue — pending T09")

    def get_time_infos(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getTimeInfos; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getTimeInfos — pending T09")

    def get_sources(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getSources; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getSources — pending T09")

    def on_set(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#onSet; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#onSet — pending T09")

    def get_symptom(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getSymptom; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getSymptom — pending T09")

    def get_source_with_high_value(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getSourceWithHighValue; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getSourceWithHighValue — pending T09")

    def get_value_from_source(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getValueFromSource; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getValueFromSource — pending T09")

    def address_source(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#addressSource; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#addressSource — pending T09")

    def get_symptom_last_updated_time(self, *args: object, **kwargs: object) -> object:
        """Java: ExpressedSymptom#getSymptomLastUpdatedTime; pending T09."""
        raise NotImplementedError("Java: ExpressedSymptom#getSymptomLastUpdatedTime — pending T09")


class SymptomInfo:
    """Java: SymptomInfo; pending T09."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: SymptomInfo constructor; pending T09."""
        self.cause: str | None = None
        self.value: object | None = None
        self.time: object | None = None
        raise NotImplementedError("Java: SymptomInfo#constructor — pending T09")


class SymptomSource:
    """Java: SymptomSource; pending T09."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: SymptomSource constructor; pending T09."""
        self.source: str | None = None
        self.resolved: bool = False
        self.lastUpdateTime: object | None = None
        self.timeInfos: dict[object, object] = {}
        raise NotImplementedError("Java: SymptomSource#constructor — pending T09")
