"""Java API skeleton: CMSStateCodeMapper.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator


class CMSStateCodeMapper:
    """Java: CMSStateCodeMapper; pending T10."""

    def __init__(self) -> None:
        """Java: CMSStateCodeMapper#CMSStateCodeMapper.

        Java overloads:
        ()
        """
        self.provider_state_codes: dict[str, str]
        self.state_to_abbrev: dict[str, str]
        self.abbrev_to_state: dict[str, str]
        self.ssa_table: dict[str, str]
        self.ssa_state_county_name_county_code: dict[str, dict[str, str]]
        self.fips_table: dict[str, str]
        raise NotImplementedError("Java: CMSStateCodeMapper#CMSStateCodeMapper — pending T10")

    def get_state_code(self, state: str) -> str:
        """Java: CMSStateCodeMapper#getStateCode.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#getStateCode — pending T10")

    def change_state_format(self, state: str) -> str:
        """Java: CMSStateCodeMapper#changeStateFormat.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#changeStateFormat — pending T10")

    def build_state_abbrev_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildStateAbbrevTable.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#buildStateAbbrevTable — pending T10")

    def build_provider_state_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildProviderStateTable.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#buildProviderStateTable — pending T10")

    def zip_to_county_code(self, zipcode: str) -> str:
        """Java: CMSStateCodeMapper#zipToCountyCode.

        Java overloads:
        (String zipcode)
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#zipToCountyCode — pending T10")

    def state_county_name_to_county_code(
        self, state: str, county_name: str, rand: RandomNumberGenerator
    ) -> str:
        """Java: CMSStateCodeMapper#stateCountyNameToCountyCode.

        Java overloads:
        (String state, String countyName, RandomNumberGenerator rand)
        """
        raise NotImplementedError(
            "Java: CMSStateCodeMapper#stateCountyNameToCountyCode — pending T10"
        )

    def build_ssa_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildSSATable.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#buildSSATable — pending T10")

    def build_county_name_lookup(self) -> dict[str, dict[str, str]]:
        """Java: CMSStateCodeMapper#buildCountyNameLookup.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#buildCountyNameLookup — pending T10")

    def zip_to_fips_county_code(self, zipcode: str) -> str:
        """Java: CMSStateCodeMapper#zipToFipsCountyCode.

        Java overloads:
        (String zipcode)
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#zipToFipsCountyCode — pending T10")

    def build_fips_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildFipsTable.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#buildFipsTable — pending T10")

    def capitalize_words(self, str: str) -> str:
        """Java: CMSStateCodeMapper#capitalizeWords.

        Java overloads:
        (String str)
        """
        raise NotImplementedError("Java: CMSStateCodeMapper#capitalizeWords — pending T10")
