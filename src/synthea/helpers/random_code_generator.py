"""Java API skeleton: RandomCodeGenerator.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.concepts.health_record import Code

    class OkHttpClient(Protocol):
        """Java boundary type: OkHttpClient; external to the mapped Python port."""

    class UrlValidator(Protocol):
        """Java boundary type: UrlValidator; external to the mapped Python port."""

    class ValueSet(Protocol):
        """Java boundary type: ValueSet; external to the mapped Python port."""

    class ValueSetExpansionComponent(Protocol):
        """Java boundary type: ValueSetExpansionComponent; external to the mapped Python
        port.
        """


class RandomCodeGenerator:
    """Java: RandomCodeGenerator; pending T08."""

    expandBaseUrl: ClassVar[str]  # Java initialization deferred to T07.
    codeListCache: ClassVar[dict[str, list[Code]]] = {}
    selectedCodes: ClassVar[list[Code]] = []
    urlValidator: ClassVar[UrlValidator]  # Java initialization deferred to T07.
    client: ClassVar[OkHttpClient]  # Java initialization deferred to T07.

    def __init__(self) -> None:
        """Java: RandomCodeGenerator#RandomCodeGenerator.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: RandomCodeGenerator#RandomCodeGenerator — pending T08")

    @staticmethod
    def get_code(value_set_uri: str, seed: int, code: Code | None = None) -> Code:
        """Java: RandomCodeGenerator#getCode.

        Java overloads:
        (String valueSetUri, long seed, Code code)
        (String valueSetUri, long seed)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#getCode — pending T08")

    @staticmethod
    def code_in_value_set(code: Code, value_set_uri: str) -> bool:
        """Java: RandomCodeGenerator#codeInValueSet.

        Java overloads:
        (Code code, String valueSetUri)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#codeInValueSet — pending T08")

    @staticmethod
    def expand_value_set(value_set_uri: str) -> None:
        """Java: RandomCodeGenerator#expandValueSet.

        Java overloads:
        (String valueSetUri)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#expandValueSet — pending T08")

    @staticmethod
    def load_value_set(value_set_uri: str, value_set: ValueSet) -> None:
        """Java: RandomCodeGenerator#loadValueSet.

        Java overloads:
        (String valueSetUri, ValueSet valueSet)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#loadValueSet — pending T08")

    @staticmethod
    def validate_expansion(expansion: ValueSetExpansionComponent) -> None:
        """Java: RandomCodeGenerator#validateExpansion.

        Java overloads:
        (ValueSetExpansionComponent expansion)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#validateExpansion — pending T08")

    @staticmethod
    def validate_code(code: Code) -> None:
        """Java: RandomCodeGenerator#validateCode.

        Java overloads:
        (Code code)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#validateCode — pending T08")

    @staticmethod
    def set_base_url(url: str) -> None:
        """Java: RandomCodeGenerator#setBaseUrl.

        Java overloads:
        (String url)
        """
        raise NotImplementedError("Java: RandomCodeGenerator#setBaseUrl — pending T08")
