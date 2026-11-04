"""Bit-exact java.util.Random implementation (JDK 21 legacy LCG)."""

from __future__ import annotations

import math
import struct


# The fdlibm log polynomial is copyright (C) 1993 Sun Microsystems, Inc.
# Permission to use, copy, modify and distribute is freely granted,
# provided that this notice is preserved.
def _strict_log(value: float) -> float:
    """Java: java.lang.StrictMath#log, fdlibm 5.3 e_log.c transliteration."""
    ln2_hi = 6.93147180369123816490e-01
    ln2_lo = 1.90821492927058770002e-10
    lg1 = 6.666666666666735130e-01
    lg2 = 3.999999999940941908e-01
    lg3 = 2.857142874366239149e-01
    lg4 = 2.222219843214978396e-01
    lg5 = 1.818357216161805012e-01
    lg6 = 1.531383769920937332e-01
    lg7 = 1.479819860511658591e-01
    bits = struct.unpack(">Q", struct.pack(">d", value))[0]
    high = bits >> 32
    low = bits & 0xFFFFFFFF
    exponent = 0
    if high < 0x00100000:
        if ((high & 0x7FFFFFFF) | low) == 0:
            return -math.inf
        if high & 0x80000000:
            return math.nan
        exponent -= 54
        value *= 18014398509481984.0
        bits = struct.unpack(">Q", struct.pack(">d", value))[0]
        high = bits >> 32
    if high >= 0x7FF00000:
        return value + value
    exponent += (high >> 20) - 1023
    high &= 0x000FFFFF
    shift = (high + 0x95F64) & 0x100000
    bits = ((high | (shift ^ 0x3FF00000)) << 32) | (bits & 0xFFFFFFFF)
    value = struct.unpack(">d", struct.pack(">Q", bits))[0]
    exponent += shift >> 20
    fraction = value - 1.0
    if (0x000FFFFF & (2 + high)) < 3:
        if fraction == 0.0:
            if exponent == 0:
                return 0.0
            scale = float(exponent)
            return scale * ln2_hi + scale * ln2_lo
        residual = fraction * fraction * (0.5 - 0.33333333333333333 * fraction)
        if exponent == 0:
            return fraction - residual
        scale = float(exponent)
        return scale * ln2_hi - ((residual - scale * ln2_lo) - fraction)
    ratio = fraction / (2.0 + fraction)
    scale = float(exponent)
    square = ratio * ratio
    selector = high - 0x6147A
    fourth = square * square
    complement = 0x6B851 - high
    term1 = fourth * (lg2 + fourth * (lg4 + fourth * lg6))
    term2 = square * (lg1 + fourth * (lg3 + fourth * (lg5 + fourth * lg7)))
    selector |= complement
    residual = term2 + term1
    if selector > 0:
        half_square = 0.5 * fraction * fraction
        if exponent == 0:
            return fraction - (half_square - ratio * (half_square + residual))
        return scale * ln2_hi - (
            (half_square - (ratio * (half_square + residual) + scale * ln2_lo)) - fraction
        )
    if exponent == 0:
        return fraction - ratio * (fraction - residual)
    return scale * ln2_hi - ((ratio * (fraction - residual) - scale * ln2_lo) - fraction)


class JavaRandom:
    """Java: java.util.Random (48-bit linear congruential generator)."""

    _MULTIPLIER = 0x5DEECE66D
    _ADDEND = 0xB
    _MASK = (1 << 48) - 1

    def __init__(self, seed: int) -> None:
        """Java: java.util.Random#Random(long)."""
        self.set_seed(seed)

    def set_seed(self, seed: int) -> None:
        """Java: java.util.Random#setSeed(long), including Gaussian cache reset."""
        self._seed = (seed ^ self._MULTIPLIER) & self._MASK
        self._have_next_gaussian = False
        self._next_gaussian = 0.0

    def next(self, bits: int) -> int:
        """Java: java.util.Random#next(int)."""
        self._seed = (self._seed * self._MULTIPLIER + self._ADDEND) & self._MASK
        return self._seed >> (48 - bits)

    @staticmethod
    def _int32(value: int) -> int:
        """Java: int narrowing conversion (two's-complement wrapping)."""
        value &= 0xFFFFFFFF
        return value if value < (1 << 31) else value - (1 << 32)

    @staticmethod
    def _int64(value: int) -> int:
        """Java: long narrowing conversion (two's-complement wrapping)."""
        value &= 0xFFFFFFFFFFFFFFFF
        return value if value < (1 << 63) else value - (1 << 64)

    def next_int(self, bound: int | None = None) -> int:
        """Java: java.util.Random#nextInt() and #nextInt(int)."""
        if bound is None:
            return self._int32(self.next(32))
        if bound <= 0 or bound > 0x7FFFFFFF:
            raise ValueError("bound must be positive Java int")
        if (bound & -bound) == bound:
            return (bound * self.next(31)) >> 31
        while True:
            bits = self.next(31)
            value = bits % bound
            if self._int32(bits - value + (bound - 1)) >= 0:
                return value

    def next_long(self) -> int:
        """Java: java.util.Random#nextLong (sign-extended low int)."""
        high = self._int32(self.next(32))
        low = self._int32(self.next(32))
        return self._int64((high << 32) + low)

    def next_boolean(self) -> bool:
        """Java: java.util.Random#nextBoolean."""
        return self.next(1) != 0

    def next_double(self) -> float:
        """Java: java.util.Random#nextDouble."""
        return ((self.next(26) << 27) + self.next(27)) / float(1 << 53)

    def next_float(self) -> float:
        """Java: java.util.Random#nextFloat."""
        return self.next(24) / float(1 << 24)

    def next_gaussian(self) -> float:
        """Java: java.util.Random#nextGaussian (cached Marsaglia polar transform)."""
        if self._have_next_gaussian:
            self._have_next_gaussian = False
            return self._next_gaussian
        while True:
            v1 = 2 * self.next_double() - 1
            v2 = 2 * self.next_double() - 1
            s = v1 * v1 + v2 * v2
            if 0 < s < 1:
                break
        multiplier = math.sqrt(-2 * _strict_log(s) / s)
        self._next_gaussian = v2 * multiplier
        self._have_next_gaussian = True
        return v1 * multiplier
