"""Java: SyncedEnumeratedDistro and Apache Commons Math 3.6.1 sampling.

The WELL19937c recurrence is translated from Apache Commons Math,
licensed under Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0).
Copyright The Apache Software Foundation.
"""

from __future__ import annotations

import math
from threading import Lock
from typing import Protocol

from synthea.javacompat.numbers import to_int32


class LongRandomSource(Protocol):
    """Java: Person#randLong, the only Person operation required here."""

    def rand_long(self) -> int:
        """Java: Person#randLong()."""
        ...


class _Well19937c:
    """Java: Apache Commons Math AbstractWell and Well19937c (long seed)."""

    def __init__(self, seed: int) -> None:
        """Java: AbstractWell#setSeed(long); preserve signed expansion shifts."""
        self.v = [(seed >> 32) & 0xFFFFFFFF, seed & 0xFFFFFFFF] + [0] * 622
        for i in range(2, 624):
            previous = to_int32(self.v[i - 2])
            self.v[i] = (1812433253 * (previous ^ (previous >> 30)) + i) & 0xFFFFFFFF
        self.index = 0

    def next(self, bits: int) -> int:
        """Java: Well19937c#next(int)."""
        i, v = self.index, self.v
        rm1, rm2 = (i - 1) % 624, (i - 2) % 624
        v0, vm1, vm2, vm3 = v[i], v[(i + 70) % 624], v[(i + 179) % 624], v[(i + 449) % 624]
        z0 = (0x80000000 & v[rm1]) ^ (0x7FFFFFFF & v[rm2])
        z1 = (v0 ^ (v0 << 25) ^ vm1 ^ (vm1 >> 27)) & 0xFFFFFFFF
        z2 = (vm2 >> 9) ^ vm3 ^ (vm3 >> 1)
        z3 = z1 ^ z2
        z4 = (z0 ^ z1 ^ (z1 << 9) ^ z2 ^ (z2 << 21) ^ z3 ^ (z3 >> 21)) & 0xFFFFFFFF
        v[i], v[rm1], v[rm2] = z3, z4, v[rm2] & 0x80000000
        self.index = rm1
        z4 ^= (z4 << 7) & 0xE46E1700
        z4 ^= (z4 << 15) & 0x9B868000
        return z4 >> (32 - bits)

    def next_double(self) -> float:
        """Java: BitsStreamGenerator#nextDouble (52 bits, not JavaRandom's 53)."""
        return ((self.next(26) << 26) | self.next(26)) * 2.0**-52


class SyncedEnumeratedDistro[T]:
    """Java: org.mitre.synthea.helpers.SyncedEnumeratedDistro."""

    def __init__(self, pmf: list[tuple[T, float]]) -> None:
        """Java: EnumeratedDistribution#EnumeratedDistribution(List<Pair<T,Double>>)."""
        self.pmf = list(pmf)
        total = 0.0
        for _, weight in pmf:
            if not math.isfinite(weight) or weight < 0:
                raise ValueError("probabilities must be nonnegative finite numbers")
            total += weight
        if total == 0:
            raise ValueError("probability sum must be positive")
        self.cumulative: list[float] = []
        cumulative = 0.0
        for _, weight in pmf:
            cumulative += weight * 1.0 / total
            self.cumulative.append(cumulative)
        self._lock = Lock()

    def synced_reseeded_sample(self, person: LongRandomSource) -> T:
        """Java: SyncedEnumeratedDistro#syncedReseededSample(Person)."""
        with self._lock:
            draw = _Well19937c(person.rand_long()).next_double()
            low, high = 0, len(self.cumulative) - 1
            while low <= high:
                middle = (low + high) >> 1
                if self.cumulative[middle] < draw:
                    low = middle + 1
                elif self.cumulative[middle] > draw:
                    high = middle - 1
                else:
                    low = middle
                    break
            if low < len(self.pmf) and draw < self.cumulative[low]:
                return self.pmf[low][0]
            return self.pmf[-1][0]
