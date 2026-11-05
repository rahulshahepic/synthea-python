"""Java API skeleton: ExpressionProcessor.java."""

from __future__ import annotations

import builtins
import re
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

    class BiMap(Protocol):
        """Java boundary type: BiMap; external to the mapped Python port."""

    class ConcurrentMap(Protocol):
        """Java boundary type: ConcurrentMap; external to the mapped Python port."""

    class Context(Protocol):
        """Java boundary type: Context; external to the mapped Python port."""

    class Library(Protocol):
        """Java boundary type: Library; external to the mapped Python port."""

    class LibraryManager(Protocol):
        """Java boundary type: LibraryManager; external to the mapped Python port."""

    class ModelManager(Protocol):
        """Java boundary type: ModelManager; external to the mapped Python port."""

    class MultiTable(Protocol):
        """Java boundary type: MultiTable; external to the mapped Python port."""


class ExpressionProcessor:
    """Java: ExpressionProcessor; pending T07."""

    LIBRARY_NAME: ClassVar[str] = "Synthea"
    modelManager: ClassVar[ModelManager]  # Java initialization deferred to T07.
    vitalSignCache: ClassVar[ConcurrentMap] = {}
    attributeSet: ClassVar[builtins.set[str]] = set()

    def __init__(self, expression: str, param_type_map: dict[str, str] | None = None) -> None:
        """Java: ExpressionProcessor#ExpressionProcessor.

        Java overloads:
        (String expression)
        (String expression, Map paramTypeMap)
        """
        self.library_manager: LibraryManager
        self.expression: str
        self.library: Library
        self.context: Context
        self.elm: str
        self.param_type_map: dict[str, str]
        self.cql_param_map: BiMap
        raise NotImplementedError("Java: ExpressionProcessor#ExpressionProcessor — pending T07")

    def cql_to_elm(self, cql: str) -> str:
        """Java: ExpressionProcessor#cqlToElm.

        Java overloads:
        (String cql)
        """
        raise NotImplementedError("Java: ExpressionProcessor#cqlToElm — pending T07")

    def get_expression(self) -> str:
        """Java: ExpressionProcessor#getExpression.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressionProcessor#getExpression — pending T07")

    def get_param_names(self) -> builtins.set[str]:
        """Java: ExpressionProcessor#getParamNames.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressionProcessor#getParamNames — pending T07")

    def get_param_types(self) -> dict[str, str]:
        """Java: ExpressionProcessor#getParamTypes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ExpressionProcessor#getParamTypes — pending T07")

    def evaluate_numeric(self, params: dict[str, object]) -> Decimal:
        """Java: ExpressionProcessor#evaluateNumeric.

        Java overloads:
        (Map params)
        """
        raise NotImplementedError("Java: ExpressionProcessor#evaluateNumeric — pending T07")

    @staticmethod
    def get_person_value(
        param: str, person: Person, time: int, expression: str | None = None
    ) -> object:
        """Java: ExpressionProcessor#getPersonValue.

        Java overloads:
        (String param, Person person, long time)
        (String param, Person person, long time, String expression)
        """
        raise NotImplementedError("Java: ExpressionProcessor#getPersonValue — pending T07")

    def evaluate_from_sim_results(self, results: MultiTable, lead_time: float) -> Decimal:
        """Java: ExpressionProcessor#evaluateFromSimResults.

        Java overloads:
        (MultiTable results, double leadTime)
        """
        raise NotImplementedError("Java: ExpressionProcessor#evaluateFromSimResults — pending T07")

    def evaluate(
        self, person_or_params: Person | dict[str, object], time: int | None = None
    ) -> object:
        """Java: ExpressionProcessor#evaluate.

        Java overloads:
        (Person person, long time)
        (Map params)
        """
        raise NotImplementedError("Java: ExpressionProcessor#evaluate — pending T07")

    def replace_parameters(self, expression: str) -> str:
        """Java: ExpressionProcessor#replaceParameters.

        Java overloads:
        (String expression)
        """
        clean_expression = expression
        for match in re.finditer(r"#([dlbs]?)\\{(.+?)\\}", expression):
            key, type_key, param = match.group(0, 1, 2)
            cql_param = param.replace(" ", "_")
            self.cql_param_map[param] = cql_param
            if type_key:
                self.param_type_map[cql_param] = {
                    "d": "Decimal",
                    "l": "List<Decimal>",
                    "b": "Boolean",
                    "s": "String",
                }[type_key]
            clean_expression = clean_expression.replace(key, cql_param)
        return clean_expression

    def convert_parameterized_expression_to_cql(self, expression: str) -> str:
        """Java: ExpressionProcessor#convertParameterizedExpressionToCql.

        Java overloads:
        (String expression)
        """
        wrapped = "library " + self.LIBRARY_NAME + " version '1'\\n"
        for param, cql_param in self.cql_param_map.items():
            wrapped += (
                "\\nparameter " + cql_param + " "
                + self.param_type_map.get(param, "Decimal")
            )
        wrapped += "\\n\\ncontext Unfiltered\\n\\n"
        statements = expression.split("\\n")
        for statement in statements[:-1]:
            wrapped += statement + "\\n"
        wrapped += "define result: " + statements[-1]
        return wrapped
