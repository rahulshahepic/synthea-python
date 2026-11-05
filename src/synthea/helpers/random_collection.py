"""Weighted random collection matching Java RandomCollection.java."""

from __future__ import annotations

from bisect import bisect_right
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator


class RandomCollection[E]:
    """Java: org.mitre.synthea.helpers.RandomCollection."""

    def __init__(self) -> None:
        """Java: RandomCollection#RandomCollection()."""
        self.map: dict[float, E] = {}
        self.total: float = 0.0

    def add(self, weight: float, result: E) -> None:
        """Java: RandomCollection#add(double, E)."""
        if weight <= 0:
            return
        self.total += weight
        self.map[self.total] = result

    def add_all(self, other: RandomCollection[E]) -> None:
        """Java: RandomCollection#addAll(RandomCollection)."""
        weight_adj = 0.0
        for cumulative_weight in sorted(other.map):
            self.add(cumulative_weight - weight_adj, other.map[cumulative_weight])
            weight_adj = cumulative_weight

    def next(self, random_or_value: RandomNumberGenerator | float) -> E:
        """Java: RandomCollection#next(RandomNumberGenerator), next(double)."""
        if isinstance(random_or_value, (float, int)):
            value = float(random_or_value)
        else:
            value = random_or_value.rand() * self.total
        keys = sorted(self.map)
        index = bisect_right(keys, value)
        if index == len(keys):
            index -= 1
        return self.map[keys[index]]
