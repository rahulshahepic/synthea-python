"""``String.format`` for the conversions Synthea uses.

Java: ``java.lang.String#format(java.util.Locale, String, Object...)`` with
``java.util.Locale.US`` (JDK 21), i.e. ``java.util.Formatter`` semantics.

Python's ``%`` operator and f-strings differ from Java in rounding (%f rounds
the exact binary value, Java rounds the shortest decimal representation,
HALF_UP), grouping, and special-value handling, so the format string is
parsed and rendered here from scratch.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Context, Decimal, localcontext

from synthea.javacompat import bigdecimal
from synthea.javacompat.numbers import double_to_string

_DIGITS = "0123456789"
# High precision so quantize never rounds beyond the requested digits.
_CTX = Context(prec=200)


@dataclass
class _Spec:
    """One parsed format specifier: ``%[arg_index$][flags][width][.precision]conversion``."""

    flags: set[str] = field(default_factory=set)
    width: int | None = None
    precision: int | None = None
    conversion: str = ""
    arg_index: int | None = None  # 1-based, from %<n>$
    reuse_last: bool = False  # %< reuses the previous argument


def _parse_spec(pattern: str, start: int) -> tuple[_Spec, int]:
    """Parse a specifier beginning just after ``%``; return (spec, index past its end)."""
    result = _Spec()
    i = start
    if i < len(pattern) and pattern[i] == "<":
        result.reuse_last = True
        i += 1
    else:
        j = i
        while j < len(pattern) and pattern[j] in _DIGITS:
            j += 1
        if j > i and j < len(pattern) and pattern[j] == "$":
            result.arg_index = int(pattern[i:j])
            i = j + 1
    while i < len(pattern) and pattern[i] in "-+ 0,(#":
        result.flags.add(pattern[i])
        i += 1
    j = i
    while j < len(pattern) and pattern[j] in _DIGITS:
        j += 1
    if j > i:
        result.width = int(pattern[i:j])
        i = j
    if i < len(pattern) and pattern[i] == ".":
        i += 1
        j = i
        while j < len(pattern) and pattern[j] in _DIGITS:
            j += 1
        if j == i:
            raise ValueError(f"Invalid format specifier in: {pattern!r}")
        result.precision = int(pattern[i:j])
        i = j
    if i >= len(pattern):
        raise ValueError("Format specifier ends prematurely")
    result.conversion = pattern[i]
    return result, i + 1


def _sign_parts(negative: bool, spec: _Spec) -> tuple[str, str]:
    """(prefix, suffix) for the sign per the ``+``, space and ``(`` flags."""
    if negative:
        if "(" in spec.flags:
            return "(", ")"
        return "-", ""
    if "+" in spec.flags:
        return "+", ""
    if " " in spec.flags:
        return " ", ""
    return "", ""


def _render(prefix: str, body: str, suffix: str, spec: _Spec, *, zero_ok: bool = True) -> str:
    """Assemble sign + body + suffix and apply width / justification / zero padding."""
    text = prefix + body + suffix
    if spec.width is None or len(text) >= spec.width:
        return text
    missing = spec.width - len(text)
    if "-" in spec.flags:
        return text + " " * missing
    if zero_ok and "0" in spec.flags:
        return prefix + "0" * missing + body + suffix
    return " " * missing + text


def _format_int(value: int, spec: _Spec) -> str:
    if spec.precision is not None:
        raise ValueError("Precision not allowed for %d")
    prefix, suffix = _sign_parts(value < 0, spec)
    digits = f"{abs(value):,}" if "," in spec.flags else str(abs(value))
    return _render(prefix, digits, suffix, spec)


def _round_shortest(value: float, precision: int) -> Decimal:
    """Round ``|value|`` to ``precision`` fraction digits, HALF_UP on the shortest repr.

    Java: ``java.util.Formatter`` rounds the decimal digits of
    ``Double.toString(x)``, so 0.125 -> 0.13, 1.005 -> 1.01, 2.675 -> 2.68 at
    precision 2, unlike Python's binary-exact float formatting.
    """
    d = Decimal(repr(abs(value)))
    quantum = Decimal((0, (1,), -precision))
    with localcontext(_CTX):
        return d.quantize(quantum, rounding="ROUND_HALF_UP")


def _special_float(value: float, spec: _Spec) -> str | None:
    """Render NaN / Infinity, or return None for finite values.

    Java: ``java.util.Formatter`` — NaN ignores sign flags and zero padding;
    Infinity honours ``+``, space and ``(`` but is padded with spaces.
    """
    if math.isnan(value):
        return _render("", "NaN", "", spec, zero_ok=False)
    if math.isinf(value):
        prefix, suffix = _sign_parts(value < 0, spec)
        return _render(prefix, "Infinity", suffix, spec, zero_ok=False)
    return None


def _format_float(value: float, spec: _Spec) -> str:
    special = _special_float(value, spec)
    if special is not None:
        return special
    precision = 6 if spec.precision is None else spec.precision
    rounded = _round_shortest(value, precision)
    digits = "".join(str(x) for x in rounded.as_tuple().digits) or "0"
    if precision == 0:
        body = digits
    else:
        if len(digits) <= precision:
            digits = "0" * (precision - len(digits) + 1) + digits
        body = f"{digits[:-precision]}.{digits[-precision:]}"
    if "," in spec.flags:
        int_part, dot, frac = body.partition(".")
        body = f"{int(int_part):,}" + dot + frac
    prefix, suffix = _sign_parts(math.copysign(1.0, value) < 0, spec)
    return _render(prefix, body, suffix, spec)


def _format_scientific(value: float, spec: _Spec) -> str:
    special = _special_float(value, spec)
    if special is not None:
        return special
    precision = 6 if spec.precision is None else spec.precision
    if value == 0.0:
        mantissa_digits = "0" * (precision + 1)
        exponent = 0
    else:
        d = Decimal(repr(abs(value)))
        quantum = Decimal((0, (1,), -precision + d.adjusted()))
        with localcontext(_CTX):
            rounded = d.quantize(quantum, rounding="ROUND_HALF_UP")
        digits = "".join(str(x) for x in rounded.as_tuple().digits)
        exponent = rounded.adjusted()
        mantissa_digits = (digits + "0" * (precision + 1))[: precision + 1]
    mantissa = (
        mantissa_digits[0] if precision == 0 else f"{mantissa_digits[0]}.{mantissa_digits[1:]}"
    )
    exp_sign = "+" if exponent >= 0 else "-"
    body = f"{mantissa}e{exp_sign}{abs(exponent):02d}"
    prefix, suffix = _sign_parts(math.copysign(1.0, value) < 0, spec)
    return _render(prefix, body, suffix, spec)


def _format_hex(value: int, spec: _Spec) -> str:
    if spec.precision is not None:
        raise ValueError("Precision not allowed for %x")
    if value < 0:
        # Java %x renders the unsigned two's-complement form, and the width is
        # the argument type's width: Integer -> 32 bits, Long -> 64 bits.
        # Python ints are unbounded, so the type is inferred from the value's
        # range: values inside int range are treated as Integer, the rest as
        # Long (documented in PORTING_NOTES).
        mask = 0xFFFFFFFF if -(2**31) <= value < 2**31 else 0xFFFFFFFFFFFFFFFF
        value &= mask
    digits = f"{value:x}"
    if "#" in spec.flags:
        digits = "0x" + digits
    return _render("", digits, "", spec)


def _string_value(arg: object) -> str:
    """Java: ``String.valueOf(Object)`` as used by ``Formatter`` for ``%s``."""
    if arg is None:
        return "null"
    if isinstance(arg, bool):
        return "true" if arg else "false"
    if isinstance(arg, float):
        return double_to_string(arg)
    if isinstance(arg, Decimal):
        return bigdecimal.to_string(arg)
    return str(arg)


def _convert(spec: _Spec, arg: object) -> str:
    conversion = spec.conversion
    if conversion == "s":
        text = _string_value(arg)
        if spec.precision is not None:
            text = text[: spec.precision]
        return _render("", text, "", spec, zero_ok=False)
    if conversion == "d":
        if isinstance(arg, Decimal) and arg == arg.to_integral_value():
            arg = int(arg)
        if isinstance(arg, bool) or not isinstance(arg, int):
            raise ValueError(f"%d requires an int argument, got {type(arg).__name__}")
        return _format_int(arg, spec)
    if conversion == "f":
        if isinstance(arg, bool) or not isinstance(arg, float | int):
            raise ValueError(f"%f requires a numeric argument, got {type(arg).__name__}")
        return _format_float(float(arg), spec)
    if conversion == "e":
        if isinstance(arg, bool) or not isinstance(arg, float | int):
            raise ValueError(f"%e requires a numeric argument, got {type(arg).__name__}")
        return _format_scientific(float(arg), spec)
    if conversion == "x":
        if isinstance(arg, bool) or not isinstance(arg, int):
            raise ValueError(f"%x requires an int argument, got {type(arg).__name__}")
        return _format_hex(arg, spec)
    raise ValueError(f"Unsupported conversion: %{conversion}")


def format(pattern: str, *args: object) -> str:
    """Java: ``java.lang.String#format(java.util.Locale, String, Object...)`` with Locale.US.

    Implements the conversions used in the Synthea codebase — ``%s %d %f %e %x
    %n %%`` — with Java's flags (``-``, ``+``, space, ``0``, ``,``, ``(``,
    ``#``), width, precision, explicit argument indexes (``%2$s``) and
    argument reuse (``%<s``).

    ``%f`` and ``%e`` round HALF_UP on the decimal digits of the shortest
    representation of the double. ``%x`` on a negative value renders the
    unsigned two's-complement form, 32-bit when the value fits a Java ``int``
    and 64-bit otherwise. Unsupported conversions and argument type
    mismatches raise ``ValueError`` (Java: ``IllegalFormatException`` and
    friends).
    """
    out: list[str] = []
    i = 0
    ordinary_index = 0
    last_arg: object = None
    have_last = False
    while i < len(pattern):
        if pattern[i] != "%":
            out.append(pattern[i])
            i += 1
            continue
        if i + 1 >= len(pattern):
            raise ValueError("Format string ends with a bare %")
        spec, i = _parse_spec(pattern, i + 1)
        if spec.conversion == "%":
            out.append("%")
            continue
        if spec.conversion == "n":
            out.append("\n")
            continue
        if spec.reuse_last:
            if not have_last:
                raise ValueError("%< used with no previous argument")
            arg = last_arg
        elif spec.arg_index is not None:
            if not 1 <= spec.arg_index <= len(args):
                raise ValueError(f"Argument index out of range: {spec.arg_index}")
            arg = args[spec.arg_index - 1]
        else:
            if ordinary_index >= len(args):
                raise ValueError("Missing format argument")
            arg = args[ordinary_index]
            ordinary_index += 1
        last_arg = arg
        have_last = True
        out.append(_convert(spec, arg))
    return "".join(out)
