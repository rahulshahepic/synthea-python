"""Java RandomNumberGenerator interface and default methods."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol, overload


class RandomNumberGenerator(Protocol):
    """Java: org.mitre.synthea.helpers.RandomNumberGenerator."""

    def rand(self, *args: float | int | list[float] | list[int] | str | None) -> float | str:
        """Java: RandomNumberGenerator#rand overloads."""
        ...

    def rand_boolean(self) -> bool:
        """Java: RandomNumberGenerator#randBoolean."""
        ...

    def rand_gaussian(self) -> float:
        """Java: RandomNumberGenerator#randGaussian."""
        ...

    def rand_int(self, bound: int | None = None) -> int:
        """Java: RandomNumberGenerator#randInt overloads."""
        ...

    def rand_long(self) -> int:
        """Java: RandomNumberGenerator#randLong."""
        ...

    def rand_uuid(self) -> str:
        """Java: RandomNumberGenerator#randUUID."""
        ...

    def get_count(self) -> int:
        """Java: RandomNumberGenerator#getCount."""
        ...

    def get_seed(self) -> int:
        """Java: RandomNumberGenerator#getSeed."""
        ...


class RandomNumberGeneratorDefaults(ABC):
    """Java: RandomNumberGenerator default rand overloads (mixin)."""

    @abstractmethod
    def _rand(self) -> float:
        """Java: RandomNumberGenerator#rand(), abstract primitive."""
        ...

    @abstractmethod
    def rand_int(self, bound: int | None = None) -> int:
        """Java: RandomNumberGenerator#randInt(int), abstract primitive."""
        ...

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
        """Java: RandomNumberGenerator#rand() and all interface default overloads."""
        if low is None and high is None and not rest:
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
            # Java BigDecimal has no signed zero after setScale/doubleValue.
            value = 0.0 if rounded == 0 else float(rounded)
        return value
