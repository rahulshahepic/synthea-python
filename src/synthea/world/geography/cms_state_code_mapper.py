"""Java: org.mitre.synthea.world.geography.CMSStateCodeMapper."""

from __future__ import annotations

import re
from functools import lru_cache

from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap


@lru_cache(maxsize=1)
def _fips_rows() -> list[dict[str, str]]:
    """Java: CMSStateCodeMapper resource loading; parse the shared table once lazily."""
    return SimpleCSV.parse(Utilities.read_resource_and_strip_bom("geography/fipscodes.csv"))


class CMSStateCodeMapper:
    """Java: org.mitre.synthea.world.geography.CMSStateCodeMapper."""

    def __init__(self) -> None:
        """Java: CMSStateCodeMapper#CMSStateCodeMapper."""
        self.provider_state_codes = self.build_provider_state_table()
        self.state_to_abbrev = self.build_state_abbrev_table()
        self.abbrev_to_state = {value: key for key, value in self.state_to_abbrev.items()}
        self.ssa_table = self.build_ssa_table()
        self.ssa_state_county_name_county_code = self.build_county_name_lookup()
        self.fips_table = self.build_fips_table()

    def get_state_code(self, state: str) -> str:
        """Java: CMSStateCodeMapper#getStateCode."""
        cleaned = (
            self.change_state_format(state) if len(state) == 2 else self.capitalize_words(state)
        )
        return self.provider_state_codes.get(cleaned or "", "NONE")

    def change_state_format(self, state: str) -> str | None:
        """Java: CMSStateCodeMapper#changeStateFormat."""
        if len(state) == 2:
            return self.abbrev_to_state.get(state.upper())
        return self.state_to_abbrev.get(self.capitalize_words(state.lower()))

    def build_state_abbrev_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildStateAbbrevTable."""
        return {
            "Alabama": "AL",
            "Alaska": "AK",
            "Alberta": "AB",
            "American Samoa": "AS",
            "Arizona": "AZ",
            "Arkansas": "AR",
            "Armed Forces (AE)": "AE",
            "Armed Forces Americas": "AA",
            "Armed Forces Pacific": "AP",
            "British Columbia": "BC",
            "California": "CA",
            "Colorado": "CO",
            "Connecticut": "CT",
            "Delaware": "DE",
            "District of Columbia": "DC",
            "Florida": "FL",
            "Georgia": "GA",
            "Guam": "GU",
            "Hawaii": "HI",
            "Idaho": "ID",
            "Illinois": "IL",
            "Indiana": "IN",
            "Iowa": "IA",
            "Kansas": "KS",
            "Kentucky": "KY",
            "Louisiana": "LA",
            "Maine": "ME",
            "Manitoba": "MB",
            "Maryland": "MD",
            "Massachusetts": "MA",
            "Michigan": "MI",
            "Minnesota": "MN",
            "Mississippi": "MS",
            "Missouri": "MO",
            "Montana": "MT",
            "Nebraska": "NE",
            "Nevada": "NV",
            "New Brunswick": "NB",
            "New Hampshire": "NH",
            "New Jersey": "NJ",
            "New Mexico": "NM",
            "New York": "NY",
            "Newfoundland": "NF",
            "North Carolina": "NC",
            "North Dakota": "ND",
            "Northwest Territories": "NT",
            "Nova Scotia": "NS",
            "Nunavut": "NU",
            "Ohio": "OH",
            "Oklahoma": "OK",
            "Ontario": "ON",
            "Oregon": "OR",
            "Pennsylvania": "PA",
            "Prince Edward Island": "PE",
            "Puerto Rico": "PR",
            "Quebec": "QC",
            "Rhode Island": "RI",
            "Saskatchewan": "SK",
            "South Carolina": "SC",
            "South Dakota": "SD",
            "Tennessee": "TN",
            "Texas": "TX",
            "Utah": "UT",
            "Vermont": "VT",
            "Virgin Islands": "VI",
            "Virginia": "VA",
            "Washington": "WA",
            "West Virginia": "WV",
            "Wisconsin": "WI",
            "Wyoming": "WY",
            "Yukon Territory": "YT",
        }

    def build_provider_state_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildProviderStateTable."""
        return {
            "Alabama": "01",
            "Alaska": "02",
            "Arizona": "03",
            "Arkansas": "04",
            "California": "05",
            "Colorado": "06",
            "Connecticut": "07",
            "Delaware": "08",
            "District of Columbia": "09",
            "Florida": "10",
            "Georgia": "11",
            "Hawaii": "12",
            "Idaho": "13",
            "Illinois": "14",
            "Indiana": "15",
            "Iowa": "16",
            "Kansas": "17",
            "Kentucky": "18",
            "Louisiana": "19",
            "Maine": "20",
            "Maryland": "21",
            "Massachusetts": "22",
            "Michigan": "23",
            "Minnesota": "24",
            "Mississippi": "25",
            "Missouri": "26",
            "Montana": "27",
            "Nebraska": "28",
            "Nevada": "29",
            "New Hampshire": "30",
            "New Jersey": "31",
            "New Mexico": "32",
            "New York": "33",
            "North Carolina": "34",
            "North Dakota": "35",
            "Ohio": "36",
            "Oklahoma": "37",
            "Oregon": "38",
            "Pennsylvania": "39",
            "Puerto Rico": "40",
            "Rhode Island": "41",
            "South Carolina": "42",
            "South Dakota": "43",
            "Tennessee": "44",
            "Texas": "45",
            "Utah": "46",
            "Vermont": "47",
            "Virgin Islands": "48",
            "Virginia": "49",
            "Washington": "50",
            "West Virginia": "51",
            "Wisconsin": "52",
            "Wyoming": "53",
            "Africa": "54",
            "Asia": "55",
            "Canada & Islands": "56",
            "Central America and West Indies": "57",
            "Europe": "58",
            "Mexico": "59",
            "Oceania": "60",
            "Philippines": "61",
            "South America": "62",
            "U.S. Possessions": "63",
            "American Samoa": "64",
            "Guam": "65",
            "Commonwealth of the Northern Marianas Islands": "66",
        }

    def zip_to_county_code(self, zipcode: str) -> str | None:
        """Java: CMSStateCodeMapper#zipToCountyCode."""
        return self.ssa_table.get(zipcode)

    def state_county_name_to_county_code(
        self, state: str, county_name: str, rand: RandomNumberGenerator
    ) -> str | None:
        """Java: CMSStateCodeMapper#stateCountyNameToCountyCode."""
        abbr = self.state_to_abbrev.get(state)
        data = self.ssa_state_county_name_county_code.get(abbr or "")
        key = county_name.upper().replace(" COUNTY", "")
        if data is not None:
            if key not in data:
                key = list(data)[rand.rand_int(len(data))]
            return data[key]
        return None

    def build_ssa_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildSSATable."""
        return {
            ("0" + row["zip"] if len(row["zip"]) == 4 else row["zip"]): row["ssacounty"]
            for row in _fips_rows()
        }

    def build_county_name_lookup(self) -> dict[str, JavaHashMap[str, str]]:
        """Java: CMSStateCodeMapper#buildCountyNameLookup; first county row wins."""
        results: dict[str, JavaHashMap[str, str]] = {}
        for row in _fips_rows():
            data = results.setdefault(row["state"], JavaHashMap())
            if row["county"] not in data:
                data[row["county"]] = row["ssacounty"]
        return results

    def zip_to_fips_county_code(self, zipcode: str) -> str:
        """Java: CMSStateCodeMapper#zipToFipsCountyCode."""
        return self.fips_table.get(zipcode, "")

    def build_fips_table(self) -> dict[str, str]:
        """Java: CMSStateCodeMapper#buildFipsTable."""
        return {
            ("0" + row["zip"] if len(row["zip"]) == 4 else row["zip"]): row["fipscounty"]
            for row in _fips_rows()
        }

    def capitalize_words(self, str: str) -> str:
        """Java: CMSStateCodeMapper#capitalizeWords; preserve rest-of-word casing."""
        words = re.split(r"\s", str)
        while words and not words[-1]:
            words.pop()
        return " ".join(
            word.lower() if word.lower() in ("of", "and", "the") else word[0].upper() + word[1:]
            for word in words
        ).strip()
