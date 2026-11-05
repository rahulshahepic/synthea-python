"""Java: org.mitre.synthea.helpers.RandomCodeGenerator, offline/cache paths.

FHIR ValueSets at the Python boundary are parsed JSON dictionaries. Network
expansion is an explicitly excluded terminology-server feature.
"""

from __future__ import annotations

import ipaddress
import re
from typing import ClassVar, cast
from urllib.parse import urlsplit

from synthea.helpers.config import Config
from synthea.javacompat.random import JavaRandom
from synthea.world.concepts.health_record import Code

type ValueSet = dict[str, object]
type ValueSetExpansionComponent = dict[str, object]
_MISSING = object()


def _valid_url(value: str | None) -> bool:
    """Java: UrlValidator#isValid with ALLOW_2_SLASHES and default schemes.

    Reject local hosts, malformed authorities, fragments containing whitespace,
    invalid ports and paths that traverse above root before consulting the cache.
    """
    if not value or re.search(r"\s", value):
        return False
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in ("http", "https", "ftp") or not parts.hostname:
            return False
        if parts.port is not None and not 0 <= parts.port <= 65535:
            return False
        host = parts.hostname
        try:
            ipaddress.ip_address(host)
        except ValueError:
            host = host.encode("idna").decode("ascii").removesuffix(".")
            labels = host.split(".")
            if len(labels) < 2 or len(host) > 253:
                return False
            if any(
                not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                for label in labels
            ):
                return False
            if labels[-1].isdigit() or len(labels[-1]) < 2:
                return False
        depth = 0
        for component in parts.path.split("/"):
            if component == "..":
                depth -= 1
                if depth < 0:
                    return False
            elif component and component != ".":
                depth += 1
        return not parts.path or parts.path.startswith("/")
    except (ValueError, UnicodeError):
        return False


class RandomCodeGenerator:
    """Java: org.mitre.synthea.helpers.RandomCodeGenerator."""

    expandBaseUrl: ClassVar[str] = (
        str(Config.get("generate.terminology_service_url")) + "/ValueSet/$expand?url="
    )
    codeListCache: ClassVar[dict[str, list[Code]]] = {}
    selectedCodes: ClassVar[list[Code]] = []

    def __init__(self) -> None:
        """Java: RandomCodeGenerator is abstract and cannot be instantiated."""
        raise TypeError("RandomCodeGenerator is a static utility class")

    @staticmethod
    def get_code(
        value_set_uri: str, seed: int, code: Code | object | None = _MISSING
    ) -> Code | None:
        """Java: RandomCodeGenerator#getCode (both overloads).

        Only the three-argument overload appends to selectedCodes, including when
        the explicitly supplied fallback is null.
        """
        if not _valid_url(value_set_uri):
            return None if code is _MISSING else cast(Code | None, code)
        RandomCodeGenerator.expand_value_set(value_set_uri)
        codes = RandomCodeGenerator.codeListCache[value_set_uri]
        selected = codes[JavaRandom(seed).next_int(len(codes))]
        RandomCodeGenerator.validate_code(selected)
        if code is not _MISSING:
            RandomCodeGenerator.validate_code(selected)
            RandomCodeGenerator.selectedCodes.append(selected)
        return selected

    @staticmethod
    def code_in_value_set(code: Code, value_set_uri: str) -> bool:
        """Java: RandomCodeGenerator#codeInValueSet."""
        if _valid_url(value_set_uri):
            RandomCodeGenerator.expand_value_set(value_set_uri)
            return code in RandomCodeGenerator.codeListCache[value_set_uri]
        return False

    @staticmethod
    def expand_value_set(value_set_uri: str) -> None:
        """Java: RandomCodeGenerator#expandValueSet, cache lookup only."""
        if value_set_uri not in RandomCodeGenerator.codeListCache:
            raise NotImplementedError("Terminology-server ValueSet expansion out of scope")

    @staticmethod
    def load_value_set(value_set_uri: str | None, value_set: ValueSet) -> None:
        """Java: RandomCodeGenerator#loadValueSet, offline FHIR JSON boundary."""
        if value_set_uri is None:
            value_set_uri = cast(str | None, value_set.get("url"))
        if value_set_uri is None or value_set_uri in RandomCodeGenerator.codeListCache:
            return
        if value_set.get("expansion"):
            expansion = cast(ValueSetExpansionComponent, value_set["expansion"])
            RandomCodeGenerator.validate_expansion(expansion)
            contains = cast(list[dict[str, object]], expansion["contains"])
            codes = [
                Code(
                    cast(str, c.get("system")),
                    cast(str, c.get("code")),
                    cast(str, c.get("display")),
                )
                for c in contains
            ]
        elif value_set.get("compose"):
            codes = []
            compose = cast(dict[str, object], value_set["compose"])
            for include in cast(list[dict[str, object]], compose.get("include", [])):
                system = cast(str, include.get("system"))
                for concept in cast(list[dict[str, object]], include.get("concept", [])):
                    codes.append(
                        Code(
                            system,
                            cast(str, concept.get("code")),
                            cast(str, concept.get("display")),
                        )
                    )
            if not codes:
                raise RuntimeError("ValueSet does not contain any codes defined within compose")
        else:
            raise RuntimeError("ValueSet does not contain compose or expansion")
        RandomCodeGenerator.codeListCache[value_set_uri] = codes
        print("Loaded " + value_set_uri)

    @staticmethod
    def validate_expansion(expansion: ValueSetExpansionComponent) -> None:
        """Java: RandomCodeGenerator#validateExpansion."""
        if not expansion.get("contains"):
            raise RuntimeError("ValueSet expansion does not contain any codes")
        if expansion.get("total", 0) == 0:
            raise RuntimeError("No total element in ValueSet expand result")

    @staticmethod
    def validate_code(code: Code) -> None:
        """Java: RandomCodeGenerator#validateCode; blanks are accepted, empty is not."""
        if any(v is None or v == "" for v in (code.system, code.code, code.display)):
            raise RuntimeError(
                "ValueSet contains element does not contain system, code and display"
            )

    @staticmethod
    def set_base_url(url: str) -> None:
        """Java: RandomCodeGenerator#setBaseUrl."""
        RandomCodeGenerator.expandBaseUrl = url + "/ValueSet/$expand?url="
