"""Java: org.mitre.synthea.helpers.ExpressionProcessor.

Compile Synthea's scalar/list CQL expressions to an expression tree once, then
execute with CQL's decimal arithmetic and three-valued Boolean semantics.
No Python source is evaluated. Physiology result tables remain out of scope.
"""

from __future__ import annotations

import logging
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from decimal import ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_UP, Decimal, localcontext
from typing import ClassVar, Protocol

from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.numbers import double_to_string, to_int32
from synthea.world.concepts.vital_sign import VITAL_SIGN_DISPLAY_NAMES, VitalSign


class ExpressionPerson(Protocol):
    """Java: Person operations needed for expression parameter resolution."""

    @property
    def attributes(self) -> dict[str, object]:
        """Java: Person#attributes."""
        ...

    def age_in_decimal_years(self, time: int) -> float:
        """Java: Person#ageInDecimalYears(long)."""
        ...

    def get_vital_sign(self, vital_sign: VitalSign, time: int) -> float:
        """Java: Person#getVitalSign(VitalSign,long)."""
        ...


@dataclass
class _Node:
    """Java: CQL/ELM expression node used by ExpressionProcessor."""

    kind: str
    value: object = None
    args: list[_Node] = field(default_factory=list)
    result_type: str = "Any"


_TOKEN = re.compile(
    r"\s*(?:(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|('(?:\\.|[^'\\])*')|"
    r'("(?:\\.|[^"\\])*")|([A-Za-z_][A-Za-z_0-9]*)|(<=|>=|!=|!~|<>|[+*/^=<>~&(),{}\[\]:-]))'
)
_PRECEDENCE = {
    "implies": 1,
    "or": 2,
    "xor": 2,
    "and": 3,
    "=": 4,
    "!=": 4,
    "<>": 4,
    "~": 4,
    "!~": 4,
    "<": 5,
    "<=": 5,
    ">": 5,
    ">=": 5,
    "in": 5,
    "contains": 5,
    "is": 5,
    "+": 6,
    "-": 6,
    "&": 6,
    "*": 7,
    "/": 7,
    "div": 7,
    "mod": 7,
    "^": 8,
}
_FUNCTION_ARITIES = {
    "Abs": (1, 1),
    "Ceiling": (1, 1),
    "Floor": (1, 1),
    "Truncate": (1, 1),
    "Round": (1, 2),
    "Power": (2, 2),
    "Ln": (1, 1),
    "Exp": (1, 1),
    "Log": (2, 2),
    "Min": (1, 1),
    "Max": (1, 1),
    "Sum": (1, 1),
    "Avg": (1, 1),
    "Count": (1, 1),
    "First": (1, 1),
    "Last": (1, 1),
    "Length": (1, 1),
    "Coalesce": (1, 1000),
    "ToDecimal": (1, 1),
    "ToInteger": (1, 1),
    "ToString": (1, 1),
    "Concatenate": (1, 1000),
    "Upper": (1, 1),
    "Lower": (1, 1),
    "Exists": (1, 1),
    "Distinct": (1, 1),
}


class _Parser:
    """Java: CqlTranslator expression parsing for scalar/list CQL."""

    def __init__(self, source: str, names: set[str]) -> None:
        """Java: CqlTranslator#fromText; reject unrecognized input at construction."""
        self.tokens: list[tuple[str, str]] = []
        position = 0
        while position < len(source.rstrip()):
            match = _TOKEN.match(source, position)
            if match is None:
                raise ValueError(f"Invalid CQL at {source[position:]!r}")
            group = next(i for i in range(1, 6) if match.group(i) is not None)
            self.tokens.append((str(group), match.group(group)))
            position = match.end()
        self.tokens.append(("end", ""))
        self.index = 0
        self.names = names

    def peek(self) -> str:
        """Java: CqlTranslator token lookahead."""
        return self.tokens[self.index][1]

    def take(self, expected: str | None = None) -> tuple[str, str]:
        """Java: CqlTranslator token consumption."""
        token = self.tokens[self.index]
        if expected is not None and token[1] != expected:
            raise ValueError(f"Expected {expected!r}, found {token[1]!r}")
        if token[0] == "end":
            raise ValueError("Unexpected end of CQL expression")
        self.index += 1
        return token

    def parse(self) -> _Node:
        """Java: CqlTranslator#fromText, one complete expression."""
        node = self.expression()
        if self.peek():
            raise ValueError(f"Unexpected CQL token {self.peek()!r}")
        return node

    def expression(self, minimum: int = 0) -> _Node:
        """Java: CQL operator precedence, conditionals, lists and function references."""
        kind, token = self.take()
        if token == "if":
            condition = self.expression()
            self.take("then")
            yes = self.expression()
            self.take("else")
            left = _Node("If", args=[condition, yes, self.expression()])
        elif token in ("-", "+", "not"):
            left = _Node("unary", token, [self.expression(8 if token != "not" else 4)])
        elif token == "(":
            left = self.expression()
            self.take(")")
        elif token == "{":
            args = []
            while self.peek() != "}":
                args.append(self.expression())
                if self.peek() != ",":
                    break
                self.take(",")
            self.take("}")
            left = _Node("List", args=args)
        elif kind == "1":
            left = _Node(
                "Literal", Decimal(token) if any(c in token for c in ".eE") else int(token)
            )
        elif kind == "2":
            text = re.sub(
                r"\\(.)", lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m[1], m[1]), token[1:-1]
            )
            left = _Node("Literal", text)
        elif token in ("true", "false", "null"):
            left = _Node("Literal", {"true": True, "false": False, "null": None}[token])
        elif kind in ("3", "4"):
            name = token[1:-1] if kind == "3" else token
            if self.peek() == "(":
                self.take("(")
                args = []
                while self.peek() != ")":
                    args.append(self.expression())
                    if self.peek() != ",":
                        break
                    self.take(",")
                self.take(")")
                arity = _FUNCTION_ARITIES.get(name)
                if arity is None or not arity[0] <= len(args) <= arity[1]:
                    raise ValueError(f"Unknown CQL function or invalid arguments: {name}")
                left = _Node("call", name, args)
            elif name in self.names:
                left = _Node("Reference", name)
            else:
                raise ValueError(f"Could not resolve identifier {name!r}")
        else:
            raise ValueError(f"Unexpected CQL token {token!r}")
        while True:
            if self.peek() == "[":
                self.take("[")
                index = self.expression()
                self.take("]")
                left = _Node("index", args=[left, index])
                continue
            operator = self.peek()
            precedence = _PRECEDENCE.get(operator, -1)
            if precedence < minimum:
                break
            self.take()
            if operator == "is":
                negate = self.peek() == "not"
                if negate:
                    self.take("not")
                _, target = self.take()
                if target not in ("null", "true", "false"):
                    raise ValueError(f"Unsupported CQL is test: {target}")
                left = _Node("is", (target, negate), [left])
            else:
                right = self.expression(precedence + (operator != "^"))
                if (
                    operator in ("=", "!=", "<>")
                    and left.kind == right.kind == "Literal"
                    and left.value is None
                    and right.value is None
                ):
                    raise ValueError("Call to operator Equal(System.Any,System.Any) is ambiguous")
                left = _Node("binary", operator, [left, right])
        return left


def _decimal(value: object) -> Decimal:
    """Java: CQL implicit Integer-to-Decimal conversion."""
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return Decimal(double_to_string(value)) if isinstance(value, float) else Decimal(value)
    raise TypeError(f"Expected CQL numeric value, got {type(value).__name__}")


def _precision(value: Decimal) -> Decimal:
    """Java: engine.runtime.Value#verifyPrecision, flooring at eight decimal places."""
    with localcontext() as ctx:
        ctx.prec = max(200, len(value.as_tuple().digits) + 16)
        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int):
            raise ValueError("Non-finite CQL decimal")
        if exponent < -8:
            return value.quantize(Decimal("0.00000001"), rounding=ROUND_FLOOR)
        if exponent > 0:
            return value.quantize(Decimal(1))
        return value


def _divide(left: object, right: object) -> Decimal | None:
    """Java: CQL DivideEvaluator#divideHelper (exact, else scale 8 FLOOR)."""
    a, b = _decimal(left), _decimal(right)
    if b == 0:
        return None
    try:
        return _precision(bd.divide_exact(a, b))
    except ArithmeticError:
        return bd.divide(a, b, 8, bd.RoundingMode.FLOOR)


def _compare[T: (str, Decimal)](operator: str, left: T, right: T) -> bool:
    """Java: CQL ordering evaluators for comparable scalar operands."""
    return {"<": left < right, "<=": left <= right, ">": left > right, ">=": left >= right}[
        operator
    ]


def _binary(operator: str, left: object, right: object) -> object:
    """Java: CQL arithmetic, comparison, membership and three-valued logic evaluators."""
    if operator == "and":
        return False if left is False or right is False else None if None in (left, right) else True
    if operator == "or":
        return True if left is True or right is True else None if None in (left, right) else False
    if operator == "xor":
        return None if left is None or right is None else bool(left) != bool(right)
    if operator == "implies":
        return _binary("or", None if left is None else not left, right)
    if operator in ("~", "!~"):
        equal = (left is None and right is None) if None in (left, right) else left == right
        return equal if operator == "~" else not equal
    if operator == "&":
        return ("" if left is None else str(left)) + ("" if right is None else str(right))
    if left is None or right is None:
        return None
    if operator in ("=", "!=", "<>"):
        return left == right if operator == "=" else left != right
    if operator in ("in", "contains"):
        container, item = (right, left) if operator == "in" else (left, right)
        if not isinstance(container, (list, str)):
            raise TypeError("CQL membership requires a list or string")
        return item in container
    if operator in ("<", "<=", ">", ">="):
        if isinstance(left, str) and isinstance(right, str):
            return _compare(operator, left, right)
        return _compare(operator, _decimal(left), _decimal(right))
    if operator == "+" and isinstance(left, str) and isinstance(right, str):
        return left + right
    if operator == "/":
        return _divide(left, right)
    if operator == "^":
        return _call("Power", [left, right])
    a, b = _decimal(left), _decimal(right)
    if operator in ("div", "mod"):
        if b == 0:
            return None
        quotient = bd.divide(a, b, 0, bd.RoundingMode.DOWN)
        result = quotient if operator == "div" else bd.subtract(a, bd.multiply(quotient, b))
    else:
        result = {"+": bd.add, "-": bd.subtract, "*": bd.multiply}[operator](a, b)
    if type(left) is int and type(right) is int:
        return to_int32(int(result))
    return _precision(result)


def _call(name: str, args: list[object]) -> object:
    """Java: CQL system function evaluators used by Synthea scalar/list expressions."""
    value = args[0]
    if name == "Coalesce":
        values = value if len(args) == 1 and isinstance(value, list) else args
        return next((v for v in values if v is not None), None)
    if name == "Count":
        return sum(v is not None for v in value) if isinstance(value, list) else 0
    if name == "Exists":
        return isinstance(value, list) and any(v is not None for v in value)
    if value is None:
        return None
    if name in ("Min", "Max", "Sum", "Avg", "First", "Last", "Distinct"):
        if not isinstance(value, list):
            value = [value]  # CQL implicitly promotes a scalar to a singleton list.
        values = [v for v in value if v is not None]
        if name == "Distinct":
            return list(dict.fromkeys(value))
        if name in ("First", "Last"):
            return value[0 if name == "First" else -1] if value else None
        if not values:
            return None
        if name in ("Min", "Max"):
            return (min if name == "Min" else max)(values)
        total = values[0]
        for item in values[1:]:
            total = _binary("+", total, item)
        return _divide(total, len(values)) if name == "Avg" else total
    if name in ("Upper", "Lower", "Length", "Concatenate", "ToString"):
        if name == "Length":
            return len(value) if isinstance(value, (str, list)) else None
        if name == "ToString":
            return str(value).lower() if isinstance(value, bool) else str(value)
        if name == "Concatenate":
            parts = value if isinstance(value, list) else args
            return "".join(str(part) for part in parts if part is not None)
        return str(value).upper() if name == "Upper" else str(value).lower()
    if name == "ToDecimal":
        try:
            return Decimal(str(value))
        except ArithmeticError:
            return None
    if name == "ToInteger":
        try:
            return int(str(value))
        except ValueError:
            return None
    number = _decimal(value)
    if name == "Abs":
        return abs(value) if isinstance(value, (int, Decimal)) else abs(number)
    if name in ("Ceiling", "Floor", "Truncate"):
        if name == "Ceiling":
            return math.ceil(number)
        if name == "Floor":
            return math.floor(number)
        return math.trunc(number)
    if name == "Round":
        places = 0 if len(args) == 1 or args[1] is None else int(_decimal(args[1]))
        with localcontext() as ctx:
            ctx.prec = 200
            return number.quantize(
                Decimal(1).scaleb(-places),
                rounding=(ROUND_HALF_DOWN if number < 0 else ROUND_HALF_UP),
            )
    if len(args) > 1 and args[1] is None:
        return None
    try:
        if name == "Power":
            exponent = _decimal(args[1])
            if type(value) is int and type(args[1]) is int:
                power = int(args[1])
                if power < 0:
                    return bd.divide_exact(Decimal(1), Decimal(pow(int(value), -power)))
                return to_int32(pow(int(value), power))
            return _precision(Decimal.from_float(math.pow(float(number), float(exponent))))
        if name == "Log":
            return _precision(
                Decimal.from_float(math.log(float(number)) / math.log(float(_decimal(args[1]))))
            )
        function = {"Sqrt": math.sqrt, "Ln": math.log, "Exp": math.exp}[name]
        result = Decimal.from_float(function(float(number)))
        return result if name == "Exp" else _precision(result)
    except (ValueError, OverflowError):
        return None


def _common_type(types: list[str]) -> str:
    """Java: CqlTranslator common-type inference and implicit numeric promotion."""
    present = set(types) - {"Any"}
    if not present:
        return "Any"
    if present <= {"Integer", "Decimal"}:
        return "Decimal" if "Decimal" in present else "Integer"
    if len(present) != 1:
        raise ValueError(f"Incompatible CQL operand types: {', '.join(sorted(present))}")
    return next(iter(present))


def _infer(
    node: _Node, types: dict[str, str], definitions: dict[str, _Node], visiting: set[str]
) -> str:
    """Java: CqlTranslator type resolution for the scalar/list system operators."""
    child_types = [_infer(arg, types, definitions, visiting) for arg in node.args]
    result = "Any"
    if node.kind == "Literal":
        value = node.value
        result = (
            "Boolean"
            if isinstance(value, bool)
            else "Integer"
            if isinstance(value, int)
            else "Decimal"
            if isinstance(value, Decimal)
            else "String"
            if isinstance(value, str)
            else "Any"
        )
    elif node.kind == "Reference":
        name = str(node.value)
        if name in types:
            result = types[name]
        elif name in definitions:
            if name in visiting:
                raise ValueError(f"Circular CQL expression reference: {name}")
            result = _infer(definitions[name], types, definitions, visiting | {name})
        else:
            raise ValueError(f"Unknown CQL identifier: {name}")
    elif node.kind == "If":
        if child_types[0] not in ("Boolean", "Any"):
            raise ValueError("CQL if condition must be Boolean")
        result = _common_type(child_types[1:])
    elif node.kind == "List":
        result = f"List<{_common_type(child_types)}>"
    elif node.kind == "is":
        result = "Boolean"
    elif node.kind == "index":
        if not child_types[0].startswith("List<") or child_types[1] != "Integer":
            raise ValueError("CQL index requires List and Integer")
        result = child_types[0][5:-1]
    elif node.kind == "unary":
        allowed = {"Boolean", "Any"} if node.value == "not" else {"Integer", "Decimal", "Any"}
        if child_types[0] not in allowed:
            raise ValueError(f"Invalid operand type for {node.value}")
        result = "Boolean" if node.value == "not" else child_types[0]
    elif node.kind == "binary":
        operator = str(node.value)
        if operator in ("and", "or", "xor", "implies"):
            if any(t not in ("Boolean", "Any") for t in child_types):
                raise ValueError("CQL Boolean operator requires Boolean operands")
            result = "Boolean"
        elif operator in ("in", "contains"):
            result = "Boolean"
        elif operator in ("=", "!=", "<>", "~", "!~", "<", "<=", ">", ">="):
            _common_type(child_types)
            result = "Boolean"
        elif operator == "&":
            if any(t not in ("String", "Any") for t in child_types):
                raise ValueError("CQL concatenate requires String operands")
            result = "String"
        else:
            common = _common_type(child_types)
            if common not in ("Integer", "Decimal", "Any") and not (
                operator == "+" and common == "String"
            ):
                raise ValueError(f"Invalid operands for CQL {operator}")
            result = "Decimal" if operator == "/" else common
    elif node.kind == "call":
        name = str(node.value)
        first = child_types[0]
        if name in ("Sum", "Avg", "Min", "Max", "Count", "First", "Last", "Distinct", "Exists"):
            element = first[5:-1] if first.startswith("List<") else first
            result = (
                "Integer"
                if name == "Count"
                else "Boolean"
                if name == "Exists"
                else "Decimal"
                if name == "Avg"
                else first
                if name == "Distinct"
                else element
            )
        elif name == "Coalesce":
            _common_type(child_types)  # Check compatibility; Coalesce preserves runtime types.
            result = "Any"
        elif name in ("Upper", "Lower", "ToString", "Concatenate"):
            result = "String"
        elif name in ("Ceiling", "Floor", "Truncate", "Length", "ToInteger"):
            result = "Integer"
        else:
            if any(t not in ("Integer", "Decimal", "Any") for t in child_types):
                raise ValueError(f"CQL {name} requires numeric operands")
            result = (
                first
                if name == "Abs"
                else (_common_type(child_types) if name == "Power" else "Decimal")
            )
    node.result_type = result
    return result


def _execute(node: _Node, context: dict[str, object]) -> object:
    """Java: ELM implicit conversions inserted by CqlTranslator."""
    result = _execute_raw(node, context)
    if node.result_type == "Decimal" and type(result) is int:
        return Decimal(result)
    return result


def _execute_raw(node: _Node, context: dict[str, object]) -> object:
    """Java: ExpressionDef#evaluate(Context)."""
    if node.kind == "Literal":
        return node.value
    if node.kind == "Reference":
        name = str(node.value)
        value = context[name]
        if isinstance(value, _Node):
            value = _execute(value, context)
            context[name] = value
        return value
    if node.kind == "If":
        return _execute(node.args[1 if _execute(node.args[0], context) is True else 2], context)
    args = [_execute(arg, context) for arg in node.args]
    if node.kind == "List":
        if any(isinstance(v, Decimal) for v in args):
            return [_decimal(v) if type(v) is int else v for v in args]
        return args
    if node.kind == "call":
        return _call(str(node.value), args)
    if node.kind == "binary":
        return _binary(str(node.value), args[0], args[1])
    if node.kind == "unary":
        value = args[0]
        if value is None:
            return None
        if node.value == "not":
            return not value
        if node.value == "-":
            return -value if type(value) is int else _decimal(value).copy_negate()
        return value
    if node.kind == "is":
        assert isinstance(node.value, tuple)
        target, negate = node.value
        result = args[0] is {"null": None, "true": True, "false": False}[target]
        return not result if negate else result
    if node.kind == "index":
        value, index = args
        if not isinstance(value, list) or not isinstance(index, int) or not 0 <= index < len(value):
            return None
        return value[index]
    raise ValueError(f"Unsupported CQL node {node.kind}")


class ExpressionProcessor:
    """Java: org.mitre.synthea.helpers.ExpressionProcessor."""

    LIBRARY_NAME: ClassVar[str] = "Synthea"
    vitalSignCache: ClassVar[dict[str, VitalSign]] = {}
    attributeSet: ClassVar[set[str]] = set()

    def __init__(self, expression: str, param_type_map: dict[str, str] | None = None) -> None:
        """Java: ExpressionProcessor#ExpressionProcessor(String,Map)."""
        self.param_type_map: dict[str, str] = {} if param_type_map is None else param_type_map
        self.cql_param_map: dict[str, str] = {}
        clean = self.replace_parameters(expression)
        self.expression: str = expression
        self.context: dict[str, object] = {}
        self.library: dict[str, _Node] = {}
        self.elm: str = self.cql_to_elm(self.convert_parameterized_expression_to_cql(clean))
        self.library_manager: dict[str, _Node] = self.library

    def cql_to_elm(self, cql: str) -> str:
        """Java: ExpressionProcessor#cqlToElm, compiling the scalar/list expression library."""
        definitions = re.findall(r'(?m)^define\s+(?:"([^"]+)"|(\w+))\s*:\s*', cql)
        names = [a or b for a, b in definitions]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate CQL definition")
        if not names:
            raise ValueError("CQL library contains no expression definitions")
        parts = re.split(r'(?m)^define\s+(?:"[^"]+"|\w+)\s*:\s*', cql)[1:]
        known = set(self.cql_param_map.values()) | set(names)
        self.library = {
            name: _Parser(source.strip(), known).parse()
            for name, source in zip(names, parts, strict=True)
        }
        types = {
            mapped: self.param_type_map.get(original, "Decimal")
            for original, mapped in self.cql_param_map.items()
        }
        for name, node in self.library.items():
            _infer(node, types, self.library, {name})
        library = ET.Element(
            "library",
            {
                "xmlns": "urn:hl7-org:elm:r1",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            },
        )
        ET.SubElement(library, "identifier", {"id": self.LIBRARY_NAME, "version": "1"})
        parameters = ET.SubElement(library, "parameters")
        for original, mapped in self.cql_param_map.items():
            parameter = ET.SubElement(parameters, "def", {"name": mapped, "accessLevel": "Public"})
            type_name = self.param_type_map.get(original, "Decimal")
            if type_name.startswith("List<"):
                specifier = ET.SubElement(
                    parameter, "parameterTypeSpecifier", {"xsi:type": "ListTypeSpecifier"}
                )
                ET.SubElement(
                    specifier,
                    "elementType",
                    {
                        "xsi:type": "NamedTypeSpecifier",
                        "name": "{urn:hl7-org:elm-types:r1}" + type_name[5:-1],
                    },
                )
            else:
                parameter.set("parameterType", "{urn:hl7-org:elm-types:r1}" + type_name)
        statements = ET.SubElement(library, "statements")
        for name, node in self.library.items():
            definition = ET.SubElement(statements, "def", {"name": name, "context": "Unfiltered"})
            self._elm_node(definition, node)
        return ET.tostring(library, encoding="unicode")

    def _elm_node(self, parent: ET.Element, node: _Node, tag: str = "expression") -> None:
        """Java: CqlTranslator#toXml; ELM representation of the supported system operators."""
        element = ET.SubElement(parent, tag)
        if node.kind == "Literal":
            if node.value is None:
                element.set("xsi:type", "Null")
            else:
                element.set("xsi:type", "Literal")
                element.set("valueType", "{urn:hl7-org:elm-types:r1}" + node.result_type)
                text = str(node.value).lower() if isinstance(node.value, bool) else str(node.value)
                element.set("value", text)
            return
        if node.kind == "Reference":
            element.set(
                "xsi:type",
                "ParameterRef" if node.value in self.cql_param_map.values() else "ExpressionRef",
            )
            element.set("name", str(node.value))
            return
        if node.kind == "If":
            element.set("xsi:type", "If")
            for name, arg in zip(("condition", "then", "else"), node.args, strict=True):
                self._elm_node(element, arg, name)
            return
        if node.kind == "List":
            element.set("xsi:type", "List")
            for arg in node.args:
                self._elm_node(element, arg, "element")
            return
        if node.kind == "index":
            element.set("xsi:type", "Indexer")
            self._elm_node(element, node.args[0], "source")
            self._elm_node(element, node.args[1], "index")
            return
        if node.kind == "is":
            assert isinstance(node.value, tuple)
            target, negate = node.value
            element.set("xsi:type", "Not" if negate else "Is" + str(target).title())
            if negate:
                element = ET.SubElement(
                    element, "operand", {"xsi:type": "Is" + str(target).title()}
                )
            self._elm_node(element, node.args[0], "operand")
            return
        operator = str(node.value)
        if node.kind == "binary":
            name = {
                "+": "Add",
                "-": "Subtract",
                "*": "Multiply",
                "/": "Divide",
                "div": "TruncatedDivide",
                "mod": "Modulo",
                "^": "Power",
                "=": "Equal",
                "!=": "Equal",
                "<>": "Equal",
                "~": "Equivalent",
                "!~": "Equivalent",
                "<": "Less",
                "<=": "LessOrEqual",
                ">": "Greater",
                ">=": "GreaterOrEqual",
                "and": "And",
                "or": "Or",
                "xor": "Xor",
                "implies": "Implies",
                "in": "In",
                "contains": "Contains",
                "&": "Concatenate",
            }[operator]
            if operator in ("!=", "<>", "!~"):
                element.set("xsi:type", "Not")
                element = ET.SubElement(element, "operand")
            element.set("xsi:type", name)
        elif node.kind == "unary":
            element.set("xsi:type", {"-": "Negate", "+": "ToDecimal", "not": "Not"}[operator])
        else:
            element.set("xsi:type", operator)
        source_functions = {"Min", "Max", "Sum", "Avg", "Count", "First", "Last", "Distinct"}
        for index, arg in enumerate(node.args):
            child_tag = (
                "source"
                if operator in source_functions
                else ("precision" if operator == "Round" and index == 1 else "operand")
            )
            self._elm_node(element, arg, child_tag)

    def get_expression(self) -> str:
        """Java: ExpressionProcessor#getExpression()."""
        return self.expression

    def get_param_names(self) -> set[str]:
        """Java: ExpressionProcessor#getParamNames()."""
        return set(self.cql_param_map)

    def get_param_types(self) -> dict[str, str]:
        """Java: ExpressionProcessor#getParamTypes()."""
        return self.param_type_map

    def evaluate_numeric(self, params: dict[str, object]) -> Decimal:
        """Java: ExpressionProcessor#evaluateNumeric(Map), a cast rather than a conversion."""
        value = self.evaluate(params)
        if not isinstance(value, Decimal):
            raise TypeError("CQL result is not a BigDecimal")
        return value

    @staticmethod
    def get_person_value(
        param: str, person: ExpressionPerson, time: int, expression: str | None = None
    ) -> object:
        """Java: ExpressionProcessor#getPersonValue(String,Person,long,String)."""
        if param == "age":
            return bd.from_double_exact(person.age_in_decimal_years(time))
        vital = ExpressionProcessor.vitalSignCache.get(param)
        if vital is None and param not in ExpressionProcessor.attributeSet:
            # T04 exposes the enum and display-name metadata; its from_string is still
            # a T11 stub. Resolve against that same metadata without requiring T11.
            vital = next(
                (
                    v
                    for v, name in VITAL_SIGN_DISPLAY_NAMES.items()
                    if name.lower() == param.lower()
                ),
                VitalSign.__members__.get(param),
            )
            if vital is None:
                ExpressionProcessor.attributeSet.add(param)
            else:
                ExpressionProcessor.vitalSignCache[param] = vital
        if vital is not None:
            return bd.from_double_exact(person.get_vital_sign(vital, time))
        value = person.attributes.get(param)
        suffix = f' in expression "{expression}"' if expression is not None else ""
        if value is None:
            raise ValueError(
                f'Unable to map "{param}"{suffix}: Invalid person attribute or vital sign.'
            )
        if isinstance(value, (str, bool)):
            return value
        if isinstance(value, (int, float, Decimal)):
            return Decimal(double_to_string(value) if isinstance(value, float) else str(value))
        raise ValueError(
            f'Unable to map person attribute "{param}"{suffix}: '
            f"Unsupported type: {type(value).__name__}."
        )

    def evaluate_from_sim_results(self, results: object, lead_time: float) -> Decimal:
        """Java: ExpressionProcessor#evaluateFromSimResults; physiology is out of scope."""
        raise NotImplementedError("physiology simulation results are out of scope")

    def evaluate(
        self, person_or_params: ExpressionPerson | dict[str, object] | None, time: int | None = None
    ) -> object:
        """Java: ExpressionProcessor#evaluate(Map) and #evaluate(Person,long)."""
        if isinstance(person_or_params, dict):
            params = person_or_params
        else:
            params = {}
            for name in self.cql_param_map:
                if person_or_params is None or time is None:
                    raise TypeError("Person and time are required to resolve parameters")
                params[name] = self.get_person_value(name, person_or_params, time, self.expression)
        missing = self.get_param_names() - params.keys()
        if missing:
            raise ValueError(
                f"Missing parameter(s): {', '.join(sorted(missing))} "
                f'for expression "{self.expression}"'
            )
        extra = params.keys() - self.get_param_names()
        if extra:
            logging.getLogger(__name__).warning(
                'unused parameter(s) provided for expression "%s": %s',
                self.expression,
                ", ".join(sorted(extra)),
            )
        self.context = dict(self.library)
        for name, mapped in self.cql_param_map.items():
            self.context[mapped] = params[name]
        result: object = None
        for name, node in self.library.items():
            result = _execute(node, self.context)
            self.context[name] = result
        return result

    def replace_parameters(self, expression: str) -> str:
        """Java: ExpressionProcessor#replaceParameters, including the type-map key quirk."""
        clean = expression
        for match in re.finditer(r"#([dlbs]?)\{(.+?)\}", expression):
            key, type_key, param = match.group(0, 1, 2)
            cql_param = param.replace(" ", "_")
            if (
                cql_param in self.cql_param_map.values()
                and self.cql_param_map.get(param) != cql_param
            ):
                raise ValueError(f"value already present: {cql_param}")
            self.cql_param_map[param] = cql_param
            if type_key:
                self.param_type_map[cql_param] = {
                    "d": "Decimal",
                    "l": "List<Decimal>",
                    "b": "Boolean",
                    "s": "String",
                }[type_key]
            clean = clean.replace(key, cql_param)
        return clean

    def convert_parameterized_expression_to_cql(self, expression: str) -> str:
        """Java: ExpressionProcessor#convertParameterizedExpressionToCql(String)."""
        wrapped = "library " + self.LIBRARY_NAME + " version '1'\n"
        for param, cql_param in self.cql_param_map.items():
            wrapped += "\nparameter " + cql_param + " " + self.param_type_map.get(param, "Decimal")
        wrapped += "\n\ncontext Unfiltered\n\n"
        statements = expression.rstrip("\n").split("\n")
        return (
            wrapped
            + "\n".join(statements[:-1])
            + ("\n" if len(statements) > 1 else "")
            + ("define result: " + statements[-1])
        )
