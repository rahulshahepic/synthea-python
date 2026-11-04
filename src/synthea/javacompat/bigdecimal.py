"""``java.math.BigDecimal`` helpers over :class:`decimal.Decimal`.

Java: ``java.math.BigDecimal`` and ``java.math.RoundingMode`` (JDK 21).

Java BigDecimal scale semantics are reproduced explicitly: Python's Decimal
already stores an exponent (``scale == -exponent``), but its arithmetic follows
the thread context, so every operation here runs under a high-precision local
context and the result's scale is then forced to the exact Java result scale.
"""

from __future__ import annotations

import decimal
import math
from decimal import Decimal
from enum import Enum
from fractions import Fraction

from synthea.javacompat.numbers import double_to_string, to_int32, to_int64

# Precision high enough that Decimal arithmetic in this module is exact for
# any realistic Synthea money value; Java BigDecimal add/subtract/multiply are
# always exact, so the context must never round silently.
_PREC = 200

_ROUNDING_CONSTANTS = {
    "UP": decimal.ROUND_UP,
    "DOWN": decimal.ROUND_DOWN,
    "CEILING": decimal.ROUND_CEILING,
    "FLOOR": decimal.ROUND_FLOOR,
    "HALF_UP": decimal.ROUND_HALF_UP,
    "HALF_DOWN": decimal.ROUND_HALF_DOWN,
    "HALF_EVEN": decimal.ROUND_HALF_EVEN,
}


class RoundingMode(Enum):
    """Java: ``java.math.RoundingMode``."""

    UP = "UP"
    DOWN = "DOWN"
    CEILING = "CEILING"
    FLOOR = "FLOOR"
    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    HALF_EVEN = "HALF_EVEN"
    UNNECESSARY = "UNNECESSARY"

    def decimal_constant(self) -> str:
        """The :mod:`decimal` rounding constant for this mode.

        Raises ``ValueError`` for ``UNNECESSARY`` (Java: ``ArithmeticException``
        if rounding actually occurs; callers check necessity themselves).
        """
        try:
            return _ROUNDING_CONSTANTS[self.name]
        except KeyError:
            raise ValueError("UNNECESSARY has no decimal rounding constant") from None


def _ctx() -> decimal.Context:
    return decimal.Context(prec=_PREC, rounding=decimal.ROUND_HALF_EVEN)


def scale_of(d: Decimal) -> int:
    """Java: ``java.math.BigDecimal#scale()`` — the negated Decimal exponent."""
    exponent = d.as_tuple().exponent
    if not isinstance(exponent, int):  # non-finite values carry a string marker
        raise ValueError("scale is undefined for non-finite values")
    return -exponent


def _positive_zero(d: Decimal) -> Decimal:
    """Strip the sign from a zero Decimal, preserving its scale.

    Java BigDecimal has no negative zero: the unscaled value is a
    ``BigInteger``, and ``BigInteger`` zero is unsigned, so every operation
    that produces zero produces ``0``/``0.00``/``0E+2``, never ``-0``.
    Python Decimals keep a sign on zero, so port results are normalized.
    """
    return d.copy_abs() if d.is_zero() else d


def _with_scale(d: Decimal, scale: int) -> Decimal:
    """Return a Decimal equal to ``d`` whose exponent is exactly ``-scale``.

    The caller guarantees the rescale is exact (only zeros are added or the
    value is zero); no rounding can occur.
    """
    sign, digits, _ = d.as_tuple()
    return _positive_zero(Decimal((sign, digits, -scale)))


# Java: the ``java.math.BigDecimal`` constants ZERO, ONE and TEN (all scale 0).
ZERO = Decimal(0)
ONE = Decimal(1)
TEN = Decimal(10)


def value_of(x: float) -> Decimal:
    """Java: ``java.math.BigDecimal#valueOf(double)``.

    Uses ``Double.toString(x)`` as the intermediate string, so ``value_of(0.1)``
    is the decimal ``0.1``, not the exact binary expansion.
    """
    return _positive_zero(Decimal(double_to_string(x)))


def from_double_exact(x: float) -> Decimal:
    """Java: ``new java.math.BigDecimal(double)`` — the exact binary expansion.

    ``new BigDecimal(0.1)`` is ``0.1000000000000000055511151231257827...``.
    Python's ``Decimal(float)`` constructor is likewise exact.
    """
    with decimal.localcontext(_ctx()):
        return _positive_zero(Decimal(x))


def from_string(s: str) -> Decimal:
    """Java: ``new java.math.BigDecimal(String)``.

    Accepts plain and scientific notation (``"1E+7"``, ``"1.00"``); raises
    ``ValueError`` where Java throws ``NumberFormatException``.
    """
    try:
        d = Decimal(s)
    except decimal.InvalidOperation:
        raise ValueError(f'For input string: "{s}"') from None
    if not d.is_finite():
        raise ValueError(f'For input string: "{s}"')
    return _positive_zero(d)


def set_scale(d: Decimal, scale: int, mode: RoundingMode) -> Decimal:
    """Java: ``java.math.BigDecimal#setScale(int, RoundingMode)``.

    ``scale`` may be negative (rounding to tens, hundreds, ...). With
    ``UNNECESSARY``, raises ``ValueError`` (Java: ``ArithmeticException``)
    when any nonzero digit would be discarded.
    """
    quantum = Decimal((0, (1,), -scale))
    with decimal.localcontext(_ctx()):
        if mode is RoundingMode.UNNECESSARY:
            result = d.quantize(quantum, rounding=decimal.ROUND_DOWN)
            if result != d:
                raise ValueError("Rounding necessary")
            return _positive_zero(result)
        return _positive_zero(d.quantize(quantum, rounding=mode.decimal_constant()))


def _scale_max(a: Decimal, b: Decimal) -> int:
    """The larger of the two operands' scales (``max`` below is BigDecimal's)."""
    sa, sb = scale_of(a), scale_of(b)
    return sa if sa >= sb else sb


def add(a: Decimal, b: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#add(BigDecimal)`` — result scale is max of scales."""
    with decimal.localcontext(_ctx()):
        result = a + b
    return _with_scale(result, _scale_max(a, b))


def subtract(a: Decimal, b: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#subtract(BigDecimal)`` — result scale is max of scales."""
    with decimal.localcontext(_ctx()):
        result = a - b
    return _with_scale(result, _scale_max(a, b))


def multiply(a: Decimal, b: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#multiply(BigDecimal)`` — result scale is the sum of scales."""
    with decimal.localcontext(_ctx()):
        result = a * b
    return _with_scale(result, scale_of(a) + scale_of(b))


def divide(a: Decimal, b: Decimal, scale: int, mode: RoundingMode) -> Decimal:
    """Java: ``java.math.BigDecimal#divide(BigDecimal, int, RoundingMode)``.

    Produces a quotient with exactly ``scale`` digits after the point, rounded
    with ``mode``. With ``UNNECESSARY``, raises ``ValueError`` (Java:
    ``ArithmeticException``) when the exact quotient needs more digits.
    """
    quantum = Decimal((0, (1,), -scale))
    with decimal.localcontext(_ctx()):
        if mode is RoundingMode.UNNECESSARY:
            quotient = (a / b).quantize(quantum, rounding=decimal.ROUND_DOWN)
            if quotient * b != a:
                raise ValueError("Rounding necessary")
            return _positive_zero(quotient)
        return _positive_zero((a / b).quantize(quantum, rounding=mode.decimal_constant()))


def divide_round(a: Decimal, b: Decimal, mode: RoundingMode) -> Decimal:
    """Java: ``java.math.BigDecimal#divide(BigDecimal, RoundingMode)``.

    The result's scale is ``a.scale()``: the quotient is rounded with ``mode``
    at exactly that scale, which is never raised. Division by zero raises
    ``decimal.DivisionByZero`` (Java: ``ArithmeticException``), an
    ``ArithmeticError`` subclass.
    """
    return divide(a, b, scale_of(a), mode)


def divide_exact(a: Decimal, b: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#divide(BigDecimal)`` (no rounding mode).

    The preferred scale is ``a.scale() - b.scale()``; the result is the exact
    quotient at the smallest scale >= the preferred scale that represents it
    exactly. Raises ``ArithmeticError`` (Java: ``ArithmeticException``) when
    the quotient has a non-terminating decimal expansion, or when ``b`` is
    zero. Implemented with exact integer arithmetic (``Fraction``), never
    with Decimal division.
    """
    if b.is_zero():
        raise ArithmeticError("Division by zero")
    preferred = scale_of(a) - scale_of(b)
    if a.is_zero():
        # Zero is representable at any scale; Java returns it at the
        # preferred scale (0.00 / 3 -> 0.00).
        return _with_scale(Decimal(0), preferred)
    quotient = Fraction(a) / Fraction(b)
    if quotient.denominator == 1:
        # An integer quotient: the minimal scale is negative, lowered by the
        # numerator's trailing zeros (100 is representable at scale -2).
        numerator = quotient.numerator
        if numerator < 0:
            numerator = -numerator
        minimal = 0
        while numerator % 10 == 0:
            numerator //= 10
            minimal -= 1
    else:
        rest = quotient.denominator
        twos = 0
        while rest % 2 == 0:
            rest //= 2
            twos += 1
        fives = 0
        while rest % 5 == 0:
            rest //= 5
            fives += 1
        if rest != 1:
            raise ArithmeticError(
                "Non-terminating decimal expansion; no exact representable decimal result."
            )
        minimal = twos if twos >= fives else fives
    scale = minimal if minimal >= preferred else preferred
    unscaled = quotient * Fraction(10) ** scale
    value = unscaled.numerator  # denominator is 1 by construction of `scale`
    sign = 1 if value < 0 else 0
    digits = tuple(int(c) for c in str(-value if value < 0 else value))
    return Decimal((sign, digits, -scale))


def compare_to(a: Decimal, b: Decimal) -> int:
    """Java: ``java.math.BigDecimal#compareTo(BigDecimal)`` — ignores scale.

    ``compareTo(1.0, 1.00)`` is 0 even though the values are not ``equals``.
    """
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def equals(a: Decimal, b: Decimal) -> bool:
    """Java: ``java.math.BigDecimal#equals(Object)`` — scale-sensitive.

    Two BigDecimals are equal only if they have the same value *and* the same
    scale, so ``2.0`` does not equal ``2.00``. A negative zero equals a
    positive zero when the scales match (Java's unscaled value has no sign
    for zero, and Python's Decimal comparison agrees).
    """
    return bool(a == b and scale_of(a) == scale_of(b))


def max(a: Decimal, b: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#max(BigDecimal)``.

    Returns the larger by ``compareTo``; on a tie it returns ``a`` (Java
    returns ``this``), so the winner's scale is the first argument's.
    """
    return a if compare_to(a, b) >= 0 else b


def min(a: Decimal, b: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#min(BigDecimal)``.

    Returns the smaller by ``compareTo``; on a tie it returns ``a`` (Java
    returns ``this``), so the winner's scale is the first argument's.
    """
    return a if compare_to(a, b) <= 0 else b


def abs(d: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#abs()`` — scale preserved, context-free."""
    return d.copy_abs()


def negate(d: Decimal) -> Decimal:
    """Java: ``java.math.BigDecimal#negate()`` — scale preserved, context-free."""
    return _positive_zero(d.copy_negate())


def signum(d: Decimal) -> int:
    """Java: ``java.math.BigDecimal#signum()`` — -1, 0 or 1 (zero is 0)."""
    if d > 0:
        return 1
    if d < 0:
        return -1
    return 0


def double_value(d: Decimal) -> float:
    """Java: ``java.math.BigDecimal#doubleValue()`` — correctly rounded.

    ``float(Fraction)`` rounds to nearest, ties to even, exactly like the
    JDK; an out-of-range magnitude becomes ``Infinity`` with the value's
    sign (Java semantics) instead of propagating ``OverflowError``.
    """
    try:
        return float(Fraction(d))
    except OverflowError:
        return math.inf if d > 0 else -math.inf


def long_value(d: Decimal) -> int:
    """Java: ``java.math.BigDecimal#longValue()``.

    Truncates toward zero, then wraps modulo 2**64 like a Java ``long``
    conversion of an out-of-range ``BigInteger``.
    """
    return to_int64(int(d))


def int_value(d: Decimal) -> int:
    """Java: ``java.math.BigDecimal#intValue()``.

    Truncates toward zero, then wraps modulo 2**32 like a Java ``int``
    conversion of an out-of-range ``BigInteger``.
    """
    return to_int32(int(d))


def _digits_str(d: Decimal) -> str:
    return "".join(str(x) for x in d.as_tuple().digits) or "0"


def _adjusted_exponent(d: Decimal) -> int:
    """Exponent of the value in ``d.dddE<adj>`` form (Java's ``adjustedExponent``)."""
    digits = d.as_tuple().digits
    return scale_of(d) * -1 + (len(digits) - 1) if digits else 0


def to_string(d: Decimal) -> str:
    """Java: ``java.math.BigDecimal#toString()``.

    Scientific notation is used when the scale is negative or the adjusted
    exponent is less than -6; otherwise plain notation. In scientific form the
    exponent carries a sign only when positive (``1E+7``, ``1E-7``).
    """
    # Zero needs no special case: its digit string is "0" and its adjusted
    # exponent is -scale, so new BigDecimal("0.0000000") -> "0E-7" falls out.
    scale = scale_of(d)
    adjusted = _adjusted_exponent(d)
    if scale < 0 or adjusted < -6:
        digits = _digits_str(d)
        sign = "-" if d.as_tuple().sign else ""
        coefficient = digits if len(digits) == 1 else f"{digits[0]}.{digits[1:]}"
        exp_sign = "+" if adjusted >= 0 else ""
        return f"{sign}{coefficient}E{exp_sign}{adjusted}"
    return to_plain_string(d)


def to_plain_string(d: Decimal) -> str:
    """Java: ``java.math.BigDecimal#toPlainString()`` — never scientific."""
    sign = "-" if d.as_tuple().sign else ""
    digits = _digits_str(d)
    scale = scale_of(d)
    if scale <= 0:
        if d.is_zero():
            return f"{sign}0"  # Java pads zeros only for nonzero values
        return f"{sign}{digits}{'0' * (-scale)}"
    if len(digits) > scale:
        return f"{sign}{digits[:-scale]}.{digits[-scale:]}"
    return f"{sign}0.{'0' * (scale - len(digits))}{digits}"
