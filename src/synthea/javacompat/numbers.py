"""Java numeric primitives: overflow wrapping, casts, parsing and ``toString``.

Java: ``java.lang.Integer``, ``java.lang.Long``, ``java.lang.Double``, ``java.lang.Float``,
``java.lang.Math`` and ``java.lang.Boolean`` numeric semantics (JDK 21).

Python ints are unbounded and Python floats are IEEE-754 doubles, so every place Java
silently wraps, truncates or saturates has to be done explicitly here.
"""

from __future__ import annotations

import math
import re
import struct
from fractions import Fraction
from functools import cache

_INT32_MIN = -(2**31)
_INT32_MAX = 2**31 - 1
_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1

# Java decimal floating-point literal grammar (after sign and suffix are removed):
#   Digits [. [Digits]] [Exponent]  |  . Digits [Exponent]
_DOUBLE_LITERAL = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")

# Java Double.toString notation thresholds (JDK 19+ FloatingDecimal semantics):
# plain notation iff 10^-3 <= |x| < 10^7.
_PLAIN_MIN_EXP = -3  # smallest decimal exponent still printed in plain notation
_PLAIN_MAX_EXP = 7  # decimal exponents >= 7 switch to scientific notation


def to_int32(x: int) -> int:
    """Wrap an integer to Java ``int`` range (two's complement).

    Java: silent overflow of ``int`` arithmetic (JLS 4.2.2).
    """
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x >= 0x80000000 else x


def to_int64(x: int) -> int:
    """Wrap an integer to Java ``long`` range (two's complement).

    Java: silent overflow of ``long`` arithmetic (JLS 4.2.2).
    """
    x &= 0xFFFFFFFFFFFFFFFF
    return x - 0x10000000000000000 if x >= 0x8000000000000000 else x


def idiv(a: int, b: int) -> int:
    """Integer division truncating toward zero.

    Java: ``/`` on integral types (JLS 15.17.2). Raises ``ZeroDivisionError``
    where Java throws ``ArithmeticException``.
    """
    if b == 0:
        raise ZeroDivisionError("/ by zero")
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def irem(a: int, b: int) -> int:
    """Integer remainder; the result takes the sign of the dividend.

    Java: ``%`` on integral types (JLS 15.17.3).
    """
    if b == 0:
        raise ZeroDivisionError("/ by zero")
    return a - idiv(a, b) * b


def floor_div(a: int, b: int) -> int:
    """Java: ``java.lang.Math#floorDiv(int, int)`` (and the ``long`` overload)."""
    if b == 0:
        raise ZeroDivisionError("/ by zero")
    q = idiv(a, b)
    if (a ^ b) < 0 and irem(a, b) != 0:
        q -= 1
    return q


def floor_mod(a: int, b: int) -> int:
    """Java: ``java.lang.Math#floorMod(int, int)`` (and the ``long`` overload)."""
    if b == 0:
        raise ZeroDivisionError("/ by zero")
    return a - floor_div(a, b) * b


def d2i(x: float) -> int:
    """Cast a double to ``int``: truncate toward zero, saturate, NaN becomes 0.

    Java: narrowing primitive conversion ``(int) someDouble`` (JLS 5.1.3).
    """
    if math.isnan(x):
        return 0
    if x >= 2147483648.0:  # 2^31: anything >= this saturates to Integer.MAX_VALUE
        return _INT32_MAX
    if x <= -2147483649.0:  # anything <= -(2^31)-1 saturates to Integer.MIN_VALUE
        return _INT32_MIN
    return int(x)  # Python int() on a float truncates toward zero


def d2l(x: float) -> int:
    """Cast a double to ``long``: truncate toward zero, saturate, NaN becomes 0.

    Java: narrowing primitive conversion ``(long) someDouble`` (JLS 5.1.3).
    """
    if math.isnan(x):
        return 0
    if x >= 9223372036854775808.0:  # 2^63
        return _INT64_MAX
    if x <= -9223372036854775808.0:  # -2^63 itself converts exactly
        return _INT64_MIN
    return int(x)


def _round_half_up_long(x: float) -> int:
    """``Math.round(double)`` core: ``floor(x + 0.5)`` with saturation.

    The addition is done on the exact value: evaluated in double arithmetic,
    ``0.49999999999999994 + 0.5`` rounds to exactly 1.0 and would give 1,
    while the JDK (which rounds the exact sum) gives 0.
    """
    if math.isnan(x):
        return 0
    if x >= 9223372036854775808.0:
        return _INT64_MAX
    if x <= -9223372036854775808.0:
        return _INT64_MIN
    return math.floor(Fraction(x) + Fraction(1, 2))


def math_round(x: float) -> int:
    """Java: ``java.lang.Math#round(double)`` — returns a ``long``.

    Equivalent to ``floor(x + 0.5)``; NaN rounds to 0 and out-of-range values
    saturate to ``Long.MAX_VALUE`` / ``Long.MIN_VALUE``.
    """
    return _round_half_up_long(x)


def math_round_float(x: float) -> int:
    """Java: ``java.lang.Math#round(float)`` — returns an ``int``.

    The argument is first rounded to float32, exactly as a Java ``float``
    argument would already be one.
    """
    x = struct.unpack("f", struct.pack("f", x))[0]
    if math.isnan(x):
        return 0
    if x >= 2147483648.0:
        return _INT32_MAX
    if x <= -2147483648.0:
        return _INT32_MIN
    return math.floor(Fraction(x) + Fraction(1, 2))


def _parse_integral(s: str, bits: int) -> int:
    """Shared body of ``Integer.parseInt`` / ``Long.parseLong`` (radix 10)."""
    if not s:
        raise ValueError(f'For input string: "{s}"')
    lo, hi = (_INT32_MIN, _INT32_MAX) if bits == 32 else (_INT64_MIN, _INT64_MAX)
    body = s
    negative = False
    if body[0] in "+-":
        negative = body[0] == "-"
        body = body[1:]
    if not body or any(c < "0" or c > "9" for c in body):
        raise ValueError(f'For input string: "{s}"')
    value = int(body)
    if negative:
        value = -value
    if value < lo or value > hi:
        raise ValueError(f'For input string: "{s}"')
    return value


def parse_int(s: str) -> int:
    """Java: ``java.lang.Integer#parseInt(String)``.

    Raises ``ValueError`` where Java throws ``NumberFormatException``.
    """
    return _parse_integral(s, 32)


def parse_long(s: str) -> int:
    """Java: ``java.lang.Long#parseLong(String)``.

    Raises ``ValueError`` where Java throws ``NumberFormatException``.
    """
    return _parse_integral(s, 64)


def parse_double(s: str) -> float:
    """Java: ``java.lang.Double#parseDouble(String)``.

    Leading/trailing whitespace (chars <= U+0020) is trimmed; an optional sign
    may precede ``NaN`` / ``Infinity``; a trailing ``d``/``D``/``f``/``F`` type
    suffix is accepted. Hexadecimal floating-point literals are not supported
    here (Synthea never produces them). Raises ``ValueError`` where Java throws
    ``NumberFormatException``.
    """
    # String.trim() semantics: remove leading/trailing chars <= U+0020.
    lo, hi = 0, len(s)
    while lo < hi and ord(s[lo]) <= 0x20:
        lo += 1
    while hi > lo and ord(s[hi - 1]) <= 0x20:
        hi -= 1
    t = s[lo:hi]
    if not t:
        raise ValueError(f'For input string: "{s}"')
    body = t
    if body[-1] in "dDfF":
        body = body[:-1]
    sign = 1.0
    core = body
    if core[:1] in ("+", "-"):
        if core[0] == "-":
            sign = -1.0
        core = core[1:]
    if core == "NaN":
        return math.nan
    if core == "Infinity":
        return math.copysign(math.inf, sign)
    if _DOUBLE_LITERAL.fullmatch(core) is None:
        raise ValueError(f'For input string: "{s}"')
    return sign * float(core)


def parse_boolean(s: str) -> bool:
    """Java: ``java.lang.Boolean#parseBoolean(String)``.

    True only when the string equals ``"true"`` ignoring case; never throws.
    """
    return s.lower() == "true"


def _s64(n: int) -> int:
    """Wrap an integer to a Java ``long`` (signed 64-bit, two's complement)."""
    n &= 0xFFFFFFFFFFFFFFFF
    return n - 0x10000000000000000 if n >= 0x8000000000000000 else n


def _multiply_high(a: int, b: int) -> int:
    """Java: ``java.lang.Math#multiplyHigh(long, long)`` — high 64 bits of the product."""
    return _s64((a * b) >> 64)


# --- Schubfach digit generation (JDK 21 jdk.internal.math.DoubleToDecimal /
#     FloatToDecimal / MathUtils), ported operation for operation. -------------

_C_10 = 661_971_961_083  # MathUtils: floor(log10(2) * 2^41)
_A_10 = -274_743_187_321  # MathUtils: floor(log10(3/4) * 2^41)
_C_2 = 913_124_641_741  # MathUtils: floor(log2(10) * 2^38)


def _flog10pow2(e: int) -> int:
    """MathUtils.flog10pow2: floor(log10(2^e))."""
    return (e * _C_10) >> 41


def _flog10three_quarters_pow2(e: int) -> int:
    """MathUtils.flog10threeQuartersPow2: floor(log10(3/4 * 2^e))."""
    return (e * _C_10 + _A_10) >> 41


def _flog2pow10(e: int) -> int:
    """MathUtils.flog2pow10: floor(log2(10^e))."""
    return (e * _C_2) >> 38


@cache
def _g_pair(k: int) -> tuple[int, int]:
    """MathUtils.g1(k), g0(k): the 126-bit constant g = floor(beta) + 1 split in halves.

    Defined by 10^-k = beta * 2^r with 2^125 <= beta < 2^126 and
    r = flog2pow10(-k) - 125. Computed exactly; verified against the JDK's
    precomputed table for every k in [-324, 292] (all 617 entries match).
    """
    r = _flog2pow10(-k) - 125
    beta = Fraction(10) ** (-k) * Fraction(2) ** (-r)
    g = beta.numerator // beta.denominator + 1
    g1 = g >> 63
    return g1, g - (g1 << 63)


def _rop_double(g1: int, g0: int, cp: int) -> int:
    """DoubleToDecimal.rop: round(cp * g * 2^-127) in 64-bit fixed point."""
    x1 = _multiply_high(g0, cp)
    y0 = _s64(g1 * cp)
    y1 = _multiply_high(g1, cp)
    z = _s64((y0 & 0xFFFFFFFFFFFFFFFF) >> 1) + x1
    z = _s64(z)
    vbp = _s64(y1 + ((z & 0xFFFFFFFFFFFFFFFF) >> 63))
    tail = ((z & 0x7FFFFFFFFFFFFFFF) + 0x7FFFFFFFFFFFFFFF) & 0xFFFFFFFFFFFFFFFF
    return _s64(vbp | (tail >> 63))


def _to_chars_result(f: int, e: int) -> tuple[str, int]:
    """Convert a Schubfach (f, e) pair (value = f * 10^e) to (digits, exp10)."""
    digits = str(f)
    return digits.rstrip("0") or "0", e + len(digits)


def _schubfach_double(q: int, c: int, dk: int, c_min: int) -> tuple[str, int]:
    """DoubleToDecimal.toDecimal(q, c, dk): choose between s and s+1 at scale k."""
    out = c & 0x1
    cb = c << 2
    cbr = cb + 2
    if c != c_min or q == -1074:  # regular spacing (Q_MIN = -1074)
        cbl = cb - 2
        k = _flog10pow2(q)
    else:  # irregular spacing: significand at the bottom of a binade
        cbl = cb - 1
        k = _flog10three_quarters_pow2(q)
    h = q + _flog2pow10(-k) + 2
    g1, g0 = _g_pair(k)
    vb = _rop_double(g1, g0, _s64(cb << (h & 63)))
    vbl = _rop_double(g1, g0, _s64(cbl << (h & 63)))
    vbr = _rop_double(g1, g0, _s64(cbr << (h & 63)))
    s = vb >> 2
    if s >= 100:
        # Prefer a multiple of 10 (fewer digits after zero-trimming) if exactly
        # one of the two surrounding multiples lies in the interval.
        sp10 = 10 * _multiply_high(s, _s64(115_292_150_460_684_698 << 4))
        tp10 = sp10 + 10
        upin = _s64(vbl + out) <= _s64(sp10 << 2)
        wpin = _s64(_s64(tp10 << 2) + out) <= vbr
        if upin != wpin:
            return _to_chars_result(sp10 if upin else tp10, k)
    t = s + 1
    uin = _s64(vbl + out) <= _s64(s << 2)
    win = _s64(_s64(t << 2) + out) <= vbr
    if uin != win:
        return _to_chars_result(s if uin else t, k + dk)
    cmp_ = vb - ((s + t) << 1)
    return _to_chars_result(s if (cmp_ < 0 or (cmp_ == 0 and (s & 0x1) == 0)) else t, k + dk)


def _shortest_digits_double(x: float) -> tuple[str, int]:
    """(digits, exp10) of a finite nonzero double, per jdk.internal.math.DoubleToDecimal."""
    bits = struct.unpack("Q", struct.pack("d", abs(x)))[0]
    t = bits & ((1 << 52) - 1)
    bq = (bits >> 52) & 0x7FF
    if bq != 0:  # normal: |x| = c * 2^-mq with c in [2^52, 2^53)
        mq = 1075 - bq
        c = (1 << 52) | t
        if 0 < mq < 53:  # fast path: the value is a small integer
            f = c >> mq
            if f << mq == c:
                return _to_chars_result(f, 0)
        return _schubfach_double(-mq, c, 0, 1 << 52)
    # subnormal: |x| = t * 2^-1074; tiny significands are scaled by 10 (C_TINY = 3)
    if t < 3:
        return _schubfach_double(-1074, 10 * t, -1, 1 << 52)
    return _schubfach_double(-1074, t, 0, 1 << 52)


def _rop_float(g: int, cp: int) -> int:
    """FloatToDecimal.rop: round(cp * g * 2^-95), returned as a Java ``int``."""
    x1 = _multiply_high(g, cp)
    vbp = (x1 & 0xFFFFFFFFFFFFFFFF) >> 31
    tail = ((x1 & 0xFFFFFFFF) + 0xFFFFFFFF) & 0xFFFFFFFFFFFFFFFF
    return _to_int32_java(vbp | (tail >> 32))


def _to_int32_java(n: int) -> int:
    n &= 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def _schubfach_float(q: int, c: int, dk: int) -> tuple[str, int]:
    """FloatToDecimal.toDecimal(q, c, dk): choose between s and s+1 at scale k."""
    out = c & 0x1
    cb = c << 2
    cbr = cb + 2
    if c != (1 << 23) or q == -149:  # regular spacing (Q_MIN = -149)
        cbl = cb - 2
        k = _flog10pow2(q)
    else:  # irregular spacing
        cbl = cb - 1
        k = _flog10three_quarters_pow2(q)
    h = q + _flog2pow10(-k) + 33
    g = _g_pair(k)[0] + 1
    vb = _rop_float(g, _s64(cb << (h & 63)))
    vbl = _rop_float(g, _s64(cbl << (h & 63)))
    vbr = _rop_float(g, _s64(cbr << (h & 63)))
    s = vb >> 2
    if s >= 100:
        sp10 = _to_int32_java(10 * _to_int32_java((s * 1_717_986_919 & 0xFFFFFFFFFFFFFFFF) >> 34))
        tp10 = _to_int32_java(sp10 + 10)
        upin = _to_int32_java(vbl + out) <= _to_int32_java(sp10 << 2)
        wpin = _to_int32_java(_to_int32_java(tp10 << 2) + out) <= vbr
        if upin != wpin:
            return _to_chars_result(sp10 if upin else tp10, k)
    t = s + 1
    uin = _to_int32_java(vbl + out) <= _to_int32_java(s << 2)
    win = _to_int32_java(_to_int32_java(t << 2) + out) <= vbr
    if uin != win:
        return _to_chars_result(s if uin else t, k + dk)
    cmp_ = vb - ((s + t) << 1)
    return _to_chars_result(s if (cmp_ < 0 or (cmp_ == 0 and (s & 0x1) == 0)) else t, k + dk)


def _shortest_digits_float(x: float) -> tuple[str, int]:
    """(digits, exp10) of a finite nonzero float32, per jdk.internal.math.FloatToDecimal.

    ``x`` is a Python float holding an exact float32 value.
    """
    bits = struct.unpack("I", struct.pack("f", abs(x)))[0]
    t = bits & ((1 << 23) - 1)
    bq = (bits >> 23) & 0xFF
    if bq != 0:  # normal: |x| = c * 2^-mq with c in [2^23, 2^24)
        mq = 150 - bq
        c = (1 << 23) | t
        if 0 < mq < 24:  # fast path: the value is a small integer
            f = c >> mq
            if f << mq == c:
                return _to_chars_result(f, 0)
        return _schubfach_float(-mq, c, 0)
    # subnormal: |x| = t * 2^-149; tiny significands are scaled by 10 (C_TINY = 8)
    if t < 8:
        return _schubfach_float(-149, 10 * t, -1)
    return _schubfach_float(-149, t, 0)


def _render_java_style(digits: str, exp10: int, negative: bool) -> str:
    """Render shortest digits with Java's plain/scientific notation rules."""
    sign = "-" if negative else ""
    n = len(digits)
    if _PLAIN_MIN_EXP <= exp10 - 1 < _PLAIN_MAX_EXP:
        if exp10 >= n:
            return f"{sign}{digits}{'0' * (exp10 - n)}.0"
        if exp10 > 0:
            return f"{sign}{digits[:exp10]}.{digits[exp10:]}"
        return f"{sign}0.{'0' * (-exp10)}{digits}"
    fraction = digits[1:] if n > 1 else "0"
    return f"{sign}{digits[0]}.{fraction}E{exp10 - 1}"


def double_to_string(x: float) -> str:
    """Java: ``java.lang.Double#toString(double)`` (JDK 21 semantics).

    Shortest digits that round-trip, produced by a port of the JDK's own
    Schubfach algorithm (``jdk.internal.math.DoubleToDecimal``); plain
    notation iff ``10^-3 <= |x| < 10^7`` (always with at least one digit
    after the point), otherwise scientific notation like ``1.0E10`` /
    ``1.23E-5``.
    """
    if math.isnan(x):
        return "NaN"
    if math.isinf(x):
        return "-Infinity" if x < 0 else "Infinity"
    if x == 0.0:
        return "-0.0" if math.copysign(1.0, x) < 0 else "0.0"
    digits, exp10 = _shortest_digits_double(x)
    return _render_java_style(digits, exp10, x < 0)


def float_to_string(x: float) -> str:
    """Java: ``java.lang.Float#toString(float)`` (JDK 21 semantics).

    The value is rounded to float32 first; the digits are produced by a port
    of the JDK's Schubfach algorithm (``jdk.internal.math.FloatToDecimal``),
    rendered with the same notation rules as :func:`double_to_string`.
    """
    x = struct.unpack("f", struct.pack("f", x))[0]
    if math.isnan(x):
        return "NaN"
    if math.isinf(x):
        return "-Infinity" if x < 0 else "Infinity"
    if x == 0.0:
        return "-0.0" if math.copysign(1.0, x) < 0 else "0.0"
    digits, exp10 = _shortest_digits_float(x)
    return _render_java_style(digits, exp10, x < 0)
