"""Java API skeleton: org/mitre/synthea/helpers/Config.java."""

from __future__ import annotations


class Config:
    """Java: Config.java#Config."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Config#Config; pending T05."""
        raise NotImplementedError("Java: Config#Config — pending T05")

    @staticmethod
    def load(source: object) -> None
        """Java: Config#load; pending T05."""
        raise NotImplementedError("Java: Config#load — pending T05")

    @staticmethod
    def get(key: str, default_value: str | None = None) -> str | None
        """Java: Config#get; pending T05."""
        raise NotImplementedError("Java: Config#get — pending T05")

    @staticmethod
    def get_as_double(key: str, default_value: float | None = None) -> float
        """Java: Config#getAsDouble; pending T05."""
        raise NotImplementedError("Java: Config#getAsDouble — pending T05")

    @staticmethod
    def get_as_boolean(key: str, default_value: bool | None = None) -> bool
        """Java: Config#getAsBoolean; pending T05."""
        raise NotImplementedError("Java: Config#getAsBoolean — pending T05")

    @staticmethod
    def get_as_integer(key: str, default_value: int | None = None) -> int
        """Java: Config#getAsInteger; pending T05."""
        raise NotImplementedError("Java: Config#getAsInteger — pending T05")

    @staticmethod
    def get_as_long(key: str, default_value: int | None = None) -> int
        """Java: Config#getAsLong; pending T05."""
        raise NotImplementedError("Java: Config#getAsLong — pending T05")

    @staticmethod
    def set(key: str, value: str) -> None
        """Java: Config#set; pending T05."""
        raise NotImplementedError("Java: Config#set — pending T05")

    @staticmethod
    def all_property_names() -> set[str]
        """Java: Config#allPropertyNames; pending T05."""
        raise NotImplementedError("Java: Config#allPropertyNames — pending T05")

    @staticmethod
    def remove(key: str) -> None
        """Java: Config#remove; pending T05."""
        raise NotImplementedError("Java: Config#remove — pending T05")
