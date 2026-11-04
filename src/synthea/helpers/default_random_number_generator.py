"""DefaultRandomNumberGenerator port from Synthea Java."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import overload

from synthea.helpers.random_number_generator import RandomNumberGeneratorDefaults
from synthea.javacompat.random import JavaRandom
from synthea.javacompat.uuid import java_uuid


class DefaultRandomNumberGenerator(RandomNumberGeneratorDefaults):
    """Java: org.mitre.synthea.helpers.DefaultRandomNumberGenerator."""

    def __init__(self, seed: int) -> None:
        """Java: DefaultRandomNumberGenerator#DefaultRandomNumberGenerator(long)."""
        self.seed = seed
        self.random = JavaRandom(seed)
        self.count = 0


    @overload
    def rand(self) -> float: ...

    @overload
    def rand(self, low: float, high: float) -> float: ...

    @overload
    def rand(self, low: float, high: float, decimals: int | None) -> float: ...

    @overload
    def rand(self, low: list[float] | list[int]) -> float: ...

    @overload
    def rand(self, low: str, *choices: str) -> str: ...

    def rand(
        self,
        low: float | list[float] | list[int] | str | None = None,
        high: float | str | None = None,
        decimals: int | str | None = None,
        *rest: str,
    ) -> float | str:
        """Java: DefaultRandomNumberGenerator#rand and interface default overloads."""
        if low is None and high is None and decimals is None and not rest:
            return self._rand()
        if isinstance(low, str):
            raw_choices = (low, high, decimals, *rest)
            if not all(isinstance(choice, str) for choice in raw_choices if choice is not None):
                raise TypeError("choices must be strings")
            choices = tuple(choice for choice in raw_choices if isinstance(choice, str))
            return choices[self.rand_int(len(choices))]
        if isinstance(low, list):
            if high is not None or decimals is not None or rest:
                raise TypeError("array overload takes one argument")
            if len(low) != 2:
                raise ValueError(f"input range must be of length 2 -- got {low}")
            if low[0] > low[1]:
                raise ValueError(f"range must be of the form {{low, high}} -- got {low}")
            return float(low[0]) + (float(low[1]) - float(low[0])) * self._rand()
        if not isinstance(low, (float, int)) or not isinstance(high, (float, int)):
            raise TypeError("expected numeric low and high")
        if rest or (decimals is not None and not isinstance(decimals, int)):
            raise TypeError("expected optional integer decimal count")
        value = float(low) + ((float(high) - float(low)) * self._rand())
        if decimals is not None:
            assert isinstance(decimals, int)
            rounded = Decimal(str(value)).quantize(
                Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP
            )
            value = float(rounded)
        return value

    def get_seed(self) -> int:
        """Java: DefaultRandomNumberGenerator#getSeed."""
        return self.seed

    def _rand(self) -> float:
        """Java: DefaultRandomNumberGenerator#rand."""
        self.count += 1
        return self.random.next_double()

    def rand_boolean(self) -> bool:
        """Java: DefaultRandomNumberGenerator#randBoolean."""
        self.count += 1
        return self.random.next_boolean()

    def rand_gaussian(self) -> float:
        """Java: DefaultRandomNumberGenerator#randGaussian."""
        self.count += 1
        return self.random.next_gaussian()

    def rand_int(self, bound: int | None = None) -> int:
        """Java: DefaultRandomNumberGenerator#randInt() and #randInt(int)."""
        self.count += 1
        return self.random.next_int(bound)

    def rand_long(self) -> int:
        """Java: DefaultRandomNumberGenerator#randLong."""
        self.count += 1
        return self.random.next_long()

    def rand_uuid(self) -> str:
        """Java: DefaultRandomNumberGenerator#randUUID (one counted long call)."""
        return java_uuid(self.seed, self.rand_long())

    def get_count(self) -> int:
        """Java: DefaultRandomNumberGenerator#getCount."""
        return self.count
