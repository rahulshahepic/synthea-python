"""Java API skeleton: RaceAndEthnicity.java."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar


class RaceAndEthnicity:
    """Java: RaceAndEthnicity; pending T11."""

    LOOK_UP_CDC_RACE: ClassVar[Mapping[str, str]] = MappingProxyType(
        {
            "white": "2106-3",
            "hispanic": "2106-3",
            "black": "2054-5",
            "asian": "2028-9",
            "native": "1002-5",
            "hawaiian": "2076-8",
            "other": "2131-1",
        }
    )
    LOOK_UP_CDC_ETHNICITY_CODE: ClassVar[Mapping[str, str]] = MappingProxyType(
        {
            "white": "2186-5",
            "hispanic": "2135-2",
            "black": "2186-5",
            "asian": "2186-5",
            "native": "2186-5",
            "hawaiian": "2186-5",
            "other": "2186-5",
        }
    )
    LOOK_UP_CDC_ETHNICITY_DISPLAY: ClassVar[Mapping[str, str]] = MappingProxyType(
        {
            "white": "non-hispanic",
            "hispanic": "hispanic",
            "black": "non-hispanic",
            "asian": "non-hispanic",
            "native": "non-hispanic",
            "hawaiian": "non-hispanic",
            "other": "non-hispanic",
        }
    )

    def __init__(self) -> None:
        """Java: RaceAndEthnicity#RaceAndEthnicity.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: RaceAndEthnicity#RaceAndEthnicity — pending T11")

    @staticmethod
    def create_cdc_race_lookup() -> Mapping[str, str]:
        """Java: RaceAndEthnicity#createCDCRaceLookup.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: RaceAndEthnicity#createCDCRaceLookup — pending T11")

    @staticmethod
    def create_cdc_ethnicity_lookup() -> Mapping[str, str]:
        """Java: RaceAndEthnicity#createCDCEthnicityLookup.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: RaceAndEthnicity#createCDCEthnicityLookup — pending T11")

    @staticmethod
    def create_cdc_ethnicity_display_lookup() -> Mapping[str, str]:
        """Java: RaceAndEthnicity#createCDCEthnicityDisplayLookup.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: RaceAndEthnicity#createCDCEthnicityDisplayLookup — pending T11"
        )
