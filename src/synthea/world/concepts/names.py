"""Java: org.mitre.synthea.world.concepts.Names."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from synthea.helpers.config import Config
from synthea.helpers.simple_yml import SimpleYML
from synthea.helpers.utilities import Utilities
from synthea.javacompat.hashing import string_hash_code
from synthea.javacompat.numbers import irem

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Names:
    """Java: org.mitre.synthea.world.concepts.Names."""

    names: ClassVar[SimpleYML]
    append_numbers_to_names: ClassVar[bool] = Config.get_as_boolean(
        "generate.append_numbers_to_person_names", False
    )

    def __init__(self) -> None:
        """Java: Names#Names() implicit constructor."""

    @staticmethod
    def load_names() -> SimpleYML:
        """Java: Names#loadNames()."""
        return SimpleYML(Utilities.read_resource("names.yml"))

    @staticmethod
    def fake_first_name(gender: str, language: str, person: Person) -> str:
        """Java: Names#fakeFirstName(String, String, Person)."""
        language = "spanish" if language.lower() == "spanish" else "english"
        choices = cast(list[str], Names.names.get(f"{language}.{gender}"))
        name = choices[person.rand_int(len(choices))]
        return Names.add_hash(name) if Names.append_numbers_to_names else name

    @staticmethod
    def fake_last_name(language: str, person: Person) -> str:
        """Java: Names#fakeLastName(String, Person)."""
        language = "spanish" if language.lower() == "spanish" else "english"
        choices = cast(list[str], Names.names.get(f"{language}.family"))
        name = choices[person.rand_int(len(choices))]
        return Names.add_hash(name) if Names.append_numbers_to_names else name

    @staticmethod
    def fake_address(include_line2: bool, person: Person) -> str:
        """Java: Names#fakeAddress(boolean, Person)."""
        number = person.rand_int(1000) + 100
        names = cast(list[str], Names.names.get("english.family"))
        street_name = names[person.rand_int(len(names))]
        types = cast(list[str], Names.names.get("street.type"))
        street_type = types[person.rand_int(len(types))]
        address = f"{number} {street_name} {street_type}"
        if include_line2:
            extra_number = person.rand_int(100)
            secondary = cast(list[str], Names.names.get("street.secondary"))
            extra_type = secondary[person.rand_int(len(secondary))]
            address += f" {extra_type} {extra_number}"
        return address

    @staticmethod
    def add_hash(name: str) -> str:
        """Java: Names#addHash(String)."""
        return name + str(abs(irem(string_hash_code(name), 1000)))


Names.names = Names.load_names()
