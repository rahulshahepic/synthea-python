"""Bit-exact java.util.Random implementation (JDK 21 legacy LCG)."""

from __future__ import annotations

import math


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
        multiplier = math.sqrt(-2 * math.log(s) / s)
        self._next_gaussian = v2 * multiplier
        self._have_next_gaussian = True
        return v1 * multiplier
