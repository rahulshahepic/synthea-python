"""Java API skeleton: Config.java."""

from __future__ import annotations

import builtins
from pathlib import Path
from typing import IO, ClassVar


class Config:
    """Java: Config; pending T05."""

    properties: ClassVar[dict[str, str]]  # Java initialization deferred to T05.

    def __init__(self) -> None:
        """Java: Config#Config.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Config#Config — pending T05")

    @staticmethod
    def load(props_file_or_stream: Path | IO[bytes]) -> None:
        """Java: Config#load.

        Java overloads:
        (File propsFile)
        (InputStream stream)
        """
        raise NotImplementedError("Java: Config#load — pending T05")

    @staticmethod
    def get(key: str, default_value: str | None = None) -> str:
        """Java: Config#get.

        Java overloads:
        (String key)
        (String key, String defaultValue)
        """
        raise NotImplementedError("Java: Config#get — pending T05")

    @staticmethod
    def get_as_double(key: str, default_value: float | None = None) -> float:
        """Java: Config#getAsDouble.

        Java overloads:
        (String key)
        (String key, double defaultValue)
        """
        raise NotImplementedError("Java: Config#getAsDouble — pending T05")

    @staticmethod
    def get_as_boolean(key: str, default_value: bool | None = None) -> bool:
        """Java: Config#getAsBoolean.

        Java overloads:
        (String key)
        (String key, boolean defaultValue)
        """
        raise NotImplementedError("Java: Config#getAsBoolean — pending T05")

    @staticmethod
    def get_as_integer(key: str, default_value: int | None = None) -> int:
        """Java: Config#getAsInteger.

        Java overloads:
        (String key)
        (String key, int defaultValue)
        """
        raise NotImplementedError("Java: Config#getAsInteger — pending T05")

    @staticmethod
    def get_as_long(key: str, default_value: int | None = None) -> int:
        """Java: Config#getAsLong.

        Java overloads:
        (String key)
        (String key, long defaultValue)
        """
        raise NotImplementedError("Java: Config#getAsLong — pending T05")

    @staticmethod
    def set(key: str, value: str) -> None:
        """Java: Config#set.

        Java overloads:
        (String key, String value)
        """
        raise NotImplementedError("Java: Config#set — pending T05")

    @staticmethod
    def all_property_names() -> builtins.set[str]:
        """Java: Config#allPropertyNames.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Config#allPropertyNames — pending T05")

    @staticmethod
    def remove(key: str) -> None:
        """Java: Config#remove.

        Java overloads:
        (String key)
        """
        raise NotImplementedError("Java: Config#remove — pending T05")
