"""Java: org.mitre.synthea.world.concepts.Names."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.helpers.simple_yml import SimpleYML
    from synthea.world.agents.person import Person


class Names:
    """Java: org.mitre.synthea.world.concepts.Names; pending T11."""

    names: ClassVar[SimpleYML]
    append_numbers_to_names: ClassVar[bool]

    def __init__(self) -> None:
        """Java: Names#Names() implicit constructor."""
        raise NotImplementedError("Java: Names#Names — pending T11")

    @staticmethod
    def load_names() -> SimpleYML:
        """Java: Names#loadNames()."""
        raise NotImplementedError("Java: Names#loadNames — pending T11")

    @staticmethod
    def fake_first_name(gender: str, language: str, person: Person) -> str:
        """Java: Names#fakeFirstName(String, String, Person)."""
        raise NotImplementedError("Java: Names#fakeFirstName — pending T11")

    @staticmethod
    def fake_last_name(language: str, person: Person) -> str:
        """Java: Names#fakeLastName(String, Person)."""
        raise NotImplementedError("Java: Names#fakeLastName — pending T11")

    @staticmethod
    def fake_address(include_line2: bool, person: Person) -> str:
        """Java: Names#fakeAddress(boolean, Person)."""
        raise NotImplementedError("Java: Names#fakeAddress — pending T11")

    @staticmethod
    def add_hash(name: str) -> str:
        """Java: Names#addHash(String)."""
        raise NotImplementedError("Java: Names#addHash — pending T11")
